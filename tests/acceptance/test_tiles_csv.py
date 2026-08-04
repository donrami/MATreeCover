"""tiles.csv index coverage (T055; completes T045).

`2026.01/meta.json` declares tile_count 460 for the full LGL DOP20 set
covering the region; the accepted workspace extract holds the 302 tiles
intersecting the buffered boundary. `tiles.csv` must index exactly those
accepted tiles, carry their grid coordinates, and agree with the imagery
`tile_count` recorded in `artifacts.manifest.json`.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

PATTERN = re.compile(r"dop20rgb_32_(\d+)_(\d+)_1_bw_(\d+)\.tif$")
HEADER = ("filename", "easting_km", "northing_km")
# Imagery extent from the manifest (m): x in [457000, 475000], y in [5472000, 5497000].
EASTING_KM_RANGE = (457, 474)
NORTHING_KM_RANGE = (5472, 5496)


def _extract_tiles(workspace: Path) -> set[str]:
    tiles = {
        p.name for p in (workspace / "mosaic" / "extract").glob("dop20rgb_*.tif")
    }
    return {t for t in tiles if PATTERN.match(t)}


def _read_index(repo_root: Path) -> list[dict[str, str]]:
    path = repo_root / "tiles.csv"
    assert path.exists(), "tiles.csv missing at repo root"
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows and list(rows[0].keys()) == list(HEADER), (
        f"tiles.csv header must be {HEADER}, got {list(rows[0].keys())}"
    )
    return rows


def test_index_covers_every_extract_tile(workspace, repo_root) -> None:
    """tiles.csv lists exactly the accepted extract tiles, no more, no less."""
    extract = _extract_tiles(workspace)
    assert extract, "no extract tiles found"
    indexed = {row["filename"] for row in _read_index(repo_root)}
    assert indexed == extract, (
        f"tiles.csv missing {sorted(extract - indexed)} and "
        f"has extra {sorted(indexed - extract)}"
    )


def test_grid_coordinates_match_filenames(workspace, repo_root) -> None:
    for row in _read_index(repo_root):
        m = PATTERN.match(row["filename"])
        assert m, f"unparseable filename {row['filename']!r}"
        easting, northing = int(m.group(1)), int(m.group(2))
        assert row["easting_km"] == str(easting), (
            f"{row['filename']}: easting_km {row['easting_km']!r} != {easting}"
        )
        assert row["northing_km"] == str(northing), (
            f"{row['filename']}: northing_km {row['northing_km']!r} != {northing}"
        )
        assert EASTING_KM_RANGE[0] <= easting <= EASTING_KM_RANGE[1], (
            f"{row['filename']}: easting {easting} outside {EASTING_KM_RANGE}"
        )
        assert NORTHING_KM_RANGE[0] <= northing <= NORTHING_KM_RANGE[1], (
            f"{row['filename']}: northing {northing} outside {NORTHING_KM_RANGE}"
        )


def test_rows_are_unique(workspace, repo_root) -> None:
    rows = _read_index(repo_root)
    names = [row["filename"] for row in rows]
    assert len(names) == len(set(names)), "duplicate rows in tiles.csv"
    assert len(rows) == len(_extract_tiles(workspace)), "row count mismatch"


def test_count_matches_manifest_tile_count(workspace, repo_root) -> None:
    manifest = json.loads((repo_root / "artifacts.manifest.json").read_text(encoding="utf-8"))
    imagery = next(a for a in manifest["artifacts"] if a["kind"] == "imagery")
    n_index = len(_read_index(repo_root))
    n_extract = len(_extract_tiles(workspace))
    assert imagery["tile_count"] == n_index, (
        f"manifest tile_count {imagery['tile_count']} != tiles.csv rows {n_index}"
    )
    assert imagery["tile_count"] == n_extract, (
        f"manifest tile_count {imagery['tile_count']} != extract tiles {n_extract}"
    )
