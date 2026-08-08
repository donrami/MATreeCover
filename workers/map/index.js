// Cloudflare Worker serving the Mannheim tree-cover map at
// https://abu-hamad.de/map/ (specs/005-host-on-personal-domain,
// contracts/hosting-config.md §1).
//
// US1: canonical redirects + static asset serving.
// US2: R2 data files (buildings.pmtiles, trees.pmtiles,
// buildings.geojson) served with HTTP Range passthrough.

const CANONICAL_ORIGIN = "https://abu-hamad.de";

// Build a Content-Range header value ("bytes start-end/size") from a
// single-range HTTP Range header. Handles bytes=start-end,
// bytes=start- and bytes=-suffix. PMTiles clients send single
// ranges; multi-range requests are not supported here.
function contentRange(rangeHeader, size) {
  const m = /^bytes=(\d*)-(\d*)$/.exec(rangeHeader);
  if (!m) return null;
  let start, end;
  if (m[1] === "") {
    start = Math.max(size - Number(m[2]), 0);
    end = size - 1;
  } else {
    start = Number(m[1]);
    end = m[2] === "" ? size - 1 : Number(m[2]);
  }
  return `bytes ${start}-${end}/${size}`;
}

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

    // Data files (>25 MiB, not in assets) are served from R2 with
    // HTTP Range passthrough: the client's Range header is forwarded
    // to env.DATA.get(key, { range }) and R2's 206 + Content-Range
    // are passed through (FR-007, research R-003).
    const key = path.slice("/map/".length);
    if (DATA_KEYS.has(key)) {
      const range = request.headers.get("Range");
      const object = await env.DATA.get(key, range ? { range: request.headers } : undefined);
      if (object === null) {
        return new Response("Not Found", { status: 404 });
      }
      const headers = new Headers();
      object.writeHttpMetadata(headers);
      headers.set("etag", object.httpEtag);
      headers.set("Accept-Ranges", "bytes");
      if (range) {
        const cr = contentRange(range, object.size);
        if (cr) headers.set("Content-Range", cr);
        return new Response(object.body, { status: 206, headers });
      }
      headers.set("Content-Length", object.size);
      return new Response(object.body, { status: 200, headers });
    }

    // Everything else under /map/ is a static asset from dist/.
    // The ASSETS binding resolves paths against the assets root, so
    // the /map prefix is stripped: /map/style.json -> /style.json
    // (the browser-visible URL stays /map/style.json).
    const assetUrl = new URL(request.url);
    assetUrl.pathname = path.slice("/map".length) || "/";
    const assetResponse = await env.ASSETS.fetch(new Request(assetUrl, request));

    // Feature 014 (contracts/cache-headers.md): content-hashed assets are
    // immutable, so serve them with a long-lived browser cache. Everything
    // else (index.html and un-hashed files) keeps the ASSETS default
    // `public, max-age=0, must-revalidate` + ETag.
    const hashed = /-[0-9a-f]{12}\.(js|css|json|geojson|svg)$/.test(path);
    if (hashed) {
      const headers = new Headers(assetResponse.headers);
      headers.set("Cache-Control", "public, max-age=31536000, immutable");
      return new Response(assetResponse.body, {
        status: assetResponse.status,
        statusText: assetResponse.statusText,
        headers,
      });
    }
    return assetResponse;
  },
};
