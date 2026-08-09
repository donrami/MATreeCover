"""Ko-fi donation button acceptance tests (feature 017).

Raw-HTML assertions against ``dist/`` after ``make publish``, plus source
assertions on ``src/site/style.css`` and ``workers/map/index.js``. Enforces
the machine checks from ``specs/017-ko-fi-button/contracts/ko-fi-button.md``
(markup shape FR-001/002/008, German text alternative FR-006, mobile
touch-target group membership FR-004) and the CSP image-host extension from
``contracts/csp-image-host.md`` (FR-009: one origin in ``img-src``, all other
directives byte-identical, Worker header byte-identical to the meta tag).

Quickstart filters: ``-k csp``, ``-k markup``, ``-k style``.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DIST = REPO_ROOT / "dist"
SRC_CSS = REPO_ROOT / "src/site/style.css"
WORKER_JS = REPO_ROOT / "workers/map/index.js"

KO_FI_HREF = "https://ko-fi.com/M4Q624RYOV"
KO_FI_IMG_SRC = "https://storage.ko-fi.com/cdn/kofi3.png?v=6"
KO_FI_IMG_HOST = "https://storage.ko-fi.com"
# Locked directives (feature 015) that must stay byte-identical to their
# pre-feature values — the CSP change is img-src only (FR-009).
LOCKED_DEFAULT_SRC = "default-src 'self'"
LOCKED_STYLE_SRC = "style-src 'self' 'unsafe-inline'"
LOCKED_SCRIPT_SRC = "script-src 'self'"
LOCKED_CONNECT_SRC = "connect-src 'self' https://sgx.geodatenzentrum.de"
LOCKED_WORKER_SRC = "worker-src 'self' blob:"
LOCKED_FONT_SRC = "font-src 'self' https://demotiles.maplibre.org"
# German donation/support words the alt text must contain (FR-006).
DONATION_WORDS = ("spenden", "unterstütz", "unterstutz", "fördern", "förder")


def _raw(name: str) -> str:
    path = DIST / name
    assert path.is_file(), f"dist/{name} missing — run `make publish` first"
    return path.read_text(encoding="utf-8")


def _csp_meta() -> str:
    metas = re.findall(
        r'<meta http-equiv="Content-Security-Policy" content="([^"]+)"',
        _raw("index.html"),
    )
    assert len(metas) == 1, "exactly one CSP meta tag expected (locked policy)"
    return metas[0]


@pytest.fixture(scope="module")
def ko_fi_anchor() -> str:
    anchors = re.findall(r'<a class="ko-fi"[^>]*>', _raw("index.html"))
    assert len(anchors) == 1, "exactly one .ko-fi anchor expected"
    return anchors[0]


@pytest.fixture(scope="module")
def ko_fi_img() -> str:
    imgs = re.findall(r'<img[^>]*>', _raw("index.html"))
    ko = [i for i in imgs if f'src="{KO_FI_IMG_SRC}"' in i]
    assert len(ko) == 1, "exactly one Ko-fi CDN image expected"
    return ko[0]


# ---------------------------------------------------------------------------
# Markup (FR-001/002/008, quickstart Q1/Q2)
# ---------------------------------------------------------------------------


def test_ko_fi_anchor_exact_attributes(ko_fi_anchor) -> None:
    assert f'href="{KO_FI_HREF}"' in ko_fi_anchor, "exact Ko-fi href required"
    assert 'target="_blank"' in ko_fi_anchor, "opens in a new tab (FR-002)"
    assert 'rel="noopener"' in ko_fi_anchor, "external-link safety (noopener)"


def test_ko_fi_anchor_no_script_tracking(ko_fi_anchor) -> None:
    # FR-008: plain external link — no inline handlers, no widget script.
    assert "onerror" not in ko_fi_anchor
    assert "onclick" not in ko_fi_anchor
    assert "ko-fi.com/widgets" not in _raw("index.html"), "Ko-fi widget script forbidden (FR-008)"


def test_ko_fi_img_exact_attributes(ko_fi_img) -> None:
    assert f'src="{KO_FI_IMG_SRC}"' in ko_fi_img, "official CDN URL with ?v=6 verbatim"
    assert 'width="143"' in ko_fi_img, "width reserves layout space (no CLS, R-8)"
    assert 'height="36"' in ko_fi_img, "height reserves layout space (no CLS, R-8)"


def test_ko_fi_img_german_donation_alt(ko_fi_img) -> None:
    alt = re.search(r'alt="([^"]*)"', ko_fi_img)
    assert alt, "img alt attribute required (FR-006)"
    alt_text = alt.group(1)
    assert "ko-fi" in alt_text.lower(), "alt must mention Ko-fi"
    assert any(word in alt_text.lower() for word in DONATION_WORDS), (
        "alt must identify a donation/support link in German (FR-006)"
    )


def test_ko_fi_dom_order_in_surface_header() -> None:
    # R-4: direct child of .surface-header, DOM order title → tools →
    # ko-fi → toggle so the chevron stays rightmost (feature 012).
    header = re.search(r'<header class="surface-header">(.*?)</header>', _raw("index.html"), re.DOTALL)
    assert header, "surface header required"
    h = header.group(1)
    tools = h.find('class="surface-tools"')
    ko = h.find('class="ko-fi"')
    toggle = h.find('id="surface-toggle"')
    assert -1 < tools < ko < toggle, "DOM order must be title → tools → ko-fi → toggle"


# ---------------------------------------------------------------------------
# CSP lockstep (FR-009, quickstart Q6)
# ---------------------------------------------------------------------------


def test_csp_meta_img_src_allows_ko_fi_host() -> None:
    img_src = re.search(r"img-src\s+([^;]+);", _csp_meta())
    assert img_src, "img-src directive required"
    hosts = img_src.group(1).split()
    assert KO_FI_IMG_HOST in hosts, "img-src must allow https://storage.ko-fi.com"
    # pre-feature allowlist stays intact (one origin added, none removed)
    assert "'self'" in hosts
    assert "data:" in hosts
    assert "https://sgx.geodatenzentrum.de" in hosts
    assert len(hosts) == 4, f"img-src must gain exactly one origin: {hosts}"


def test_csp_locked_directives_byte_identical() -> None:
    csp = _csp_meta()
    assert LOCKED_DEFAULT_SRC in csp
    assert LOCKED_STYLE_SRC in csp
    assert LOCKED_SCRIPT_SRC in csp
    assert LOCKED_CONNECT_SRC in csp
    assert LOCKED_WORKER_SRC in csp
    assert LOCKED_FONT_SRC in csp
    # the Ko-fi host appears in exactly one directive (img-src)
    assert csp.count(KO_FI_IMG_HOST) == 1, "Ko-fi host allowed in img-src only (FR-009)"


def test_csp_no_unsafe_inline_scripts() -> None:
    # the widget script (ko-fi.com/widgets/widget_2.js) must NOT appear and
    # script-src stays 'self' without 'unsafe-inline'/'unsafe-eval' (FR-008).
    csp = _csp_meta()
    assert "'unsafe-inline'" not in re.search(r"script-src\s+([^;]+)", csp).group(1)
    assert "'unsafe-eval'" not in csp


def test_worker_header_csp_byte_identical_to_meta() -> None:
    worker_src = WORKER_JS.read_text(encoding="utf-8")
    match = re.search(r'"Content-Security-Policy":\s*"([^"]+)"', worker_src)
    assert match, "SECURITY_HEADERS CSP string required"
    assert match.group(1) == _csp_meta(), (
        "Worker header CSP must be byte-identical to the meta tag (feature 015)"
    )


# ---------------------------------------------------------------------------
# Style (FR-003/004/006, quickstart Q4/Q6/Q7)
# ---------------------------------------------------------------------------


def test_ko_fi_base_styles_present() -> None:
    css = SRC_CSS.read_text(encoding="utf-8")
    assert re.search(r"\.ko-fi\s*\{", css), ".ko-fi base rule required"
    assert re.search(
        r"\.ko-fi\s+img\s*\{[^}]*width:\s*143px[^}]*height:\s*36px", css, re.DOTALL
    ), "brand image sized 143x36 (CLS reserve, R-8)"


def test_ko_fi_in_mobile_touch_target_group() -> None:
    # FR-004: .ko-fi joins the feature-012 44x44 rule group in the mobile
    # block; the 36px visual is preserved via padding (R-3). This assertion
    # lands with the US2 mobile rules.
    css = SRC_CSS.read_text(encoding="utf-8")
    mobile = re.search(r"@media \(max-width: 767\.98px\)\s*\{(.*)", css, re.DOTALL)
    assert mobile, "mobile media block required"
    block = mobile.group(1)
    assert re.search(r"\.ko-fi[^}]*min-width:\s*44px", block, re.DOTALL), (
        ".ko-fi must have min-width 44px in the mobile block (FR-004)"
    )
    assert re.search(r"\.ko-fi[^}]*min-height:\s*44px", block, re.DOTALL), (
        ".ko-fi must have min-height 44px in the mobile block (FR-004)"
    )


def test_ko_fi_focus_visible_rule() -> None:
    # FR-006: visible focus indicator matching the existing control pattern
    # (.surface-toggle uses outline: 2px solid var(--subtle)). Lands with US3.
    css = SRC_CSS.read_text(encoding="utf-8")
    assert re.search(r"\.ko-fi(?::hover|:focus-visible)[^{]*\{[^}]*outline:", css, re.DOTALL), (
        ".ko-fi must show a visible focus indicator (FR-006)"
    )
