"""Feature 013 — SC-003: district rank/quartile automated cross-check.

Two independent computations of the district rankings must agree 100 %
over the 38-district set:

1. A Python reference implementing contracts/rank-quartile.md (R-2):
   filter valid means, sort by mean descending then name ascending
   (tie-break, FR-009), assign distinct sequential ranks 1..n, and
   derive the quartile band with the q1 = ceil(n/4) / q2 = q3 = floor(n/4)
   formula (FR-010; n = 38 -> 10/9/9/10).
2. The shipped `computeDistrictRankings` from `dist/main.js`, loaded in a
   node VM with minimal browser stubs, so the cross-check tests the real
   function that renders the popup (R-10), not a re-implementation.

The JS side is skipped when node or `dist/main.js` is missing (existing
dist-fixture pattern); it also requires `make publish` to have refreshed
`dist/main.js` from `src/site/main.js`.
"""

from __future__ import annotations

import json
import math
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DIST_STADTTEILE = REPO_ROOT / "dist" / "stadtteile.geojson"
DIST_MAIN = REPO_ROOT / "dist" / "main.js"

QUARTILE_LABELS = [
    "oberstes Viertel",
    "oberes Mittelfeld",
    "unteres Mittelfeld",
    "unterstes Viertel",
]


def _quartile_label(rank: int, n: int) -> str:
    """R-2 band formula. For n = 38: 1-10, 11-19, 20-28, 29-38."""
    q1 = math.ceil(n / 4)
    q2 = math.floor(n / 4)
    q3 = math.floor(n / 4)
    if rank <= q1:
        return QUARTILE_LABELS[0]
    if rank <= q1 + q2:
        return QUARTILE_LABELS[1]
    if rank <= q1 + q2 + q3:
        return QUARTILE_LABELS[2]
    return QUARTILE_LABELS[3]


def python_reference_rankings(features: list[dict]) -> dict[str, dict]:
    """Return {code: {rank, quartile}} per R-2. None if < 2 valid means."""
    valid = [
        f for f in features
        if f.get("properties") and f["properties"].get("mean_value") is not None
    ]
    if len(valid) < 2:
        return None
    # sort by mean descending, then name ascending (tie-break, FR-009)
    sorted_ = sorted(
        valid,
        key=lambda f: (
            -float(f["properties"]["mean_value"]),
            f["properties"]["name"],
        ),
    )
    n = len(sorted_)
    rankings = {}
    for i, f in enumerate(sorted_):
        rank = i + 1
        rankings[f["properties"]["code"]] = {
            "rank": rank,
            "quartile": _quartile_label(rank, n),
        }
    return rankings


@pytest.fixture(scope="module")
def dist_features() -> list[dict]:
    if not DIST_STADTTEILE.exists():
        pytest.skip("dist/stadtteile.geojson missing (run make publish)")
    data = json.loads(DIST_STADTTEILE.read_text(encoding="utf-8"))
    return data["features"]


def test_reference_ranks_are_1_to_38_unique(dist_features) -> None:
    """SC-003: exactly ranks 1..38 over the 38-district set, no ties."""
    ref = python_reference_rankings(dist_features)
    assert len(ref) == 38
    ranks = sorted(v["rank"] for v in ref.values())
    assert ranks == list(range(1, 39))


def test_reference_band_bounds(dist_features) -> None:
    """FR-010: every quartile label matches the band formula for its rank
    (n = 38 -> 1-10 / 11-19 / 20-28 / 29-38)."""
    ref = python_reference_rankings(dist_features)
    for code, v in ref.items():
        expected = _quartile_label(v["rank"], len(ref))
        assert v["quartile"] == expected, (code, v, expected)


def test_reference_tie_breaks_alphabetical(dist_features) -> None:
    """FR-009: tied means get distinct sequential ranks, alphabetical."""
    ref = python_reference_rankings(dist_features)
    by_name = {
        f["properties"]["name"]: ref[f["properties"]["code"]]["rank"]
        for f in dist_features
    }
    assert by_name["Friedrichsfeld"] < by_name["Neckarau"]  # both 21.5
    assert by_name["Neckarstadt-Nordost"] < by_name["Seckenheim"]  # both 19.5


def test_reference_table_spot_checks(dist_features) -> None:
    """contracts/rank-quartile.md reference table anchors."""
    ref = python_reference_rankings(dist_features)
    by_name = {
        f["properties"]["name"]: ref[f["properties"]["code"]]
        for f in dist_features
    }
    assert by_name["Lindenhof"] == {"rank": 13, "quartile": "oberes Mittelfeld"}
    assert by_name["Niederfeld"] == {"rank": 1, "quartile": "oberstes Viertel"}
    assert by_name["Innenstadt"] == {"rank": 38, "quartile": "unterstes Viertel"}


# ---------------------------------------------------------------------
# JS cross-check: the shipped computeDistrictRankings via a node VM.
# ---------------------------------------------------------------------

_NODE_STUB = r"""
const vm = require('vm');
const fs = require('fs');
let input = '';
process.stdin.on('data', c => (input += c));
process.stdin.on('end', () => {
  const features = JSON.parse(input);
  class FakeMap { on(){} addControl(){} fitBounds(){} getStyle(){ return null; }
    getCanvas(){ return { style: {} }; } }
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
  };
    vm.createContext(sandbox);
  try {
    vm.runInContext(fs.readFileSync('@@MAIN_PATH@@', 'utf8'), sandbox);
    const out = sandbox.computeDistrictRankings(features);
    const result = {};
    if (out) for (const [code, v] of out) result[code] = v;
    process.stdout.write(JSON.stringify(result));
  } catch (err) {
    process.stdout.write(JSON.stringify({ __error: String(err) }));
  }
});
"""


def _js_rankings(features: list[dict]) -> dict:
    """Run the shipped computeDistrictRankings in a node VM."""
    if shutil.which("node") is None:
        pytest.skip("node not available")
    if not DIST_MAIN.exists():
        pytest.skip("dist/main.js missing (run make publish)")
    # simplified feature objects: the JS reads only .properties
    slim = [
        {"properties": {k: f["properties"][k] for k in ("code", "name", "mean_value")}}
        for f in features
    ]
    script = _NODE_STUB.replace('@@MAIN_PATH@@', str(DIST_MAIN))
    proc = subprocess.run(
        ["node", "-e", script],
        input=json.dumps(slim),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    assert "__error" not in result, result["__error"]
    return result


@pytest.mark.skipif(
    shutil.which("node") is None or not DIST_MAIN.exists(),
    reason="node or dist/main.js missing (run make publish)",
)
def test_js_ranks_match_python_reference(dist_features) -> None:
    """SC-003: all 38 ranks + quartiles match the Python reference 100 %."""
    ref = python_reference_rankings(dist_features)
    js = _js_rankings(dist_features)
    assert len(js) == len(ref)
    for code, expected in ref.items():
        assert code in js, code
        assert js[code] == expected, (code, expected, js[code])


@pytest.mark.skipif(
    shutil.which("node") is None or not DIST_MAIN.exists(),
    reason="node or dist/main.js missing (run make publish)",
)
def test_js_returns_null_below_two_valid_means(dist_features) -> None:
    """R-2 step 5: fewer than two valid means -> no rankings at all."""
    if shutil.which("node") is None:
        pytest.skip("node not available")
    script = _NODE_STUB.replace('@@MAIN_PATH@@', str(DIST_MAIN))
    slim = [{"properties": {"code": "A", "name": "A", "mean_value": 10.0}}]
    proc = subprocess.run(
        ["node", "-e", script],
        input=json.dumps(slim),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout) == {}
