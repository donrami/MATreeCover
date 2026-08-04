/* Mannheim Tree Cover — frontend bootstrap (US1), popup + hover (US2),
 * Bäume toggle (US3). No build tool; vendored libs load via classic
 * <script> tags in index.html (their UMD builds set window globals). */
const maplibregl = window.maplibregl;
const pmtiles = window.pmtiles;

const STYLE_URL = 'style.json';
const ATTRIBUTION_HTML = 'attribution.html';
const UNAVAILABLE = '\u2013'; // en dash, FR-009

let map = null;
// FR-001..FR-011: one persistent popup instance for the page lifetime.
// closeOnClick: false removes MapLibre's default map-wide close listener
// so a building click never closes the popup (research R-001/R-002).
let buildingPopup = null;

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
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
  map.on('click', 'buildings-fill', (event) => {
    const feature = event.features && event.features[0];
    if (!feature) return;
    const props = feature.properties || {};
    const hasValue = props.has_value === true;
    const valueDisplay = hasValue ? `${escapeHtml(props.value_str)}%` : UNAVAILABLE;
    buildingPopup
      .setLngLat(event.lngLat)
      .setHTML(`<div class="popup-label">Baumanteil im 60-m-Umkreis</div><div class="popup-value">${valueDisplay}</div>`);
    if (!buildingPopup.isOpen()) {
      buildingPopup.addTo(map);
    }
  });

  // FR-003: map-level close — empty space (no building at point)
  // closes the popup. Layer-filtered click above fires first for
  // building clicks; this handler then sees the building feature and
  // does nothing (research R-003). Boundary mask and outside-Mannheim
  // clicks have no buildings-fill feature, so they close the popup.
  map.on('click', (event) => {
    const features = map.queryRenderedFeatures(event.point, {
      layers: ['buildings-fill'],
    });
    if (features.length === 0) {
      buildingPopup.remove();
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
    // basemap-inverted (min 1 / max 0, so the raster shader computes
    // out = 1 - in) renders streets and labels lighter than the
    // near-black background. Opacity s(v) = clamp((25 - v)/20, 0, 1);
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
      customAttribution: `<a href="${ATTRIBUTION_HTML}">Datenquellen</a>`,
    }),
    'bottom-right'
  );

  wireBuildingsInteractions();
  wireTreesToggle();
  wireBrightnessSlider();
  wireErrorHandling();
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
  map.on('load', onMapLoad);
}

init();
