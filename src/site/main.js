/* Mannheim Tree Cover — frontend bootstrap (US1), popup + hover (US2),
 * Bäume toggle (US3). No build tool; vendored libs load via classic
 * <script> tags in index.html (their UMD builds set window globals). */
const maplibregl = window.maplibregl;
const pmtiles = window.pmtiles;

const STYLE_URL = 'style.json';
const ATTRIBUTION_PATH = 'attribution';
const UNAVAILABLE = '\u2013'; // en dash, FR-009

let map = null;
// FR-001..FR-011: one persistent popup instance for the page lifetime.
// closeOnClick: false removes MapLibre's default map-wide close listener
// so a building click never closes the popup (research R-001/R-002).
let buildingPopup = null;
// Feature 011: second persistent popup for the district stats (US2);
// district clicks close the building popup and vice versa.
let districtPopup = null;

// Feature 013 (R-1/R-2): code -> { rank, quartile } computed once at map
// load from the full 38-district set (never viewport-limited). null when
// the fetch failed or fewer than two valid means (FR-014 edge cases).
let districtRankings = null;

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

/* Feature 011 formatting (city-overview.md): percentages with one dot
 * decimal, integers with a thin space thousands separator. */
function formatPercent(value) {
  return `${Number(value).toFixed(1)} %`;
}

function formatInteger(value) {
  return String(value).replace(/\B(?=(\d{3})+(?!\d))/g, '\u2009');
}

/* Feature 013 (R-3, FR-003/FR-004/FR-008): signed-delta comparison
 * helpers. Pure — no map/DOM access — so the node-VM cross-check in
 * tests/acceptance/test_rank.py can exercise them (SC-003). */
const DELTA_TOLERANCE = 0.1; // pp neutral band, inclusive (FR wording normative)

function classifyDelta(delta) {
  if (delta > DELTA_TOLERANCE) return 'above';
  if (delta < -DELTA_TOLERANCE) return 'below';
  return 'neutral';
}

/* R-3/R-11: the displayed delta derives from the classification, so the
 * word and number can never contradict — a raw |delta| <= 0.1 always
 * renders "±0.0 pp". Otherwise sign + magnitude rounded to 1 decimal
 * (half-up on the magnitude), plus sign "+", minus sign U+2212. */
function formatDelta(delta, cls) {
  if (cls === 'neutral') return '\u00b10.0 pp'; // "±0.0 pp"
  const magnitude = Math.abs(delta).toFixed(1); // half-up on the magnitude
  const sign = cls === 'above' ? '+' : '\u2212'; // U+2212 minus for below
  return `${sign}${magnitude} pp`;
}

/* R-4 assessment words, exact German copy per comparison kind (FR-017).
 * "building-district": building vs district mean; "building-city" and
 * "district-city" share the same city-average wording. */
const ASSESSMENT_WORDS = {
  'building-district': {
    above: '\u00fcber dem Stadtteil-Durchschnitt',
    below: 'unter dem Stadtteil-Durchschnitt',
    neutral: 'auf Stadtteil-Niveau',
  },
  'building-city': {
    above: '\u00fcber dem Stadtdurchschnitt',
    below: 'unter dem Stadtdurchschnitt',
    neutral: 'auf Stadtniveau',
  },
  'district-city': {
    above: '\u00fcber dem Stadtdurchschnitt',
    below: 'unter dem Stadtdurchschnitt',
    neutral: 'auf Stadtniveau',
  },
};

function assessmentWord(kind, cls) {
  return ASSESSMENT_WORDS[kind][cls];
}

/* Map a delta classification to its color class (R-12). Neutral gets no
 * color; the class exists so FR-013's "never color-only" holds via the
 * text word rendered alongside. */
function deltaClass(cls) {
  if (cls === 'above') return 'delta-up';
  if (cls === 'below') return 'delta-down';
  return 'delta-neutral';
}

/* Feature 013 (R-2, FR-009/FR-010): district ranking. Pure — no map/DOM
 * access — so the node-VM cross-check in tests/acceptance/test_rank.py
 * exercises the shipped function (SC-003). */
const QUARTILE_LABELS = [
  'oberstes Viertel',
  'oberes Mittelfeld',
  'unteres Mittelfeld',
  'unterstes Viertel',
];

/* Band from rank and n: q1 = ceil(n/4), q2 = q3 = floor(n/4), remainder
 * to the last band. For n = 38: 10/9/9/10 -> 1-10, 11-19, 20-28, 29-38.
 * Returns the band index into QUARTILE_LABELS. */
function quartileBand(rank, n) {
  const q1 = Math.ceil(n / 4);
  const q2 = Math.floor(n / 4);
  const q3 = Math.floor(n / 4);
  if (rank <= q1) return 0;
  if (rank <= q1 + q2) return 1;
  if (rank <= q1 + q2 + q3) return 2;
  return 3;
}

/* R-12: quartile label -> badge color class (cool = better, warm = worse). */
function quartileBadgeClass(label) {
  if (label === 'oberstes Viertel') return 'badge-good';
  if (label === 'oberes Mittelfeld') return 'badge-good-soft';
  if (label === 'unteres Mittelfeld') return 'badge-mid';
  return 'badge-bad'; // unterstes Viertel
}

/* Map district `code` -> { rank, quartile-label }. Sorts by mean_value
 * descending then name ascending (tie-break, FR-009), assigning distinct
 * sequential ranks. JS `<` string ordering matches Python code-point
 * ordering for all 38 BMP names — the reproducibility contract between
 * this implementation and the Python reference. Fewer than two valid
 * means -> null (rank/quartile hidden everywhere). */
function computeDistrictRankings(districtFeatures) {
  const valid = districtFeatures.filter(
    (f) => f.properties && typeof f.properties.mean_value === 'number'
  );
  if (valid.length < 2) return null;
  const sorted = valid.slice().sort((a, b) => {
    const byMean = b.properties.mean_value - a.properties.mean_value;
    if (byMean !== 0) return byMean;
    return a.properties.name < b.properties.name ? -1 : 1;
  });
  const rankings = new Map();
  sorted.forEach((feature, i) => {
    const rank = i + 1;
    rankings.set(feature.properties.code, {
      rank,
      quartile: QUARTILE_LABELS[quartileBand(rank, sorted.length)],
    });
  });
  return rankings;
}

/* Feature 013 (R-1, FR-014): fetch the stadtteile source once at map
 * load (same URL the style's `stadtteile` source already loads, so the
 * browser serves it from cache — no new network transfer) and compute
 * the module-level districtRankings. On failure leave it null so the
 * district popup hides rank/quartile (defensive degradation). */
function loadDistrictRankings() {
  fetch('stadtteile.geojson')
    .then((response) => {
      if (!response.ok) throw new Error(`stadtteile fetch ${response.status}`);
      return response.json();
    })
    .then((data) => {
      districtRankings = computeDistrictRankings(data.features || []);
    })
    .catch((err) => {
      console.warn('district rankings unavailable:', err);
      districtRankings = null;
    });
}

/* Feature 011 (FR-009, R-6): district at a click coordinate via the
 * already-loaded stadtteile source (no fetch). querySourceFeatures
 * returns the viewport features; the containing district always
 * intersects the viewport because the point is inside it. */
function pointInPolygon(x, y, geometry) {
  function ringContains(ring) {
    let inside = false;
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const xi = ring[i][0];
      const yi = ring[i][1];
      const xj = ring[j][0];
      const yj = ring[j][1];
      const intersects = (yi > y) !== (yj > y) &&
        x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;
      if (intersects) inside = !inside;
    }
    return inside;
  }
  if (geometry.type === 'Polygon') return ringContains(geometry.coordinates[0]);
  if (geometry.type === 'MultiPolygon') {
    return geometry.coordinates.some((polygon) => ringContains(polygon[0]));
  }
  return false;
}

function districtAt(lngLat) {
  const features = map.querySourceFeatures('stadtteile');
  for (const feature of features) {
    if (pointInPolygon(lngLat.lng, lngLat.lat, feature.geometry)) {
      return feature.properties || {};
    }
  }
  return null;
}

function boundaryBboxFromStyle() {
  const style = map.getStyle();
  const bbox = style && style.metadata && style.metadata.mannheim_bbox;
  if (Array.isArray(bbox) && bbox.length === 4) return bbox;
  return null;
}

async function boundaryBboxFromFile() {
  try {
    const response = await fetch('boundary.geojson');
    const data = await response.json();
    const feature = data.features && data.features[0];
    const bbox = feature && feature.properties && feature.properties.bbox4326;
    if (Array.isArray(bbox) && bbox.length === 4) return bbox;
  } catch (err) {
    console.warn('boundary.geojson unavailable:', err);
  }
  return null;
}

/* Feature 013 (R-6, FR-001..FR-006): building popup content — district
 * header, headline value, 30 % threshold badge, district and city
 * comparison lines with signed deltas, and the metric footnote. Merges
 * the former buildingDistrictHtml(lngLat) so the whole body is one
 * renderer; the district lookup via districtAt() is unchanged. */
function buildingPopupHtml(props, lngLat) {
  const district = districtAt(lngLat);
  const header = district && district.name
    ? `<div class="popup-header">Stadtteil: ${escapeHtml(district.name)}</div>`
    : '';

  const hasValue = props.has_value === true;
  const valueDisplay = hasValue ? `${escapeHtml(props.value_str)}%` : UNAVAILABLE;

  let badge = '';
  let districtLine = '';
  let cityLine = '';

  if (hasValue) {
    const value = Number(props.value_str);
    const reached = value >= 30; // exactly 30.0 counts as erreicht (FR-005)
    badge = `<div class="popup-badge ${reached ? 'badge-good' : 'badge-bad'}">${reached ? 'erreicht' : 'verfehlt'}</div>`;

    // FR-003: building vs district mean (delta + word, only when the
    // district has a mean).
    if (district && typeof district.mean_value === 'number') {
      const delta = value - district.mean_value;
      const cls = classifyDelta(delta);
      districtLine = `<div class="popup-context-line ${deltaClass(cls)}">` +
        `<div class="popup-label">Durchschnitt im Stadtteil</div>` +
        `<div class="popup-value">${formatPercent(district.mean_value)} · ${formatDelta(delta, cls)} · ${assessmentWord('building-district', cls)}</div></div>`;
    }

    // FR-004: building vs city average (hidden when city stats missing,
    // FR-014).
    const cityMean = cityStats();
    if (typeof cityMean === 'number') {
      const delta = value - cityMean;
      const cls = classifyDelta(delta);
      cityLine = `<div class="popup-context-line ${deltaClass(cls)}">` +
        `<div class="popup-label">Stadtdurchschnitt</div>` +
        `<div class="popup-value">${formatPercent(cityMean)} · ${formatDelta(delta, cls)} · ${assessmentWord('building-city', cls)}</div></div>`;
    }
  } else if (district && district.mean_value != null) {
    // FR-006: no value -> no badge/deltas/city line, but the plain
    // district context line still renders.
    districtLine = `<div class="popup-context-line">` +
      `<div class="popup-label">Durchschnitt im Stadtteil</div>` +
      `<div class="popup-value">${formatPercent(district.mean_value)}</div></div>`;
  }

  const context = (districtLine || cityLine)
    ? `<div class="popup-context">${districtLine}${cityLine}</div>`
    : '';

  // FR-012 (R-8): one plain-German sentence for the metric; the 30 %
  // threshold is explained only on the building popup.
  const footnote = `<div class="popup-footnote"><div class="popup-label">Was bedeutet das?</div>` +
    `<p>Der Baumanteil im 60-m-Umkreis ist der Anteil der Baumkronen an der Fl\u00e4che im Umkreis von 60 m um das Geb\u00e4ude. Ab 30 % gilt die Beschattung als ausreichend.</p></div>`;

  return header +
    `<div class="popup-headline"><div class="popup-label">Baumanteil im 60-m-Umkreis</div><div class="popup-value popup-value-headline">${valueDisplay}</div></div>` +
    badge + context + footnote;
}

function districtPopupHtml(props) {
  const hasMean = props.mean_value != null;
  const name = escapeHtml(props.name);
  const ranking = hasMean && districtRankings ? districtRankings.get(props.code) : undefined;

  const meanDisplay = hasMean ? formatPercent(props.mean_value) : 'keine Daten';
  const headline = `<div class="popup-headline">` +
    `<div class="popup-label">Baumanteil im Durchschnitt</div>` +
    `<div class="popup-value popup-value-headline">${meanDisplay}</div></div>`;

  let badge = '';
  let rankLine = '';
  let cityLine = '';
  let shareLine = '';

  if (hasMean) {
    // FR-010: quartile badge + FR-009 rank line, only when the
    // rankings are available (fetch succeeded, >= 2 valid means).
    if (ranking) {
      badge = `<div class="popup-badge ${quartileBadgeClass(ranking.quartile)}">${ranking.quartile}</div>`;
      rankLine = `<div class="popup-context-line"><div class="popup-value">Platz ${ranking.rank} von ${districtRankings.size}</div></div>`;
    }

    // FR-008: district vs city average (hidden when city stats missing,
    // FR-014).
    const cityMean = cityStats();
    if (typeof cityMean === 'number') {
      const delta = props.mean_value - cityMean;
      const cls = classifyDelta(delta);
      cityLine = `<div class="popup-context-line ${deltaClass(cls)}">` +
        `<div class="popup-label">Stadtdurchschnitt</div>` +
        `<div class="popup-value">${formatPercent(cityMean)} · ${formatDelta(delta, cls)} · ${assessmentWord('district-city', cls)}</div></div>`;
    }

    // FR-007: existing statistics kept when the mean is valid.
    shareLine = `<div class="popup-context-line">` +
      `<div class="popup-label">Anteil unter 30 %</div>` +
      `<div class="popup-value">${formatPercent(props.share_lt30)}</div></div>`;
  }

  // FR-007: building count always shown (FR-011 keeps name + count when
  // the mean is missing).
  const buildingLine = `<div class="popup-context-line">` +
    `<div class="popup-label">Geb\u00e4ude</div>` +
    `<div class="popup-value">${formatInteger(props.n_buildings)}</div></div>`;

  const context = `<div class="popup-context">${cityLine}${rankLine}${buildingLine}${shareLine}</div>`;

  // FR-012 (R-8): one plain-German sentence for the district mean metric.
  const footnote = `<div class="popup-footnote"><div class="popup-label">Was bedeutet das?</div>` +
    `<p>Der Baumanteil im Durchschnitt ist der mittlere Baumanteil im 60-m-Umkreis aller Geb\u00e4ude in diesem Stadtteil.</p></div>`;

  return `<div class="popup-header">Stadtteil: ${name}</div>` + headline + badge + context + footnote;
}

function openDistrictPopup(event, feature) {
  if (buildingPopup) buildingPopup.remove();
  if (!districtPopup) {
    // feature 011: own className, closable, offset 8 (district-stats.md)
    districtPopup = new maplibregl.Popup({
      closeButton: true,
      offset: 8,
      className: 'district-popup',
      closeOnClick: false,
    });
    localizePopupClose(districtPopup);
  }
  districtPopup
    .setLngLat(event.lngLat)
    .setHTML(districtPopupHtml(feature.properties || {}));
  if (!districtPopup.isOpen()) {
    districtPopup.addTo(map);
  }
}

function wireBuildingsInteractions() {
  // FR-014: selection pointer on hover
  map.on('mousemove', 'buildings-fill', () => {
    map.getCanvas().style.cursor = 'pointer';
  });
  map.on('mouseleave', 'buildings-fill', () => {
    map.getCanvas().style.cursor = '';
  });

  // FR-001..FR-011: single persistent popup instance, created once.
  // closeOnClick: false disables MapLibre's default map-wide close
  // listener so a building click never closes the popup (R-001/R-002).
  if (!buildingPopup) {
    buildingPopup = new maplibregl.Popup({
      closeButton: true,
      offset: 8,
      className: 'building-popup',
      closeOnClick: false,
    });
  }

  // FR-002/FR-003: building click updates the single popup at the
  // click point. addTo(map) re-attaches after a previous close (FR-011).
  // FR-007: has_value === false shows the en dash, never 0.00%.
  // Feature 011: the district context lines (FR-009) are appended
  // here; a district popup is closed by any building click (click
  // arbitration, district-stats.md).
  map.on('click', 'buildings-fill', (event) => {
    const feature = event.features && event.features[0];
    if (!feature) return;
    if (districtPopup) districtPopup.remove();
    buildingPopup
      .setLngLat(event.lngLat)
      .setHTML(buildingPopupHtml(feature.properties || {}, event.lngLat));
    if (!buildingPopup.isOpen()) {
      buildingPopup.addTo(map);
    }
  });

  // FR-003 / feature 011 click arbitration (district-stats.md):
  // 1. building hit -> the layer-filtered handler above owns it;
  // 2. no building, district hit -> district popup opens, building
  //    popup closes;
  // 3. neither hit -> both popups close.
  // The layer-filtered click fires first for building clicks (research
  // R-003); boundary mask and outside-Mannheim clicks hit neither.
  map.on('click', (event) => {
    const buildingHits = map.queryRenderedFeatures(event.point, {
      layers: ['buildings-fill'],
    });
    if (buildingHits.length > 0) return;
    const districtHits = map.queryRenderedFeatures(event.point, {
      layers: ['stadtteile-fill'],
    });
    if (districtHits.length > 0) {
      openDistrictPopup(event, districtHits[0]);
    } else {
      buildingPopup.remove();
      if (districtPopup) districtPopup.remove();
    }
  });
}

function wireTreesToggle() {
  const button = document.getElementById('baeume');
  if (!button) return;
  let visible = false;
  button.addEventListener('click', () => {
    visible = !visible;
    // FR-016: visibility-only change; camera untouched
    if (map.getLayer('trees-fill')) {
      map.setLayoutProperty('trees-fill', 'visibility', visible ? 'visible' : 'none');
    }
    button.classList.toggle('active', visible);
    button.setAttribute('aria-pressed', String(visible));
  });
}

/* Feature 011 (contracts/city-overview.md): the city overview card is
 * a view over publish-time metadata; it hides itself when the metadata
 * is missing (stale bundle). */
/* Feature 013 (R-5, FR-014): city-average reference for both popups,
 * read at render time from the same metadata block renderCityPanel()
 * consumes, so popups and the "Mannheim im Überblick" panel can never
 * contradict. Returns mean_value_pct (number) or null when missing. */
function cityStats() {
  const style = map.getStyle();
  const stats = style && style.metadata && style.metadata.city_stats;
  return stats && typeof stats.mean_value_pct === 'number'
    ? stats.mean_value_pct
    : null;
}

function renderCityPanel() {
  const panel = document.getElementById('city-panel');
  if (!panel) return;
  const style = map.getStyle();
  const stats = style && style.metadata && style.metadata.city_stats;
  if (!stats || typeof stats.mean_value_pct !== 'number') {
    panel.hidden = true;
    return;
  }
  panel.innerHTML =
    '<h2 class="panel-title">Mannheim im Überblick</h2>' +
    `<p>Durchschnittlicher Baumanteil im 60-m-Umkreis: ${formatPercent(stats.mean_value_pct)}</p>` +
    `<p>Gebäude mit ausreichender Beschattung (30 %): ${formatPercent(stats.share_gte30_pct)}</p>` +
    `<p>Anzahl der erkannten Baumflächen: ${formatInteger(stats.tree_count)}</p>`;
  panel.hidden = false;
}

function wireBrightnessSlider() {
  // FR-001..FR-007: slider value (5..100) maps identity to the
  // basemap's raster-brightness-max (0.05..1.0); default 65 == the
  // style's static 0.65, so a load with no interaction renders the
  // published appearance (FR-003). Session-only: nothing is stored.
  const slider = document.getElementById('brightness-slider');
  if (!slider) return;
  const apply = () => {
    const v = Number(slider.value);
    if (map.getLayer('basemap')) {
      map.setPaintProperty('basemap', 'raster-brightness-max', v / 100);
    }
    // FR-019: below 25 the basemap crossfades into a photo-negative —
    // basemap-inverted (min 0.65 / max 0, so the raster shader computes
    // out = 0.65 * (1 - in) — inverted features never exceed the 0.65
    // cap, clarification Q4) renders streets and labels lighter than
    // the near-black background. Opacity s(v) = clamp((25 - v)/20, 0, 1);
    // visibility "none" at s = 0 skips the wasted render pass
    // (research R-011/R-012). Values stay in [0, 1] — MapLibre clamps
    // raster-brightness-* outside that range (research R-011).
    const s = Math.min(1, Math.max(0, (25 - v) / 20));
    if (map.getLayer('basemap-inverted')) {
      if (s > 0) {
        map.setLayoutProperty('basemap-inverted', 'visibility', 'visible');
        map.setPaintProperty('basemap-inverted', 'raster-opacity', s);
      } else {
        map.setPaintProperty('basemap-inverted', 'raster-opacity', 0);
        map.setLayoutProperty('basemap-inverted', 'visibility', 'none');
      }
    }
  };
  slider.addEventListener('input', apply);
  apply();
}

function wireErrorHandling() {
  // FR-020: a failed trees load never blocks buildings
  map.on('error', (event) => {
    const sourceId = event && event.sourceId;
    if (sourceId === 'trees') {
      console.warn('trees layer unavailable, buildings unaffected:', event.error);
      if (map.getLayer('trees-fill')) {
        map.setLayoutProperty('trees-fill', 'visibility', 'none');
      }
    } else if (sourceId === 'buildings') {
      // pmtiles-sources contract: surface unrecoverable buildings failure
      const slot = document.getElementById('attribution');
      if (slot) {
        slot.innerHTML = 'Gebäudedaten derzeit nicht verfügbar.';
      }
      console.error('buildings layer failed:', event.error);
    }
  });
}

/* First-visit story modal (US1, FR-004/FR-008/FR-009/FR-014).
 * Self-contained: no MapLibre API calls, static DOM only. */
function wireStoryModal() {
  const backdrop = document.getElementById('story-backdrop');
  const dialog = document.getElementById('story-dialog');
  const closeButton = document.getElementById('story-close');
  if (!backdrop || !dialog || !closeButton) return;

  let previousFocus = null;
  let inMemoryDismissed = false; // FR-013 fallback when storage unavailable

  // Dismissal persistence (FR-005, contracts/dismissal-state.md):
  // key present => never re-show in this browser; written only on
  // explicit dismissal; every access guarded (FR-013).
  const storage = {
    read() {
      try {
        return window.localStorage.getItem('matreecover.story-dismissed') === '1';
      } catch (err) {
        return inMemoryDismissed;
      }
    },
    write() {
      try {
        window.localStorage.setItem('matreecover.story-dismissed', '1');
      } catch (err) {
        inMemoryDismissed = true;
      }
    },
  };

  if (storage.read()) return; // already dismissed in this browser

  const focusables = () =>
    [...dialog.querySelectorAll('button, a[href]')]
      .filter((el) => !el.hidden);

  function close() {
    backdrop.remove();
    document.removeEventListener('keydown', onKeydown);
    closeButton.removeEventListener('click', onCloseClick);
    storage.write(); // explicit dismissal only (close button / Escape)
    if (previousFocus && previousFocus.focus) previousFocus.focus();
  }

  function onKeydown(event) {
    if (event.key === 'Escape') {
      event.preventDefault();
      close();
      return;
    }
    if (event.key !== 'Tab') return;
    // FR-008: trap focus inside the dialog while open
    const els = focusables();
    if (els.length === 0) return;
    const first = els[0];
    const last = els[els.length - 1];
    const current = document.activeElement;
    if (event.shiftKey) {
      if (current === first || !dialog.contains(current)) {
        event.preventDefault();
        last.focus();
      }
    } else if (current === last || !dialog.contains(current)) {
      event.preventDefault();
      first.focus();
    }
  }

  function onCloseClick() {
    close();
  }

  function open() {
    previousFocus = document.activeElement;
    backdrop.hidden = false;
    dialog.focus(); // FR-009: screen reader announces dialog from aria-labelledby
    document.addEventListener('keydown', onKeydown);
    closeButton.addEventListener('click', onCloseClick);
    // Feature 016 (Clarifications 2026-08-09, final): the story copy
    // lives in this modal (single DOM copy, full feature 007 content).
    // The modal shows over the map without scrolling; links open in
    // new tabs; no scrollIntoView, scroll position stays put.
  }

  open();
}

/* Feature 012 (contracts/surface-interaction.md): the shared
 * legend/summary surface toggle. Flips `is-collapsed` on #surface,
 * mirrors state on the button (aria-expanded, aria-controls), and
 * calls map.setPadding so building and district popups stay fully
 * visible above the surface (FR-006, FR-008). */
function wireSurfaceToggle() {
  const surface = document.getElementById('surface');
  const toggle = document.getElementById('surface-toggle');
  if (!surface || !toggle) return;

  /* Apply popup-clearance padding. Only the mobile bottom sheet needs
   * bottom padding (popups open above it). The desktop panel is
   * top-left, so bottom padding would only shove the map up; popups
   * clear a top-left panel naturally (FR-006, US3). Measured after
   * the expand/collapse transition settles (0.28 s). */
  const syncPadding = () => {
    if (!map) return;
    const collapsed = surface.classList.contains('is-collapsed');
    const mobileSheet = window.matchMedia('(max-width: 767.98px)').matches;
    setTimeout(() => {
      map.setPadding({ bottom: collapsed || !mobileSheet ? 0 : surface.offsetHeight });
    }, 300);
  };

  const apply = () => {
    const collapsed = surface.classList.contains('is-collapsed');
    toggle.setAttribute('aria-expanded', String(!collapsed));
    toggle.setAttribute('aria-label', collapsed ? 'Legende einblenden' : 'Legende ausblenden');
    syncPadding();
  };

  toggle.addEventListener('click', () => {
    surface.classList.toggle('is-collapsed');
    apply();
  });
  // Keep popup clearance accurate if the sheet size changes (e.g. the
  // city panel renders, the window resizes across the breakpoint).
  window.addEventListener('resize', () => {
    if (map && !surface.classList.contains('is-collapsed')) syncPadding();
  });
  apply(); // sync initial ARIA state + padding to the HTML default
}

/* Feature 012 localization: MapLibre's default controls ship English
 * tooltips (zoom in/out, compass, attribution toggle, popup close).
 * Every tooltip on the site must be German (FR-011, FR-014). */
function setGermanLabel(el, label) {
  if (!el) return;
  el.setAttribute('aria-label', label);
  el.title = label;
}

function localizePopupClose(popup) {
  if (!popup) return;
  popup.on('open', () => {
    const root = popup.getElement();
    setGermanLabel(root && root.querySelector('.maplibregl-popup-close-button'), 'Schließen');
  });
}

/* Localize MapLibre tooltips and, on mobile, collapse the attribution
 * to the compact button by default (screen overload, user wish). */
function localizeMapLibreControls() {
  setGermanLabel(document.querySelector('.maplibregl-ctrl-zoom-in'), 'Vergrößern');
  setGermanLabel(document.querySelector('.maplibregl-ctrl-zoom-out'), 'Verkleinern');
  setGermanLabel(document.querySelector('.maplibregl-ctrl-compass'), 'Norden ausrichten');
  setGermanLabel(document.querySelector('.maplibregl-ctrl-attrib-button'), 'Quellenangaben');
  localizePopupClose(buildingPopup);
  localizePopupClose(districtPopup);
  // Mobile (< 768 px): attribution starts collapsed (ⓘ button only).
  // Removing both open markers keeps it collapsed; the ⓘ tap still
  // expands it via MapLibre's own toggle.
  if (window.matchMedia('(max-width: 767.98px)').matches) {
    const attrib = document.querySelector('.maplibregl-ctrl-attrib');
    if (attrib) {
      attrib.classList.add('maplibregl-compact');
      attrib.classList.remove('maplibregl-compact-show');
      attrib.removeAttribute('open');
    }
  }
}

async function onMapLoad() {
  let bbox = boundaryBboxFromStyle();
  if (!bbox) bbox = await boundaryBboxFromFile();

  if (bbox) {
    // FR-002: full official boundary, minimal padding, north up, no flight
    map.fitBounds(
      [
        [bbox[0], bbox[1]],
        [bbox[2], bbox[3]],
      ],
      { padding: 24, bearing: 0, pitch: 0, duration: 0 }
    );
  }

  // FR-017: zoom in/out + north reset
  map.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right');

  // FR-019: required attributions reachable
  map.addControl(
    new maplibregl.AttributionControl({
      compact: true,
      customAttribution: `<a href="${ATTRIBUTION_PATH}">Datenquellen</a>`,
    }),
    'bottom-right'
  );

  wireBuildingsInteractions();
  wireTreesToggle();
  wireBrightnessSlider();
  wireErrorHandling();
  renderCityPanel();
  loadDistrictRankings(); // feature 013: rank/quartile from the full 38-district set
  localizeMapLibreControls();
}

function init() {
  // pmtiles protocol: client-side range reads, no tile server
  const protocol = new pmtiles.Protocol();
  maplibregl.addProtocol('pmtiles', protocol.tile);

  map = new maplibregl.Map({
    container: 'map',
    style: STYLE_URL,
    attributionControl: false,
    fadeDuration: 0, // feature 014: no cross-fade render pass at init/zoom (contracts/low-zoom-simplification.md)
  });
  window.__map = map; // debug handle (smoke checks)
  window.__renderCityPanel = renderCityPanel; // debug handle (perf re-measurement)
  window.__districtRankings = computeDistrictRankings; // feature 013 debug handle (SC-003 cross-check)
  wireStoryModal();

  // Feature 012 (FR-008): the surface is collapsed by default on
  // mobile (FR-001, HTML class); on desktop it starts expanded to
  // match the previous default view. State stays session-only.
  const surface = document.getElementById('surface');
  if (surface && window.matchMedia('(min-width: 768px)').matches) {
    surface.classList.remove('is-collapsed');
  }
  wireSurfaceToggle();

  map.on('load', onMapLoad);
}

init();
