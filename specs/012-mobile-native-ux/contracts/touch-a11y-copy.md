# Contract: Touch Targets, Accessibility, Copy

Feature 012, FR-003, FR-011, FR-014, SC-009, SC-010.

## Touch targets (FR-003)

On mobile viewports (`< 768px`) every interactive control MUST have a touch target of at least
**44x44 px** and at least **8 px** clear spacing between adjacent targets. Controls in scope:

- Bäume toggle (`#baeume`).
- Helligkeit slider (`#brightness-slider`, thumb and track are large; ensure the input is
  styled to a >= 44 px hit area).
- Surface expand/collapse toggle button.
- MapLibre NavigationControl zoom buttons. MapLibre's default buttons are 29 px, so on mobile
  they MUST be enlarged to 44x44 px via a CSS override (R-3).
- Popup close buttons (MapLibre default `closeButton`; verify >= 44x44 px on mobile).

Implementation: set `min-width`/`min-height: 44px` (or `width`/`height`) on these controls
inside the mobile media query, and use `gap >= 8px` for spacing. The desktop layout may keep
smaller targets since FR-003 scopes touch targets to mobile.

## Accessibility (FR-014)

- **Keyboard**: every control is a native focusable element (`<button>`, `<input>`). No
  click-only interactive element is added. The surface toggle and all tools are reachable and
  operable with the keyboard alone (SC-010).
- **Focus**: every control has a visible `:focus-visible` outline. Existing focus styles
  (e.g. `.legal-link:focus-visible`) are the pattern to extend to the new controls.
- **Contrast**: all new surfaces and text meet WCAG AA on the dark theme. Use the existing
  `--text` (#ffffff) and `--subtle` (#888888) on `--panel-bg` (#0e0e0e); verify any new text
  against AA.
- **ARIA**:
  - Surface toggle: `aria-expanded` (state) + `aria-controls="surface-body"`.
  - Bäume toggle already uses `aria-pressed` (unchanged).
  - Helligkeit slider has a visible label and an accessible name.
  - The surface header/body roles and labels describe their content to screen readers
    (SC-010).
- The first-visit story modal and popups keep their existing accessibility behaviour (FR-010).

## Copy (FR-011, SC-009)

- All new copy is German.
- No em-dashes, no en-dashes; hyphens appear only inside compound words (feature 007
  convention).
- New strings are limited to the expand/collapse affordance labels (e.g. `Legende
  einblenden` / `Legende ausblenden`) and any new surface heading or helper text. Reuse
  existing German legend and city-overview copy where possible.
- The existing `UNAVAILABLE` en-dash constant (`\u2013`, FR-009) is unchanged.
- SC-009: a mechanical check asserts zero em-dashes and zero en-dashes in the new copy strings
  (extend the existing copy check that currently lives in the smoke checklist).
