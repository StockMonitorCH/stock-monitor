# Nächstes Release – Änderungsprotokoll

> Diese Datei sammelt alle Änderungen seit v5.9.0 für die GitHub-Release-Beschreibung (Release: v5.9.1).
> Bitte ergänzen, sobald neue Features / Fixes fertig sind.

---

## Neue Features

*(noch leer)*

---

## Verbesserungen

*(noch leer)*

---

## Bug-Fixes

*(noch leer)*

---

## Entfernt

*(noch leer)*

---

## Status
- v5.9.0 released am 08.11.2026
- Nächste Version: v5.9.1

## Ideen / Backlog

- [ ] Timer-Stopp im Update-Dialog beim Scrollen / Info öffnen
- [ ] Februar 2027: `dividend_lists.json` nach S&P-Rebalancing (Ende Januar) erneut abgleichen; Kenvue-Übernahme, GPC-Aufspaltung beachten
- [ ] Börsenfeiertage nach offiziellen Kalendern ergänzen: Hongkong 2028 (Mondkalender, Liste 2026/27 prüfen), Shanghai/Shenzhen, Korea, Singapur, Indien, Tel Aviv (Handel Mo–Fr seit 2026) – erst wenn die Börsen sie veröffentlicht haben; in `market_data.py` unter `_MANUAL_HOLIDAYS`
- [ ] Analysten-Ampel: eigene Berechnung statt Yahoo-Label (gewichteter Mittelwert)
- [ ] Stresstest Komplex: Zinserhöhungs-Szenario einbauen
- [ ] (später, nicht 5.9.0) Zentrales Dark-Mode-Theme `theme.py`: eine Dark-Erkennung statt 38, Farben nach Bedeutung (Zeile pessimistisch/optimistisch, positiv/negativ, Infobox, Trennlinie, Link) mit Hell-/Dunkel-Variante; ab dann für Neues verwenden, Bestehendes schrittweise umstellen (910 feste Farben in stock_monitor.py). Optional: automatischer Dark-Mode-Kontrasttest.
