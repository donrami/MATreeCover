"""Feature 014 hashing engine tests (T003, contracts/hashed-bundle.md).

The publish post-process must be deterministic, idempotent, and must
rewrite every reference consistently. Each pattern the engine rewrites
must occur exactly once; a missing or duplicated pattern fails the
publish (refuses to ship a broken bundle).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from src.pipeline.publish import HASHED_ASSETS, _hash_static_assets, _rewrite_once


INDEX_HTML = """<!doctype html>
<html><head>
  <link rel="stylesheet" href="vendor/maplibre-gl.css">
  <link rel="stylesheet" href="style.css">
</head><body>
  <script src="vendor/maplibre-gl.js"></script>
  <script src="vendor/pmtiles.js"></script>
  <script type="module" src="main.js"></script>
</body></html>
"""

MAIN_JS = """const STYLE_URL = 'style.json';
fetch('stadtteile.geojson').then(r => r.json());
fetch('boundary.geojson').then(r => r.json());
"""

STYLE_JSON = {
    "version": 8,
    "sources": {
        "boundary": {"type": "geojson", "data": "boundary.geojson"},
        "stadtteile": {"type": "geojson", "data": "stadtteile.geojson"},
        "buildings": {"type": "vector", "url": "pmtiles://buildings.pmtiles"},
    },
    "layers": [],
}


def _make_dist(tmp_path: Path) -> Path:
    dist = tmp_path / "dist"
    vendor = dist / "vendor"
    vendor.mkdir(parents=True, exist_ok=True)
    (dist / "index.html").write_text(INDEX_HTML, encoding="utf-8")
    (dist / "main.js").write_text(MAIN_JS, encoding="utf-8")
    (dist / "style.json").write_text(json.dumps(STYLE_JSON), encoding="utf-8")
    (dist / "style.css").write_text("body {}\n", encoding="utf-8")
    (vendor / "maplibre-gl.js").write_text("// maplibre\n", encoding="utf-8")
    (vendor / "maplibre-gl.css").write_text("/* css */\n", encoding="utf-8")
    (vendor / "pmtiles.js").write_text("// pmtiles\n", encoding="utf-8")
    (dist / "boundary.geojson").write_text("{}", encoding="utf-8")
    (dist / "stadtteile.geojson").write_text("{}", encoding="utf-8")
    return dist


def test_hash_renames_all_assets(tmp_path: Path) -> None:
    dist = _make_dist(tmp_path)
    hashed = _hash_static_assets(dist)
    assert set(hashed) == set(HASHED_ASSETS)
    for rel, new_rel in hashed.items():
        assert not (dist / rel).exists(), f"original not removed: {rel}"
        assert (dist / new_rel).exists(), f"hashed target missing: {new_rel}"
        assert re.search(r"-[0-9a-f]{12}\.[a-z]+$", new_rel), new_rel


def test_references_rewritten_consistently(tmp_path: Path) -> None:
    dist = _make_dist(tmp_path)
    hashed = _hash_static_assets(dist)
    index = (dist / "index.html").read_text(encoding="utf-8")
    main = (dist / hashed["main.js"]).read_text(encoding="utf-8")
    style = json.loads((dist / hashed["style.json"]).read_text(encoding="utf-8"))
    # index.html references only hashed names, never originals
    for rel in HASHED_ASSETS:
        assert f'"{rel}"' not in index, f"index.html still references {rel}"
    assert f'src="{hashed["vendor/maplibre-gl.js"]}"' in index
    assert f'src="{hashed["main.js"]}"' in index
    # main.js points at hashed style + data files
    assert f"const STYLE_URL = '{hashed['style.json']}'" in main
    assert f"fetch('{hashed['stadtteile.geojson']}')" in main
    assert f"fetch('{hashed['boundary.geojson']}')" in main
    # style.json data URLs point at hashed geojsons, pmtiles untouched
    assert style["sources"]["boundary"]["data"] == hashed["boundary.geojson"]
    assert style["sources"]["stadtteile"]["data"] == hashed["stadtteile.geojson"]
    assert style["sources"]["buildings"]["url"] == "pmtiles://buildings.pmtiles"


def test_critical_path_head_transforms(tmp_path: Path) -> None:
    dist = _make_dist(tmp_path)
    hashed = _hash_static_assets(dist)
    index = (dist / "index.html").read_text(encoding="utf-8")
    # no stylesheet link tags remain; one inline style block with both files
    assert '<link rel="stylesheet"' not in index
    assert index.count("<style>") == 1
    assert "/* style.css */" in index and "/* vendor/maplibre-gl.css */" in index
    # cascade order preserved: maplibre-gl.css first, then style.css (regression guard)
    assert index.index("/* vendor/maplibre-gl.css */") < index.index("/* style.css */")
    # preload, preconnect, favicon present
    assert f'rel="preload" href="{hashed["vendor/maplibre-gl.js"]}" as="script"' in index
    assert 'rel="preconnect" href="https://sgx.geodatenzentrum.de"' in index
    assert 'rel="icon" type="image/svg+xml" href="favicon.svg"' in index
    # the hashed css files are no longer referenced by name
    assert hashed["style.css"] not in index
    assert hashed["vendor/maplibre-gl.css"] not in index


def test_deterministic_and_idempotent(tmp_path: Path) -> None:
    first = _hash_static_assets(_make_dist(tmp_path))
    second = _hash_static_assets(_make_dist(tmp_path))
    assert first == second


def test_content_change_changes_only_that_hash(tmp_path: Path) -> None:
    dist = _make_dist(tmp_path)
    before = _hash_static_assets(dist)
    # restore pristine sources (rewrites are in-place), change one file
    for rel, new_rel in before.items():
        (dist / new_rel).rename(dist / rel)
    (dist / "main.js").write_text(MAIN_JS, encoding="utf-8")
    (dist / "style.json").write_text(json.dumps(STYLE_JSON), encoding="utf-8")
    (dist / "index.html").write_text(INDEX_HTML, encoding="utf-8")
    (dist / "style.css").write_text("body { color: red; }\n", encoding="utf-8")
    after = _hash_static_assets(dist)
    assert after["style.css"] != before["style.css"]
    for rel in before:
        if rel != "style.css":
            assert after[rel] == before[rel], f"{rel} hash changed unexpectedly"


def test_missing_pattern_fails_publish(tmp_path: Path) -> None:
    dist = _make_dist(tmp_path)
    (dist / "main.js").write_text("no style url here\n", encoding="utf-8")
    with pytest.raises(Exception, match="STYLE_URL"):
        _hash_static_assets(dist)


def test_rewrite_once_rejects_duplicates(tmp_path: Path) -> None:
    p = tmp_path / "f.js"
    p.write_text("a a a", encoding="utf-8")
    with pytest.raises(Exception, match="occurs 3 times"):
        _rewrite_once(p, "a", "b", "dup test")


def test_stale_hashed_files_removed(tmp_path: Path) -> None:
    dist = _make_dist(tmp_path)
    stale = dist / "main-deadbeef0000.js"
    stale.write_text("// stale\n", encoding="utf-8")
    (dist / "style-0123456789ab.css").write_text("/* stale */\n", encoding="utf-8")
    hashed = _hash_static_assets(dist)
    assert not stale.exists(), "stale hashed file not removed"
    assert not (dist / "style-0123456789ab.css").exists()
    for new_rel in hashed.values():
        assert (dist / new_rel).exists()
