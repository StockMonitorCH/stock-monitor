# Nächstes Release – Änderungsprotokoll

> Diese Datei sammelt alle Änderungen seit v5.7.3 für die GitHub-Release-Beschreibung (Release: v5.7.4).
> Bitte ergänzen, sobald neue Features / Fixes fertig sind.

---

## Neue Features

*(noch leer)*

---

## Verbesserungen

- **5D-Candlestick-Chart**: gaplose Integer-Index-X-Achse – keine Lücken mehr über Nacht / am Wochenende
- **Monte Carlo Szenarien**: Y-Achsen im Dual-Chart-Modus synchronisiert (gleicher Maßstab links/rechts)
- **Monte Carlo Szenarien**: Vergleichstabelle zeigt jetzt Szenario | Echtes Portfolio | Differenz nebeneinander
- **Monte Carlo Szenarien**: ±10%-Sperre klemmt Werte nicht mehr still, sondern zeigt echten Prozentwert rot + Warnung „⚠ Abweichung über ±10%"
- **Komplex – Stress-Korrelation**: Schwellwert von >10 auf ≥5 Krisenperioden gesenkt; bei knapper Datenbasis erscheint `*` mit Fussnoten-Hinweis

---

## Bug-Fixes

- **Candlestick-Chart**: Doji-Kerzen (Open = Close) erzeugten riesige Spike-Balken – Mindest-Körperhöhe ist jetzt preisbasiert (5 % des mittleren Kursbereichs) statt zeitbasiert
- **Screener**: Deutscher Text erschien im Englisch-Modus (AND/OR-Hinweis)
- **Screener + MC-Szenarien**: `RuntimeError: wrapped C++ object deleted` – Race Condition beim schnellen Schließen behoben
- **Hilfetexte**: 5 Korrekturen (Tippfehler, fehlende TOC-Einträge, doppelte Anker, falsches Button-Label, HTML-Struktur)

---

## Entfernt

- **RPM-Paketformat eingestellt**: `build_rpm.sh` und `stock-monitor.spec` entfernt; kein RPM-Build mehr

---

## Status
- v5.7.2 released am 14.10.2026
- v5.7.3 released am 17.10.2026
- Nächste Version: v5.7.4

## Ideen / Backlog

- [ ] Timer-Stopp im Update-Dialog beim Scrollen / Info öffnen
- [ ] Analysten-Ampel: eigene Berechnung statt Yahoo-Label (gewichteter Mittelwert)
- [ ] Stresstest Komplex: Zinserhöhungs-Szenario einbauen
