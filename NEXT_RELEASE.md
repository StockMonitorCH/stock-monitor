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

- **Swissquote-Import: falsche Symbole bei kurzen Tickern** – Kinross Gold (`K`) wurde als KOSPI-Index (`^KS11`) importiert, weil die Yahoo-Suche den Index zuerst lieferte. Die Symbol-Auflösung akzeptiert jetzt keine Indizes, Währungen oder Futures mehr; bei Importen werden nur noch exakte Treffer übernommen.
- **Swissquote-Import: Börsenplatz aus Handelswährung** – Das Suffix wird jetzt aus der Handelswährung abgeleitet (CAD → `.TO`, CHF → `.SW`, GBP → `.L`, JPY → `.T`, SEK → `.ST`, HKD, AUD, NOK, DKK). Kinross in CAD wird so zu `K.TO`. In USD gehandelte Titel mit ausländischer ISIN (z.B. Garmin, Chubb) bekommen kein falsches `.SW`/`.L` mehr. Aktienklassen wie `SAAB^B` werden zu `SAAB-B.ST`.
- **Swissquote-Import: Londoner Aktien fehlten** – Swissquote schreibt LSE-Ticker mit Punkt am Ende (`RR.` = Rolls-Royce), daraus wurde das ungültige Symbol `RR.`. Wird jetzt zu `RR.L`. Zudem werden GBP-Preise aus der CSV in Pence umgerechnet (Yahoo notiert LSE in GBp), und der historische FX-Kurs nutzt `GBPCHF=X` statt des nicht existierenden `GBpCHF=X`.
- **Swissquote-Import: in EUR gekaufte US-Aktien** – Bei Handelswährung EUR wird ein europäischer Börsenplatz bevorzugt (z.B. `NVD` → `NVD.DE` statt des gleichnamigen US-ETFs, `WMT` → `WMT.MU`, `ASML` → `ASML.AS`). Gleiche Ticker in verschiedenen Währungen werden nicht mehr vermischt.

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
