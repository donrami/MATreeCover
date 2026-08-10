"""SEO metadata acceptance tests (feature 016).

Raw-HTML assertions against ``dist/`` after ``make publish``. Covers the
on-page metadata contract (FR-002/003/004), the story-in-modal contract
(FR-006, final Clarifications 2026-08-09: full story in the first-visit
modal, single DOM copy, nothing under the map), the link-preview
contract (FR-005), the structured-data contract (FR-007), and the
crawler-files contract (FR-008/009). Every machine-checkable rule from
the contracts is enforced here, never by documentation alone.

Quickstart filters: ``-k "metadata or story"``, ``-k og``,
``-k robots``, ``-k jsonld``.
"""

from __future__ import annotations

import json
import re
import struct
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DIST = REPO_ROOT / "dist"

CANONICALS = {
    "index.html": "https://abu-hamad.de/map/",
    "impressum.html": "https://abu-hamad.de/map/impressum",
    "attribution.html": "https://abu-hamad.de/map/attribution",
    "datenschutz.html": "https://abu-hamad.de/map/datenschutz",  # feature 018
}
KEPT_TITLES = {
    "impressum.html": "Impressum – Mannheim Baumfläche",
    "attribution.html": "Datenquellen – Mannheim Baumfläche",
    "datenschutz.html": "Datenschutzerklärung – Mannheim Baumfläche",  # feature 018
}
# ISO date the Datenschutzerklärung was last edited; mirrors the page's
# "Stand" footer and the <lastmod> in src/site/sitemap.xml (data-model E4).
DATENSCHUTZ_LASTMOD = "2026-08-10"
SITE_NAME = "Baumfläche Mannheim"
OG_IMAGE_URL = "https://abu-hamad.de/map/og-image.png"
# Distinctive phrase of the story copy; must occur exactly once in the
# document (single DOM copy, Clarifications 2026-08-09).
STORY_PHRASE = "Im Juli 2026 berichtete der SPIEGEL"
WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+")


class PageParser(HTMLParser):
    """Parse dist HTML into the assertions the contracts need.

    Tracks hidden containers (``hidden``, ``.sr-only``, ``aria-hidden``,
    ``display:none``) and splits collected text into visible and hidden
    parts. Collects head metadata, OG/Twitter tags, canonical, CSP, and
    JSON-LD data blocks.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.titles: list[str] = []
        self.descriptions: list[str] = []
        self.canonicals: list[str] = []
        self.properties: list[tuple[str, str]] = []
        self.twitter: list[tuple[str, str]] = []
        self.csp: list[str] = []
        self.jsonld: list[str] = []
        self.visible_parts: list[str] = []
        self.hidden_parts: list[str] = []
        self.modal_parts: list[str] = []
        self._title_buf: list[str] | None = None
        self._jsonld_buf: list[str] | None = None
        self._in_modal = False

    def _is_hidden(self, attrs: list[tuple[str, str | None]]) -> bool:
        a = dict(attrs)
        if "hidden" in a:
            return True
        if "sr-only" in a.get("class", "").split():
            return True
        if a.get("aria-hidden") == "true":
            return True
        style = (a.get("style") or "").replace(" ", "")
        return "display:none" in style

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        hidden = self._is_hidden(attrs)
        self.stack.append((tag, hidden))
        if tag == "meta":
            content = a.get("content", "") or ""
            if a.get("name") == "description":
                self.descriptions.append(content)
            name = a.get("name") or ""
            if name.startswith("twitter:"):
                self.twitter.append((name, content))
            if a.get("property"):
                self.properties.append((a["property"], content))
            if a.get("http-equiv") == "Content-Security-Policy":
                self.csp.append(content)
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a.get("href", "") or "")
        elif tag == "title":
            self._title_buf = []
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._jsonld_buf = []
        elif tag == "div" and a.get("id") == "story-dialog":
            self._in_modal = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self._title_buf is not None:
            self.titles.append("".join(self._title_buf).strip())
            self._title_buf = None
        if tag == "script" and self._jsonld_buf is not None:
            self.jsonld.append("".join(self._jsonld_buf).strip())
            self._jsonld_buf = None
        if tag == "div" and self._in_modal:
            self._in_modal = False
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data: str) -> None:
        if self._title_buf is not None:
            self._title_buf.append(data)
            return
        if self._jsonld_buf is not None:
            self._jsonld_buf.append(data)
            return
        if not self.stack or self.stack[-1][0] in ("script", "style"):
            return
        if not data.strip():
            return
        if self._in_modal:
            self.modal_parts.append(data.strip())
        if any(h for _, h in self.stack):
            self.hidden_parts.append(data.strip())
        else:
            self.visible_parts.append(data.strip())


def _parse(name: str) -> PageParser:
    path = DIST / name
    if not path.exists():
        pytest.skip(f"dist/{name} missing; run make publish first")
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def _raw(name: str) -> str:
    path = DIST / name
    if not path.exists():
        pytest.skip(f"dist/{name} missing; run make publish first")
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def map_page() -> PageParser:
    return _parse("index.html")


@pytest.fixture(scope="module")
def impressum_page() -> PageParser:
    return _parse("impressum.html")


@pytest.fixture(scope="module")
def datenschutz_page() -> PageParser:
    return _parse("datenschutz.html")


@pytest.fixture(scope="module")
def attribution_page() -> PageParser:
    return _parse("attribution.html")


# ---------------------------------------------------------------------------
# On-page metadata (FR-002/003/004, quickstart Q1)
# ---------------------------------------------------------------------------


def test_metadata_single_title_per_page(
    map_page, impressum_page, attribution_page, datenschutz_page
) -> None:
    for parser, name in (
        (map_page, "index.html"),
        (impressum_page, "impressum.html"),
        (attribution_page, "attribution.html"),
        (datenschutz_page, "datenschutz.html"),
    ):
        assert len(parser.titles) == 1, f"{name}: expected exactly one <title>"


def test_metadata_map_title_descriptive(map_page) -> None:
    title = map_page.titles[0]
    assert 30 <= len(title) <= 60, f"map title {len(title)} chars, need 30-60"
    assert title != "Baumfläche", "bare title forbidden (FR-002)"
    assert title == "Baumfläche Mannheim: Baumanteil je Gebäude im 60-m-Umkreis"


def test_metadata_legal_page_titles_kept(impressum_page, attribution_page, datenschutz_page) -> None:
    assert impressum_page.titles[0] == KEPT_TITLES["impressum.html"]
    assert attribution_page.titles[0] == KEPT_TITLES["attribution.html"]
    assert datenschutz_page.titles[0] == KEPT_TITLES["datenschutz.html"]


def test_metadata_single_description_per_page(
    map_page, impressum_page, attribution_page, datenschutz_page
) -> None:
    for parser, name in (
        (map_page, "index.html"),
        (impressum_page, "impressum.html"),
        (attribution_page, "attribution.html"),
        (datenschutz_page, "datenschutz.html"),
    ):
        assert len(parser.descriptions) == 1, f"{name}: expected exactly one meta description"


def test_metadata_descriptions_unique_and_in_range(
    map_page, impressum_page, attribution_page, datenschutz_page
) -> None:
    descriptions = [
        p.descriptions[0] for p in (map_page, impressum_page, attribution_page, datenschutz_page)
    ]
    for desc in descriptions:
        assert 100 <= len(desc) <= 160, f"description {len(desc)} chars, need 100-160"
    assert len(set(descriptions)) == 4, "descriptions must be pairwise distinct (FR-003)"


def test_metadata_canonical_per_page(
    map_page, impressum_page, attribution_page, datenschutz_page
) -> None:
    for parser, name in (
        (map_page, "index.html"),
        (impressum_page, "impressum.html"),
        (attribution_page, "attribution.html"),
        (datenschutz_page, "datenschutz.html"),
    ):
        assert len(parser.canonicals) == 1, f"{name}: expected exactly one canonical tag"
        assert parser.canonicals[0] == CANONICALS[name], f"{name}: canonical mismatch"


# ---------------------------------------------------------------------------
# Link previews (FR-005, quickstart Q2)
# ---------------------------------------------------------------------------


def test_link_preview_og_tags(map_page) -> None:
    props: dict[str, str] = {}
    for key, value in map_page.properties:
        assert key not in props, f"duplicate og property {key}"
        props[key] = value
    expected = {
        "og:title": map_page.titles[0],
        "og:description": map_page.descriptions[0],
        "og:type": "website",
        "og:url": CANONICALS["index.html"],
        "og:site_name": SITE_NAME,
        "og:locale": "de_DE",
        "og:image": OG_IMAGE_URL,
        "og:image:width": "1200",
        "og:image:height": "630",
    }
    assert props == expected, f"OG properties mismatch: {props}"
    assert map_page.twitter == [("twitter:card", "summary_large_image")]


def test_link_preview_og_image_file() -> None:
    image_name = urlsplit(OG_IMAGE_URL).path.rsplit("/", 1)[-1]
    path = DIST / image_name
    assert path.exists(), f"og:image {image_name} not in dist/"
    assert path.stat().st_size < 1_000_000, "og:image must be under 1 MB"
    data = path.read_bytes()[:33]
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "og:image must be a PNG"
    width, height = struct.unpack(">II", data[16:24])
    assert (width, height) == (1200, 630), f"og:image {width}x{height}, need 1200x630"


# ---------------------------------------------------------------------------
# Story content in the first-visit modal (FR-006, quickstart Q4, final
# Clarifications 2026-08-09: full story restored in the modal, nothing
# under the map)
# ---------------------------------------------------------------------------


def test_no_visible_story_section(map_page) -> None:
    raw = _raw("index.html")
    assert '<section id="about"' not in raw, "no visible story section may exist under the map"


def test_story_lives_in_modal(map_page) -> None:
    assert map_page.modal_parts, "story content missing from the first-visit modal"
    modal = " ".join(map_page.modal_parts)
    assert "Genauigkeit" in modal, "accuracy disclaimer missing from the modal"
    assert "Details unter Datenquellen" in modal, "data-source link missing from the modal"
    assert "Quellcode auf GitHub" in modal, "source-repository link missing"


def test_story_single_dom_copy(map_page) -> None:
    raw = _raw("index.html")
    assert raw.count(STORY_PHRASE) == 1, "story copy must occur exactly once in the DOM"


# ---------------------------------------------------------------------------
# Structured data (FR-007, quickstart Q5)
# ---------------------------------------------------------------------------


def _jsonld_records(map_page) -> list[dict]:
    assert map_page.jsonld, "no application/ld+json block present"
    records: list[dict] = []
    for block in map_page.jsonld:
        data = json.loads(block)
        if isinstance(data, dict) and "@graph" in data:
            records.extend(data["@graph"])
        elif isinstance(data, dict):
            records.append(data)
        elif isinstance(data, list):
            records.extend(data)
    return records


def test_jsonld_website_and_organization(map_page) -> None:
    records = _jsonld_records(map_page)
    types = {r.get("@type") for r in records}
    assert "WebSite" in types, "WebSite record required"
    assert "Organization" in types, "Organization record required"
    website = next(r for r in records if r.get("@type") == "WebSite")
    org = next(r for r in records if r.get("@type") == "Organization")
    assert website.get("name"), "WebSite.name required"
    assert website.get("url"), "WebSite.url required"
    assert website.get("alternateName"), "WebSite.alternateName required"
    assert "SearchAction" not in json.dumps(website), "SearchAction forbidden (sitelinks search box removed)"
    assert org.get("name"), "Organization.name required"
    assert org.get("url"), "Organization.url required"


def test_jsonld_no_forbidden_types(map_page) -> None:
    records = _jsonld_records(map_page)
    types = {r.get("@type") for r in records}
    forbidden = {"FAQPage", "LocalBusiness", "Speakable"}
    assert not (types & forbidden), f"forbidden rich-result types present: {types & forbidden}"


def test_jsonld_csp_compatible(map_page) -> None:
    assert len(map_page.csp) == 1, "exactly one CSP meta tag expected (locked policy)"
    csp = map_page.csp[0]
    directive = re.search(r"script-src\s+([^;]+)", csp)
    assert directive, "script-src directive required"
    assert "'self'" in directive.group(1), "script-src 'self' must be present"
    assert "'unsafe-inline'" not in directive.group(1), "scripts must not be inline-allowed"


# ---------------------------------------------------------------------------
# Crawler files (FR-008/009, quickstart Q3)
# ---------------------------------------------------------------------------


def test_robots_txt_rules() -> None:
    text = _raw("robots.txt")
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    assert "User-agent: *" in text, "robots.txt must start with User-agent: *"
    disallows = [line for line in lines if line.startswith("Disallow:")]
    assert disallows == [
        "Disallow: /buildings.pmtiles",
        "Disallow: /trees.pmtiles",
        "Disallow: /buildings.geojson",
    ], f"exactly the three data-file disallows expected: {disallows}"
    for line in disallows:
        assert ".html" not in line and "/map/" not in line, "no HTML path may be disallowed"


def test_sitemap_xml_lists_exactly_four_canonical_urls() -> None:
    """Feature 018: sitemap grows from 3 to 4 URLs with the new
    Datenschutzerklärung. Its <lastmod> is the page's "Stand" date; the
    other three pages keep no lastmod (staleness-edge-case contract)."""
    root = ET.fromstring(_raw("sitemap.xml"))
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    url_els = list(root.findall("s:url", ns))
    locs = [el.findtext("s:loc", namespaces=ns) for el in url_els]
    assert locs == [
        CANONICALS["index.html"],
        CANONICALS["impressum.html"],
        CANONICALS["attribution.html"],
        CANONICALS["datenschutz.html"],
    ], f"sitemap must list exactly the four canonical URLs in order: {locs}"
    lastmods = [el.find("s:lastmod", ns) for el in url_els]
    assert lastmods[:3] == [None, None, None], "index/impressum/attribution must omit lastmod"
    assert lastmods[3] is not None, "datenschutz must carry a lastmod date"
    assert lastmods[3].text == DATENSCHUTZ_LASTMOD, (
        f"datenschutz lastmod must equal page Stand date {DATENSCHUTZ_LASTMOD}"
    )
    xml = _raw("sitemap.xml")
    assert "og-image" not in xml, "og-image must not appear in the sitemap"
    assert ".pmtiles" not in xml and ".geojson" not in xml, "no data files in the sitemap"
    assert not re.search(r"[0-9a-f]{12}\.", xml), "no hashed assets in the sitemap"
