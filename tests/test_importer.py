"""File import of listings the owner provides: folders, CSV, JSON, zip, the inbox folder and the upload page."""

import io
import json
import os
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import pytest
from PIL import Image
from sqlalchemy import select

from fyndjakt import importer
from fyndjakt.images import ImageLoader
from fyndjakt.models import Job, Listing
from tests.test_pages_m3 import client as client  # noqa: F401  (pytest fixture)


def _jpg() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (80, 60), (90, 60, 30)).save(buf, "JPEG")
    return buf.getvalue()


@pytest.mark.parametrize(
    ("text", "price"),
    [
        ("1 500 kr", 1500),
        ("1.200:-", 1200),
        ("800", 800),
        ("Gratis", 0),
        ("", None),
        ("Bud", None),
        ("2 500,00 kr", 2500),
    ],
)
def test_parse_price(text, price):
    assert importer.parse_price(text) == price


def test_parse_text_labels_and_plain():
    d = importer.parse_text(
        "Rubrik: Fåtölj ek\nPris: 800 kr\nOrt: Mölndal\nLänk: https://www.blocket.se/recommerce/forsale/item/77\n"
        "Källa: blocket\nBeskrivning:\nFin fåtölj.\nPris: står i texten"
    )
    assert (d.title, d.price_sek, d.place, d.source_hint) == ("Fåtölj ek", 800, "Mölndal", "blocket")
    assert d.description == "Fin fåtölj.\nPris: står i texten"  # labels inside the description are just text
    plain = importer.parse_text("\nGammal stol från mormor\nLite sliten men stabil.")
    assert plain.title == "Gammal stol från mormor" and plain.description == "Lite sliten men stabil."
    assert importer.source_for(None, "https://www.facebook.com/marketplace/item/1") == "fb_import"
    assert importer.source_for("Blocket", None) == "blocket_import" and importer.source_for(None, None) == "import"


def _folder(root: Path, name: str, text: str, n_images: int = 2) -> Path:
    f = root / name
    f.mkdir(parents=True)
    (f / "annons.txt").write_text(text, encoding="utf-8")
    for i in range(n_images):
        (f / f"{i}.jpg").write_bytes(_jpg())
    return f


def test_folder_csv_and_json_import(session, tmp_path):
    loader = ImageLoader(tmp_path / "img", "ua")
    src = tmp_path / "src"
    _folder(src, "a", "Rubrik: Fåtölj ek\nPris: 800\nLänk: https://www.blocket.se/recommerce/forsale/item/77")
    (src / "b").mkdir()
    (src / "b" / "x.jpg").write_bytes(_jpg())
    (src / "b" / "annonser.csv").write_text(
        "rubrik,pris,ort,kalla,bilder\nByrå teak,1200,Borås,facebook,x.jpg|saknas.jpg|../../etc/passwd\n,100,,,\n",
        encoding="utf-8",
    )
    (src / "c.json").write_text(json.dumps([{"title": "Soffbord", "price": 300, "images": ["https://img.x/1.jpg"]}]))
    res = importer.import_path(session, loader, src)
    assert len(res.imported) == 3 and len(res.errors) == 1 and "rubrik saknas" in res.errors[0]
    rows = {lst.title: lst for lst in session.scalars(select(Listing))}
    a, b, c = rows["Fåtölj ek"], rows["Byrå teak"], rows["Soffbord"]
    assert (a.source, a.external_id, len(a.image_urls)) == ("blocket_import", "77", 2)
    assert (b.source, b.municipality, len(b.image_urls)) == ("fb_import", "Borås", 1)  # path escape ignored
    assert c.source == "import" and c.image_urls == []  # remote image ignored while the flag is off
    assert all(u.startswith("local:") for u in a.image_urls + b.image_urls)
    # importing the same folder again updates instead of duplicating
    importer.import_path(session, loader, src / "a")
    assert len(list(session.scalars(select(Listing)))) == 3


def test_inbox_scan_waits_for_copy_then_moves(session, tmp_path):
    loader = ImageLoader(tmp_path / "img", "ua")
    inbox = tmp_path / "inbox"
    good = _folder(inbox, "lamino", "Fåtölj\nfin")
    bad = inbox / "trasig.csv"
    bad.write_text("rubrik\n\n", encoding="utf-8")
    now = datetime.now(UTC)
    assert importer.scan_inbox(session, loader, inbox, now).imported == []  # just written: still settling
    for p in [good, *good.iterdir(), bad]:
        os.utime(p, (now.timestamp() - 60, now.timestamp() - 60))
    res = importer.scan_inbox(session, loader, inbox, now)
    assert len(res.imported) == 1
    assert not good.exists() and not bad.exists()
    assert [p.name.split("-", 2)[2] for p in (inbox / "_klart").iterdir()] == ["lamino"]
    fel = list((inbox / "_fel").glob("*.fel.txt"))
    assert len(fel) == 1 and "inga annonser" in fel[0].read_text()
    assert session.scalar(select(Job).where(Job.kind == "assess")) is not None


def test_zip_import_rejects_path_escape(session, tmp_path):
    loader = ImageLoader(tmp_path / "img", "ua")
    good = tmp_path / "good.zip"
    with zipfile.ZipFile(good, "w") as z:
        z.writestr("annons/annons.txt", "Rubrik: Stol\nPris: 100")
        z.writestr("annons/1.jpg", _jpg())
    assert len(importer.import_zip(session, loader, good).imported) == 1
    evil = tmp_path / "evil.zip"
    with zipfile.ZipFile(evil, "w") as z:
        z.writestr("../utanfor.txt", "x")
    res = importer.import_zip(session, loader, evil)
    assert res.imported == [] and "otillåten sökväg" in res.errors[0]
    assert not (tmp_path / "utanfor.txt").exists()


def test_import_page_upload(client):  # noqa: F811
    from fyndjakt.db import session_scope

    assert "Importera annonser" in client.get("/importera").text
    files = [
        ("files", ("annons.txt", "Rubrik: Pinnstol\nPris: 50 kr\nOrt: Alingsås".encode(), "text/plain")),
        ("files", ("1.jpg", _jpg(), "image/jpeg")),
    ]
    page = client.post("/importera", files=files).text
    assert "1 annonser" in page and "Pinnstol" in page and "Bedöms" in page
    with session_scope() as s:
        lst = s.scalar(select(Listing))
        assert (lst.title, lst.price_sek, lst.municipality, len(lst.image_urls)) == ("Pinnstol", 50, "Alingsås", 1)


def test_inbox_scan_is_a_periodic_job():
    from fyndjakt.jobs import HANDLERS, PERIODIC

    assert "inbox_scan" in PERIODIC and "inbox_scan" in HANDLERS
    assert all(kind in HANDLERS for kind in PERIODIC)


def test_multi_listing_text_file_with_named_images(session, tmp_path):
    loader = ImageLoader(tmp_path / "img", "ua")
    src = tmp_path / "lista"
    src.mkdir()
    for n in ("a1.jpg", "a2.jpg", "b.jpg"):
        (src / n).write_bytes(_jpg())
    (src / "annonser.txt").write_text(
        "Rubrik: Fåtölj ek\nPris: 800\nBilder: a1.jpg, a2.jpg\nBeskrivning:\nFin.\n---\n"
        "Rubrik: Byrå teak\nPris: 1 200 kr\nKälla: facebook\nBilder: b.jpg\n",
        encoding="utf-8",
    )
    res = importer.import_path(session, loader, src)
    assert len(res.imported) == 2 and not res.errors
    rows = {lst.title: lst for lst in session.scalars(select(Listing))}
    assert len(rows["Fåtölj ek"].image_urls) == 2 and rows["Fåtölj ek"].description == "Fin."
    assert rows["Byrå teak"].price_sek == 1200 and rows["Byrå teak"].source == "fb_import"
    assert len(rows["Byrå teak"].image_urls) == 1


def test_screenshot_only_folder_queues_capture_jobs(session, tmp_path):
    loader = ImageLoader(tmp_path / "img", "ua")
    src = tmp_path / "blocket-skarmbilder"
    src.mkdir()
    for n in ("s1.png", "s2.png"):
        (src / n).write_bytes(_jpg())
    res = importer.import_path(session, loader, src, capture_dir=tmp_path / "captures")
    assert res.imported == [] and res.screenshots == 2 and not res.errors
    jobs = list(session.scalars(select(Job).where(Job.kind == "screen_capture")))
    assert len(jobs) == 2 and all(j.payload["source"] == "blocket_import" for j in jobs)
    assert all(Path(j.payload["path"]).exists() for j in jobs)
    assert src.exists() and len(list(src.iterdir())) == 2  # originals untouched (the inbox moves them)


def test_import_templates_download(client):  # noqa: F811
    txt = client.get("/importera/mall.txt")
    assert txt.status_code == 200 and "---" in txt.text and "Bilder:" in txt.text
    assert client.get("/importera/mall.csv").text.startswith("rubrik,pris,ort")
