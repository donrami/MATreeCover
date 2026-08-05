# Notizen zur Verifikation (owner writeup)

Diese Datei wird von `verify-report` in den Bericht
(`verification/report.md`) uebernommen. Inhalt: Einschaetzung des
Pruefers (Eigentuemer), Stand 2026-08-05.

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

## Einschraenkungen (zusaezlich)

- Einzelpruefer-Urteil, ergaenzt durch eine unabhaengige Sichtpruefung
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
