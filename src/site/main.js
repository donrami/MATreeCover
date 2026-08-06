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

/* Feature 011 (FR-009): building popup content — the existing value
 * line plus the district context lines (R-6). */
function buildingPopupHtml(props) {
  const hasValue = props.has_value === true;
  const valueDisplay = hasValue ? `${escapeHtml(props.value_str)}%` : UNAVAILABLE;
  return `<div class="popup-label">Baumanteil im 60-m-Umkreis</div><div class="popup-value">${valueDisplay}</div>`;
}

function buildingDistrictHtml(lngLat) {
  const district = districtAt(lngLat);
  if (!district) return '';
  const mean = district.mean_value == null
    ? 'keine Daten'
    : formatPercent(district.mean_value);
  return `<div class="popup-label">Stadtteil</div><div class="popup-value">${escapeHtml(district.name)}</div>` +
    `<div class="popup-label">Durchschnitt im Stadtteil</div><div class="popup-value">${mean}</div>`;
}

function districtPopupHtml(props) {
  const mean = props.mean_value == null
    ? 'keine Daten'
    : formatPercent(props.mean_value);
  return `<div class="popup-label">Stadtteil</div><div class="popup-value">${escapeHtml(props.name)}</div>` +
    `<div class="popup-label">Gebäude</div><div class="popup-value">${formatInteger(props.n_buildings)}</div>` +
    `<div class="popup-label">Baumanteil im Durchschnitt</div><div class="popup-value">${mean}</div>` +
    `<div class="popup-label">Anteil unter 30 %</div><div class="popup-value">${formatPercent(props.share_lt30)}</div>`;
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
      .setHTML(buildingPopupHtml(feature.properties || {}) + buildingDistrictHtml(event.lngLat));
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
  }

  open();
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
}

function init() {
  // pmtiles protocol: client-side range reads, no tile server
  const protocol = new pmtiles.Protocol();
  maplibregl.addProtocol('pmtiles', protocol.tile);

  map = new maplibregl.Map({
    container: 'map',
    style: STYLE_URL,
    attributionControl: false,
  });
  window.__map = map; // debug handle (smoke checks)
  window.__renderCityPanel = renderCityPanel; // debug handle (perf re-measurement)
  wireStoryModal();
  map.on('load', onMapLoad);
}

init();
