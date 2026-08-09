# Manueller Smoke-Check: Ko-fi-Spendenbutton (Feature 017)

Browser-Checkliste für die US1-US4-Abnahme. Führe die Punkte in einem echten
Browser (Desktop und Mobile) gegen die veröffentlichte Seite
(`https://abu-hamad.de/map/` oder `dist/` über HTTP) aus. Alle Punkte müssen
abhaken sein. Ein offener Punkt blockiert den Story-Abschluss (OR-004).

## US1: Desktop, Button sichtbar und bedienbar (FR-001/002)

- [ ] Desktop-Viewport (≥ 768 px, prüfe 768 / 1280 / 1920): Der Ko-fi-Button
      ist ohne Scrollen im Panel-Header sichtbar.
- [ ] Zustand erweitert (Standard) und eingeklappt (Chevron). Der Button
      bleibt in beiden Zuständen im Header.
- [ ] Klick öffnet `https://ko-fi.com/M4Q624RYOV` in einem neuen Tab. Die
      Karte bleibt im ursprünglichen Tab offen und bedienbar.
- [ ] Der Chevron ist weiterhin das rechteste Header-Element (Feature 012).

## US2: Mobile, Touch-Ziel und Einpassung (FR-004/007)

- [ ] Mobile-Viewport (375 × 812), Sheet standardmäßig eingeklappt: Button
      im Header sichtbar; Map ≥ 80 % der Viewport-Höhe.
- [ ] `getBoundingClientRect()` des `.ko-fi`-Links ≥ 44 × 44 px
      (Quickstart Q4); das Bild bleibt visuell 36 px hoch.
- [ ] ≥ 8 px Abstand zu Bäume-Toggle und Surface-Toggle (bestehendes
      `gap: 8px`; der visuelle Abstand darf nur größer sein).
- [ ] 320 px Breite: Header höchstens zwei Zeilen, keine horizontale
      Überlauf, eingeklappte Leiste ≤ 20 % der Viewport-Höhe (≤ 113 px bei
      568 px Höhe; sonst das 32-34-px-Bild-Fallback prüfen).
- [ ] Kein Überlappen und keine Interzeption: Overlap-Matrix leer
      (Quickstart Q5) für Bäume-Toggle, Helligkeitsregler, Surface-Toggle,
      Zoom, Attribution, Impressum, Legende, Ko-fi.
- [ ] Safe-Area: Auf gekerbten Geräten wird der Button nie abgeschnitten
      (`env(safe-area-inset-bottom)` des Headers).
- [ ] Resize über die 768-px-Schwelle in beide Richtungen: sauberer
      Übergang ohne gebrochene Überlappungen.

## US3: Rendering und Zugänglichkeit (FR-003/006)

- [ ] Bild rendert (kein Broken-Image/Blank). Die Konsole zeigt null
      CSP-Verletzungen (die erweiterte `img-src` erlaubt den Ko-fi-CDN).
- [ ] Tab vom Seitenanfang: Der Button erreicht Fokus mit sichtbarem
      Fokus-Indikator; Enter öffnet Ko-fi im neuen Tab.
- [ ] Barrierefreier Name (Accessibility-Panel): identifiziert den Link als
      Spenden-/Unterstützungslink auf Deutsch
      („Baumfläche auf Ko-fi unterstützen").

## Edge Cases (Spec)

- [ ] CSP-blockiertes Bild: Die `img-src` enthält
      `https://storage.ko-fi.com`. Die Policy erlaubt weder Skripte noch
      Verbindungen zu Ko-fi (`script-src 'self'`, `connect-src` unverändert;
      der Worker-Header ist byte-identisch zum Meta-Tag).
- [ ] 36-px-Bild vs. 44-px-Touch-Ziel: Die Hit-Area entsteht durch Padding,
      nicht durch Bildskalierung (R-3).
- [ ] 320-px-Header-Packing: Zeile 1 `[Titel, Ko-fi, Chevron]`, Zeile 2
      `[Tools]` (R-4).
- [ ] External-Link-Sicherheit: `rel="noopener"`; die Ko-fi-Seite kann die
      Karte nicht steuern.
- [ ] Ko-fi nicht erreichbar (CDN oder Seite down): Der Alt-Text rendert,
      der Link funktioniert weiterhin, die Seite bleibt voll nutzbar
      (kein JS-Fallback nötig, R-9).
- [ ] Sprachkonsistenz: Der Alt-Text ist deutsch; das Markenlabel im Bild
      bleibt wie geliefert (R-6).
