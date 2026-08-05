# Verifikation der Baumerkennung (Mannheim)

Datum: 2026-08-05 | Seed: 20260805 | Stichprobe: 100 Patches | Bezirksdaten: Stadt Mannheim, GDI-MA, dl-de/by-2-0

## Methode

- Stichprobendesign: 38 Stadtteile x Wertbaender 0-10 / 10-30 / 30-100, proportional nach Gebaeudeanzahl, Mindestzahl 1 pro Stadtteil, groesster Rest.
- Seed: 20260805; Auswahl deterministisch und reproduzierbar.
- Bewertungskriterien: contracts/verify-ratings.md (correct / over / under).
- Wiederholungspruefung: jedes 10. Patch erneut bewertet.

## Gesamtergebnis

- Bewertete Patches: 100; correct: 59 (59.0%), over: 39, under: 2.
- Korrektheitsanteil gesamt: 59.0% (Referenzwert fuer die Stadtteil-Flags).
- Nicht bewertet (no-imagery): 0.

## Ergebnisse nach Stadtteil

| Stadtteil | n | correct | over | under | Einschaetzung | Flag |
|-----------|----|---------|------|-------|---------------|------|
| Innenstadt | 4 | 2 | 2 | 0 | inconclusive |  |
| Jungbusch | 1 | 0 | 1 | 0 | inconclusive | FLAGGED |
| Neckarstadt-West | 4 | 2 | 2 | 0 | inconclusive |  |
| Neckarstadt-Ost | 2 | 2 | 0 | 0 | inconclusive |  |
| Herzogenried | 1 | 0 | 1 | 0 | inconclusive | FLAGGED |
| Neckarstadt-Nordost | 1 | 0 | 1 | 0 | inconclusive | FLAGGED |
| Wohlgelegen | 1 | 0 | 1 | 0 | inconclusive | FLAGGED |
| Oststadt | 2 | 2 | 0 | 0 | inconclusive |  |
| Schwetzingerstadt | 2 | 2 | 0 | 0 | inconclusive |  |
| Lindenhof | 2 | 1 | 0 | 1 | inconclusive |  |
| Sandhofen | 5 | 2 | 3 | 0 | overstated | FLAGGED |
| Sandhofen-Nord | 2 | 1 | 1 | 0 | inconclusive |  |
| Schönau-Nord | 2 | 2 | 0 | 0 | inconclusive |  |
| Schönau-Süd | 3 | 1 | 2 | 0 | inconclusive | FLAGGED |
| Waldhof-West | 1 | 1 | 0 | 0 | inconclusive |  |
| Gartenstadt | 6 | 4 | 2 | 0 | trustworthy |  |
| Luzenberg | 1 | 1 | 0 | 0 | inconclusive |  |
| Waldhof-Ost | 2 | 2 | 0 | 0 | inconclusive |  |
| Neuostheim | 1 | 1 | 0 | 0 | inconclusive |  |
| Neuhermsheim | 1 | 1 | 0 | 0 | inconclusive |  |
| Seckenheim | 7 | 6 | 1 | 0 | trustworthy |  |
| Hochstätt | 1 | 0 | 1 | 0 | inconclusive | FLAGGED |
| Friedrichsfeld | 4 | 2 | 2 | 0 | inconclusive |  |
| Käfertal-Mitte | 4 | 1 | 3 | 0 | inconclusive | FLAGGED |
| Speckweggebiet | 2 | 1 | 1 | 0 | inconclusive |  |
| Sonnenschein | 2 | 2 | 0 | 0 | inconclusive |  |
| Franklin | 1 | 0 | 1 | 0 | inconclusive | FLAGGED |
| Käfertal-Süd | 2 | 0 | 2 | 0 | inconclusive | FLAGGED |
| Vogelstang | 2 | 1 | 1 | 0 | inconclusive |  |
| Wallstadt | 4 | 2 | 1 | 1 | inconclusive |  |
| Feudenheim | 7 | 3 | 4 | 0 | overstated | FLAGGED |
| Neckarau | 6 | 5 | 1 | 0 | trustworthy |  |
| Niederfeld | 2 | 1 | 1 | 0 | inconclusive |  |
| Almenhof | 2 | 1 | 1 | 0 | inconclusive |  |
| Casterfeld | 3 | 3 | 0 | 0 | inconclusive |  |
| Pfingstberg | 1 | 0 | 1 | 0 | inconclusive | FLAGGED |
| Rheinau-Mitte | 2 | 1 | 1 | 0 | inconclusive |  |
| Rheinau-Süd | 4 | 3 | 1 | 0 | inconclusive |  |

## Vergleich mit dem Referenz-Transferproblem

Der Modellautor berichtet deutlich schlechtere Ergebnisse, als die
Erlangen-trainierten Gewichte auf Bamberg-DOP20 angewendet wurden
(geringerer Kontrast, andere Sonnenposition, wenige Trainingsdaten).
In Mannheim ist der Transfer nicht schlechter, aber die Stichprobe
zeigt ein klares Fehlerbild: 59 % der Patches korrekt, 39 % mit
dominierender Uebersegmentierung, 2 % mit Untererkennung. Die
Uebersegmentierung betrifft vor allem Dae cher, Rasen-/Wiesenflaechen,
Felder und Gleisbett und ist in den betroffenen Patches deutlich
sichtbar (zweite Pruefung von sechs Patches bestaetigt: 35-70 % der
detektierten Flaechen liegen auf Nicht-Baum-Oberflaechen). Ein
direkter Zahlenvergleich mit Bamberg ist nicht moeglich, da der Autor
keine Referenzwerte veroeffentlicht hat; die Einschaetzung ist
qualitativ.

## Einschraenkungen

- Degenerierte Patches: keine.
- Kleine Stichproben (n < 5): Innenstadt, Jungbusch, Neckarstadt-West, Neckarstadt-Ost, Herzogenried, Neckarstadt-Nordost, Wohlgelegen, Oststadt, Schwetzingerstadt, Lindenhof, Sandhofen-Nord, Schönau-Nord, Schönau-Süd, Waldhof-West, Luzenberg, Waldhof-Ost, Neuostheim, Neuhermsheim, Hochstätt, Friedrichsfeld, Käfertal-Mitte, Speckweggebiet, Sonnenschein, Franklin, Käfertal-Süd, Vogelstang, Wallstadt, Niederfeld, Almenhof, Casterfeld, Pfingstberg, Rheinau-Mitte, Rheinau-Süd.
- - Einzelpruefer-Urteil, ergaenzt durch eine unabhaengige Sichtpruefung
  einer Teilmenge der als "over" bewerteten Patches.
- Systematische Uebersegmentierung an Baeumen zu benachbarten
  Rasen-/Wiesen-/Feldflaechen, auf Dae chern, Schattenflaechen und
  Gleisbett (in der Stichprobe: zwei Patches mit leichter
  Rasen-Segmentierung, eines mit Rasen als Baeume fehlidentifiziert,
  eines mit moeglicherweise als Baeume fehldetektierten Hecken, eines
  mit leicht uebersegmentiertem Feld; unabhaengig bestaetigt auf
  sechs weiteren Patches).
- Randbereiche am Stadtrand und an der Stadtgrenze.
- Die Wiederholungspruefung (jedes 10. Patch) wurde vom Eigentuemer
  durchgefuehrt; Abweichungen sind nicht dokumentiert.

## Empfehlungen

- Keine erneute Inferenz-Runde mit denselben Gewichten und
  Einstellungen: sie wuerde dieselben Masken erzeugen und das
  beobachtete Muster nicht veraendern.
- Falls die Karte vertrauenswuerdig bleiben soll: eine gezielte
  Schwellwert-Kalibrierung (Sigmoid-Schwelle ueber 0.5) mit einer
  Inferenz-Runde auf denselben Gewichten, danach erneute Bewertung
  der betroffenen Patches und Quantifizierung der Wert-Abweichung pro
  Gebaeude. Dies ist eine separate Entscheidung (nicht Teil dieser
  Verifikation).
- Andernfalls die Uebersegmentierung als dokumentierte Einschraenkung
  akzeptieren; die Gebaeudewerte sind dann in den betroffenen
  Stadtteilen tendenziell ueberhoeht.

---

## Kalibrierung und Entscheidung (Feature 009, 2026-08-05)

- Kandidaten: Sigmoid-Schwellen 0.6 und 0.65, gleiche Gewichte und Kacheln (RunPod, RTX 3090, 12314 Patches pro Lauf).
- Wiedererkennung der bei 0.5 detektierten Baumflaeche je Kandidat: zuvor korrekte Patches 82.9 % (0.6) / 75.8 % (0.65); zuvor over-bewertete Patches 80.6 % / 72.8 %.
- Unabhaengige Sichtpruefung der fuenf staerksten Verluste in zuvor korrekten Patches: 70-85 % der bei 0.6 entfernten Flaeche sind echte Baumkronen; der zusaetzliche 0.65-Schritt entfernt ueberwiegend Kronenraender. Beide Schwellen verlieren echte Baeume; 0.6 staerker als der 0.65-Zusatzschritt.
- Entscheidung (Eigentuemer): die veroeffentlichten Werte bleiben bei Schwelle 0.5. Keine Uebernahme der Kandidaten. Massnahme: allgemeiner Genauigkeitshinweis auf der Website (Feature 010), ohne Nennung einzelner Stadtteile.
- Zusaetzlicher Befund: vorbestehender `values.py`-Fehler (fftconvolve-Float-Rauschen) fuehrte zu 109 Gebaeuden ohne Wert in der veroeffentlichten Datei; im Pipeline-Code behoben, die Karte bleibt unveraendert (Entscheidung oben).

### Wert-Abweichung der Kandidaten (Dokumentation der Entscheidung)

| Kandidat | Mittlere Abweichung (pp) | Gebäude mit Verschiebung > 0,5 pp | Stadtmittel veroeffentlicht | Stadtmittel Kandidat |
|----------|--------------------------|-----------------------------------|----------------------------|----------------------|
| 0.6  | -3.90 | 98.0 % | 22.22 % | 18.33 % |
| 0.65 | -5.53 | 98.6 % | 22.22 % | 16.69 % |

Bewertung: Bei 0.6 wuerden fast alle Gebaeudewerte (98 %) um durchschnittlich
3,9 Prozentpunkte fallen, bei 0.65 um 5,5 Prozentpunkte. Die Ueberhoehung der
veroeffentlichten Werte ist damit in dieser Groessenordnung — der Hinweis auf
der Website (Feature 010) bleibt die gewaehlte Massnahme; eine Neu-Veröffentlichung
der Daten ist nicht beschlossen.
