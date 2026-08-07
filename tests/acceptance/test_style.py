"""US1 style contract test (T012) — `contracts/map-style.md`.

Asserts the five layers in order, the verbatim palette stops
0/12/24/29.9/30/45/60/75/90/100, the hidden trees layer, the legend
labels, and JSON round-trip stability.
"""

from __future__ import annotations

import json
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parents[2] / "src" / "site"
STYLE_PATH = SITE_DIR / "style.json"
INDEX_PATH = SITE_DIR / "index.html"

EXPECTED_LAYERS = ["basemap", "basemap-inverted", "outside-mask", "stadtteile-fill", "buildings-fill", "buildings-line", "trees-fill"]
PALETTE_STOPS = {
    0: "#ffd524",
    12: "#e6854a",
    24: "#a97e65",
    29.9: "#a97e65",
    30: "#0674aa",
    45: "#1db6ff",
    60: "#39c2ff",
    75: "#56ceff",
    90: "#6ad4ff",
    100: "#6ad4ff",
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
    assert case_expr[-1] == "#b8b8b8"  # FR-009 gray (darkened base map)
    opacity = buildings_fill["paint"]["fill-opacity"]
    assert opacity[0] == "case"
    assert opacity[2] == 0.75  # FR-010
    assert opacity[3] == 0.8


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
    assert sources["stadtteile"]["type"] == "geojson"  # feature 011
    assert sources["stadtteile"]["data"] == "stadtteile.geojson"


def test_stadtteile_fill_transparent_between_mask_and_buildings() -> None:
    """Feature 011: transparent fill below buildings-fill — hit-testable
    without changing the default render (research R-4, SC-004)."""
    style = _style()
    ids = [layer["id"] for layer in style["layers"]]
    assert ids.index("stadtteile-fill") == ids.index("outside-mask") + 1
    assert ids.index("stadtteile-fill") < ids.index("buildings-fill")
    layer = next(layer for layer in style["layers"] if layer["id"] == "stadtteile-fill")
    assert layer["type"] == "fill"
    assert layer["source"] == "stadtteile"
    assert layer["paint"]["fill-opacity"] == 0  # transparent, still queryable
    assert "line-color" not in layer["paint"]  # no stroke


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


def test_city_panel_present() -> None:
    """Feature 011 (city-overview.md): #city-panel card in the left stack."""
    html = INDEX_PATH.read_text(encoding="utf-8")
    assert 'id="city-panel"' in html


# =====================================================================
# Feature 012 — Mobile-First Native UX (contracts/ in feature 012).
# Static DOM/CSS assertions for the shared #surface component.
# =====================================================================

STYLE_CSS = SITE_DIR / "style.css"
MAIN_JS = SITE_DIR / "main.js"


def test_surface_markup_present() -> None:
    """Feature 012 (FR-008): one shared surface with a persistent header
    and a collapsible body."""
    html = INDEX_PATH.read_text(encoding="utf-8")
    assert 'id="surface"' in html
    assert 'class="surface-header"' in html
    assert 'id="surface-body"' in html
    assert 'id="surface-toggle"' in html
    assert 'aria-controls="surface-body"' in html


def test_surface_collapsed_by_default() -> None:
    """Feature 012 (FR-001, SC-001): mobile loads with the surface
    collapsed so the map is the dominant surface."""
    html = INDEX_PATH.read_text(encoding="utf-8")
    assert 'class="surface is-collapsed"' in html


def test_map_full_bleed() -> None:
    """Feature 012: the map stays full-bleed in every layout."""
    css = STYLE_CSS.read_text(encoding="utf-8")
    assert "#map {" in css
    assert "position: absolute" in css
    assert "inset: 0" in css


def test_reduced_motion_block_present() -> None:
    """Feature 012 (FR-008): reduced motion makes surface transitions
    instant and non-animated."""
    css = STYLE_CSS.read_text(encoding="utf-8")
    assert "prefers-reduced-motion" in css
    assert "transition: none" in css


def test_mobile_breakpoint_is_768px() -> None:
    """Feature 012 (R-8): a single 768 px breakpoint (mobile bottom sheet
    below, desktop panel at/above)."""
    css = STYLE_CSS.read_text(encoding="utf-8")
    assert "@media (max-width: 767.98px)" in css
    assert "@media (min-width: 768px)" in css


def test_mobile_touch_targets_min_44px() -> None:
    """Feature 012 (FR-003): on mobile, interactive controls are
    >= 44x44 px touch targets."""
    css = STYLE_CSS.read_text(encoding="utf-8")
    assert "min-width: 44px" in css
    assert "min-height: 44px" in css
    assert "#baeume" in css
    assert ".surface-toggle" in css
    assert 'input[type="range"]' in css


def test_tools_in_surface_header() -> None:
    """Feature 012 (FR-004): Bäume and Helligkeit live in the persistent
    surface header so they stay visible while the surface is collapsed."""
    html = INDEX_PATH.read_text(encoding="utf-8")
    assert 'id="baeume"' in html
    assert 'id="brightness-slider"' in html
    # header comes before the collapsible body in the DOM
    header = html.index('class="surface-header"')
    body = html.index('id="surface-body"')
    assert header < body


def test_new_copy_no_em_or_en_dashes() -> None:
    """Feature 012 (FR-011, SC-009): all new user-facing copy is German
    with zero em-dashes and zero en-dashes (hyphens inside compounds only)."""
    html = INDEX_PATH.read_text(encoding="utf-8")
    assert "\u2014" not in html  # em dash
    assert "\u2013" not in html  # en dash


# =====================================================================
# Feature 013 — Popup Comparative Context (contracts/popup-content.md).
# Static CSS assertions: popup hierarchy classes (FR-013), badge colors
# (R-12), delta color classes. Popup HTML is JS-rendered in main.js, so
# these guard the shared structure CSS only.
# =====================================================================


def test_popup_hierarchy_classes_present() -> None:
    """Feature 013 (FR-013): both popups share the header -> headline ->
    badge -> context -> footnote block classes."""
    css = STYLE_CSS.read_text(encoding="utf-8")
    for cls in (".popup-header", ".popup-headline", ".popup-badge",
                ".popup-context", ".popup-footnote"):
        assert cls in css


def test_building_badge_colors() -> None:
    """Feature 013 (R-12): erreicht / verfehlt badges carry their
    palette-semantic colors with the text label, never color-only."""
    css = STYLE_CSS.read_text(encoding="utf-8")
    assert ".badge-good" in css
    assert ".badge-bad" in css
    assert "#39c2ff" in css  # erreicht (cool, high tree share)
    assert "#ffd524" in css  # verfehlt (warm, low tree share)


def test_delta_color_classes() -> None:
    """Feature 013 (FR-003/FR-004/FR-008): signed deltas get a color
    class by direction; neutral gets none."""
    css = STYLE_CSS.read_text(encoding="utf-8")
    assert ".delta-up" in css
    assert ".delta-down" in css
    assert ".delta-neutral" in css


def test_district_quartile_badge_colors() -> None:
    """Feature 013 (R-12): all four quartile bands carry their palette-
    semantic colors with the text label (FR-010, FR-013)."""
    css = STYLE_CSS.read_text(encoding="utf-8")
    for cls in (".badge-good", ".badge-good-soft", ".badge-mid", ".badge-bad"):
        assert cls in css
    assert "#1db6ff" in css  # oberes Mittelfeld
    assert "#e6854a" in css  # unteres Mittelfeld


def test_popup_mobile_fit() -> None:
    """Feature 013 (FR-016/SC-006): both popup content boxes scroll
    internally and clamp width so no line clips at a 360 px viewport."""
    css = STYLE_CSS.read_text(encoding="utf-8")
    assert ".building-popup .maplibregl-popup-content" in css
    assert ".district-popup .maplibregl-popup-content" in css
    assert "max-height" in css
    assert "overflow-y: auto" in css
    assert "min(240px, calc(100vw - 24px))" in css  # width clamp (R-9)


def test_popup_hierarchy_order_guarded() -> None:
    """Feature 013 (FR-013): the shared block classes appear in the CSS in
    header -> headline -> badge -> context -> footnote order, so a
    divergence in the shared structure is caught statically."""
    css = STYLE_CSS.read_text(encoding="utf-8")
    order = [css.index(c) for c in (
        ".popup-header", ".popup-headline", ".popup-badge",
        ".popup-context", ".popup-footnote",
    )]
    assert order == sorted(order)


def test_feature013_copy_no_em_or_en_dashes() -> None:
    """Feature 013 (R-3 / feature 012 convention): all new German popup
    copy uses hyphens inside compounds only (e.g. "60-m-Umkreis",
    "Stadtteil-Durchschnitt") — zero em-dashes, zero en-dashes; the delta
    minus sign is U+2212."""
    js = MAIN_JS.read_text(encoding="utf-8")
    strings = [
        "erreicht", "verfehlt",
        "über dem Stadtteil-Durchschnitt", "unter dem Stadtteil-Durchschnitt",
        "auf Stadtteil-Niveau", "über dem Stadtdurchschnitt",
        "unter dem Stadtdurchschnitt", "auf Stadtniveau",
        "oberstes Viertel", "oberes Mittelfeld", "unteres Mittelfeld",
        "unterstes Viertel", "Platz ", "Stadtteil: ",
        "Baumanteil im 60-m-Umkreis", "Baumanteil im Durchschnitt",
        "Gebäude", "Anteil unter 30 %", "Stadtdurchschnitt",
        "Durchschnitt im Stadtteil", "Was bedeutet das?", "keine Daten",
        "Der Baumanteil im 60-m-Umkreis ist der Anteil",
        "Der Baumanteil im Durchschnitt ist der mittlere",
    ]
    blob = " ".join(strings)
    assert "\u2014" not in blob  # em dash
    assert "\u2013" not in blob  # en dash
    assert "\\u2212" in js  # formatDelta uses the U+2212 minus sign



