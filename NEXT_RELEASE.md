# Nächstes Release – Änderungsprotokoll

> Diese Datei sammelt alle Änderungen seit v5.9.0 für die GitHub-Release-Beschreibung (Release: v5.9.1).
> Bitte ergänzen, sobald neue Features / Fixes fertig sind.

---

## Neue Features

- **Krypto-Staking importieren** – Swissquote verbucht Staking-Erträge als „Crypto Deposit“; diese wurden bisher ignoriert, ETH/SOL-Mengen waren dadurch zu tief. Der Swissquote-Import zeigt jetzt – nur wenn solche Buchungen vorhanden sind – eine Checkbox „Staking-Erträge importieren (x ETH, y SOL)“. Die Coins werden mit Einstandspreis 0 übernommen, der Ertrag erscheint als Gewinn der Position. Warnung bei auffällig grossen Einzelbuchungen (könnte ein Wallet-Übertrag sein). Im generischen Import gibt es für unbekannte Transaktionstypen die neue Option „Als Staking-Ertrag“.
- **Vergleich: Aktien ausserhalb der Charts** – Im Fenster „Charts vergleichen“ öffnet der neue Button „➕ Weitere Aktie…“ die Firmensuche. Die gewählte Aktie erscheint kursiv als zusätzliche Checkbox und wird sofort verglichen, ohne dass einer der Charts ersetzt werden muss. Bis zu 4 zusätzliche Aktien; sie werden in `config.json` gespeichert und stehen beim nächsten Öffnen wieder zur Verfügung. Entfernen per Rechtsklick. Die Charts im Hauptfenster bleiben unverändert.
- **Kaufkurs von Hand anpassen** – Beim Hinzufügen einer Position erscheint der automatisch geladene Schlusskurs in einem Bestätigungsfenster und kann überschrieben werden, z.B. wenn die Aktie am Kauftag stark geschwankt hat. Angezeigt werden Währung (inkl. Hinweis auf Pence bei London) und Tagesspanne Tief–Hoch; liegt der eingegebene Kurs mehr als 10 % ausserhalb, fragt Stock Monitor nach (Tippfehler-Schutz). „↺ Schlusskurs“ stellt den automatischen Kurs wieder her. **Zukauf (+) und Teilverkauf (−):** Datum, Stückzahl und Kurs in einem Fenster; der Schlusskurs wird beim Datumswechsel neu geladen, ein von Hand geänderter Kurs bleibt erhalten. Zukauf öffnete bisher kein Fenster (nur Meldung „Symbol eingetragen“, Eingabe oben im Formular). Ohne Yahoo-Kurs kann beim Zukauf von Hand ein Kurs eingetragen werden. Der Verkaufskurs wird beim Teilverkauf gespeichert (Grundlage für spätere „Realisierte Gewinne“, noch keine Anzeige); ohne Kurs bleibt der Verkauf möglich. Ersetzt die bisherige Meldung „Handelstag angepasst“ (Hinweis erscheint jetzt im selben Fenster). *(Wunsch eines Users)*
- **Indizes im Chart** – Index-Namen wie „SMI“, „SPI“, „S&P 500“, „Nikkei“, „Euro Stoxx 50“ können direkt ins Symbolfeld eingegeben werden und werden in das Yahoo-Symbol umgewandelt (SMI → `^SSMI`, SPI → `^SSHI` usw., rund 30 Indizes). In der Firmensuche erscheint der Index als erster Treffer. Kurznamen, die bei Yahoo auch ein Wertpapier sind (DAX = Global X DAX ETF, DOW = Dow Inc., CAC, HSI), werden nur in der Firmensuche als Index angeboten, nicht bei direkter Eingabe.
- **Watchlist: Symbol-Prüfung mit Vorschlägen** – Symbole werden vor dem Hinzufügen bei Yahoo auf Kursdaten geprüft (parallel, ca. 1–2 s). Unbekannte Symbole werden nicht mehr übernommen, sondern bleiben zur Korrektur im Eingabefeld. Bei Tippfehlern erscheinen anklickbare Vorschläge aus den Screener-Indexlisten (NVAD → NVDA, APPL → AAPL, TSAL → TSLA); Buchstabendreher zählen als ein Fehler, bekannte Titel werden bevorzugt. Kürzel ohne Börse werden ergänzt (NESN → NESN.SW). Ohne Internet wird das Symbol trotzdem übernommen.

---

## Verbesserungen

- **Update-Dialog: Countdown stoppt beim Lesen** – Sobald im Update-Fenster gescrollt, geklickt oder eine Taste gedrückt wird, schliesst sich das Fenster nicht mehr nach 10 Sekunden automatisch. Die Update-Funktion selbst ist unverändert.
- **Firmensuche: Trefferliste statt Einzeltreffer** – Die Suche (⌕ im Chart und in der Watchlist) zeigt alle Treffer als Liste mit Symbol, Börse und Name. Der wahrscheinlichste Treffer steht oben, fett mit ★ und vorausgewählt; Übernehmen per Doppelklick, Enter oder „Übernehmen“. Bisher war nur ein Treffer wählbar, Alternativen standen als nicht anklickbarer Text daneben.
- **Firmensuche: nur Treffer mit Kursdaten** – Futures und Optionen werden ausgeblendet; jeder Treffer wird vorab auf Kursdaten geprüft (z.B. fehlen bei `NESTLEIND.BO`, `TAAPL=F` die Kurse). Indische Doppel-Listings: `.BO` wird ausgeblendet, wenn dieselbe Aktie an der NSE (`.NS`) gelistet ist. Hinweis „(x ohne Kursdaten ausgeblendet)“.
- **Firmensuche: Heimatbörse statt Zweitlisting** – Ist der erste Yahoo-Treffer nur ein Zweitlisting (Frankfurt, München, Wien, London IOB …), wird dieselbe Firma an der Heimatbörse bevorzugt, Schweizer Börse zuerst. Beispiel: „Mobimo“ → `MOBN.SW` statt `M1H.F`.
- **Chart: verständliche Meldung bei lückenhaften Yahoo-Daten** – Statt des technischen yfinance-Fehlers „Dividends events are out-of-range…“ erscheint ein Hinweis mit Tipp (anderer Börsenplatz, kürzerer Zeitraum).
- **Vergleichsfenster breiter** – 95 % statt 82 % der Bildschirmbreite; der Zähler „Mindestens 2 auswählen“ wird nicht mehr abgeschnitten (Breite nach längstem Text, auch EN).
- **Hilfe erweitert** – Neuer Abschnitt „Firmensuche“ inkl. Indizes (Tabelle der Kurznamen); „Vergleich“ ausführlich beschrieben (Zusatz-Aktien, Limit, Rechtsklick); Watchlist mit Symbol-Prüfung und Vorschlägen (DE/EN).

---

## Bug-Fixes

- **Firmensuche: OK übernahm nichts** – Wer einen Namen eintippte und direkt OK drückte, landete ohne Ergebnis wieder im Chart, weil nur nach „Suchen“ ein Symbol gesetzt wurde. Zudem schloss Enter im Suchfeld den Dialog. Jetzt startet „Übernehmen“ ohne Treffer die Suche, Enter im Suchfeld sucht nur.
- **Vergleich: „nan%“ bei einzelnen Aktien** – Lieferte Yahoo leere Schlusskurse (z.B. `000660.KS` SK hynix), zeigte der Vergleich „nan%“ und eine abgebrochene Linie. Leere Kurse werden jetzt vor der Berechnung entfernt (Vergleich und Export).
- **Swissquote-Import: Schweizer Nebenwerte nicht gefunden** – Swissquote verwendet teils kürzere Kürzel als die SIX (`MOB` statt `MOBN` für Mobimo); daraus wurde das nicht existierende `MOB.SW`. Liefert ein Symbol keine Kurse, wird es jetzt über die ISIN aus der CSV gesucht (`CH0011108872` → `MOBN.SW`), mit Börsenplatz passend zur Handelswährung. Bereits importierte Positionen mit falschem Symbol (z.B. `MOB.SW`) bleiben bestehen und müssen neu importiert oder von Hand korrigiert werden.
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

- [ ] **Realisierte Gewinne** (Wunsch eines Users): Verkaufskurs beim Teilverkauf erfassen (wie Kaufkurs: Schlusskurs vorausgefüllt, überschreibbar; beim Swissquote-Import aus der CSV). Das Feld `sell_price` existiert bereits in `_record_sale`, wird aber nirgends gefüllt/ausgewertet. Neue Ansicht „Realisierte Gewinne“: je Verkauf Kauf-/Verkaufskurs, Stück, Haltedauer, Gewinn in Handelswährung und Portfoliowährung (FX am Kauf- bzw. Verkaufstag), Jahressummen, Export. Gesamtertrag = realisierte Kursgewinne + Dividenden.
  - **Nicht ins Dividendenkonto buchen:** Dividenden sind reiner Ertrag, Verkaufserlöse dagegen Kapitalrückfluss. Ohne gleichzeitige Belastung der Käufe würde der Kontostand mit jedem Verkauf „aus dem Nichts“ wachsen. Ein echtes Cash-Konto (Käufe belasten, Verkäufe gutschreiben, Ein-/Auszahlungen) wäre ein eigenes, grösseres Projekt.
  - Steuerauszug: realisierte Gewinne relevant für DE/AT (Abgeltung/KESt), in CH steuerfrei (Privatvermögen) – länderspezifisch prüfen.
- [ ] Februar 2027: `dividend_lists.json` nach S&P-Rebalancing (Ende Januar) erneut abgleichen; Kenvue-Übernahme, GPC-Aufspaltung beachten
- [ ] Börsenfeiertage nach offiziellen Kalendern ergänzen: Hongkong 2028 (Mondkalender, Liste 2026/27 prüfen), Shanghai/Shenzhen, Korea, Singapur, Indien, Tel Aviv (Handel Mo–Fr seit 2026) – erst wenn die Börsen sie veröffentlicht haben; in `market_data.py` unter `_MANUAL_HOLIDAYS`
- [ ] Generischer CSV-Import: optionale Währungsspalte (Auto-Erkennung + Spalten-Dialog), dann Swissquote-Regeln übernehmen (Börsensuffix aus Handelswährung, GBP→Pence, EUR-Börsen bevorzugen). Erst umsetzen, wenn eine echte Beispiel-CSV einer anderen Bank vorliegt.
- [ ] Staking im Dividendenkonto / Steuerauszug: bewusst nicht umgesetzt (ca. 0.1 % des Portfolios, Swissquote-Steuerauszug ist massgebend). Falls doch: Ertrag zum Kurs am Zuflusstag, länderspezifische Regeln (CH Einkommen, AT erst bei Verkauf, DE Freigrenze) einzeln prüfen.
- [ ] Analysten-Ampel: eigene Berechnung statt Yahoo-Label (gewichteter Mittelwert)
- [ ] Stresstest Komplex: Zinserhöhungs-Szenario einbauen
- [ ] (später, nicht 5.9.0) Zentrales Dark-Mode-Theme `theme.py`: eine Dark-Erkennung statt 38, Farben nach Bedeutung (Zeile pessimistisch/optimistisch, positiv/negativ, Infobox, Trennlinie, Link) mit Hell-/Dunkel-Variante; ab dann für Neues verwenden, Bestehendes schrittweise umstellen (910 feste Farben in stock_monitor.py). Optional: automatischer Dark-Mode-Kontrasttest.
