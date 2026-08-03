/* Mannheim Tree Cover — frontend bootstrap (US1), popup + hover (US2),
 * Bäume toggle (US3). No build tool; vendored libs load via classic
 * <script> tags in index.html (their UMD builds set window globals). */
const maplibregl = window.maplibregl;
const pmtiles = window.pmtiles;

const STYLE_URL = 'style.json';
const ATTRIBUTION_HTML = 'attribution.html';
const UNAVAILABLE = '\u2013'; // en dash, FR-009

let map = null;

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

  // FR-008/FR-009/FR-014: compact popup with the two-decimal value
  map.on('click', 'buildings-fill', (event) => {
    const feature = event.features && event.features[0];
    if (!feature) return;
    const props = feature.properties || {};
    const hasValue = props.has_value === true;
    const valueStr = hasValue ? `${escapeHtml(props.value_str)}%` : UNAVAILABLE;
    new maplibregl.Popup({ closeButton: true, offset: 8, className: 'building-popup' })
      .setLngLat(event.lngLat)
      .setHTML(`<div class="popup-label">Baumanteil im 60-m-Umkreis</div><div class="popup-value">${valueStr}</div>`)
      .addTo(map);
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
