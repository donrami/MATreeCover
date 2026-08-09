# Manueller Smoke-Check: Ko-fi-Spendenbutton (Feature 017)

Browser-Checkliste für die US1-US4-Abnahme. Führe die Punkte in einem echten
Browser (Desktop und Mobile) gegen die veröffentlichte Seite
(`https://abu-hamad.de/map/` oder `dist/` über HTTP) aus. Alle Punkte müssen
abgehakt sein. Ein offener Punkt blockiert den Story-Abschluss (OR-004).

Hinweis: Der Button liegt im Panel-/Sheet-Footer und ist nur bei erweiterter
Oberfläche sichtbar (FR-001, Klärung 2026-08-09: Header war zu präsent).

## US1: Desktop, Button sichtbar und bedienbar (FR-001/002)

- [ ] Desktop-Viewport (≥ 768 px, prüfe 768 / 1280 / 1920): Der Ko-fi-Button
      ist ohne Scrollen im Panel-Footer sichtbar — zentriert, am unteren Rand
      des erweiterten Panels (Standardzustand).
- [ ] Die abgerundeten unteren Paneelecken bleiben beim Erweitern erhalten
      (der Footer respektiert die 8-px-Radius-Kontur).
- [ ] Chevron eingeklappt: Der Button verschwindet (Footer ist Teil des
      einklappbaren Bodys); Chevron wieder erweitert: Der Button erscheint
      erneut. Kein schwebender Footer über der Karte im eingeklappten Zustand.
- [ ] Klick öffnet `https://ko-fi.com/M4Q624RYOV` in einem neuen Tab. Die
      Karte bleibt im ursprünglichen Tab offen und bedienbar.
- [ ] Header-Zeile ist wieder Titel → Tools → Chevron (Chevron rechtestes
      Header-Element, Feature 012; keine Spenden-Chrome im Header).

## US2: Mobile, Touch-Ziel und Einpassung (FR-004/007)

- [ ] Mobile-Viewport (375 × 812), Sheet standardmäßig eingeklappt: KEIN
      Spenden-Button sichtbar; Sheet-Chrome ≤ 20 % der Viewport-Höhe,
      Map ≥ 80 %.
- [ ] Sheet erweitert: Der Button ist im Sheet-Footer ohne Scrollen sichtbar
      (sticky), zentriert.
- [ ] `getBoundingClientRect()` des `.ko-fi`-Links ≥ 44 × 44 px
      (Quickstart Q4); das Bild bleibt visuell 36 px hoch (Padding-Hit-Area).
- [ ] ≥ 8 px Abstand zu angrenzendem interaktiven Inhalt (Legend-Link
      „Details unter Datenquellen“; `.surface-body-inner`-Abstand 12 px).
- [ ] 320 px Breite: Footer-Button ohne Überlauf (143-px-Bild passt in die
      292-px-Footerbreite); kein Bild-Shrink-Fallback nötig.
- [ ] Kein Überlappen und keine Interzeption: Overlap-Matrix leer
      (Quickstart Q5) für Bäume-Toggle, Helligkeitsregler, Surface-Toggle,
      Zoom, Attribution, Impressum, Legende, Ko-fi — erweiterter Zustand.
- [ ] Stadtpanel geöffnet (Stadtteil antippen): Der Inhalt scrollt unter dem
      sticky Footer durch; der Button bleibt sichtbar.
- [ ] Safe-Area: Auf gekerbten Geräten wird der Button nie abgeschnitten
      (Sheet-Regel `env(safe-area-inset-bottom)`).
- [ ] Resize über die 768-px-Schwelle in beide Richtungen: sauberer
      Übergang ohne gebrochene Überlappungen.

## US3: Rendering und Zugänglichkeit (FR-003/006)

- [ ] Bild rendert (kein Broken-Image/Blank). Die Konsole zeigt null
      CSP-Verletzungen (die erweiterte `img-src` erlaubt den Ko-fi-CDN).
- [ ] Tab vom Seitenanfang: Der Button erreicht Fokus mit sichtbarem
      Fokus-Indikator; Enter öffnet Ko-fi im neuen Tab.
- [ ] Barrierefreier Name (Accessibility-Panel): exakt „Unterstützen“
      (deutscher Kurz-Label, Eigentümer-Entscheid).

## Edge Cases (Spec)

- [ ] CSP-blockiertes Bild: Die `img-src` enthält
      `https://storage.ko-fi.com`. Die Policy erlaubt weder Skripte noch
      Verbindungen zu Ko-fi (`script-src 'self'`, `connect-src` unverändert;
      der Worker-Header ist byte-identisch zum Meta-Tag).
- [ ] Sichtbarkeit im eingeklappten Zustand (bewusster Kompromiss): Auf
      Mobile ist das Sheet standardmäßig eingeklappt und der Button bis zum
      Erweitern verborgen — gewollte Zurückhaltung, kein Regressionstest-
      Fehler.
- [ ] 36-px-Bild vs. 44-px-Touch-Ziel: Die Hit-Area entsteht durch Padding,
      nicht durch Bildskalierung (R-3).
- [ ] External-Link-Sicherheit: `rel="noopener"`; die Ko-fi-Seite kann die
      Karte nicht steuern.
- [ ] Ko-fi nicht erreichbar (CDN oder Seite down): Der Alt-Text rendert,
      der Link funktioniert weiterhin, die Seite bleibt voll nutzbar
      (kein JS-Fallback nötig, R-9).
- [ ] Sprachkonsistenz: Der barrierefreie Name ist deutsch („Unterstützen“);
      das sichtbare Markenbild behält bewusst Ko-fis englisches Standard-
      Branding (R-6).
