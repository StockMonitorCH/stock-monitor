# Nächstes Release – Änderungsprotokoll

> Diese Datei sammelt alle Änderungen seit v5.8.0 für die GitHub-Release-Beschreibung (Release: v5.9.0).
> Bitte ergänzen, sobald neue Features / Fixes fertig sind.

---

## Neue Features

- **Logarithmische Preisachse** – neue Checkbox „Log“ in der Zoom-Ansicht (Linie und Candlesticks). Gleiche prozentuale Veränderungen erscheinen gleich hoch – ideal für lange Zeiträume (5J, Max). Gut lesbare Achsenbeschriftung, Crosshair und Bollinger-Bänder werden korrekt mitskaliert; Einstellung wird gespeichert. *(Wunsch aus einer App-Store-Rezension)*
- **Dividendenkonto** – neues Mehrwährungskonto im Dividendenfenster (Button „💰 Dividendenkonto“). Dividenden werden automatisch am Ex-Tag mit dem damaligen Bestand dem Konto ihrer Währung gutgeschrieben; Quellensteuer je nach Sitzland der Firma und eigenem Steuerwohnsitz (CH/DE/AT/UK/US, W-8BEN). Umschalter Brutto/Netto, Gesamtsaldo in der Portfolio-Währung, Doppelklick zeigt alle Buchungen eines Kontos mit laufendem Saldo. Manuelle Ein-/Auszahlungen, Dividenden korrigierbar, Export PDF/XLSX/ODS. Wird verschlüsselt mit dem Portfolio gespeichert. Neue Dateien: `dividend_account.py`, `dividend_account_translations.py`. Beim Laden erscheint die gewohnte Dollarnote mit Fortschrittsanzeige.
- **Steuerauszug AT: Ausschüttungsgleiche Erträge (AGE)** – neuer Button „📝 AGE erfassen“: Werte thesaurierender Fonds aus der OeKB-Meldung (AGE und anrechenbare QSt je Anteil, Zuflussdatum) manuell eintragen. KESt auf AGE wird mit dem Bestand am Zuflusstag berechnet, erscheint als eigene Spalten, in der Zusammenfassung, in der Gesamtsteuer und in allen Exporten. Der Dialog zeigt nur Fonds/ETFs (Option „Alle Positionen anzeigen“); Währung der OeKB-Meldung wählbar, Umrechnung zum Kurs am Zuflusstag. Zeilen abwechselnd hell/grau (auch bei ausgeblendeten Zeilen und im Dark Mode), OeKB-Link im Dark Mode lesbar.

- **Verkaufshistorie** – Verkäufe (manueller Teilverkauf, Broker-Import) werden intern mit Datum gespeichert. Die Hauptansicht zeigt weiterhin nur offene Positionen; Dividendenkonto und Steuerauszug kennen aber den Bestand an jedem Ex-Tag – auch für ganz verkaufte Titel (erscheinen im Steuerauszug des Verkaufsjahres mit Menge 0). Der Teilverkauf-Dialog fragt jetzt zusätzlich das Verkaufsdatum ab (auch nachträglich; Vorgabe = letzter Handelstag; Wochenenden werden abgelehnt, bei Börsenfeiertagen der jeweiligen Börse erscheint eine Warnung mit „Trotzdem übernehmen“; Krypto 24/7). Wird verschlüsselt mit dem Portfolio gespeichert.

---

## Verbesserungen

- **Hilfe ergänzt** – neue Abschnitte Log-Skala, Dividendenkonto, Steuermodul (Währung, Sitzland & Quellensteuer, AT-AGE); AT-Steuerhilfe mit neuen Spalten und AGE-Anleitung (DE/EN).
- **Steuerauszug: Fenstergrösse** – öffnet so breit, dass alle Buttons vollständig sichtbar sind (max. 95 % des Bildschirms), zentriert. Auf kleinen Bildschirmen (z. B. Full HD mit 150 % Skalierung) kompakte Kopfzeile und niedrigere Tabelle.
- **Monte Carlo (Portfolio und Szenarien): Legende** – Legendenleiste über den Diagrammen statt Legende im Diagramm; auf Full HD werden die Kurven nicht mehr verdeckt. Abstand zum Titel wird gemessen und ist bei jeder Auflösung/Skalierung gleich. Im Vergleichsmodus eine gemeinsame Y-Achsenbeschriftung statt zwei überlappender.

- **Börsenkalender** – Feiertage werden jetzt nach festen Regeln berechnet (Ostern, „3. Montag im Januar“, Ersatztage) statt von Hand gepflegt, für 2024–2028. Neu mit Feiertagen: Wien, Mailand, Madrid, Lissabon, Stockholm, Oslo, Kopenhagen, Helsinki, Johannesburg, Mexiko, São Paulo, NZX, CME. Wirkt in der Anzeige der Börsenzeiten und im Teilverkauf-Dialog.
- **yfinance 1.8.0** – Datenbibliothek auf die aktuelle Version aktualisiert.

---

## Bug-Fixes

- **Monte-Carlo-Szenarien: Ergebnistabelle im Dark Mode unlesbar** – helle Zeilenfarben mit heller Schrift; jetzt dunkle Palette wie in der Portfolio-Ansicht. Auch im Light Mode besserer Kontrast für Grün/Rot. Trennlinien beider Monte-Carlo-Tabellen im Dark Mode deutlich sichtbar. Spaltenlinien von Kopfzeile und Tabelle bei skalierten Bildschirmen (ab 125 %, z. B. 4K) nicht mehr um 1 Pixel versetzt.
- **Hilfe: Inhaltsverzeichnis** – „Candlestick“ sprang zu „Stop-Loss & Zielkurs“, „News“ (EN) ins Leere.
- **Steuerhilfe: Kursangaben** – beschrieb „Kurs per 31.12. (Jahreskurs)“, der Auszug nutzt aber den aktuellen Kurs; Texte korrigiert.
- **Monte Carlo: Achsenbeschriftung** – „Portfoliowert (USD) (USD)“ bzw. bei CHF-Portfolios „Portfoliowert (USD) (CHF)“; jetzt nur die tatsächliche Währung.
- **Steuerauszug: Sitzland der Wertpapiere** – Das Sitzland wurde bisher nie erkannt (Positionen speichern kein Land): im CH-Auszug galt jede ausländische Aktie als US-Aktie, im AT-Auszug als österreichische. Jetzt wird das Land aus den Yahoo-Firmendaten bestimmt (Apple bleibt US, auch an der Börse Frankfurt), bei ETFs aus dem Fondsnamen (UCITS → IE/LU ohne Quellensteuer, „(CH)“ → Verrechnungssteuer), sonst aus der Börsenendung. Ergebnis wird zwischengespeichert.
- **Steuerauszug CH/AT: korrekte DBA-Sätze** – neue Tabelle mit den Restsätzen je Land (UK, HK, SG, UCITS-Fonds 0 %; FR 12,8 %; JP/FI 10 %; meist 15 %). Behoben u. a.: UK-Dividenden in AT fälschlich mit 15 % QSt, österreichische Aktien im CH-Auszug mit pauschal 30 %, unbekannte Börsen im AT-Auszug als österreichisch behandelt, UCITS-ETFs an der SIX mit 35 % Verrechnungssteuer.
- **Steuerauszug: UK-Dividenden 100-fach zu hoch** – Yahoo liefert Dividenden Londoner Aktien in Pence; sie wurden als Pfund gerechnet. Jetzt korrekt umgerechnet (auch ZAc, ILA).
- **Steuerauszug: Währungen gemischt** – Dividenden und Kurse in USD, GBP, CHF usw. wurden ohne Umrechnung addiert und als EUR/CHF ausgewiesen. Jetzt alles in der Auszugswährung (AT/DE EUR, CH CHF, UK GBP, US USD): Dividenden zum Kurs am Ex-Tag, Kurse/Marktwerte zum aktuellen Kurs. Hinweis im Auszug, falls ein Kurs fehlt.
- **Steuerauszug: aktueller Kurs** – Es wurde immer der Kaufkurs als aktueller Kurs angezeigt (Kurs-Cache falsch gelesen); Marktwert und KESt-Schätzung auf Kursgewinne waren dadurch falsch.
- **Steuerauszug: Verkauf am Ex-Tag** – Positionen, die am Ex-Tag verkauft wurden, verloren fälschlich den Dividendenanspruch; am Ex-Tag gekaufte wurden fälschlich mitgezählt. Jetzt gleiche Regel wie im Dividendenkonto (vor dem Ex-Tag gekauft, nicht vor dem Ex-Tag verkauft).
- **Börsenzeiten: falsche Feiertage 2027** – Ostern 2027 war mit dem 25. April statt dem 28. März hinterlegt; Karfreitag/Ostermontag (alle Börsen) sowie Auffahrt/Pfingstmontag (SIX) waren falsch. Weitere Korrekturen: SIX ohne Ersatztag für den 1. August, Berchtoldstag ergänzt; Toronto Civic Holiday ergänzt; ASX/Toronto Ersatztage an Weihnachten; Tokio Ersatz- und Brückenfeiertage.
- **Dividend Kings / Aristocrats aktualisiert (Stand November 2026)** – Liste war seit 2025 nicht gepflegt und enthielt Fehler: u. a. 3M und V.F. Corp (Dividende gekürzt) noch als Kings, AT&T, Walgreens, Ventas u. a. fälschlich als Aristocrats. Neu u. a.: Carlisle, McDonald's, MGE Energy, Pentair, ADM, RLI, United Bankshares (Kings); Erie, Eversource, FactSet, Brown-Forman, Cardinal Health, West Pharmaceutical u. a. (Aristocrats). Umbenennungen berücksichtigt (Marzetti MZTI, H2O America HTO).
- **Steuerauszug AT: Hinweisspalte fehlte** – Die Tabelle hatte eine Spalte zu wenig, die DBA-Hinweise wurden nie angezeigt; Spaltentitel „Quellensteuer/DBA-Satz“ passten nicht zu den Werten (KESt / ausl. QSt).
- **macOS: Ziffern mit grossen Abständen** – in Labels und Buttons mit Emoji (z. B. ECY-Zeile „4 1 . 0“, Monte-Carlo-Szenarien „± 1 0 %-Sperre“) wurde „Apple Color Emoji“ als Hauptschrift verwendet, deren Ziffern breite Keycap-Glyphen sind. Jetzt Systemschrift mit Emoji-Schrift als Fallback.

---

## Entfernt

*(noch leer)*

---

## Status
- v5.8.0 released am 02.11.2026
- Nächste Version: v5.9.0 (APP_VERSION bereits gesetzt)

## Ideen / Backlog

- [ ] Timer-Stopp im Update-Dialog beim Scrollen / Info öffnen
- [ ] Februar 2027: `dividend_lists.json` nach S&P-Rebalancing (Ende Januar) erneut abgleichen; Kenvue-Übernahme, GPC-Aufspaltung beachten
- [ ] Börsenfeiertage nach offiziellen Kalendern ergänzen: Hongkong 2028 (Mondkalender, Liste 2026/27 prüfen), Shanghai/Shenzhen, Korea, Singapur, Indien, Tel Aviv (Handel Mo–Fr seit 2026) – erst wenn die Börsen sie veröffentlicht haben; in `market_data.py` unter `_MANUAL_HOLIDAYS`
- [ ] Analysten-Ampel: eigene Berechnung statt Yahoo-Label (gewichteter Mittelwert)
- [ ] Stresstest Komplex: Zinserhöhungs-Szenario einbauen
- [ ] (später, nicht 5.9.0) Zentrales Dark-Mode-Theme `theme.py`: eine Dark-Erkennung statt 38, Farben nach Bedeutung (Zeile pessimistisch/optimistisch, positiv/negativ, Infobox, Trennlinie, Link) mit Hell-/Dunkel-Variante; ab dann für Neues verwenden, Bestehendes schrittweise umstellen (910 feste Farben in stock_monitor.py). Optional: automatischer Dark-Mode-Kontrasttest.
