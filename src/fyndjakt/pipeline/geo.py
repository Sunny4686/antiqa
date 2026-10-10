"""Step 6: distance and transport cost."""

import csv
import math
from pathlib import Path

from fyndjakt.pipeline.prefilter import normalize

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def transport_sek(distance_km: float, base_sek: int, per_km_sek: float) -> int:
    """Round trip: base + per_km x 2 x distance."""
    return round(base_sek + per_km_sek * 2 * distance_km)


def load_municipalities(path: str | Path) -> dict[str, tuple[float, float, str | None]]:
    """CSV columns: kommun,lat,lon[,lan]. Returns normalised name -> (lat, lon, län)."""
    p = Path(path)
    if not p.exists():
        return {}
    out = {}
    with p.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[normalize(row["kommun"])] = (float(row["lat"]), float(row["lon"]), row.get("lan") or None)
    return out


def locate(
    lat: float | None,
    lon: float | None,
    municipality: str | None,
    municipalities: dict[str, tuple[float, float, str | None]],
) -> tuple[float, float, str | None] | None:
    """Prefer the listing's own coordinates; fall back to the municipality centroid."""
    region = None
    if municipality:
        hit = municipalities.get(normalize(municipality)) or municipalities.get(
            normalize(municipality.removesuffix(" kommun"))
        )
        if hit:
            region = hit[2]
            if lat is None or lon is None:
                return hit
    if lat is not None and lon is not None:
        return lat, lon, region
    return None
