// Cloudflare Worker serving the Mannheim tree-cover map at
// https://abu-hamad.de/map/ (specs/005-host-on-personal-domain,
// contracts/hosting-config.md §1).
//
// US1 scope: canonical redirects + static asset serving. The R2
// data path (buildings.pmtiles, trees.pmtiles, buildings.geojson)
// is added by US2 (tasks.md T008) — until then those files are
// intentionally absent and return 404, which the frontend surfaces
// as "Gebäudedaten derzeit nicht verfügbar".

const CANONICAL_ORIGIN = "https://abu-hamad.de";

// The three large data files are excluded from the assets directory
// (wrangler.toml) and not yet served (US2).
const DATA_KEYS = new Set([
  "buildings.pmtiles",
  "trees.pmtiles",
  "buildings.geojson",
]);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // www variant of the map path -> canonical apex (single 301, FR-003).
    if (url.hostname.startsWith("www.") && (path === "/map" || path.startsWith("/map/"))) {
      return Response.redirect(CANONICAL_ORIGIN + (path === "/map" ? "/map/" : path), 301);
    }

    // /map without trailing slash -> /map/ (relative asset refs require
    // the trailing slash, research R-004).
    if (path === "/map") {
      return Response.redirect(CANONICAL_ORIGIN + "/map/", 301);
    }

    // The production routes only ever send /map* here (contract
    // hosting-config.md §1); anything else falls through to the origin.
    if (!path.startsWith("/map/")) {
      return env.ASSETS.fetch(request);
    }

    // Data files: not served until US2. 404 keeps the frontend's
    // buildings-failure handling honest and never serves partial data.
    const key = path.slice("/map/".length);
    if (DATA_KEYS.has(key)) {
      return new Response("Not Found", { status: 404 });
    }

    // Everything else under /map/ is a static asset from dist/.
    // The ASSETS binding resolves paths against the assets root, so
    // the /map prefix is stripped: /map/style.json -> /style.json
    // (the browser-visible URL stays /map/style.json).
    const assetUrl = new URL(request.url);
    assetUrl.pathname = path.slice("/map".length) || "/";
    return env.ASSETS.fetch(new Request(assetUrl, request));
  },
};
