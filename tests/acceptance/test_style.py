"""US1 style contract test (T012) — `contracts/map-style.md`.

Asserts the five layers in order, the verbatim palette stops
0/12/24/24.08/32/40/48/80, the hidden trees layer, the legend labels,
and JSON round-trip stability.
"""

from __future__ import annotations

import json
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parents[2] / "src" / "site"
STYLE_PATH = SITE_DIR / "style.json"
INDEX_PATH = SITE_DIR / "index.html"

EXPECTED_LAYERS = ["basemap", "outside-mask", "buildings-fill", "buildings-line", "trees-fill"]
PALETTE_STOPS = {
    0: "#ffd524",
    12: "#e6854a",
    24: "#a97e65",
    24.08: "#0674aa",
    32: "#1db6ff",
    40: "#39c2ff",
    48: "#56ceff",
    80: "#6ad4ff",
}
LEGEND_LABELS = ["0", "15", "30", "50", "100"]


def _style() -> dict:
    return json.loads(STYLE_PATH.read_text(encoding="utf-8"))


def test_style_file_exists_and_is_valid_json() -> None:
    style = _style()
    assert style["version"] == 8
    assert style["name"] == "Mannheim Tree Cover"


def test_five_layers_in_order() -> None:
    style = _style()
    ids = [layer["id"] for layer in style["layers"]]
    assert ids == EXPECTED_LAYERS


def test_palette_stops_verbatim() -> None:
    style = _style()
    buildings_fill = next(layer for layer in style["layers"] if layer["id"] == "buildings-fill")
    color_expr = buildings_fill["paint"]["fill-color"]
    # case(has_value, interpolate(linear, get value, stops...), fallback)
    assert color_expr[0] == "case"
    interp = color_expr[2]
    assert interp[0] == "interpolate"
    assert interp[1] == ["linear"]
    assert interp[2] == ["get", "value"]
    stops = list(zip(interp[3::2], interp[4::2]))
    expected = [(k, v) for k, v in PALETTE_STOPS.items()]
    assert stops == expected


def test_unavailable_fallback_and_opacity() -> None:
    style = _style()
    buildings_fill = next(layer for layer in style["layers"] if layer["id"] == "buildings-fill")
    case_expr = buildings_fill["paint"]["fill-color"]
    assert case_expr[-1] == "#444444"  # FR-009 gray
    opacity = buildings_fill["paint"]["fill-opacity"]
    assert opacity[0] == "case"
    assert opacity[2] == 0.75  # FR-010
    assert opacity[3] == 0.4


def test_buildings_line_thin_gray() -> None:
    style = _style()
    line = next(layer for layer in style["layers"] if layer["id"] == "buildings-line")
    assert line["paint"]["line-color"] == "#555555"
    assert line["paint"]["line-width"] == 0.5


def test_trees_layer_hidden_on_load() -> None:
    style = _style()
    trees = next(layer for layer in style["layers"] if layer["id"] == "trees-fill")
    assert trees["layout"]["visibility"] == "none"  # FR-015
    assert trees["paint"]["fill-color"] == "#39C43D"
    assert trees["paint"]["fill-opacity"] == 0.75


def test_outside_mask_black() -> None:
    style = _style()
    mask = next(layer for layer in style["layers"] if layer["id"] == "outside-mask")
    assert mask["paint"]["fill-color"] == "#000000"
    assert mask["paint"]["fill-opacity"] == 1  # FR-003


def test_sources_present() -> None:
    style = _style()
    sources = style["sources"]
    assert "basemap" in sources and sources["basemap"]["type"] == "raster"
    assert sources["buildings"]["url"] == "pmtiles://buildings.pmtiles"
    assert sources["trees"]["url"] == "pmtiles://trees.pmtiles"
    assert sources["boundary"]["type"] == "geojson"


def test_json_roundtrip() -> None:
    style = _style()
    assert json.loads(json.dumps(style)) == style


def test_legend_labels_present() -> None:
    html = INDEX_PATH.read_text(encoding="utf-8")
    for label in LEGEND_LABELS:
        assert label in html  # FR-012


def test_title_baumflaeche() -> None:
    html = INDEX_PATH.read_text(encoding="utf-8")
    assert "<title>Baumfläche</title>" in html  # FR-013
