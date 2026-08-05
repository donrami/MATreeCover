# Data Model: First-Visit Story Modal

**Feature**: 007-first-visit-story | **Branch**: `007-first-visit-story`

This feature introduces two entities. No pipeline data is touched;
the model describes the on-device dismissal state and the modal UI
component. Source of truth: `contracts/dismissal-state.md` (state)
and `contracts/story-modal.md` (UI).

## Entity: FirstVisitDismissalState

On-device record that a visitor already dismissed the story modal.
Determines whether the modal shows on page load (FR-005, FR-013).

| Field | Type | Value | Notes |
|-------|------|-------|-------|
| storage | `localStorage` | — | Per-origin, survives reloads, tab close, browser restart |
| key | string | `matreecover.story-dismissed` | Namespaced to this project on the shared origin |
| value | string | `"1"` | Presence of the key means "dismissed"; value is a constant marker, not data |

**Validation rules** (from spec):
- Absent key (or `localStorage` entirely unavailable) ⇒ first visit ⇒ modal shows (FR-001, FR-013).
- Present key ⇒ modal never shows (FR-005, SC-002).
- Key is written **only** on explicit dismissal (close button click or Escape) — never on page load, never on show (no measurement/analytics, FR-011).
- Any `localStorage` access (read or write) is wrapped in `try/catch`; on failure a session-only in-memory boolean flag substitutes (FR-013: modal appears and dismisses for the current visit, reappears next visit).
- No timestamp, counter, or version stored (spec: no tracking, no analytics, no scheduled re-show).

**State transitions**:

```text
storage unavailable ──► in-memory session flag (fallback)
      │                        │
      ▼                        ▼
absent ──page load──► modal shows ──dismiss──► flag set ──► modal hidden for visit
      ▲                                                      │
      └────────────── storage cleared (user/devtools) ◄──────┘
```

## Entity: StoryModal (UI component)

The dialog overlay shown on first visit. Static markup shipped in
`index.html`; layout in `style.css`; behavior in `main.js`.

| Field | Type | Value | Notes |
|-------|------|-------|-------|
| container | `div.story-backdrop` | fixed overlay, `inset: 0`, `z-index: 30` | Covers the map while open; pointer events land on it, not the map |
| dialog | `div.story-modal` | `role="dialog"`, `aria-modal="true"`, `aria-labelledby="story-title"`, `tabindex="-1"` | Announced dialog name (FR-009); focusable |
| close control | `button#story-close` | `type="button"`, `aria-label="Schließen"` | Visible close button (FR-004) |
| title | `h2#story-title` | German heading | Labels the dialog |
| content | static elements | story paragraphs + 2 links | See `contracts/story-content.md` |
| links | `a` × 2 | `target="_blank" rel="noopener"` | Never navigate the map tab away (FR-006) |

**Component states**:

| State | Entered when | Exit on |
|-------|--------------|---------|
| `hidden` | page load, dismissal state present (or in-memory flag set) | — (never shown) |
| `open` | page load, no dismissal state | close button click, Escape key |
| `dismissed` | close action | persist (storage or in-memory), focus restore, overlay removal |

**Transitions — open** (FR-001, FR-008, FR-009):
1. Remove `hidden` attribute from the backdrop.
2. Move focus to the dialog element (announces dialog name to screen readers).
3. Install keydown listeners: Escape closes; Tab/Shift+Tab cycle focus within the dialog (focus trap).

**Transitions — dismissed** (FR-004, FR-005, FR-007, FR-008):
1. Remove the backdrop from the DOM (map immediately interactive, no reflow).
2. Persist dismissal: write `localStorage` key, or set in-memory flag when storage is unavailable (FR-013).
3. Restore focus to the previously focused element (the document body on page-load open).
4. Tear down listeners.

**Invariants**:
- The modal never overlaps `#legend`, `#controls`, the MapLibre
  NavigationControl, `#attribution`, or the MapLibre attribution at
  any width ≥320 px (FR-010; `contracts/story-modal.md` safe-zone
  geometry; verified by the extended overlap matrix).
- Modal markup and wiring exist only in `index.html`/`main.js`; the
  attribution page never shows the modal (FR-012).
- No network request is added at any point in the lifecycle
  (FR-011): content is static, state stays on-device.
- Map data, building values, tree layer, legend, popup, Bäume
  toggle, Helligkeit slider, and zoom controls are untouched
  (FR-014).
