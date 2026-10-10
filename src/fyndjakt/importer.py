"""Import listings from files the owner provides (folder, CSV, zip). Nothing is fetched from listing sites here:
only local image files are used; remote image addresses are ignored unless ai_send_listing_images allows them.

Supported layouts inside the inbox (data/inbox) or an uploaded zip:

  one folder per listing     <folder>/annons.txt | annons.json  + image files (jpg/png/webp/heic as jpg)
  a CSV with many listings   annonser.csv with columns rubrik,pris,ort,lank,beskrivning,bilder,kalla,id
                             (bilder = file names separated by |, relative to the CSV's folder)
  loose JSON                 <name>.json with the same keys as annons.json, images next to it

annons.txt: "Rubrik: ...", "Pris: 1 500 kr", "Ort: ...", "Länk: ...", "Källa: blocket|facebook", "Id: ...",
and "Beskrivning:" followed by free text. A file without labels: first line = title, the rest = description.
"""

import csv
import hashlib
import json
import re
import shutil
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from fyndjakt.capture import item_id
from fyndjakt.images import ImageLoader
from fyndjakt.services import IngestListing, upsert_listing

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
TEXT_NAMES = ("annons.txt", "annons.json", "listing.txt", "listing.json")
DONE, FAILED = "_klart", "_fel"
MAX_IMAGES = 8

_LABEL = re.compile(
    r"^\s*(rubrik|titel|title|pris|price|ort|plats|place|länk|lank|url|källa|kalla|source|id)\s*:\s*(.*)$", re.I
)
_DESC = re.compile(r"^\s*(beskrivning|description|text)\s*:\s*(.*)$", re.I)


@dataclass
class Draft:
    title: str = ""
    price_sek: int | None = None
    place: str | None = None
    url: str | None = None
    description: str | None = None
    source_hint: str | None = None
    ext_id: str | None = None
    images: list[Path] = field(default_factory=list)
    remote_images: list[str] = field(default_factory=list)


def parse_price(text: str | None) -> int | None:
    """'1 500 kr' -> 1500, '1.200:-' -> 1200, 'Gratis' -> 0, '' -> None."""
    if not text:
        return None
    t = text.lower().replace("\xa0", " ")
    if any(w in t for w in ("gratis", "bortskänkes", "free")):
        return 0
    m = re.search(r"\d[\d .]*", t.split(",")[0])
    digits = re.sub(r"[^\d]", "", m.group(0)) if m else ""
    return int(digits) if digits else None


def source_for(hint: str | None, url: str | None) -> str:
    h = f"{hint or ''} {url or ''}".lower()
    if "facebook" in h or "marketplace" in h or (hint or "").strip().lower() == "fb":
        return "fb_import"
    if "blocket" in h:
        return "blocket_import"
    return "import"


def parse_text(text: str) -> Draft:
    d = Draft()
    free: list[str] = []  # unlabelled lines and everything after "Beskrivning:"
    in_desc = False
    for line in text.splitlines():
        m = None if in_desc else _LABEL.match(line)
        if m:
            key, val = m.group(1).lower(), m.group(2).strip() or None
            if key in ("rubrik", "titel", "title"):
                d.title = val or ""
            elif key in ("pris", "price"):
                d.price_sek = parse_price(val)
            elif key in ("ort", "plats", "place"):
                d.place = val
            elif key in ("länk", "lank", "url"):
                d.url = val
            elif key in ("källa", "kalla", "source"):
                d.source_hint = val
            else:
                d.ext_id = val
            continue
        m = _DESC.match(line) if not in_desc else None
        if m:
            in_desc = True
            line = m.group(2)
        free.append(line)
    if not d.title:  # no label: the first non-empty line is the title
        while free and not free[0].strip():
            free.pop(0)
        d.title = free.pop(0).strip() if free else ""
    d.description = "\n".join(free).strip() or None
    return d


def from_mapping(row: dict) -> Draft:
    def g(*keys: str) -> str | None:
        for k in keys:
            v = row.get(k)
            if v not in (None, ""):
                return str(v).strip()
        return None

    price = row.get("pris", row.get("price", row.get("price_sek")))
    return Draft(
        title=g("rubrik", "titel", "title") or "",
        price_sek=price if isinstance(price, int) else parse_price(str(price) if price is not None else None),
        place=g("ort", "plats", "place", "municipality"),
        url=g("lank", "länk", "url"),
        description=g("beskrivning", "description", "text"),
        source_hint=g("kalla", "källa", "source"),
        ext_id=g("id", "external_id"),
    )


def _split_images(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [p.strip() for p in str(value or "").split("|") if p.strip()]


def _attach_images(d: Draft, names: list[str], base: Path) -> None:
    for name in names:
        if name.startswith(("http://", "https://")):
            d.remote_images.append(name)
            continue
        p = (base / name).resolve()
        if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES and base.resolve() in p.parents:
            d.images.append(p)


def read_folder(folder: Path) -> Draft:
    """A folder for one listing: a text/json file plus images (all images in the folder, sorted by name)."""
    text_file = next((folder / n for n in TEXT_NAMES if (folder / n).is_file()), None)
    if text_file is None:
        text_file = next((p for p in sorted(folder.iterdir()) if p.suffix.lower() in (".txt", ".json")), None)
    if text_file is None:
        raise ValueError("ingen annons.txt eller annons.json i mappen")
    if text_file.suffix.lower() == ".json":
        data = json.loads(text_file.read_text(encoding="utf-8-sig"))
        d = from_mapping(data)
        _attach_images(d, _split_images(data.get("bilder", data.get("images"))), folder)
    else:
        d = parse_text(text_file.read_text(encoding="utf-8-sig"))
    if not d.images:
        d.images = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)
    return d


def read_csv(path: Path) -> list[Draft]:
    rows = list(csv.DictReader(path.read_text(encoding="utf-8-sig").splitlines()))
    out = []
    for row in rows:
        row = {(k or "").strip().lower(): v for k, v in row.items()}
        d = from_mapping(row)
        _attach_images(d, _split_images(row.get("bilder", row.get("images"))), path.parent)
        out.append(d)
    return out


def drafts_in(path: Path, errors: list[str] | None = None) -> list[Draft]:
    """Everything importable at path: a folder for one listing, a folder of folders/files, a CSV, JSON or TXT.
    Problems with one entry are added to errors (when given) instead of stopping the others."""
    errors = errors if errors is not None else []
    if path.is_file():
        suffix = path.suffix.lower()
        if suffix == ".csv":
            return read_csv(path)
        if suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            out = []
            for row in data if isinstance(data, list) else [data]:
                d = from_mapping(row)
                _attach_images(d, _split_images(row.get("bilder", row.get("images"))), path.parent)
                out.append(d)
            return out
        if suffix == ".txt":
            return [parse_text(path.read_text(encoding="utf-8-sig"))]
        raise ValueError(f"okänt filformat: {path.name}")
    entries = [p for p in sorted(path.iterdir()) if not p.name.startswith((".", "_"))]
    has_text = any((path / n).is_file() for n in TEXT_NAMES)
    has_list = any(p.suffix.lower() in (".csv", ".json") and p.name not in TEXT_NAMES for p in entries)
    has_images = any(p.suffix.lower() in IMAGE_SUFFIXES for p in entries)
    if has_text or (has_images and not has_list and any(p.suffix.lower() == ".txt" for p in entries)):
        return [read_folder(path)]  # one listing: its text file + its images
    out: list[Draft] = []
    for child in entries:
        if child.is_dir() or child.suffix.lower() in (".csv", ".json", ".txt"):
            try:
                out += drafts_in(child, errors)
            except (ValueError, OSError, json.JSONDecodeError, csv.Error) as e:
                errors.append(f"{child.name}: {e}")
    return out


def ingest_draft(session: Session, images: ImageLoader, d: Draft, remote_allowed: bool) -> int:
    if not d.title.strip():
        raise ValueError("rubrik saknas")
    urls = [images.save_upload(p.read_bytes()) for p in d.images[:MAX_IMAGES]]
    if remote_allowed:
        urls += d.remote_images[: max(MAX_IMAGES - len(urls), 0)]
    ext = d.ext_id or (item_id(d.url) if d.url else None)
    if not ext:
        key = f"{d.title.strip().lower()}|{d.price_sek}|{(d.place or '').lower()}|{d.url or ''}"
        ext = "f" + hashlib.sha256(key.encode()).hexdigest()[:20]
    listing, _new, _changed = upsert_listing(
        session,
        IngestListing(
            source=source_for(d.source_hint, d.url),
            external_id=ext[:64],
            title=d.title.strip()[:512],
            price_sek=d.price_sek,
            municipality=d.place,
            url=d.url,
            description=d.description,
            image_urls=urls,
        ),
    )
    return listing.id


@dataclass
class ImportResult:
    imported: list[int] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def import_path(session: Session, images: ImageLoader, path: Path, remote_allowed: bool = False) -> ImportResult:
    res = ImportResult()
    try:
        drafts = drafts_in(path, res.errors)
    except (ValueError, OSError, json.JSONDecodeError, csv.Error) as e:
        res.errors.append(f"{path.name}: {e}")
        return res
    for i, d in enumerate(drafts, 1):
        try:
            res.imported.append(ingest_draft(session, images, d, remote_allowed))
        except Exception as e:  # one bad listing must not stop the rest
            res.errors.append(f"{path.name} #{i} ({d.title[:40] or 'utan rubrik'}): {e}")
    return res


def scan_inbox(
    session: Session,
    images: ImageLoader,
    inbox: Path,
    now: datetime,
    settle_s: float = 10.0,
    remote_allowed: bool = False,
) -> ImportResult:
    """Import every entry in the inbox that hasn't changed for settle_s seconds, then move it to _klart or _fel."""
    total = ImportResult()
    inbox.mkdir(parents=True, exist_ok=True)
    for entry in sorted(inbox.iterdir()):
        if entry.name.startswith((".", "_")):
            continue
        newest = max((p.stat().st_mtime for p in [entry, *entry.rglob("*")]), default=0)
        if now.timestamp() - newest < settle_s:
            continue  # still being copied
        if entry.suffix.lower() == ".zip":
            res = import_zip(session, images, entry, remote_allowed)
        else:
            res = import_path(session, images, entry, remote_allowed)
        if not res.imported and not res.errors:
            res.errors.append(f"{entry.name}: inga annonser hittades")
        total.imported += res.imported
        total.errors += res.errors
        target = inbox / (FAILED if res.errors and not res.imported else DONE)
        target.mkdir(exist_ok=True)
        dest = target / f"{now:%Y%m%d-%H%M%S}-{entry.name}"
        shutil.move(str(entry), dest)
        if res.errors:
            (target / f"{dest.name}.fel.txt").write_text("\n".join(res.errors), encoding="utf-8")
    return total


def import_zip(session: Session, images: ImageLoader, zip_path: Path, remote_allowed: bool = False) -> ImportResult:
    """Unpack into a temporary folder next to the zip (refusing paths that escape it) and import that."""
    tmp = zip_path.parent / f"_unzip-{zip_path.stem}"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir()
    try:
        with zipfile.ZipFile(zip_path) as z:
            for info in z.infolist():
                target = (tmp / info.filename).resolve()
                if tmp.resolve() not in target.parents and target != tmp.resolve():
                    raise ValueError(f"otillåten sökväg i zip: {info.filename}")
                if info.file_size > 20 * 1024 * 1024:
                    raise ValueError(f"för stor fil i zip: {info.filename}")
            z.extractall(tmp)
        inner = [p for p in tmp.iterdir() if not p.name.startswith((".", "__MACOSX"))]
        root = inner[0] if len(inner) == 1 and inner[0].is_dir() else tmp
        res = import_path(session, images, root, remote_allowed)
        if res.imported or res.errors:
            return res
        return ImportResult(errors=[f"{zip_path.name}: inga annonser hittades"])
    except (zipfile.BadZipFile, ValueError) as e:
        return ImportResult(errors=[f"{zip_path.name}: {e}"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
