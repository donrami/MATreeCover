# Contract: Dismissal State (localStorage)

**Feature**: First-Visit Story Modal |
**Branch**: `007-first-visit-story`
**Source of truth**: `src/site/main.js`.

## Purpose

Fix how "already dismissed" is recorded on-device so the modal
appears exactly once per browser (FR-005), and how the feature
degrades when storage is unavailable (FR-013).

## Storage contract

| Field | Value |
|---|---|
| Storage | `localStorage` (per-origin, survives reloads and browser restarts) |
| Key | `matreecover.story-dismissed` |
| Value | `"1"` (constant marker; presence of the key means "dismissed") |

**Read** — once, at page load, in `main.js` `init()`: key present ⇒
modal hidden; key absent or storage unavailable ⇒ modal shows.

**Write** — only on explicit dismissal (close button click or
Escape): `localStorage.setItem("matreecover.story-dismissed", "1")`.

**Never** written on page load or on show (no measurement, no
analytics — FR-011; spec: no tracking, no modal-view counting).

## Storage-unavailable fallback (FR-013)

Every `localStorage` access (reading the key, writing the key) is
wrapped in `try/catch` — access itself can throw (blocked storage in
private or sandboxed contexts). On failure:

- A session-only in-memory boolean flag substitutes for the key.
- The modal still appears and remains dismissible for the current
  visit.
- On the next visit (new page load), the in-memory flag is gone and
  the modal appears again — acceptable and required by FR-013.

## Semantics / validation rules

- Absent key ⇒ first visit ⇒ modal shows (FR-001).
- Present key ⇒ modal never shows again in this browser while the
  key exists (FR-005, SC-002).
- User or devtools clearing site data removes the key ⇒ first-visit
  behavior restored (spec US2 scenario 3).
- No timestamp, counter, or version is stored (spec: no analytics,
  no scheduled re-show).

## Invariants

- All state stays on-device; nothing is sent anywhere (FR-011).
- The key is namespaced (`matreecover.`) so it cannot collide with
  other scripts on the origin (the site has no other storage keys
  today).
- The fallback never throws: storage failure must never break page
  load or the map (FR-013).

## Verification

- Dismiss, reload, revisit in a fresh session: modal appears zero
  further times (quickstart Scenario 3; `smoke_us5.md`).
- Devtools "Block storage" (or private mode): modal appears and
  dismisses for the visit; reappears on reload (quickstart
  Scenario 4).
