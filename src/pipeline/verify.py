"""Verification of tree-detection quality (feature 008).

Structured visual inspection of the reused canopy model on Mannheim
imagery: sample -> render -> rate -> report.

- Read-only over the workspace and the published map (FR-005/FR-010).
- CPU-only; never runs the model (OR-003).
- Contracts: specs/008-verify-tree-detection/contracts/.

Only implemented functions live here; no stubs. Subcommands are
registered in cli.py (verify-sample, verify-render, verify-report).
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import pyproj
from pyogrio import raw as pyogrio_raw
from shapely.geometry import box, shape
from shapely.ops import unary_union
from shapely.wkb import loads as wkb_loads

from . import workspace as ws

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# --------------------------------------------------------------------------
# Constants (contracts/verify-sample.md, verify-ratings.md, verify-report.md)
# --------------------------------------------------------------------------

DEFAULT_SEED = 20260805
SAMPLE_SIZE = 100
DISTRICT_FLOOR = 1

VALUE_BANDS: tuple[tuple[str, float, float], ...] = (
    ("0-10", 0.0, 10.0),
    ("10-30", 10.0, 30.0),
    ("30-100", 30.0, 100.0),
)

GSD_M = 0.2  # DOP20 ground sampling distance
PATCH_PX = 1024
PATCH_M = PATCH_PX * GSD_M

RATING_VALUES = ("correct", "over", "under")
FLAG_THRESHOLD = 0.5
MIN_CONCLUSIVE_N = 5
REINSPECT_EVERY = 10
DEGENERACIES = ("no-imagery", "empty-mask", "full-mask")

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------

VERIFICATION_DIR = REPO_ROOT / "verification"
STADTTEILE_FILE = VERIFICATION_DIR / "stadtteile.geojson"
SAMPLE_FILE = VERIFICATION_DIR / "sample.jsonl"
RATINGS_FILE = VERIFICATION_DIR / "ratings.jsonl"
NOTES_FILE = VERIFICATION_DIR / "notes.md"
REPORT_FILE = VERIFICATION_DIR / "report.md"
PATCHES_DIR = VERIFICATION_DIR / "patches"

TILES_CSV = REPO_ROOT / "tiles.csv"

# Workspace inputs (relative to MANNHEIM_WORKSPACE / data/archive/workspace)
EXTRACT_DIR = "mosaic/extract"
CANOPY_MASK_REL = "mosaic/canopy_prediction_mask.tif"
BUILDINGS_VALUES_REL = "buildings.geojson"  # derived: values.py (60 m fftconvolve)


# --------------------------------------------------------------------------
# Small file helpers
# --------------------------------------------------------------------------

def read_jsonl(path: Path | str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path | str, rows: list[dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)


# --------------------------------------------------------------------------
# Input readers
# --------------------------------------------------------------------------

def load_districts() -> list[dict[str, Any]]:
    """Official GDI-MA Stadtteile (38) from verification/stadtteile.geojson."""
    fc = json.loads(STADTTEILE_FILE.read_text(encoding="utf-8"))
    districts: list[dict[str, Any]] = []
    for feature in fc["features"]:
        props = feature["properties"]
        districts.append(
            {
                "code": str(props["code"]),
                "name": props["name"],
                "polygon": shape(feature["geometry"]),
            }
        )
    districts.sort(key=lambda d: d["code"])
    return districts


def _read_geojson(path: Path) -> tuple[list[str], list[Any], list[Any]]:
    """Return (field names, column arrays, geometry rows) for a GeoJSON.

    Handles the pyogrio raw.read layout (0.13): result is
    (meta, geometry, field_data, field_mask) where field columns live in
    the last element in meta["fields"] order and geometry rows are WKB.
    """
    _meta, geometry, field_data, columns = pyogrio_raw.read(path)
    fields = [str(f) for f in _meta["fields"]]
    if columns is None and field_data is not None and hasattr(field_data, "dtype"):
        structured = field_data
        if structured.dtype.names is not None:
            columns = [structured[name] for name in fields]
        else:
            raise ValueError(f"unexpected pyogrio layout for {path}")
    if columns is None:
        raise ValueError(f"no field data for {path}")
    wkb = geometry if geometry is not None else field_data
    return fields, columns, wkb


def load_buildings_frame(workspace_root: Path | None = None) -> list[dict[str, Any]]:
    """Sampling frame: buildings with values, inside the city boundary.

    Each entry: id, value (%), centroid (x, y) in EPSG:25832.
    """
    root = Path(workspace_root) if workspace_root is not None else ws.workspace_root()
    path = root / BUILDINGS_VALUES_REL
    fields, columns, wkb_rows = _read_geojson(path)
    index = {name: fields.index(name) for name in ("id", "value", "has_value", "in_boundary")}
    ids = columns[index["id"]]
    values = columns[index["value"]]
    has_value = columns[index["has_value"]]
    in_boundary = columns[index["in_boundary"]]

    # The derived buildings file is EPSG:4326 (values.py OUT_CRS); the
    # verification geometry (districts, tiles, mask) is EPSG:25832.
    transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:25832", always_xy=True)

    frame: list[dict[str, Any]] = []
    for i in range(len(ids)):
        if bool(has_value[i]) and bool(in_boundary[i]) and values[i] is not None:
            geom = wkb_loads(wkb_rows[i])
            centroid = geom.centroid
            x, y = transformer.transform(centroid.x, centroid.y)
            frame.append(
                {
                    "id": str(ids[i]),
                    "value": float(values[i]),
                    "cx": x,
                    "cy": y,
                }
            )
    return frame


def load_imagery_extent(workspace_root: Path | None = None) -> Any:
    """Union of the DOP20 tile footprints actually present in the workspace.

    Tiles are 1 km x 1 km at 0.2 m GSD (5000 px). The easting/northing
    km grid reference is parsed from the tile file name
    (dop20rgb_32_<e>_<n>_1_bw_<year>.tif).
    """
    root = Path(workspace_root) if workspace_root is not None else ws.workspace_root()
    extract = root / EXTRACT_DIR
    boxes = []
    for tif in sorted(extract.glob("dop20rgb_*.tif")):
        # dop20rgb_32_457_5488_1_bw_2024.tif -> easting 457, northing 5488
        parts = tif.stem.split("_")
        if len(parts) < 4:
            continue
        try:
            e_km = int(parts[2])
            n_km = int(parts[3])
        except ValueError:
            continue
        boxes.append(box(e_km * 1000, n_km * 1000, (e_km + 1) * 1000, (n_km + 1) * 1000))
    if not boxes:
        raise ValueError(f"no DOP20 tiles found in {extract}")
    return unary_union(boxes)


def band_name(value: float) -> str:
    """Value band label for a building value in percent."""
    for name, lo, hi in VALUE_BANDS:
        if lo <= value < hi:
            return name
    return VALUE_BANDS[-1][0]  # value == 100.0


# --------------------------------------------------------------------------
# Sample selection (contracts/verify-sample.md, FR-004)
# --------------------------------------------------------------------------

def _assign_districts(frame: list[dict[str, Any]], districts: list[dict[str, Any]]) -> dict[str, list[int]]:
    """Map each frame index to its district code via STRtree lookup."""
    from shapely.geometry import Point
    from shapely.strtree import STRtree

    tree = STRtree([d["polygon"] for d in districts])
    by_code: dict[str, list[int]] = {}
    for i, b in enumerate(frame):
        point = Point(b["cx"], b["cy"])
        for idx in tree.query(point):
            if districts[idx]["polygon"].contains(point):
                code = districts[idx]["code"]
                by_code.setdefault(code, []).append(i)
                break
    return by_code


def select_sample(
    workspace_root: Path | None = None,
    seed: int = DEFAULT_SEED,
    districts: list[dict[str, Any]] | None = None,
    frame: list[dict[str, Any]] | None = None,
    extent: Any | None = None,
    size: int = SAMPLE_SIZE,
    floor: int = DISTRICT_FLOOR,
) -> list[dict[str, Any]]:
    """Draw the reproducible verification sample (contracts/verify-sample.md).

    Allocation: district share proportional to building count, floor of
    `floor` per district with buildings, remainder by largest remainder;
    within a district, the same across its non-empty value bands.
    Draws are seeded and without replacement; centers outside the imagery
    extent are replaced deterministically from the same cell and marked
    `resampled: true`.
    """
    if districts is None:
        districts = load_districts()
    if frame is None:
        frame = load_buildings_frame(workspace_root)
    if extent is None:
        extent = load_imagery_extent(workspace_root)

    rng = random.Random(seed)
    by_code = _assign_districts(frame, districts)

    # District allocation: floor + largest remainder on building counts.
    codes = [d["code"] for d in districts]
    counts = [len(by_code.get(c, [])) for c in codes]
    district_seats = _largest_remainder_allocation(counts, size, floor)

    records: list[dict[str, Any]] = []
    for code, seats in zip(codes, district_seats):
        indices = by_code.get(code, [])
        if not indices or seats <= 0:
            continue
        # Band allocation within the district (non-empty bands only).
        band_counts: dict[str, int] = {}
        for i in indices:
            band_counts[band_name(frame[i]["value"])] = band_counts.get(band_name(frame[i]["value"]), 0) + 1
        bands = [b[0] for b in VALUE_BANDS]
        band_seats = _largest_remainder_allocation([band_counts.get(b, 0) for b in bands], seats, 0)
        for band, bseats in zip(bands, band_seats):
            if bseats <= 0:
                continue
            cell = [i for i in indices if band_name(frame[i]["value"]) == band]
            if not cell:
                continue
            order = rng.sample(cell, len(cell))
            for _ in range(bseats):
                chosen, resampled = _pick_in_extent(order, frame, extent)
                b = frame[chosen]
                records.append(
                    {
                        "patch_id": "",
                        "seed": seed,
                        "district_code": code,
                        "district_name": _district_name(districts, code),
                        "value_band": band,
                        "center_easting": round(b["cx"], 1),
                        "center_northing": round(b["cy"], 1),
                        "building_id": b["id"],
                        "resampled": resampled,
                        "degeneracy": None,
                    }
                )
                order.remove(chosen)

    records.sort(key=lambda r: (r["district_code"], r["value_band"]))
    for n, rec in enumerate(records, start=1):
        rec["patch_id"] = f"p{n:03d}"
    return records


def _largest_remainder_allocation(counts: list[int], seats: int, floor: int) -> list[int]:
    """Allocate seats proportional to counts (largest remainder), enforcing a
    floor per non-zero count. Districts raised to the floor leave the pool;
    the rest split the remaining seats proportionally."""
    result = [0] * len(counts)
    pool = {i for i, c in enumerate(counts) if c > 0}
    remaining = seats
    while pool and remaining > 0:
        total = sum(counts[i] for i in pool)
        exact = {i: counts[i] * remaining / total for i in pool}
        base = {i: int(exact[i]) for i in pool}
        leftover = remaining - sum(base.values())
        for i in sorted(pool, key=lambda i: exact[i] - base[i], reverse=True)[:leftover]:
            base[i] += 1
        deficit = [i for i in pool if base[i] < floor]
        if deficit:
            for i in deficit:
                give = min(floor - base[i], counts[i], remaining)
                result[i] += give
                remaining -= give
                pool.discard(i)
            continue
        for i in pool:
            result[i] += base[i]
        break
    return result


def _pick_in_extent(order: list[int], frame: list[dict[str, Any]], extent: Any) -> tuple[int, bool]:
    """First pool element inside the extent; if none, first element, flagged."""
    from shapely.geometry import Point

    for i, idx in enumerate(order):
        b = frame[idx]
        if extent.contains(Point(b["cx"], b["cy"])):
            return idx, i > 0
    return order[0], True


def _district_name(districts: list[dict[str, Any]], code: str) -> str:
    for d in districts:
        if d["code"] == code:
            return d["name"]
    return code




# --------------------------------------------------------------------------
# Patch rendering (contracts/verify-sample.md step 7, research R-4)
# --------------------------------------------------------------------------

def _tile_bounds(path: Path) -> tuple[float, float, float, float] | None:
    """1 km tile footprint from the filename grid reference (EPSG:25832)."""
    parts = path.stem.split("_")  # dop20rgb_32_457_5488_1_bw_2024.tif
    if len(parts) < 4:
        return None
    try:
        e = int(parts[2])
        n = int(parts[3])
    except ValueError:
        return None
    return (e * 1000, n * 1000, (e + 1) * 1000, (n + 1) * 1000)


def _overlapping_tiles(extract: Path, bounds: tuple[float, float, float, float]) -> list[Path]:
    x0, y0, x1, y1 = bounds
    tiles: list[Path] = []
    for e in range(int(x0 // 1000), int((x1 - 1e-9) // 1000) + 1):
        for n in range(int(y0 // 1000), int((y1 - 1e-9) // 1000) + 1):
            tiles.extend(sorted(extract.glob(f"dop20rgb_32_{e}_{n}_1_bw_*.tif")))
    return tiles


def _intersect(a: tuple[float, float, float, float], b: tuple[float, float, float, float]):
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return (x0, y0, x1, y1)


def _read_window(path: Path, bounds: tuple[float, float, float, float]):
    """Read (3, h, w) uint8 RGB clipped to the raster extent; None if no overlap."""
    import rasterio
    from rasterio.windows import from_bounds

    with rasterio.open(path) as src:
        b = src.bounds
        clipped = _intersect(bounds, (b.left, b.bottom, b.right, b.top))
        if clipped is None:
            return None
        win = from_bounds(*clipped, transform=src.transform)
        data = src.read(window=win)
        return data, (clipped[0], clipped[3])  # (west, north) — rows are north-up


def _mask_window(path: Path, bounds: tuple[float, float, float, float], px: int):
    """Binary mask for `bounds` placed on a px x px grid; None if no overlap."""
    import rasterio
    from rasterio.windows import from_bounds

    with rasterio.open(path) as src:
        b = src.bounds
        clipped = _intersect(bounds, (b.left, b.bottom, b.right, b.top))
        if clipped is None:
            return None
        win = from_bounds(*clipped, transform=src.transform)
        data = src.read(window=win)
    grid = np.zeros((px, px), dtype=np.uint8)
    ox = round((clipped[0] - bounds[0]) / GSD_M)
    oy = round((bounds[3] - clipped[3]) / GSD_M)  # north-anchored, rows north-up
    h, w = data.shape[1], data.shape[2]
    hh = min(h, px - oy)
    ww = min(w, px - ox)
    if hh > 0 and ww > 0:
        grid[oy : oy + hh, ox : ox + ww] = (data[0][:hh, :ww] > 0).astype(np.uint8)
    return grid


def render_patches(
    workspace_root: Path | None = None,
    sample: list[dict[str, Any]] | None = None,
    sample_path: Path | str | None = None,
    patches_dir: Path | str | None = None,
    mask_rel: str | None = None,
) -> list[dict[str, Any]]:
    """Render review PNGs with the canopy-mask overlay; classify degeneracy.

    Windows are PATCH_PX x PATCH_PX (PATCH_M x PATCH_M at 0.2 m GSD),
    EPSG:25832. Windowed reads only — no full tile is ever loaded
    (OR-001). Degeneracies per contract: no-imagery (no tile overlap;
    no PNG), empty-mask (no tree pixels in the window), full-mask
    (> 99 % tree pixels). Degeneracy is persisted back into the sample
    file (FR-008). `mask_rel` selects a workspace-relative mask (default:
    the published canopy mask), enabling per-candidate re-rendering.
    """
    root = Path(workspace_root) if workspace_root is not None else ws.workspace_root()
    extract = root / EXTRACT_DIR
    mask_path = root / (mask_rel or CANOPY_MASK_REL)
    if sample is None:
        sample = read_jsonl(SAMPLE_FILE)
    out_path = Path(sample_path) if sample_path is not None else SAMPLE_FILE
    pdir = Path(patches_dir) if patches_dir is not None else PATCHES_DIR
    pdir.mkdir(parents=True, exist_ok=True)

    half = PATCH_M / 2.0
    tint = np.array([110, 210, 110], dtype=np.uint8)

    for rec in sample:
        cx = float(rec["center_easting"])
        cy = float(rec["center_northing"])
        w = (cx - half, cy - half, cx + half, cy + half)
        composite = np.zeros((PATCH_PX, PATCH_PX, 3), dtype=np.uint8)
        covered = False
        for tile in _overlapping_tiles(extract, w):
            tb = _tile_bounds(tile)
            if tb is None:
                continue
            inter = _intersect(w, tb)
            if inter is None:
                continue
            got = _read_window(tile, inter)
            if got is None:
                continue
            data, origin = got
            ox = round((origin[0] - w[0]) / GSD_M)
            oy = round((w[3] - origin[1]) / GSD_M)  # north-anchored
            h, wd = data.shape[1], data.shape[2]
            # rounding can push the window 1 px past the composite edge;
            # clip instead of letting numpy raise
            hh = min(h, PATCH_PX - oy)
            ww = min(wd, PATCH_PX - ox)
            if hh > 0 and ww > 0:
                composite[oy : oy + hh, ox : ox + ww] = data[:, :hh, :ww].transpose(1, 2, 0)
            covered = True
        if not covered:
            rec["degeneracy"] = "no-imagery"
            continue

        mask = _mask_window(mask_path, w, PATCH_PX)
        if mask is not None:
            fraction = float(mask.mean())
            if fraction == 0.0:
                rec["degeneracy"] = "empty-mask"
            elif fraction > 0.99:
                rec["degeneracy"] = "full-mask"
            blended = composite.astype(np.uint16)
            blended = np.where(
                mask[..., None] > 0,
                (blended + tint.astype(np.uint16)) // 2,
                blended,
            )
            composite = blended.astype(np.uint8)

        png = pdir / f"{rec['patch_id']}.png"
        import rasterio

        with rasterio.open(
            png, "w", driver="PNG", width=PATCH_PX, height=PATCH_PX, count=3, dtype="uint8"
        ) as dst:
            dst.write(composite.transpose(2, 0, 1))

    write_jsonl(out_path, sample)
    return sample


# --------------------------------------------------------------------------
# Report generation (contracts/verify-report.md, FR-003/006/007/008)
# --------------------------------------------------------------------------

_NOTES_HEADINGS = ("vergleich", "einschr", "empfehl")


def _notes_section(text: str, heading: str) -> str | None:
    """Body of a `## <heading>` section from the notes file, or None."""
    lines = text.splitlines()
    out: list[str] = []
    capture = False
    for line in lines:
        if line.startswith("## "):
            if capture:
                break
            capture = line[3:].strip().lower().startswith(heading)
            continue
        if capture:
            out.append(line)
    body = "\n".join(out).strip()
    return body or None


def _assessment(n: int, correct: int, over: int, under: int) -> str:
    if n < MIN_CONCLUSIVE_N:
        return "inconclusive"
    if correct / n >= FLAG_THRESHOLD:
        return "trustworthy"
    return "overstated" if over >= under else "understated"


def generate_report(
    sample: list[dict[str, Any]] | None = None,
    ratings: list[dict[str, Any]] | None = None,
    notes_text: str | None = None,
    today: str | None = None,
) -> str:
    """Generate the German findings report (contracts/verify-report.md).

    Raises ValueError on invalid input: unrated patches, unknown rating
    values, ratings for no-imagery patches, ratings for unknown patches,
    or a notes file missing the required sections.
    """
    import datetime

    if sample is None:
        sample = read_jsonl(SAMPLE_FILE)
    if ratings is None:
        ratings = read_jsonl(RATINGS_FILE)
    if notes_text is None:
        notes_text = NOTES_FILE.read_text(encoding="utf-8") if NOTES_FILE.exists() else ""
    if today is None:
        today = datetime.date.today().isoformat()

    sample_by_id = {r["patch_id"]: r for r in sample}
    rating_by_id: dict[str, dict[str, Any]] = {}
    for rec in ratings:
        pid = rec.get("patch_id")
        errors = validate_rating_record(rec)
        if errors:
            raise ValueError(f"ungueltiger Rating-Eintrag {pid}: {'; '.join(errors)}")
        if pid in rating_by_id:
            raise ValueError(f"doppelter Rating-Eintrag fuer {pid}")
        rating_by_id[pid] = rec

    unknown = sorted(set(rating_by_id) - set(sample_by_id))
    if unknown:
        raise ValueError(f"Ratings fuer unbekannte Patches: {unknown}")
    no_imagery_rated = [
        pid for pid in rating_by_id if sample_by_id[pid].get("degeneracy") == "no-imagery"
    ]
    if no_imagery_rated:
        raise ValueError(f"Ratings fuer no-imagery Patches: {no_imagery_rated}")
    unrated = [
        pid
        for pid, rec in sample_by_id.items()
        if rec.get("degeneracy") != "no-imagery" and pid not in rating_by_id
    ]
    if unrated:
        raise ValueError(f"fehlende Ratings fuer {len(unrated)} Patches: {unrated[:5]} ...")

    comparison = _notes_section(notes_text, "vergleich")
    limitations_extra = _notes_section(notes_text, "einschr")
    recommendations = _notes_section(notes_text, "empfehl")
    if comparison is None or limitations_extra is None or recommendations is None:
        raise ValueError(
            "notes.md muss die Sektionen '## Vergleich mit dem Referenz-Transferproblem', "
            "'## Einschraenkungen' und '## Empfehlungen' enthalten"
        )

    seed = sample[0]["seed"] if sample else DEFAULT_SEED
    n_sample = len(sample)

    counts = {r: sum(1 for x in rating_by_id.values() if x["rating"] == r) for r in RATING_VALUES}
    n_rated = len(rating_by_id)
    deg = {d: sum(1 for r in sample if r.get("degeneracy") == d) for d in DEGENERACIES}
    deg_summary = ", ".join(f"{d}: {c}" for d, c in deg.items() if c)

    by_district: dict[str, list[dict[str, Any]]] = {}
    for rec in ratings:
        by_district.setdefault(rec["district_code"], []).append(rec)
    name_by_code = {r["district_code"]: r["district_name"] for r in sample}
    small: list[str] = []
    rows: list[str] = []
    for code in sorted(by_district):
        rs = by_district[code]
        n = len(rs)
        correct = sum(1 for r in rs if r["rating"] == "correct")
        over = sum(1 for r in rs if r["rating"] == "over")
        under = sum(1 for r in rs if r["rating"] == "under")
        assess = _assessment(n, correct, over, under)
        flag = "FLAGGED" if n and correct / n < FLAG_THRESHOLD else ""
        if n < MIN_CONCLUSIVE_N:
            small.append(name_by_code.get(code, code))
        rows.append(
            f"| {name_by_code.get(code, code)} | {n} | {correct} | {over} | {under} | {assess} | {flag} |"
        )

    correct_share = f"{counts['correct'] / n_rated:.1%}" if n_rated else "n/a"
    small_list = ", ".join(small) if small else "keine"

    return f"""# Verifikation der Baumerkennung (Mannheim)

Datum: {today} | Seed: {seed} | Stichprobe: {n_sample} Patches | Bezirksdaten: Stadt Mannheim, GDI-MA, dl-de/by-2-0

## Methode

- Stichprobendesign: 38 Stadtteile x Wertbaender 0-10 / 10-30 / 30-100, proportional nach Gebaeudeanzahl, Mindestzahl 1 pro Stadtteil, groesster Rest.
- Seed: {seed}; Auswahl deterministisch und reproduzierbar.
- Bewertungskriterien: contracts/verify-ratings.md (correct / over / under).
- Wiederholungspruefung: jedes 10. Patch erneut bewertet.

## Gesamtergebnis

- Bewertete Patches: {n_rated}; correct: {counts['correct']} ({counts['correct'] / n_rated:.1%}), over: {counts['over']}, under: {counts['under']}.
- Korrektheitsanteil gesamt: {correct_share} (Referenzwert fuer die Stadtteil-Flags).
- Nicht bewertet (no-imagery): {deg.get('no-imagery', 0)}.

## Ergebnisse nach Stadtteil

| Stadtteil | n | correct | over | under | Einschaetzung | Flag |
|-----------|----|---------|------|-------|---------------|------|
{chr(10).join(rows)}

## Vergleich mit dem Referenz-Transferproblem

{comparison}

## Einschraenkungen

- Degenerierte Patches: {deg_summary or 'keine'}.
- Kleine Stichproben (n < 5): {small_list}.
- {limitations_extra}

## Empfehlungen

{recommendations}
"""


# --------------------------------------------------------------------------
# Value delta (contracts/value-delta.md, FR-005/008)
# --------------------------------------------------------------------------

BOUNDARY_INPUT = "boundary.geojson"
BUILDINGS_INPUT = "tables/buildings.geojson"
PUBLISHED_VALUES_REL = "buildings.geojson"  # derived: values.py (EPSG:4326, `value`)


def _threshold_from_stem(stem: str) -> float | None:
    """Expected threshold from a mask stem like canopy_prediction_mask_t060."""
    marker = "_t"
    if marker not in stem:
        return None
    digits = stem.rsplit(marker, 1)[-1]
    if not digits.isdigit() or len(digits) != 3:
        return None
    return int(digits) / 1000.0


def compute_delta_rows(
    published: list[dict[str, Any]], candidate: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Join candidate values against published values per building_id.

    delta = value_candidate - value_published. Every published building
    must appear exactly once in the candidate set.
    """
    candidate_by_id = {b["id"]: b for b in candidate}
    rows: list[dict[str, Any]] = []
    for b in published:
        cand = candidate_by_id.get(b["id"])
        if cand is None:
            raise ValueError(f"candidate value missing for building {b['id']}")
        v_pub = b.get("value")
        v_cand = cand.get("value")
        if v_pub is None or v_cand is None:
            raise ValueError(f"missing value for building {b['id']} (pub={v_pub}, cand={v_cand})")
        rows.append(
            {
                "building_id": b["id"],
                "value_published": float(v_pub),
                "value_candidate": float(v_cand),
                "delta": float(v_cand) - float(v_pub),
            }
        )
    if len(rows) != len(published):
        raise ValueError("candidate/published building sets differ")
    return rows


def value_delta(
    mask_rel: str,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    """Per-building value comparison candidate vs published.

    Trust checks (FR-008): companion metadata exists, records the
    threshold, EPSG:25832 and 0.2 m GSD; candidate extent matches the
    published mask. Returns the summary; the CLI writes the artifacts.
    """
    import rasterio

    from . import boundary as boundary_mod
    from . import buildings as buildings_mod
    from . import values as values_mod

    root = Path(workspace_root) if workspace_root is not None else ws.workspace_root()
    mask_path = root / mask_rel
    meta_path = mask_path.with_suffix(".json")
    if not meta_path.exists():
        raise ValueError(f"missing metadata for {mask_rel}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if not isinstance(meta.get("threshold"), (int, float)):
        raise ValueError(f"metadata for {mask_rel} has no numeric threshold")
    expected = _threshold_from_stem(Path(mask_rel).stem)
    if expected is not None and abs(float(meta["threshold"]) - expected) > 1e-9:
        raise ValueError(
            f"metadata threshold {meta['threshold']} != filename threshold {expected}"
        )
    if meta.get("crs") != "EPSG:25832":
        raise ValueError(f"metadata crs {meta.get('crs')!r} != EPSG:25832")
    gsd = meta.get("ground_sampling_distance_m")
    if gsd is not None and abs(float(gsd) - GSD_M) > 1e-9:
        raise ValueError(f"metadata gsd {gsd} != {GSD_M}")
    with rasterio.open(mask_path) as cand, rasterio.open(root / CANOPY_MASK_REL) as pub:
        if (cand.bounds, cand.width, cand.height) != (pub.bounds, pub.width, pub.height):
            raise ValueError(f"candidate extent/size != published mask")

    boundary = boundary_mod.load_boundary(root / BOUNDARY_INPUT)
    buffered = boundary_mod.load_buffered(root / BOUNDARY_INPUT)
    buildings = buildings_mod.load_buildings(root / BUILDINGS_INPUT)
    selected = buildings_mod.select_in_buffer(buildings, buffered["geometry"])
    out_path = root / f"buildings_candidate_{Path(mask_rel).stem}.geojson"
    features = values_mod.compute_building_values(
        mask_path, selected, out_path, boundary["geometry"]
    )
    candidate = [f["properties"] for f in features]
    published_path = root / PUBLISHED_VALUES_REL
    _fields, _columns, _wkb = _read_geojson(published_path)
    index = {name: _fields.index(name) for name in ("id", "value")}
    published = [
        {"id": str(i), "value": float(v)}
        for i, v in zip(_columns[index["id"]], _columns[index["value"]])
        if v is not None
    ]
    rows = compute_delta_rows(published, candidate)
    return summarize_deltas(rows, mask_rel, meta.get("threshold"))


def summarize_deltas(
    rows: list[dict[str, Any]], mask_rel: str, threshold: float
) -> dict[str, Any]:
    """Aggregates per contract (city level)."""
    import statistics

    deltas = [r["delta"] for r in rows]
    n_moved = sum(1 for d in deltas if abs(d) > 0.5)
    summary: dict[str, Any] = {
        "mask": mask_rel,
        "threshold": threshold,
        "n_buildings": len(rows),
        "mean_delta": round(statistics.mean(deltas), 4),
        "mean_abs_delta": round(statistics.mean(abs(d) for d in deltas), 4),
        "share_moved_gt_0_5pp": round(n_moved / len(rows), 4),
        "city_mean_published": round(statistics.mean(r["value_published"] for r in rows), 4),
        "city_mean_candidate": round(statistics.mean(r["value_candidate"] for r in rows), 4),
    }
    return summary


def validate_sample_record(rec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(rec.get("patch_id"), str) or not rec["patch_id"].startswith("p"):
        errors.append("patch_id must be a string starting with 'p'")
    if not isinstance(rec.get("seed"), int):
        errors.append("seed must be an integer")
    if not isinstance(rec.get("district_code"), str) or len(rec["district_code"]) != 3:
        errors.append("district_code must be a 3-digit string")
    if not isinstance(rec.get("district_name"), str) or not rec["district_name"]:
        errors.append("district_name must be a non-empty string")
    if rec.get("value_band") not in [b[0] for b in VALUE_BANDS]:
        errors.append("value_band must be one of 0-10, 10-30, 30-100")
    for key in ("center_easting", "center_northing"):
        if not isinstance(rec.get(key), (int, float)):
            errors.append(f"{key} must be a number")
    if not isinstance(rec.get("building_id"), str) or not rec["building_id"]:
        errors.append("building_id must be a non-empty string")
    if not isinstance(rec.get("resampled"), bool):
        errors.append("resampled must be a boolean")
    if rec.get("degeneracy") is not None and rec["degeneracy"] not in DEGENERACIES:
        errors.append(f"degeneracy must be null or one of {DEGENERACIES}")
    return errors


def validate_rating_record(rec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(rec.get("patch_id"), str) or not rec["patch_id"]:
        errors.append("patch_id must be a non-empty string")
    if rec.get("rating") not in RATING_VALUES:
        errors.append(f"rating must be one of {RATING_VALUES}")
    if not isinstance(rec.get("note"), str):
        errors.append("note must be a string")
    if not isinstance(rec.get("ts"), str) or not rec["ts"]:
        errors.append("ts must be an ISO 8601 string")
    return errors
