"""Visual matching inputs: the watchlist as a compact catalog for screening, and one reference photo per
candidate (a sold comp of that model) so verification compares picture against picture."""

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from fyndjakt.images import ImageLoader
from fyndjakt.models import Comp, WatchModel


def catalog_text(models: list[WatchModel]) -> str:
    """One line per model. Stable order so the cached prompt prefix stays identical between calls."""
    lines = []
    for m in sorted(models, key=lambda m: m.id):
        bits = [f"{m.designer or '?'} – {m.model_name or '?'}"]
        if m.manufacturer:
            bits.append(m.manufacturer)
        if m.category:
            bits.append(m.category)
        if m.identifying_features:
            bits.append(m.identifying_features.replace("\n", " ")[:160])
        lines.append(f"{m.id}: " + ", ".join(bits))
    return (
        "Katalog över bevakade modeller (id: formgivare – modell, tillverkare, kategori, kännetecken):\n"
        + "\n".join(lines)
    )


def model_photos(
    session: Session,
    loader: ImageLoader,
    model_id: int,
    n: int = 5,
    max_px: int = 512,
    exclude_comp_ids: set[int] | None = None,
) -> list[dict]:
    """Up to n photos of different sold comps of a model, most expensive first (clearest examples)."""
    out: list[dict] = []
    comps = session.scalars(
        select(Comp)
        .where(Comp.model_id == model_id, Comp.state == "sold", Comp.hammer_sek.is_not(None))
        .order_by(desc(Comp.hammer_sek))
        .limit(n * 3)
    )
    for c in comps:
        if len(out) >= n:
            break
        if exclude_comp_ids and c.id in exclude_comp_ids or not c.image_urls:
            continue
        out += loader.blocks(c.image_urls[:1], max_px, 1)
    return out


def siblings(models: list[WatchModel], m: WatchModel) -> list[str]:
    return [o.model_name for o in models if o.id != m.id and o.designer == m.designer and o.model_name]


def reference_blocks(
    session: Session,
    loader: ImageLoader,
    model_ids: list[int],
    exclude_comp_ids: set[int] | None = None,
    max_px: int = 512,
) -> dict[int, dict]:
    """model id -> image block of a sold comp of that model (the most expensive one with photos: usually the
    clearest, most typical example). Models without a usable photo are left out."""
    out: dict[int, dict] = {}
    for mid in model_ids:
        comps = session.scalars(
            select(Comp)
            .where(Comp.model_id == mid, Comp.state == "sold", Comp.hammer_sek.is_not(None))
            .order_by(desc(Comp.hammer_sek))
            .limit(5)
        )
        for c in comps:
            if exclude_comp_ids and c.id in exclude_comp_ids or not c.image_urls:
                continue
            blocks = loader.blocks(c.image_urls[:1], max_px, 1)
            if blocks:
                out[mid] = blocks[0]
                break
    return out
