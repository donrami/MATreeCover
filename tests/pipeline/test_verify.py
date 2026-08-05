"""Feature 008 verification tests (tasks T005, T008, T011).

- US1 sample: reproducibility, allocation, coverage, schema
- US2 render: determinism, dimensions, degeneracy classification
- US3 report: structure, flagging rule, disclosure, validation

Read-only over the mannheim workspace (conftest `workspace` fixture);
synthetic fixtures for deterministic unit tests. Tests reference the
contracts in specs/008-verify-tree-detection/contracts/.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from shapely.geometry import box

from src.pipeline import verify as v

# --------------------------------------------------------------------------
# Synthetic fixtures (EPSG:25832)
# --------------------------------------------------------------------------


def _synthetic_districts() -> list[dict]:
    return [
        {"code": "011", "name": "A", "polygon": box(1000, 1000, 2000, 2000)},
        {"code": "020", "name": "B", "polygon": box(3000, 1000, 4000, 2000)},
        {"code": "030", "name": "C", "polygon": box(5000, 1000, 6000, 2000)},
    ]


def _synthetic_frame(n_per_district: int = 60) -> list[dict]:
    """Buildings on a 15 m grid strictly inside each district, values cycling bands.

    Districts are 1000 m boxes; 60 buildings at 15 m spacing span
    100..985 m inside the box (margin 15 m), so every building is
    assigned to its own district."""
    frame: list[dict] = []
    bid = 0
    for code, dx in (("011", 1000), ("020", 3000), ("030", 5000)):
        for i in range(n_per_district):
            value = [3.0, 15.0, 40.0][i % 3]
            frame.append(
                {
                    "id": f"b-{bid:04d}",
                    "value": value,
                    "cx": dx + 100.0 + 15.0 * i,
                    "cy": 1500.0,
                }
            )
            bid += 1
    return frame


def _synthetic_extent() -> object:
    districts = _synthetic_districts()
    from shapely.ops import unary_union

    return unary_union([d["polygon"] for d in districts])


def _largest_remainder(shares: list[float], seats: int) -> list[int]:
    """Independent largest-remainder allocation for assertions."""
    total = sum(shares)
    if total <= 0:
        return [0] * len(shares)
    exact = [s * seats / total for s in shares]
    base = [int(x) for x in exact]
    remainder = seats - sum(base)
    order = sorted(range(len(exact)), key=lambda i: exact[i] - base[i], reverse=True)
    for i in order[:remainder]:
        base[i] += 1
    return base


# --------------------------------------------------------------------------
# US1: sample (T005)
# --------------------------------------------------------------------------


def test_sample_reproducible_synthetic() -> None:
    districts = _synthetic_districts()
    frame = _synthetic_frame()
    extent = _synthetic_extent()
    first = v.select_sample(seed=20260805, districts=districts, frame=frame, extent=extent)
    second = v.select_sample(seed=20260805, districts=districts, frame=frame, extent=extent)
    assert first == second
    assert len(first) == v.SAMPLE_SIZE


def test_sample_different_seed_differs() -> None:
    districts = _synthetic_districts()
    frame = _synthetic_frame()
    extent = _synthetic_extent()
    a = v.select_sample(seed=1, districts=districts, frame=frame, extent=extent)
    b = v.select_sample(seed=2, districts=districts, frame=frame, extent=extent)
    assert a != b


def test_sample_allocation_proportional_with_floor() -> None:
    districts = _synthetic_districts()
    frame = _synthetic_frame(n_per_district=10)  # 10, 10, 10 buildings
    extent = _synthetic_extent()
    records = v.select_sample(seed=7, districts=districts, frame=frame, extent=extent, size=10)
    counts = {code: 0 for code in ("011", "020", "030")}
    for rec in records:
        counts[rec["district_code"]] += 1
    # equal building counts -> equal shares (largest remainder, floor 1)
    expected = _largest_remainder([10, 10, 10], 10)
    got = [counts[c] for c in ("011", "020", "030")]
    assert got == expected
    assert all(c >= 1 for c in got)  # floor


def test_sample_allocation_proportional_uneven() -> None:
    districts = _synthetic_districts()
    frame = _synthetic_frame(n_per_district=0)
    # 5 / 15 / 30 buildings
    frame += [
        {"id": f"b-a{i:04d}", "value": 3.0, "cx": 1500.0, "cy": 1500.0} for i in range(5)
    ]
    frame += [
        {"id": f"b-b{i:04d}", "value": 3.0, "cx": 3500.0, "cy": 1500.0} for i in range(15)
    ]
    frame += [
        {"id": f"b-c{i:04d}", "value": 3.0, "cx": 5500.0, "cy": 1500.0} for i in range(30)
    ]
    records = v.select_sample(seed=7, districts=districts, frame=frame, extent=_synthetic_extent(), size=10)
    counts = {code: 0 for code in ("011", "020", "030")}
    for rec in records:
        counts[rec["district_code"]] += 1
    expected = _largest_remainder([5, 15, 30], 10)
    got = [counts[c] for c in ("011", "020", "030")]
    assert got == expected


def test_sample_band_stratification() -> None:
    districts = _synthetic_districts()
    frame = _synthetic_frame(n_per_district=30)  # 10 per band
    records = v.select_sample(seed=7, districts=districts, frame=frame, extent=_synthetic_extent(), size=30)
    per_district: dict[str, dict[str, int]] = {}
    for rec in records:
        per_district.setdefault(rec["district_code"], {})
        per_district[rec["district_code"]][rec["value_band"]] = (
            per_district[rec["district_code"]].get(rec["value_band"], 0) + 1
        )
    for code, bands in per_district.items():
        expected = _largest_remainder([10, 10, 10], 10)  # district share 10
        got = [bands.get(b, 0) for b in ("0-10", "10-30", "30-100")]
        assert got == expected, f"district {code} bands {got} != {expected}"


def test_sample_schema_valid() -> None:
    districts = _synthetic_districts()
    frame = _synthetic_frame()
    records = v.select_sample(seed=3, districts=districts, frame=frame, extent=_synthetic_extent())
    assert len(records) == v.SAMPLE_SIZE
    ids = [r["patch_id"] for r in records]
    assert len(set(ids)) == v.SAMPLE_SIZE
    assert ids == sorted(ids)
    for rec in records:
        assert v.validate_sample_record(rec) == [], f"invalid record {rec}"


def test_sample_resample_flag_when_outside_extent() -> None:
    districts = _synthetic_districts()
    frame = _synthetic_frame(n_per_district=1)  # one building per district
    # extent excludes the only building of district 020
    extent = box(1000, 1000, 2000, 2000).union(box(5000, 1000, 6000, 2000))
    records = v.select_sample(seed=5, districts=districts, frame=frame, extent=extent, size=3)
    by_code = {r["district_code"]: r for r in records}
    assert by_code["020"]["resampled"] is True  # pool exhausted, flagged
    assert by_code["011"]["resampled"] is False
    assert by_code["030"]["resampled"] is False


def test_sample_real_workspace(workspace: Path) -> None:
    """End-to-end on the real workspace: coverage + reproducibility."""
    first = v.select_sample(seed=v.DEFAULT_SEED)
    assert len(first) == v.SAMPLE_SIZE
    codes = {r["district_code"] for r in first}
    districts = v.load_districts()
    assert codes == {d["code"] for d in districts}  # all 38 covered
    for rec in first:
        assert v.validate_sample_record(rec) == []
    second = v.select_sample(seed=v.DEFAULT_SEED)
    assert first == second


# --------------------------------------------------------------------------
# US2: rendering (T008)
# --------------------------------------------------------------------------


def _write_raster(path: Path, array, transform, driver: str = "GTiff") -> None:
    import numpy as np
    import rasterio

    profile = {
        "driver": driver,
        "width": array.shape[1],
        "height": array.shape[0],
        "count": array.shape[2] if array.ndim == 3 else 1,
        "dtype": array.dtype,
        "crs": "EPSG:25832",
        "transform": transform,
    }
    with rasterio.open(path, "w", **profile) as dst:
        if array.ndim == 3:
            dst.write(array.transpose(2, 0, 1))
        else:
            dst.write(array, 1)


def _render_workspace(tmp_path: Path, mask_full: bool = False, tree_rows: int = 1648) -> Path:
    """Workspace with one 2048x2048 px tile (409.6 m) at 0.2 m, origin (0,0).

    Filename grid claims a 1 km tile (e=0, n=0); the actual raster is
    smaller, which exercises clipped and out-of-raster windows.
    `tree_rows` anchors the 200x200 px tree block (rows are north-up:
    y = 409.6 - row*0.2)."""
    import numpy as np
    from rasterio.transform import from_origin

    ws = tmp_path / "ws"
    (ws / "mosaic" / "extract").mkdir(parents=True)
    transform = from_origin(0.0, 409.6, v.GSD_M, v.GSD_M)  # 2048 px @ 0.2 m

    img = np.zeros((2048, 2048, 3), dtype=np.uint8)
    img[..., 0] = 200  # red imagery
    img[..., 1] = 100
    _write_raster(ws / "mosaic" / "extract" / "dop20rgb_32_0_0_1_bw_2024.tif", img, transform)

    if mask_full:
        mask = np.ones((2048, 2048), dtype=np.uint8)
    else:
        mask = np.zeros((2048, 2048), dtype=np.uint8)
        # rows are north-up: y = 409.6 - row*0.2 -> block at y 40..80 m,
        # x 40..80 m, inside the p001 window [0, 204.8]^2
        mask[tree_rows : tree_rows + 200, 200:400] = 1
    _write_raster(ws / "mosaic" / "canopy_prediction_mask.tif", mask, transform)
    return ws


def _sample_record(patch_id: str, cx: float, cy: float) -> dict:
    return {
        "patch_id": patch_id,
        "seed": v.DEFAULT_SEED,
        "district_code": "011",
        "district_name": "A",
        "value_band": "0-10",
        "center_easting": cx,
        "center_northing": cy,
        "building_id": "b-test",
        "resampled": False,
        "degeneracy": None,
    }


def test_render_writes_pngs_and_persists_degeneracy(tmp_path: Path) -> None:
    ws = _render_workspace(tmp_path)
    sample = [
        _sample_record("p001", 102.4, 102.4),  # inside tile, mask has a tree
        _sample_record("p002", 1000.0, 1000.0),  # window outside raster -> no-imagery
    ]
    sample_path = tmp_path / "sample.jsonl"
    v.write_jsonl(sample_path, sample)
    out = v.render_patches(workspace_root=ws, sample=sample, sample_path=sample_path, patches_dir=tmp_path / "patches")

    by_id = {r["patch_id"]: r for r in out}
    assert by_id["p001"]["degeneracy"] is None
    assert by_id["p002"]["degeneracy"] == "no-imagery"

    assert (tmp_path / "patches" / "p001.png").exists()
    assert not (tmp_path / "patches" / "p002.png").exists()
    persisted = v.read_jsonl(sample_path)
    assert {r["patch_id"]: r["degeneracy"] for r in persisted} == {
        "p001": None,
        "p002": "no-imagery",
    }


def test_render_png_dimensions_and_overlay(tmp_path: Path) -> None:
    import rasterio

    ws = _render_workspace(tmp_path)
    sample = [_sample_record("p001", 102.4, 102.4)]
    out = v.render_patches(workspace_root=ws, sample=sample, sample_path=tmp_path / "s.jsonl", patches_dir=tmp_path / "patches")
    assert out[0]["degeneracy"] is None
    png = tmp_path / "patches" / "p001.png"
    with rasterio.open(png) as src:
        assert src.width == v.PATCH_PX and src.height == v.PATCH_PX
        assert src.count == 3 and src.dtypes[0] == "uint8"
        data = src.read()
    # base imagery is (200, 100, 0); the mask tree block (x 40..80 m ->
    # cols 200..400, y 40..80 m -> rows 624..824 in the north-up window)
    # is blended toward the overlay tint, so a block pixel differs from a
    # no-tree pixel
    assert int(data[0, 700, 300]) != int(data[0, 100, 100])


def test_render_deterministic(tmp_path: Path) -> None:
    ws = _render_workspace(tmp_path)
    sample = [_sample_record("p001", 102.4, 102.4)]
    v.render_patches(workspace_root=ws, sample=sample, sample_path=tmp_path / "s1.jsonl", patches_dir=tmp_path / "patches")
    first = (tmp_path / "patches" / "p001.png").read_bytes()
    sample2 = [_sample_record("p001", 102.4, 102.4)]
    v.render_patches(workspace_root=ws, sample=sample2, sample_path=tmp_path / "s2.jsonl", patches_dir=tmp_path / "patches")
    second = (tmp_path / "patches" / "p001.png").read_bytes()
    assert first == second


def test_render_empty_mask_classified(tmp_path: Path) -> None:
    ws = _render_workspace(tmp_path)
    # window [204.8, 409.6]^2 is inside the raster but has no trees
    sample = [_sample_record("p001", 307.2, 307.2)]
    out = v.render_patches(workspace_root=ws, sample=sample, sample_path=tmp_path / "s.jsonl", patches_dir=tmp_path / "patches")
    assert out[0]["degeneracy"] == "empty-mask"
    assert (tmp_path / "patches" / "p001.png").exists()  # still rendered (FR-008)


def test_render_full_mask_classified(tmp_path: Path) -> None:
    ws = _render_workspace(tmp_path, mask_full=True)
    sample = [_sample_record("p001", 102.4, 102.4)]
    out = v.render_patches(workspace_root=ws, sample=sample, sample_path=tmp_path / "s.jsonl", patches_dir=tmp_path / "patches")
    assert out[0]["degeneracy"] == "full-mask"
    assert (tmp_path / "patches" / "p001.png").exists()


def test_render_partial_window_placement(tmp_path: Path) -> None:
    """Window extending beyond the raster top (y 409.6): the read strip
    must land at the BOTTOM of the composite (north-anchored), and rows
    above the raster stay black."""
    import rasterio

    ws = _render_workspace(tmp_path, tree_rows=448)  # tree block at y 280..320 m
    # window y 256..460.8 -> raster overlap y 256..409.6 (768 rows)
    sample = [_sample_record("p001", 102.4, 358.4)]
    out = v.render_patches(workspace_root=ws, sample=sample, sample_path=tmp_path / "s.jsonl", patches_dir=tmp_path / "patches")
    assert out[0]["degeneracy"] is None  # tree block at y 280..320 present
    png = tmp_path / "patches" / "p001.png"
    with rasterio.open(png) as src:
        data = src.read()
    # window y 256..460.8; raster ends at 409.6 -> rows 0..255 black
    # (y 460.8..409.6); row 300 (y 400.8) pure imagery; row 800 (y 300.8)
    # inside the tree block (y 280..320, x 60 m) and blended
    assert int(data[0, 100, 300]) == 0
    assert int(data[0, 300, 300]) == 200
    assert int(data[0, 800, 300]) != 200


# --------------------------------------------------------------------------
# US3: report generation (T011)
# --------------------------------------------------------------------------

NOTES_FIXTURE = """## Vergleich mit dem Referenz-Transferproblem

Der Modellautor berichtet deutlich schlechtere Ergebnisse fuer Erlangen-auf-Bamberg.
Die Stichprobe in Mannheim zeigt ein anderes Bild: [placeholder].

## Einschraenkungen (zusaezlich)

Einzelpruefer-Urteil; Randbereiche am Stadtrand; Wiederholungspruefung ohne Abweichung.

## Empfehlungen

Keine Massnahmen in diesem Feature; Entscheidung nach Sichtung des Berichts.
"""


def _report_fixtures(n_per_district: int = 6) -> tuple[list[dict], list[dict]]:
    """18-patch sample across 3 districts + ratings:
    A all correct (trustworthy), B all over (overstated, FLAGGED),
    C half correct half under (understated, not flagged)."""
    sample: list[dict] = []
    ratings: list[dict] = []
    for code, name in (("011", "A"), ("020", "B"), ("030", "C")):
        for i in range(n_per_district):
            pid = f"p{len(sample) + 1:03d}"
            sample.append(
                {
                    "patch_id": pid,
                    "seed": v.DEFAULT_SEED,
                    "district_code": code,
                    "district_name": name,
                    "value_band": "0-10",
                    "center_easting": 1500.0,
                    "center_northing": 1500.0,
                    "building_id": "b-x",
                    "resampled": False,
                    "degeneracy": None,
                }
            )
            if code == "011":
                rating = "correct"
            elif code == "020":
                rating = "over"
            else:
                rating = "correct" if i % 3 == 0 else "under"  # 2 correct, 4 under
            ratings.append(
                {
                    "patch_id": pid,
                    "district_code": code,
                    "district_name": name,
                    "value_band": "0-10",
                    "rating": rating,
                    "note": "",
                    "ts": "2026-08-06T18:00:00+00:00",
                }
            )
    return sample, ratings


def test_report_structure_and_flagging() -> None:
    sample, ratings = _report_fixtures()
    text = v.generate_report(sample=sample, ratings=ratings, notes_text=NOTES_FIXTURE, today="2026-08-06")

    assert "Verifikation der Baumerkennung" in text
    assert "Methode" in text and "Gesamtergebnis" in text
    assert "Ergebnisse nach Stadtteil" in text
    assert "Vergleich mit dem Referenz-Transferproblem" in text
    assert "Einschraenkungen" in text and "Empfehlungen" in text

    # district A: 6/6 correct -> trustworthy, not flagged
    assert "| A | 6 | 6 | 0 | 0 | trustworthy |" in text
    # district B: 0 correct -> overstated + FLAGGED
    assert "| B | 6 | 0 | 6 | 0 | overstated | FLAGGED |" in text
    # district C: 2 correct, 4 under -> understated, correct share 0.33 -> FLAGGED
    assert "| C | 6 | 2 | 0 | 4 | understated | FLAGGED |" in text
    # overall counts 18 ratings: 8 correct, 6 over, 4 under
    assert "correct: 8" in text.split("Gesamtergebnis")[1].split("Ergebnisse")[0]
    # notes text merged
    assert "Erlangen-auf-Bamberg" in text
    # all five limitation classes present
    for cls in ("degenerierte", "kleine stichprobe", "rand", "einzelpruefer", "wiederholungspruefung"):
        assert cls in text.lower(), f"missing limitation class {cls}"


def test_report_requires_rating_for_every_patch() -> None:
    sample, ratings = _report_fixtures()
    ratings = ratings[:-1]  # one patch unrated
    with pytest.raises(ValueError, match="fehlende Ratings"):
        v.generate_report(sample=sample, ratings=ratings, notes_text=NOTES_FIXTURE)


def test_report_rejects_unknown_rating_value() -> None:
    sample, ratings = _report_fixtures()
    ratings[0]["rating"] = "mixed"
    with pytest.raises(ValueError):
        v.generate_report(sample=sample, ratings=ratings, notes_text=NOTES_FIXTURE)


def test_report_rejects_rating_for_no_imagery_patch() -> None:
    sample, ratings = _report_fixtures()
    sample[0]["degeneracy"] = "no-imagery"
    # p001 is now no-imagery but still has a rating -> must be rejected
    with pytest.raises(ValueError):
        v.generate_report(sample=sample, ratings=ratings, notes_text=NOTES_FIXTURE)


def test_report_requires_notes_sections() -> None:
    sample, ratings = _report_fixtures()
    with pytest.raises(ValueError, match="notes"):
        v.generate_report(sample=sample, ratings=ratings, notes_text="# Nur Titel\n\nohne Sektionen")


def test_report_inconclusive_small_district() -> None:
    sample, ratings = _report_fixtures(n_per_district=2)  # n=2 < 5
    text = v.generate_report(sample=sample, ratings=ratings, notes_text=NOTES_FIXTURE, today="2026-08-06")
    assert "inconclusive" in text
    # the small-sample limitation must name at least one district
    assert "A" in text.split("Einschraenkungen")[1].split("Empfehlungen")[0]


# --------------------------------------------------------------------------
# Feature 009: mask parameter + value delta (T002/T003)
# --------------------------------------------------------------------------


def test_render_mask_param_changes_overlay(tmp_path: Path) -> None:
    """Same sample, two different masks -> different overlays (T002)."""
    import numpy as np
    import rasterio

    ws = _render_workspace(tmp_path, tree_rows=448)  # published: block y 280..320, inside window
    # candidate: block y 340..380, also inside the window, different position
    _write_raster(
        ws / "mosaic" / "canopy_prediction_mask_t060.tif",
        _make_mask_block(2048, 148).astype(np.uint8),
        rasterio.transform.from_origin(0.0, 409.6, v.GSD_M, v.GSD_M),
    )
    sample = [_sample_record("p001", 102.4, 358.4)]
    out_pub = v.render_patches(
        workspace_root=ws, sample=list(sample), sample_path=tmp_path / "s_pub.jsonl",
        patches_dir=tmp_path / "patches_pub",
    )
    out_cand = v.render_patches(
        workspace_root=ws, sample=list(sample), sample_path=tmp_path / "s_cand.jsonl",
        patches_dir=tmp_path / "patches_cand", mask_rel="mosaic/canopy_prediction_mask_t060.tif",
    )
    # both rendered; the overlay pixels differ because the tree block moved
    pub = (tmp_path / "patches_pub" / "p001.png").read_bytes()
    cand = (tmp_path / "patches_cand" / "p001.png").read_bytes()
    assert pub != cand
    assert out_pub[0]["degeneracy"] is None and out_cand[0]["degeneracy"] is None


def _make_mask_block(px: int, tree_rows: int) -> np.ndarray:
    import numpy as np

    mask = np.zeros((px, px), dtype=np.uint8)
    mask[tree_rows : tree_rows + 200, 200:400] = 1
    return mask


def test_value_delta_join_and_summary() -> None:
    published = [{"id": f"b{i}", "value": 10.0 + i} for i in range(3)]
    candidate = [{"id": f"b{i}", "value": 5.0 + i} for i in range(3)]
    rows = v.compute_delta_rows(published, candidate)
    assert [r["delta"] for r in rows] == [-5.0, -5.0, -5.0]
    summary = v.summarize_deltas(rows, "mask_t060.tif", 0.6)
    assert summary["threshold"] == 0.6
    assert summary["n_buildings"] == 3
    assert summary["mean_delta"] == -5.0
    assert summary["mean_abs_delta"] == 5.0
    assert summary["share_moved_gt_0_5pp"] == 1.0


def test_value_delta_missing_candidate_raises() -> None:
    published = [{"id": "b1", "value": 1.0}, {"id": "b2", "value": 2.0}]
    candidate = [{"id": "b1", "value": 0.5}]
    with pytest.raises(ValueError, match="b2"):
        v.compute_delta_rows(published, candidate)


def test_value_delta_metadata_trust(tmp_path: Path) -> None:
    """Missing or wrong-threshold metadata aborts (FR-008)."""
    import json

    import numpy as np
    import rasterio
    from rasterio.transform import from_origin

    ws = tmp_path / "ws"
    (ws / "mosaic").mkdir(parents=True)
    transform = from_origin(0.0, 204.8, v.GSD_M, v.GSD_M)
    mask = np.zeros((v.PATCH_PX, v.PATCH_PX), dtype=np.uint8)
    _write_raster(ws / "mosaic" / "canopy_prediction_mask.tif", mask, transform)
    # candidate mask same extent
    _write_raster(ws / "mosaic" / "canopy_prediction_mask_t060.tif", mask, transform)
    # missing metadata -> abort
    with pytest.raises(ValueError, match="missing metadata"):
        v.value_delta("mosaic/canopy_prediction_mask_t060.tif", workspace_root=ws)
    # wrong threshold vs filename (_t060 -> 0.6) -> abort
    (ws / "mosaic" / "canopy_prediction_mask_t060.json").write_text(
        json.dumps({"threshold": 0.5, "crs": "EPSG:25832", "ground_sampling_distance_m": 0.2}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="threshold"):
        v.value_delta("mosaic/canopy_prediction_mask_t060.tif", workspace_root=ws)
