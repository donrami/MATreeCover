"""Feature 013 — popup renderer regression test (FR-001..FR-012, FR-014).

Loads the shipped `buildingPopupHtml`/`districtPopupHtml` from
`dist/main.js` in a node VM (browser stubs) and asserts the popup-content
contract (`contracts/popup-content.md`): valid/neutral/threshold/no-value
building, valid/null-mean district, and the FR-006/FR-011/FR-014
degradation matrix, plus the pure delta helpers (FR-003/FR-004/FR-008,
R-3/R-4/R-11).

This is the automated guard for the popup HTML that test_rank.py does not
cover (test_rank.py guards only computeDistrictRankings). It is skipped
when node or `dist/main.js` is missing (dist-fixture pattern); it requires
`make publish` to have refreshed `dist/main.js`.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DIST_MAIN = REPO_ROOT / "dist" / "main.js"
DIST_STADTTEILE = REPO_ROOT / "dist" / "stadtteile.geojson"


def _district(name: str) -> dict:
    """Real published properties for a district by display name."""
    data = json.loads(DIST_STADTTEILE.read_text(encoding="utf-8"))
    for f in data["features"]:
        if f["properties"]["name"] == name:
            return dict(f["properties"])
    raise KeyError(name)


LINDEHOF = _district("Lindenhof")  # rank 13 / oberes Mittelfeld (reference table)


# The node-VM harness. Reads one scenario from stdin:
#   { cityMean: number|null, district: {name,mean_value}|null, rankings: bool,
#     features: [slim features], render: {kind, props, lngLat} }
# and returns the rendered popup HTML (or {__error}) on stdout.
_NODE_RENDER = r"""
const vm = require('vm');
const fs = require('fs');
let input = '';
process.stdin.on('data', c => (input += c));
process.stdin.on('end', () => {
  const cfg = JSON.parse(input);
  const districtFeat = cfg.district
    ? { properties: cfg.district,
        geometry: { type: 'Polygon',
          coordinates: [[[-1, -1], [1, -1], [1, 1], [-1, 1], [-1, -1]]] } }
    : null;
  class FakeMap {
    querySourceFeatures(){ return districtFeat ? [districtFeat] : []; }
    on(){} addControl(){} fitBounds(){}
    getStyle(){
      if (cfg.cityMean === null) return { metadata: {} };
      return { metadata: { city_stats: { mean_value_pct: cfg.cityMean } } };
    }
    getCanvas(){ return { style: {} }; }
  }
  class FakeMGL {
    static addProtocol() {}
    static Map = FakeMap;
    static NavigationControl = class {};
    static AttributionControl = class {};
    static Popup = class {
      constructor(){ this._e = { querySelector: () => null }; }
      on(){} setLngLat(){ return this; } setHTML(){ return this; }
      addTo(){ return this; } remove(){} isOpen(){ return false; }
      getElement(){ return this._e; }
    };
  }
  const sandbox = {
    window: { maplibregl: FakeMGL, pmtiles: { Protocol: class {
      constructor(){ this.tile = () => {}; } } } },
    document: { getElementById: () => null, querySelector: () => null },
    console,
    matchMedia: () => ({ matches: false }),
    __feats: cfg.features,
  };
  vm.createContext(sandbox);
  try {
    vm.runInContext(fs.readFileSync('@@MAIN_PATH@@', 'utf8'), sandbox);
    const epilogue = cfg.rankings
      ? "globalThis.__r = (k, p, l) => { districtRankings = computeDistrictRankings(__feats);" +
        " return k === 'building' ? buildingPopupHtml(p, l) : districtPopupHtml(p); };"
      : "globalThis.__r = (k, p, l) =>" +
        " (k === 'building' ? buildingPopupHtml(p, l) : districtPopupHtml(p));";
    vm.runInContext(epilogue, sandbox);
    const html = sandbox.__r(cfg.render.kind, cfg.render.props, cfg.render.lngLat || { lng: 0, lat: 0 });
    const __h = { c: sandbox.classifyDelta, f: sandbox.formatDelta,
                  d: sandbox.deltaClass, w: sandbox.assessmentWord };
    const helpers = {
      c: [__h.c(0.1), __h.c(-0.1), __h.c(0.1001), __h.c(-0.1001)],
      f: [__h.f(0.1, 'neutral'), __h.f(2.7, 'above'), __h.f(-2.3, 'below'), __h.f(2.66, 'above')],
      d: [__h.d('above'), __h.d('below'), __h.d('neutral')],
      w: { bda: __h.w('building-district', 'above'),
           bdn: __h.w('building-district', 'neutral'),
           bcb: __h.w('building-city', 'below'),
           dcn: __h.w('district-city', 'neutral'),
           all: ['building-district', 'building-city', 'district-city'].flatMap(
             k => ['above', 'below', 'neutral'].map(cls => __h.w(k, cls))) },
    };
    process.stdout.write(JSON.stringify({ html, helpers }));
  } catch (err) {
    process.stdout.write(JSON.stringify({ __error: String(err) }));
  }
});
"""


def _render(city_mean, district, rankings, render):
    """Run one render scenario in a node VM; return the popup HTML."""
    data = json.loads(DIST_STADTTEILE.read_text(encoding="utf-8"))
    features = [
        {"properties": {k: f["properties"][k] for k in ("code", "name", "mean_value")}}
        for f in data["features"]
    ]
    script = _NODE_RENDER.replace("@@MAIN_PATH@@", str(DIST_MAIN))
    payload = {
        "cityMean": city_mean,
        "district": district,
        "rankings": rankings,
        "features": features,
        "render": render,
    }
    proc = subprocess.run(
        ["node", "-e", script],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert "__error" not in out, out["__error"]
    return out


def _render_html(city_mean, district, rankings, render) -> str:
    return _render(city_mean, district, rankings, render)["html"]


@pytest.fixture(scope="module")
def env_ok() -> bool:
    if shutil.which("node") is None or not DIST_MAIN.exists():
        pytest.skip("node or dist/main.js missing (run make publish)")
    return True


# Sentinel to distinguish "no district" (None) from "default Lindenhof".
_DEFAULT = object()


def _building(props, city_mean=22.2, district=_DEFAULT, rankings=True):
    if district is _DEFAULT:
        district = {"name": "Lindenhof", "mean_value": 26.2}
    return _render_html(city_mean, district, rankings,
                        {"kind": "building", "props": props})


def _district_props(props, city_mean=22.2, rankings=True):
    return _render_html(city_mean, {"name": "Lindenhof", "mean_value": 26.2}, rankings,
                        {"kind": "district", "props": props})


# ---------------------------------------------------------------------
# Delta helpers (FR-003/FR-004/FR-008, R-3/R-11)
# ---------------------------------------------------------------------

@pytest.fixture(scope="module")
def js_helpers(env_ok):
    """Shipped pure delta helpers, computed by the node-VM harness."""
    out = _render(22.2, None, True,
                  {"kind": "building", "props": {"has_value": False}})
    return out["helpers"]


def test_classify_delta_band(js_helpers) -> None:
    """FR-003/FR-004/FR-008: 0.1 pp band inclusive; beyond it above/below."""
    c = js_helpers["c"]  # [0.1, -0.1, 0.1001, -0.1001]
    assert c == ["neutral", "neutral", "above", "below"]


def test_format_delta(js_helpers) -> None:
    """R-3/R-11: neutral always ±0.0 pp; otherwise U+2212 minus, half-up."""
    f = js_helpers["f"]  # [(0.1,'neutral'),(2.7,'above'),(-2.3,'below'),(2.66,'above')]
    assert f == ["\u00b10.0 pp", "+2.7 pp", "\u22122.3 pp", "+2.7 pp"]


def test_delta_class_and_words(js_helpers) -> None:
    """R-4: color classes and exact German assessment words, no em/en dash."""
    d = js_helpers["d"]  # [above, below, neutral]
    assert d == ["delta-up", "delta-down", "delta-neutral"]
    w = js_helpers["w"]
    assert w["bda"] == "\u00fcber dem Stadtteil-Durchschnitt"
    assert w["bdn"] == "auf Stadtteil-Niveau"
    assert w["bcb"] == "unter dem Stadtdurchschnitt"
    assert w["dcn"] == "auf Stadtniveau"
    assert not "".join(w["all"]).count("\u2013")  # no en dash
    assert not "".join(w["all"]).count("\u2014")  # no em dash


# ---------------------------------------------------------------------
# Building popup (FR-001..FR-006)
# ---------------------------------------------------------------------

def test_building_popup_valid_value(env_ok) -> None:
    """FR-001..FR-004: value headline, threshold badge, district + city
    comparison lines with signed deltas and assessment words."""
    html = _building({"has_value": True, "value_str": "26.2"})
    assert "Stadtteil: Lindenhof" in html
    assert "Baumanteil im 60-m-Umkreis" in html
    assert "26.2%" in html
    assert "verfehlt" in html                                  # 26.2 < 30
    assert "26.2 % · \u00b10.0 pp · auf Stadtteil-Niveau" in html  # neutral vs district
    assert "22.2 % · +4.0 pp · \u00fcber dem Stadtdurchschnitt" in html
    assert "Was bedeutet das?" in html


def test_building_popup_below_both(env_ok) -> None:
    """FR-003/FR-004: value below district and city means."""
    html = _building({"has_value": True, "value_str": "10.0"})
    assert "unter dem Stadtteil-Durchschnitt" in html
    assert "unter dem Stadtdurchschnitt" in html
    assert "\u221212.2 pp" in html                             # 10.0 - 22.2


def test_building_popup_threshold_exactly_30(env_ok) -> None:
    """FR-005 edge case: exactly 30.0 counts as erreicht."""
    html = _building({"has_value": True, "value_str": "30.0"})
    assert "erreicht" in html
    assert "verfehlt" not in html


def test_building_popup_no_value(env_ok) -> None:
    """FR-006: en-dash marker, no badge/deltas/city line, district line kept."""
    html = _building({"has_value": False})
    assert "\u2013" in html                                   # UNAVAILABLE en dash
    assert "Durchschnitt im Stadtteil" in html
    assert "26.2 %" in html                                    # plain district mean
    assert "verfehlt" not in html and "erreicht" not in html
    assert "pp" not in html                                    # no deltas
    assert "Stadtdurchschnitt" not in html                     # no city line


def test_building_popup_no_district(env_ok) -> None:
    """contracts/popup-content.md: no district found -> header/context omitted."""
    html = _building({"has_value": True, "value_str": "26.2"},
                     district=None)
    assert "Stadtteil:" not in html
    assert "Durchschnitt im Stadtteil" not in html
    assert "Stadtdurchschnitt" in html                         # city line still shown


def test_building_popup_city_missing(env_ok) -> None:
    """FR-014: city stats missing -> city line hidden, rest intact."""
    html = _building({"has_value": True, "value_str": "26.2"}, city_mean=None)
    assert "Stadtdurchschnitt" not in html
    assert "Durchschnitt im Stadtteil" in html
    assert "verfehlt" in html


# ---------------------------------------------------------------------
# District popup (FR-007..FR-011, FR-014)
# ---------------------------------------------------------------------

def test_district_popup_valid(env_ok) -> None:
    """FR-007..FR-010: header, mean, quartile badge, rank, city line,
    existing stats, footnote."""
    html = _district_props(LINDEHOF)
    assert "Stadtteil: Lindenhof" in html
    assert "Baumanteil im Durchschnitt" in html
    assert "26.2 %" in html
    assert "oberes Mittelfeld" in html                          # rank 13 band
    assert "Platz 13 von 38" in html
    assert "22.2 % · +4.0 pp · \u00fcber dem Stadtdurchschnitt" in html
    assert "Geb\u00e4ude" in html and "2 020".replace(" ", "\u2009") in html  # thin-space thousands
    assert "Anteil unter 30 %" in html
    assert "Was bedeutet das?" in html


def test_district_popup_null_mean(env_ok) -> None:
    """FR-011: name + building count only; rank/quartile/city/share hidden."""
    props = {**LINDEHOF, "mean_value": None}
    html = _district_props(props)
    assert "keine Daten" in html
    assert "Stadtteil: Lindenhof" in html
    assert "Geb\u00e4ude" in html
    assert "Platz" not in html
    assert "Viertel" not in html
    assert "Stadtdurchschnitt" not in html
    assert "Anteil unter 30 %" not in html


def test_district_popup_city_missing(env_ok) -> None:
    """FR-014: city stats missing -> city line hidden, rank/quartile still render."""
    html = _district_props(LINDEHOF, city_mean=None)
    assert "Stadtdurchschnitt" not in html
    assert "Platz 13 von 38" in html
    assert "oberes Mittelfeld" in html


def test_district_popup_rankings_unavailable(env_ok) -> None:
    """R-1/R-2: rankings fetch failed -> rank/quartile hidden, city line kept."""
    html = _district_props(LINDEHOF, rankings=False)
    assert "Platz" not in html
    assert "Viertel" not in html
    assert "Stadtdurchschnitt" in html
    assert "Geb\u00e4ude" in html and "Anteil unter 30 %" in html
