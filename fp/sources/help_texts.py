"""
help_texts.py – Help content for Stock Monitor
===============================================
Contains all help texts in DE and EN.
Completely decoupled from translations.py (UI strings) and from
the main application code.

Usage:
    from help_texts import get_help
    h = get_help("DE")   # or "EN"
    html        = h["html"]
    toc_items   = h["toc_items"]
    anchor_map  = h["anchor_map"]
    search_ph   = h["search_placeholder"]
    title       = h["window_title"]
"""

# ── Shared CSS (language-independent) ────────────────────────────────────────
_CSS = """
    <style>
        body { font-family: Arial, sans-serif; padding: 18px; font-size: 13px; line-height: 1.5; }
        h2 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; margin-top: 30px; }
        h3 { color: #34495e; margin-top: 14px; }
        code { background-color: #ecf0f1; padding: 2px 6px; border-radius: 3px; font-size: 12px; font-family: monospace; }
        .tip     { background-color: #e8f8f5; padding: 10px 14px; border-left: 4px solid #00b894; margin: 10px 0; border-radius: 0 4px 4px 0; }
        .warning { background-color: #fff3cd; padding: 10px 14px; border-left: 4px solid #ffc107; margin: 10px 0; border-radius: 0 4px 4px 0; }
        .new     { background-color: #eaf4ff; padding: 7px 12px; border-left: 4px solid #3498db; margin: 6px 0 10px 0; font-weight: bold; color: #1a5276; border-radius: 0 4px 4px 0; }
        ul { margin: 6px 0 8px 0; }
        li { margin: 4px 0; }
        table { border-collapse: collapse; width: 100%; margin: 8px 0; }
        th { background: #2c3e50; color: white; padding: 6px 10px; text-align: left; font-size: 12px; }
        td { padding: 5px 10px; border-bottom: 1px solid #dee2e6; font-size: 12px; }
        tr:nth-child(even) td { background: #f8f9fa; }
    </style>
"""

# ── Support / Donation block (language-specific) ──────────────────────────────
_SUPPORT_DE = """
        <h2>&#128222; Support</h2>
        <p>&#128231; <a href="mailto:info@stock-monitor.ch">info@stock-monitor.ch</a><br>
        &#127760; <a href="https://www.stock-monitor.ch">www.stock-monitor.ch</a></p>
        <br>
        <h2>&#10084; Unterstützung</h2>
        <p>Stock Monitor ist kostenlos und wird in der Freizeit entwickelt.<br>
        Wenn dir die App gefällt und du die Weiterentwicklung unterstützen möchtest,
        freue ich mich über eine kleine Spende – jeder Betrag hilft!</p>
"""

_SUPPORT_EN = """
        <h2>&#128222; Support</h2>
        <p>&#128231; <a href="mailto:info@stock-monitor.ch">info@stock-monitor.ch</a><br>
        &#127760; <a href="https://www.stock-monitor.ch">www.stock-monitor.ch</a></p>
        <br>
        <h2>&#10084; Support the Project</h2>
        <p>Stock Monitor is free and developed in spare time.<br>
        If you enjoy the app and would like to support further development,
        any donation is greatly appreciated!</p>
"""

_DONATION_TABLE = """
        <table cellspacing="0" cellpadding="8"><tr>
        <td valign="middle">
        <b>PayPal:</b><br>
        <a href="https://paypal.me/StockMonitor">paypal.me/StockMonitor</a>
        </td>
        <td width="20"></td>
        <td valign="middle">
        <b>Bank transfer (CH):</b><br>
        <span style="font-family:monospace; background:#f0f7ff; border:1px solid #2980b9; border-radius:4px; padding:4px 10px; display:inline-block;">CH81 0900 0000 6010 1573 2</span>
        </td>
        </tr></table>
"""


# ══════════════════════════════════════════════════════════════════════════════
# GERMAN  ─  DEUTSCH
# ══════════════════════════════════════════════════════════════════════════════
_HTML_DE = """
        <a name="überblick"><h2>&#128202; Überblick</h2></a>
        <p>Stock Monitor ist eine professionelle Trading-App zum gleichzeitigen Überwachen
        von Aktien, ETFs und Kryptowährungen &mdash; mit Portfolio-Management, Risikokennzahlen,
        KI-Analyse und verschlüsselter Datenhaltung.<br>
        <b>Plattformen:</b> Linux (KDE Plasma, GNOME, ...) &bull; Windows (als .exe, Download auf GitHub)</p>
        <div class="tip"><b>Kurz-Übersicht der Hauptfunktionen:</b><br>
        <b>Oben:</b> Administration &bull; Charts &bull; Portfolio-Ansicht &bull; Analyse-Tools &bull; Export<br>
        <b>Mitte:</b> Live-Charts mit technischer Analyse<br>
        <b>Unten:</b> Gesamt-Summe Investiert / Aktuell / G&amp;V</div>

        <div class="new">&#127381; <b>Demo-Portfolio vorgeladen</b><br>
        Stock Monitor wird mit einem Demo-Portfolio geliefert, damit du alle Funktionen sofort ausprobieren kannst.<br>
        <b>Passwort:</b> <code>Stock-Monitor 5.0</code></div>

        <a name="quickstart"><h2>&#128640; Quickstart – In 5 Minuten loslegen</h2></a>
        <p>Noch nie mit Stock Monitor gearbeitet? Hier der schnellste Weg zum ersten Ergebnis:</p>
        <table>
            <tr><th>Schritt</th><th>Was tun</th><th>Wo</th></tr>
            <tr><td><b>1</b></td><td>App starten – 4 leere Charts erscheinen</td><td>Hauptfenster</td></tr>
            <tr><td><b>2</b></td><td>Symbol eingeben (z.B. <code>AAPL</code>, <code>NESN.SW</code>, <code>BTC-USD</code>) + Enter</td><td>Eingabefeld oben im Chart</td></tr>
            <tr><td><b>3</b></td><td>Zeitraum wählen (1M / 6M / 1J / 5J / Max)</td><td>Dropdown im Chart</td></tr>
            <tr><td><b>4</b></td><td>Weitere Symbole in die anderen Charts eingeben</td><td>Jeden Chart einzeln</td></tr>
            <tr><td><b>5</b></td><td>Anzahl Charts ändern (4 / 6 / 8 / 12 / 16 &ndash; <i>16 nur bei 4K</i>)</td><td>Dropdown oben links in der Toolbar</td></tr>
            <tr><td><b>6</b></td><td>Chart doppelklicken für Vollbild mit RSI, BB, Candlestick</td><td>Beliebiger Chart</td></tr>
            <tr><td><b>7</b></td><td>Portfolio anlegen: ⚙ Administration → Positionen hinzufügen</td><td>Toolbar</td></tr>
            <tr><td><b>8</b></td><td>Portfolio speichern: 💾 Speichern (AES-256 verschlüsselt)</td><td>Toolbar</td></tr>
        </table>
        <div class="tip"><b>Tipp:</b> Symbole ohne Börsen-Suffix eingeben (z.B. <code>NESN</code> statt <code>NESN.SW</code>) –
        Stock Monitor erkennt die richtige Börse automatisch.</div>
        <div class="tip"><b>Tipp:</b> Die letzte Session wird beim Schliessen automatisch gespeichert
        und beim nächsten Start wiederhergestellt – inklusive Watchlist.</div>

        <a name="zahlenformat"><h2>&#128290; Zahlenformat</h2></a>
        <p>Mit dem <b>Format-Button</b> in der Toolbar lässt sich das Zahlenformat für alle dargestellten Werte anpassen.
        Drei Formate stehen zur Verfügung:</p>
        <table>
            <tr><th>Format</th><th>Land</th><th>Tausender-Trenner</th><th>Dezimalzeichen</th><th>Beispiel</th></tr>
            <tr><td><b>CH</b></td><td>Schweiz</td><td>Apostroph <code>'</code></td><td>Punkt <code>.</code></td><td>1'234'567.89</td></tr>
            <tr><td><b>DE</b></td><td>Deutschland</td><td>Punkt <code>.</code></td><td>Komma <code>,</code></td><td>1.234.567,89</td></tr>
            <tr><td><b>US</b></td><td>USA / International</td><td>Komma <code>,</code></td><td>Punkt <code>.</code></td><td>1,234,567.89</td></tr>
        </table>
        <div class="tip"><b>Hinweis:</b> Das gewählte Format wird für Portfoliowerte, Kennzahlen, Kurse und alle
        numerischen Anzeigen übernommen. Nach dem Umschalten werden die Werte beim nächsten Refresh
        im neuen Format angezeigt.</div>
        <div class="warning"><b>Wichtig:</b> Das Zahlenformat beeinflusst nur die <i>Darstellung</i> – intern
        arbeitet die App immer mit englischen Dezimalzahlen. Eingaben (z.B. Kaufpreis, Anzahl) müssen
        weiterhin mit Punkt als Dezimalzeichen eingegeben werden.</div>
        <div class="tip"><b>Börsenkurse in Charts:</b> Die Y-Achsenbeschriftung in den Kurs-Charts
        (Hauptcharts, Portfolio-Performance) verwendet immer den internationalen Standard mit Punkt
        als Dezimalzeichen – unabhängig vom gewählten Format. Dies entspricht dem Börsenstandard.
        Alle berechneten Werte (Portfoliowerte, Alpha, Beta, Sharpe-Ratio usw.) folgen dem
        gewählten Format.</div>

        <a name="datumsformat"><h2>&#128197; Datumsformat</h2></a>
        <p>Mit dem <b>📅-Button</b> in der Toolbar lässt sich das Datumsformat für alle angezeigten Daten anpassen.
        Drei Formate stehen zur Verfügung:</p>
        <table>
            <tr><th>Format</th><th>Beispiel</th><th>Verwendung</th></tr>
            <tr><td><b>EU</b></td><td>28.03.2026</td><td>Deutsch / Schweiz / Europa</td></tr>
            <tr><td><b>ISO</b></td><td>2026-03-28</td><td>International / ISO 8601</td></tr>
            <tr><td><b>US</b></td><td>03/28/2026</td><td>USA / Englisch</td></tr>
        </table>
        <div class="tip"><b>Hinweis:</b> Das gewählte Datumsformat gilt für alle Datumsanzeigen in der App –
        Kaufdaten, Ex-Dividenden-Termine, Chart-Achsen, Portfolioexporte und Zeitstempel.
        Die Einstellung wird dauerhaft in <code>~/.stock_monitor_config.json</code> gespeichert.</div>
        <div class="warning"><b>Wichtig:</b> Das Datumsformat beeinflusst nur die <i>Darstellung</i> –
        intern speichert die App Daten immer im ISO-Format (<code>YYYY-MM-DD</code>).
        Bei der Eingabe von Kaufdaten werden alle drei Formate automatisch erkannt.</div>

        <a name="sprache"><h2>&#127760; Sprache / Language</h2></a>
        <p>Die Sprache der App lässt sich durch einen <b>Klick auf die entsprechende Flagge</b> in der Toolbar umschalten.
        Aktuell unterstützte Sprachen: <b>Deutsch (DE)</b> und <b>Englisch (EN)</b>.</p>
        <div class="tip"><b>Hinweis:</b> Die Spracheinstellung gilt für alle UI-Beschriftungen, Tooltips
        und diese Hilfe. Sie wird dauerhaft in <code>~/.stock_monitor_config.json</code> gespeichert.</div>

        <a name="charts_erstellen"><h2>&#128200; Charts erstellen</h2></a>
        <p>Klicke auf <b>&#128200; Akt.</b> im Header &rarr; Symbol eingeben &rarr; Enter.</p>
        <ul>
            <li>Börsen-Suffixe werden <b>automatisch</b> erkannt (z.B. &quot;NESN&quot; &rarr; NESN.SW)</li>
            <li>Mehrere Layouts: 4 &bull; 6 &bull; 8 &bull; 12 &bull; 16 Charts gleichzeitig &ndash; <i>16 Charts (4&times;4) erfordert 4K-Auflösung</i></li>
            <li>Klick auf Symbol in der Portfolio-Übersicht &rarr; Chart in neuem Fenster</li>
        </ul>

        <a name="rsi-indikator"><h2>&#128200; RSI-Indikator</h2></a>
        <p><b>Aktivieren:</b> Checkbox <b>RSI</b> im Zoom-Modus (Vollbild-Chart) &rarr; separates Panel unterhalb des Charts.</p>
        <table>
            <tr><th>Wert</th><th>Signal</th><th>Faustregel</th></tr>
            <tr><td><b>&gt; 70</b></td><td style="color:#e74c3c">&#9650; Überkauft</td><td>Möglicher Rücksetzer</td></tr>
            <tr><td><b>30–70</b></td><td style="color:#27ae60">&#9644; Neutral</td><td>Normaler Bereich</td></tr>
            <tr><td><b>&lt; 30</b></td><td style="color:#3498db">&#9660; Überverkauft</td><td>Mögliche Erholung</td></tr>
        </table>
        <div class="tip">&#128270; <b>Vertiefung:</b> Berechnung, Divergenzen, typische Fehler und wann der RSI versagt &rarr;
        <a href="#rsi-analyse">RSI – Analyse-Vertiefung</a></div>

        <a name="52w_hochtief"><h2>&#128200; 52W Hoch / Tief</h2></a>
        <div class="new">Feature: 52-Wochen Hoch/Tief Linien</div>
        <p>Im Zoom-Modus (Vollbild-Chart) können zwei horizontale Referenzlinien eingeblendet werden:</p>
        <ul>
            <li><b>52W Hoch:</b> Höchstkurs der letzten 52 Wochen &ndash; grüne gestrichelte Linie</li>
            <li><b>52W Tief:</b> Tiefstkurs der letzten 52 Wochen &ndash; rote gestrichelte Linie</li>
        </ul>
        <div class="tip"><b>Tipp:</b> Liegt der aktuelle Kurs nahe am 52W-Hoch, ist die Aktie auf Jahreshöchststand &ndash;
        manche Trader sehen das als Ausbruchssignal, andere als Warnsignal. Nahe am 52W-Tief kann auf eine günstige
        Einstiegsgelegenheit hindeuten.</div>

        <a name="kaufpreis-linie"><h2>&#128178; Kaufpreis-Linie</h2></a>
        <div class="new">Feature: Persönlicher Einstandskurs</div>
        <p>Wenn die Aktie im Portfolio vorhanden ist, wird im Chart eine <b>orange gestrichelte Linie</b>
        auf Höhe deines durchschnittlichen Kaufpreises eingeblendet (Checkbox <b>Kaufpreis</b>).</p>
        <ul>
            <li>Zeigt deinen <b>gewichteten Durchschnittskaufpreis</b> (Ø aller Tranchen)</li>
            <li>Sofortiger Blick: Kurs darüber = Gewinn &bull; Kurs darunter = Verlust</li>
            <li>Nur sichtbar wenn das Symbol im aktiven Portfolio vorhanden ist</li>
        </ul>

        <a name="stop-loss__zielkurs"><h2>&#128683; Stop-Loss &amp; &#127919; Persönlicher Zielkurs</h2></a>
        <div class="new">Feature: Persönliche Kursgrenzen</div>
        <p>Im Zoom-Modus können für jede Aktie persönliche Kursgrenzen gesetzt werden:</p>
        <ul>
            <li><b>Stop-Loss (rot):</b> Untergrenze &ndash; wird diese unterschritten, erscheint eine rote Warnung im Chart</li>
            <li><b>Zielkurs (grün):</b> Obergrenze &ndash; dein persönliches Kursziel</li>
        </ul>
        <p>Setzen: Klick auf <b>&#128683; SL / &#127919; ZK</b> Button im Zoom-Modus &rarr; Wert eingeben &rarr; Speichern.<br>
        Die Werte werden dauerhaft gespeichert und sind unabhängig vom Analysten-Zielkurs.</p>
        <div class="tip"><b>Tipp:</b> Stop-Loss und Zielkurs werden auch in der Portfolio-Übersicht in der Spaltenansicht angezeigt.</div>

        <h3>&#963; Sharpe-Ratio (Zoom-Modus)</h3>
        <p>Im <b>gezoomten Chart</b> (Klick auf Vollbild-Symbol) erscheint die Checkbox
        <b>Sharpe-Ratio anzeigen</b>. Sie berechnet das Risiko-Rendite-Verhältnis des
        dargestellten Zeitraums.</p>
        <p><b>Formel:</b> Annualisierte Sharpe-Ratio = (Rendite &minus; risikofreier Zins) &divide; Volatilität &times; &#8730;252<br>
        Risikofreier Zins: 5 % p.a. (0,05/252 pro Tag)</p>
        <table>
            <tr><th>Wert</th><th>Farbe</th><th>Einschätzung</th></tr>
            <tr><td>&ge; 1,0</td><td style="color:#27ae60">&#9632; Grün</td><td>Gut – gutes Rendite-Risiko-Verhältnis</td></tr>
            <tr><td>&ge; 0,5</td><td style="color:#e67e22">&#9632; Orange</td><td>Akzeptabel</td></tr>
            <tr><td>&ge; 0,0</td><td style="color:#7f8c8d">&#9632; Grau</td><td>Schwach – kaum Mehrwert ggü. risikolosem Zins</td></tr>
            <tr><td>&lt; 0,0</td><td style="color:#e74c3c">&#9632; Rot</td><td>Negativ – Rendite unter risikolosem Zins</td></tr>
        </table>
        <div class="tip">&#128270; <b>Vertiefung:</b> Formel, Grenzen der Sharpe-Ratio, Sortino-Ratio als Alternative &rarr;
        <a href="#sharpe-vertiefung">Sharpe-Ratio – Analyse-Vertiefung</a></div>

        <h3>&#127869; Candlestick-Darstellung (Zoom-Modus)</h3>
        <p>Im <b>gezoomten Chart</b> erscheint die Checkbox <b>&#127869; Candles</b>.</p>
        <ul>
            <li><b>Grüne Kerze:</b> Schlusskurs &gt; Eröffnungskurs (positiver Tag)</li>
            <li><b>Rote Kerze:</b> Schlusskurs &lt; Eröffnungskurs (negativer Tag)</li>
            <li>Der Docht zeigt das Tages-Hoch und Tages-Tief</li>
            <li>Nur im Zoom-Modus verfügbar</li>
        </ul>
        <div class="tip"><b>Tipp:</b> Candlestick-Charts eignen sich besonders gut für kurzfristige technische Analyse (z.B. Zeitraum 1T &ndash; 1M).</div>

        <a name="zeiträume"><h2>&#9200; Zeiträume</h2></a>
        <p><b>Global:</b> Ändert alle Charts gleichzeitig &bull; <b>Pro Chart:</b> Individuell wählbar</p>
        <p>Verfügbar: <code>1T</code> &bull; <code>5T</code> &bull; <code>1M</code> &bull; <code>3M</code> &bull; <code>6M</code> &bull; <code>YTD</code> &bull; <code>1J</code> &bull; <code>2J</code> &bull; <code>5J</code> &bull; <code>Max</code></p>
        <h3>&#10000; Crosshair &amp; Tooltip</h3>
        <p>Im <b>Zoom-Modus</b> (Vollbild-Chart) wird ein Crosshair aktiviert:</p>
        <ul>
            <li>Fadenkreuz folgt der Maus und zeigt Datum + Kurs als Tooltip</li>
            <li>Verschwindet automatisch beim Verlassen des Charts</li>
            <li>Nur ein Chart kann gleichzeitig aktiv sein</li>
        </ul>

        <a name="eigener_zeitraum"><h2>&#128197; Eigener Zeitraum</h2></a>
        <p>Wählbar über <b>&#128197; Eigener Zeitraum</b> &mdash; Start und End-Datum frei bestimmbar (max. 10 Jahre zurück).</p>
        <div class="tip"><b>Tipp:</b> Ideal um historische Ereignisse zu analysieren (z.B. COVID-Crash März 2020).</div>

        <a name="moving_averages_ma"><h2>&#128201; Moving Averages (MA)</h2></a>
        <ul>
            <li><b>MA20:</b> Kurzfristiger Trend (20 Tage)</li>
            <li><b>MA50:</b> Mittelfristiger Trend (50 Tage)</li>
            <li><b>MA200:</b> Langfristiger Trend (200 Tage)</li>
        </ul>
        <div class="tip"><b>Trading-Tipp:</b> <b>Golden Cross</b> = MA50 kreuzt MA200 nach oben = klassisches Kaufsignal!</div>

        <a name="trendlinie"><h2>&#128208; Trendlinie</h2></a>
        <p>Schwarze gestrichelte Linie = lineare Regression. Steigung aufwärts = Aufwärtstrend.</p>

        <a name="beta-wert_chart"><h2>&#946; Beta-Wert (Chart)</h2></a>
        <p><b>Aktivieren:</b> Checkbox <b>Beta</b> im Zoom-Modus &rarr; Wert wird im Chart eingeblendet.</p>
        <table>
            <tr><th>Beta</th><th>Bedeutung</th></tr>
            <tr><td><b>&beta; = 1.0</b></td><td>Bewegt sich wie der S&amp;P 500</td></tr>
            <tr><td><b>&beta; &gt; 1.0</b></td><td>Volatiler als der Markt</td></tr>
            <tr><td><b>&beta; &lt; 1.0</b></td><td>Defensiv, weniger Schwankung</td></tr>
            <tr><td><b>&beta; &lt; 0</b></td><td>Gegenläufer (z.B. Gold)</td></tr>
        </table>
        <div class="tip">&#128270; <b>Vertiefung:</b> &rarr; <a href="#beta-vertiefung">Beta – Analyse-Vertiefung</a></div>

        <a name="alpha-wert_chart"><h2>&#945; Alpha-Wert (Chart)</h2></a>
        <p><b>Aktivieren:</b> Checkbox <b>Alpha</b> im Zoom-Modus.</p>
        <p>Jensen's Alpha = risikobereinigte Überrendite vs. S&amp;P 500. <b>Positiv = Outperformance</b>, Negativ = Underperformance.
        Basis: tägliche Renditen, annualisiert. Risikofreier Zins: 5 % p.a.</p>
        <div class="tip">&#128270; <b>Vertiefung:</b> &rarr; <a href="#alpha-vertiefung">Alpha – Analyse-Vertiefung</a></div>

        <a name="zielkurs"><h2>&#127919; Zielkurs-Linie</h2></a>
        <p>Orange gestrichelte Linie = durchschnittlicher Analysten-Zielkurs (Quelle: Yahoo Finance).</p>

        <a name="analysten-info"><h2>&#128678; Analysten-Info</h2></a>
        <p>Klicke auf <b>i Info</b> in einem Chart:</p>
        <ul>
            <li>Analysten-Empfehlung (5-Stufen-Ampel: Stark Kaufen bis Stark Verkaufen)</li>
            <li>Zielkurs-Bandbreite (Min / Durchschnitt / Max)</li>
            <li>Beta, Alpha, Sharpe-Ratio auf einen Blick</li>
            <li><b>News-Score:</b> Automatische Stimmungsanalyse aktueller Schlagzeilen</li>
        </ul>

        <a name="firmeninfo"><h2>&#127970; Firmeninfo</h2></a>
        <p>Im Analysten-Dialog: <b>Firmeninfo</b> &rarr; CEO, Mitarbeiterzahl, Marktkapitalisierung,
        Umsatz, Gewinn (TTM), Firmenbeschreibung.</p>
        <div class="tip">Exportierbar als PDF!</div>

        <a name="finanzdaten"><h2>&#128202; Finanzdaten</h2></a>
        <p>Im Analysten-Dialog: <b>Finanzdaten</b> &rarr; GuV, Bilanz, Cashflow &mdash;
        umschaltbar zwischen <b>quartalsweise</b> und <b>jährlich</b>.</p>

        <a name="finment"><h2>&#128269; Finment</h2></a>
        <p>Der <b>Finment</b>-Button öffnet eine externe Aktienanalyse von
        <a href="https://finment.com">finment.com</a> für das aktuell angezeigte Symbol.</p>
        <ul>
            <li>Öffnet sich in einem <b>eingebetteten Browser-Fenster</b> direkt in der App</li>
            <li>Die passende Seite wird anhand des Symbols <b>automatisch gesucht</b></li>
        </ul>
        <div class="tip"><b>Tipp:</b> Finment eignet sich besonders für deutsche und europäische Aktien.</div>
        <div class="warning"><b>Hinweis:</b> Finment ist ein externer Dienst – für unbekannte Symbole kann die Seite leer bleiben.</div>

        <a name="vergleich"><h2>&#9878; Vergleich</h2></a>
        <p>Mehrere Aktien als Overlay übereinanderlegen &mdash; ideal um relative Performance zu vergleichen.</p>

        <a name="performance-diagramm"><h2>&#128202; Performance-Diagramm</h2></a>
        <p>Alle aktiven Charts als Balkendiagramm. Hover-Tooltip zeigt Symbol und Prozent.</p>

        <a name="excel_export"><h2>&#128202; Excel Export (Charts)</h2></a>
        <p>Exportiert Performance aller Charts als Excel-Datei mit farbcodierten Werten und nativem 3D-Säulendiagramm.</p>

        <a name="auto-refresh"><h2>&#128260; Auto-Refresh</h2></a>
        <p>Automatische Aktualisierung: <b>Aus &bull; 30 Sek &bull; 1 Min &bull; 5 Min</b><br>
        Manuell: Alle-Button für sofortige Aktualisierung aller Charts.</p>

        <a name="favoriten"><h2>&#11088; Favoriten</h2></a>
        <p><b>Hinzufügen:</b> Favoriten hinzufügen im Header &bull;
        <b>Nutzen:</b> Stern-Button direkt im Chart für schnellen Symbolwechsel.</p>

        <a name="watchlist"><h2>&#128203; Watchlist</h2></a>
        <p>Die Watchlist ermöglicht das schnelle Vergleichen der Performance von bis zu <b>50 Symbolen</b> in einem einzigen Balkendiagramm.</p>
        <h3>Öffnen</h3>
        <p>Hauptmenü &rarr; <b>Watchlist</b>-Button in der Toolbar.</p>
        <h3>Symbole verwalten</h3>
        <ul>
            <li><b>Symbol eingeben + Enter</b> oder <b>&#10133; Hinzufügen</b></li>
            <li><b>&#128190; Speichern / &#128194; Laden</b>: Watchlist als JSON-Datei sichern und laden</li>
        </ul>
        <h3>Berechnen</h3>
        <p>Zeitraum wählen &rarr; <b>&#9654; Berechnen</b> klicken. Alle Symbole werden parallel abgerufen.</p>
        <h3>Export</h3>
        <p><b>&#128228; Exportieren</b>: Ergebnisse als PDF, Excel (.xlsx) oder OpenDocument (.ods) speichern.</p>
        <div class="tip"><b>Tipp:</b> Die Watchlist wird automatisch gespeichert und beim nächsten Start wiederhergestellt.</div>

        <a name="währungsrechner"><h2>&#128178; Währungsrechner</h2></a>
        <ul>
            <li>23 Fiat-Währungen inkl. BTC, ETH, XRP, SOL</li>
            <li>Edelmetalle &amp; Rohstoffe: <b>XAU (Gold/oz), XAG (Silber/oz), XPT (Platin/oz), XPD (Palladium/oz), XCU (Kupfer/lb)</b></li>
            <li>Echtzeit-Kurse via Yahoo Finance (ca. 15 Min. Verzögerung)</li>
        </ul>

        <a name="portfolio_übersicht"><h2>&#128188; Portfolio Übersicht</h2></a>
        <p>Alle Positionen mit Echtzeit-Kursen auf einen Blick:</p>
        <ul>
            <li>Spalten: Symbol &bull; Anzahl &bull; Kaufkurs &Oslash; &bull; Kaufwert &bull; Akt. Kurs &bull; Akt. Wert &bull; G&amp;V &bull; G&amp;V% &bull; Anteil% &bull; Perf-Beitrag% &bull; Sektor-Beitrag% &bull; Sektor &bull; Sub-Industry</li>
            <li>Darstellungswährung wählbar: <b>USD &bull; CHF &bull; EUR &bull; GBP</b></li>
            <li>Klick auf Symbol &rarr; Chart in neuem Fenster</li>
        </ul>

        <a name="rohstoffe"><h2>&#127775; Rohstoffe</h2></a>
        <p>Stock Monitor unterstützt <b>5 Rohstoffe</b> als eigene Anlageklasse neben Aktien und Krypto.</p>
        <table>
            <tr><th>Symbol</th><th>Rohstoff</th><th>Einheit</th></tr>
            <tr><td><code>XAU</code></td><td>Gold</td><td>Unze (oz)</td></tr>
            <tr><td><code>XAG</code></td><td>Silber</td><td>Unze (oz)</td></tr>
            <tr><td><code>XPT</code></td><td>Platin</td><td>Unze (oz)</td></tr>
            <tr><td><code>XPD</code></td><td>Palladium</td><td>Unze (oz)</td></tr>
            <tr><td><code>XCU</code></td><td>Kupfer</td><td>Pound (lb)</td></tr>
        </table>

        <a name="portfolio_diagramme"><h2>&#128202; Portfolio Diagramme</h2></a>
        <p>Über die Schaltflächen in der Portfolio-Übersicht lassen sich vier verschiedene Diagramme öffnen:</p>
        <ul>
            <li><b>🥧 Positionen / Anteil je Aktie:</b> Kuchendiagramm mit der prozentualen Gewichtung jeder Position. Hover-Tooltip zeigt Symbol, Wert und Anteil. Ideal um auf einen Blick zu sehen, ob das Portfolio zu stark auf einzelne Titel konzentriert ist.</li>
            <li><b>📊 Performance-Vergl. / Performance-Vergleich:</b> Balkendiagramm aller Positionen sortiert nach Performance. &rarr; <a href="#performance_vergleich">Performance-Vergleich</a></li>
            <li><b>🏭 Branchen / Branchen-Verteilung:</b> Zeigt die Aufteilung des Portfolios nach GICS-Sektoren. &rarr; <a href="#portfolio_branchen">Branchen-Verteilung</a></li>
            <li><b>🌍 Regionen / Regionen-Verteilung:</b> Geographische Verteilung nach Kontinent. &rarr; <a href="#portfolio_regionen">Regionen-Verteilung</a></li>
            <li><b>📉 Indizes / Indexvergleich:</b> Performance der 20 wichtigsten Börsenindizes weltweit im Balkendiagramm. &rarr; <a href="#indexvergleich">Indexvergleich</a></li>
        </ul>

        <a name="performance_vergleich"><h2>&#128202; Performance-Vergleich</h2></a>
        <p>Balkendiagramm aller Portfolio-Positionen sortiert nach Performance – grüne Balken im Plus, rote im Minus.</p>
        <ul>
            <li>Zeitraum frei wählbar (1M / 3M / 6M / YTD / 1J / 2J / 5J / Max / Seit Kauf)</li>
            <li>Hover-Tooltip zeigt Firmenname; bei Balkens am rechten Rand erscheint Tooltip links</li>
            <li>Krypto und Rohstoffe ein-/ausblendbar</li>
            <li><b>p.a.-Ansicht (CAGR):</b> Aktivieren für annualisierte Rendite seit Kauf &mdash; Zeitraum wird automatisch auf <i>Seit Kauf (Einstand)</i> gesetzt und gesperrt
                <ul>
                    <li><b>Filter ≥ 1 Jahr Haltedauer:</b> Erscheint nur in p.a.-Ansicht &mdash; blendet Positionen unter 1 Jahr aus (CAGR unter 1 Jahr wenig vergleichbar), standardmässig aktiv</li>
                    <li>Statuszeile zeigt Anzahl Positionen <span style="color:green">im Plus</span> und <span style="color:red">im Minus</span>; bei aktivem Filter: <i>X von Y Positionen (≥1J)</i></li>
                </ul>
            </li>
        </ul>
        <div class="tip"><b>Tipp:</b> Die p.a.-Ansicht (CAGR) macht Positionen mit unterschiedlicher Haltedauer direkt vergleichbar – eine Aktie mit +200% in 4 Jahren hat p.a. ~31%, eine mit +50% in 6 Monaten wäre hochgerechnet +125% p.a., aber weniger aussagekräftig.</div>

        <a name="portfolio_performance"><h2>&#128200; Portfolio Performance (TWR/MWR)</h2></a>
        <div class="new">Feature: Zeitgewichtete Rendite</div>
        <ul>
            <li><b>TWR:</b> Eliminiert den Einfluss von Ein-/Auszahlungen &mdash; zeigt reine Investment-Performance</li>
            <li><b>MWR (XIRR):</b> Berücksichtigt Timing der Käufe &mdash; zeigt persönliche Rendite</li>
            <li>Benchmark-Vergleich: S&amp;P 500, NASDAQ 100, MSCI World, SMI, DAX u.a.</li>
        </ul>

        <a name="monte-carlo"><h2>&#127922; Monte Carlo Simulation</h2></a>
        <div class="new">Feature: Portfolio Zukunftsszenarien</div>
        <p>Die Monte Carlo Simulation berechnet <b>tausende mögliche Zukunftsszenarien</b> für dein Portfolio –
        basierend auf der historischen Volatilität und Rendite deiner Positionen.</p>
        <ul>
            <li><b>Zeithorizont:</b> 1, 3, 5, 10, 15, 20, 25 oder 30 Jahre wählbar</li>
            <li><b>Szenarien:</b> 500 bis 10 000 Simulationen (Geometric Brownian Motion)</li>
            <li><b>Farbige Bänder:</b> 10. / 25. / 50. (Median) / 75. / 90. Perzentil</li>
            <li><b>Tabelle:</b> Portfoliowert in USD pro Szenario am Enddatum</li>
        </ul>
        <div class="tip">&#128270; <b>Vertiefung:</b> Was genau ist eine Monte Carlo Simulation? &rarr;
        <a href="#monte-carlo-vertiefung">Monte Carlo – Vertiefung</a></div>
        <div class="warning">&#9888; Keine Prognose! Die Simulation basiert auf Vergangenheitsdaten und ist <b>keine Anlageberatung</b>.</div>

        <a name="ecy"><h2>&#128202; Excess CAPE Yield (ECY)</h2></a>
        <div class="new">Feature: Marktbewertungsindikator</div>
        <p>Der <b>Excess CAPE Yield (ECY)</b> zeigt auf einen Blick, ob der US-Aktienmarkt (S&amp;P 500)
        im Vergleich zu sicheren Staatsanleihen attraktiv oder teuer bewertet ist.</p>
        <ul>
            <li><b>Formel:</b> ECY = Gewinnrendite (1/CAPE × 100) − realer 10J-Anleiheziins (TIPS)</li>
            <li><b>Ampel:</b> 🟢 &gt;3% attraktiv · 🟡 1–3% neutral · 🟠 0–1% erhöht · 🔴 &lt;0% teuer</li>
            <li><b>Historischer Chart:</b> ECY seit 1993 mit farbigen Bewertungszonen</li>
            <li><b>Datenquelle:</b> Yahoo Finance (^GSPC, ^TNX, RINF) – bereits in der App integriert, kein API-Key</li>
        </ul>
        <div class="tip">&#128270; <b>Vertiefung:</b> Was bedeutet ECY konkret, und wie interpretiere ich die Ampel? &rarr;
        <a href="#ecy-vertiefung">ECY – Vertiefung</a></div>
        <div class="warning">&#9888; ECY ist ein <b>Marktindikator</b>, kein Portfolio-Indikator. Er sagt nichts über deine einzelnen Positionen aus und ist <b>keine Anlageberatung</b>.</div>


        <a name="alpha-analyse"><h2>&#945; Alpha-Analyse</h2></a>
        <ul>
            <li>Jensen's Alpha des <b>gesamten Portfolios</b> (gewichtet nach Marktwert)</li>
            <li><b>Vier Abschnitte:</b> Gesamt &bull; Nur Aktien/ETFs &bull; Nur Krypto &bull; Nur Rohstoffe</li>
        </ul>

        <a name="beta-analyse"><h2>&#946; Beta-Analyse</h2></a>
        <ul>
            <li>Gewichtetes Portfolio-Beta (Gesamt / Aktien / Krypto / Rohstoffe)</li>
            <li><b>Gold hat typischerweise negatives Beta</b> – steigt wenn Aktien fallen</li>
        </ul>

        <a name="sharpe-ratio"><h2>&#963; Sharpe-Ratio</h2></a>
        <ul>
            <li>Rendite pro Risikoeinheit (Standardabweichung), annualisiert</li>
            <li>Faustregel: &gt; 1.0 = gut &bull; &gt; 2.0 = sehr gut &bull; &lt; 0 = schlechter als risikofreie Anlage</li>
        </ul>
        <div class="warning">Alle Kennzahlen basieren auf historischen Daten. Keine Anlageberatung!</div>

        <a name="ai-balance"><h2>&#9878; AI-Balance (Rebalancing)</h2></a>
        <p>Zeigt wie das Portfolio aussehen würde, wenn Positionsgrößen der Performance folgen.</p>
        <ul>
            <li>Zeitraum wählbar für die Performance-Basis</li>
            <li>Tabelle: Rang &bull; Symbol &bull; Perf.% &bull; Score &bull; Ist-Wert &rarr; Soll-Wert &bull; Aktion</li>
            <li>Aktionen: Halten &bull; Kaufen +X Stk. &bull; Verkaufen -X Stk.</li>
        </ul>
        <div class="warning">Dies ist kein Anlageratschlag. Vergangene Performance garantiert keine zukünftige Entwicklung.</div>

        <a name="zielgerichtetes-rebalancing"><h2>&#127919; Zielgerichtetes Rebalancing</h2></a>
        <p>Mit dem <b>🎯 Zielgerichtet</b>-Button und der danebenstehenden Checkbox lässt sich das
        AI-Balance-Rebalancing auf eine gezielte Teilmenge des Portfolios einschränken – mit optionaler
        Ziel-Gewichtung pro Währung und Sektor.</p>
        <h3>Checkbox – Filter aktivieren/deaktivieren</h3>
        <p>Die Checkbox <b>☑ Zielgerichtet</b> schaltet den Filter ein oder aus. Der gespeicherte
        Filter bleibt erhalten auch wenn die Checkbox deaktiviert ist – so kann man den Filter
        temporär ausschalten ohne ihn zu verlieren. Der Button leuchtet <b style="color:#e67e22">orange</b>
        wenn Filter aktiv und eingeschaltet, <b style="color:#aaa">grau</b> wenn gespeichert aber
        deaktiviert.</p>
        <h3>Filter-Kriterien</h3>
        <ul>
            <li><b>Währungen:</b> Nur im Portfolio vorhandene Währungen werden angeboten (z.&nbsp;B. USD, CHF, EUR).
            Pro Währung kann ein <b>Ziel-% </b> eingegeben werden.</li>
            <li><b>GICS-Sektoren (Ebene 1):</b> Die im Portfolio vertretenen GICS-Hauptsektoren.
            Pro Sektor ebenfalls optional ein <b>Ziel-%</b>.</li>
        </ul>
        <h3>Ziel-%-Gewichtung</h3>
        <p>Das optionale %-Feld gibt vor, wie viel des gefilterten Gesamtkapitals einer Währung
        oder einem Sektor zugeteilt werden soll. Die Summe pro Gruppe sollte <b>100%</b> ergeben
        – die App zeigt die aktuelle Summe in <span style="color:#27ae60">Grün</span> (=100%) oder
        <span style="color:#e67e22">Orange</span> (≠100%) an und normalisiert automatisch.</p>
        <table>
            <tr><th>Beispiel</th><th>Effekt</th></tr>
            <tr><td>USD 60%, CHF 40%</td><td>60% des Kapitals in USD-Positionen, 40% in CHF</td></tr>
            <tr><td>Technology 50%, Healthcare 50%</td><td>Gleiche Aufteilung auf zwei Sektoren</td></tr>
            <tr><td>Kein % eingegeben</td><td>Gleichmässige Verteilung nach AI-Score</td></tr>
        </table>
        <h3>Logik</h3>
        <p>Es werden nur Positionen berücksichtigt, die <i>beide</i> Bedingungen erfüllen:
        gewählte Währung <b>UND</b> gewählter Sektor (AND-Logik). Wenn sowohl Währungs-% als auch
        Sektor-% gesetzt sind, wird der Durchschnitt beider Gewichtungen für ein Symbol verwendet.</p>
        <h3>Speicherung</h3>
        <p>Die Filtereinstellungen werden <b>pro Portfolio</b> gespeichert. Mit <b>↺ Zurücksetzen</b>
        werden alle Filter entfernt und das vollständige Portfolio wieder berücksichtigt.</p>
        <div class="tip"><b>Tipp:</b> CHF-Anteil auf 30% erhöhen? Wähle CHF=30%, USD=70% bei den
        Währungen – das Rebalancing schlägt dann vor wie du dieses Ziel erreichst.</div>
        <div class="warning">Ein sehr enger Filter (z.&nbsp;B. nur 1–2 Positionen) kann zu
        unausgewogenen Rebalancing-Vorschlägen führen.</div>

        <a name="portfolio-vergleich"><h2>&#128202; Portfolio-Vergleich</h2></a>
        <div class="new">Feature: Portfolios grafisch vergleichen</div>
        <p>Stellt bis zu <b>4 gespeicherte Portfolios</b> gleichzeitig nebeneinander dar – als
        Balken- oder Liniendiagramm. So lassen sich verschiedene Anlagestrategien oder
        Zeitpunkte direkt vergleichen.</p>
        <h3>Bedienung</h3>
        <ul>
            <li><b>Portfolios hinzufügen:</b> Aus der linken Liste auswählen und mit dem
            <b>+ Hinzufügen</b>-Button in die Vergleichsliste übernehmen. Jedes Portfolio
            benötigt sein Passwort.</li>
            <li><b>Portfolios entfernen:</b> In der rechten Liste auswählen und mit
            <b>– Entfernen</b> herausnehmen.</li>
            <li><b>Währung:</b> Alle Werte werden in die gewählte Währung (USD, CHF, EUR, GBP)
            umgerechnet, damit die Portfolios vergleichbar sind.</li>
        </ul>
        <h3>Diagramm-Typen</h3>
        <ul>
            <li><b>📊 Balkendiagramm:</b> Zeigt den aktuellen Gesamtwert jedes Portfolios als
            Balken – ideal für einen schnellen Wertvergleich.</li>
            <li><b>📈 Liniendiagramm:</b> Zeigt die Wertentwicklung über die Zeit – ideal um
            zu sehen welches Portfolio besser performt hat.</li>
        </ul>
        <h3>Export</h3>
        <p>Die Vergleichsdaten können über den <b>📤 Exportieren</b>-Button als Excel/CSV
        gespeichert werden.</p>
        <div class="tip"><b>Tipp:</b> Vergleiche z.&nbsp;B. dein aktuelles Portfolio mit
        einem gespeicherten AI-Balance-Vorschlag – so siehst du konkret was sich geändert
        hätte.</div>
        <div class="warning">Mindestens 2 gespeicherte Portfolios (.smpf-Dateien) müssen
        vorhanden sein um den Vergleich zu nutzen.</div>

        <a name="dividenden"><h2>&#128181; Dividenden</h2></a>
        <div class="new">Feature: Dividenden-Übersicht</div>
        <p>Zeigt historische und prognostizierte Dividenden aller Portfolio-Positionen.</p>

        <a name="dividenden-details"><h2>&#128176; Dividenden Details</h2></a>
        <p>Detailansicht je Aktie mit Dividendenhistorie, CAGR, Stabilitätskennzahl und Aristokrat-Titeln.</p>

        <a name="ki-analyse"><h2>&#129504; KI-Analyse</h2></a>
        <div class="new">Feature: KI-gestützte Portfolio-Analyse</div>
        <p>Sendet Portfolio-Daten an Google Gemini und erhält eine strukturierte Analyse.</p>
        <div class="warning">KI-Analysen sind keine Anlageberatung und können Fehler enthalten.</div>

        <a name="rsi-analyse"><h2>&#128200; RSI – Analyse-Vertiefung</h2></a>
        <p>Der <b>Relative Strength Index (RSI)</b> wurde 1978 von J. Welles Wilder entwickelt.
        Er misst das Verhältnis von durchschnittlichen Gewinntagen zu Verlusttagen der letzten
        <b>14 Perioden</b> und normiert das Ergebnis auf eine Skala von 0–100.</p>
        <p><b>Formel:</b> <code>RSI = 100 − (100 / (1 + RS))</code><br>
        wobei <code>RS = Ø Gewinne der letzten 14 Tage / Ø Verluste der letzten 14 Tage</code></p>
        <div class="tip"><b>Praxis-Tipp:</b> RSI unter 30 in einem langfristigen Aufwärtstrend ist historisch
        einer der zuverlässigsten Einstiegspunkte für langfristige Anleger.</div>

        <a name="bb-analyse"><h2>&#128200; Bollinger-Bänder – Analyse-Vertiefung</h2></a>
        <p><b>Bollinger-Bänder</b> umrahmen den Kurschart mit MA20 ± 2 Standardabweichungen.</p>
        <table>
            <tr><th>Linie</th><th>Berechnung</th><th>Farbe</th></tr>
            <tr><td>Mittellinie (SMA20)</td><td>20-Tage Simple Moving Average</td><td>Blau gestrichelt</td></tr>
            <tr><td>Oberes Band</td><td>SMA20 + 2 × Standardabweichung</td><td>Cyan</td></tr>
            <tr><td>Unteres Band</td><td>SMA20 − 2 × Standardabweichung</td><td>Orange</td></tr>
        </table>
        <div class="tip"><b>Praxis-Tipp:</b> BB + RSI kombiniert: Kurs am unteren Band <i>und</i> RSI unter 30
        erhöht die Trefferquote erheblich.</div>

        <a name="dd-analyse"><h2>&#128201; Drawdown – Analyse-Vertiefung</h2></a>
        <p>Der <b>Drawdown</b> misst den prozentualen Rückgang vom rollierenden Höchststand bis zum aktuellen Tiefpunkt.</p>
        <div class="tip"><b>Praxis-Tipp:</b> Bevor du eine Position kaufst, schau dir den Max-DD im
        5-Jahres-Zeitraum an. Frage dich: <i>Hätte ich einen −50 %-Drawdown gehalten?</i></div>

        <a name="alpha-vertiefung"><h2>&#945; Alpha – Analyse-Vertiefung</h2></a>
        <p><b>Jensen's Alpha</b> misst ob eine Aktie <b>mehr Rendite erzielt als das Risiko rechtfertigt</b>.</p>
        <p><b>Formel:</b> <code>Alpha = Tatsächliche Rendite − (Rf + β × (Rm − Rf))</code></p>
        <div class="tip"><b>Praxis-Tipp:</b> Positives Alpha über 1–2 Jahre kann bedeuten, dass du eine gute Aktie
        gewählt hast – oder dass du in einem Sektor übergewichtet bist der gerade im Trend liegt.</div>

        <a name="beta-vertiefung"><h2>&#946; Beta – Analyse-Vertiefung</h2></a>
        <p><b>Beta</b> misst die Sensitivität einer Aktie gegenüber Marktbewegungen.</p>
        <p><b>Formel:</b> <code>&beta; = Kovarianz(Aktie, Markt) / Varianz(Markt)</code></p>
        <div class="tip"><b>Praxis-Tipp:</b> Beta &lt; 0.5 in Kombination mit positivem Alpha ist der
        Heilige Gral der Aktienauswahl – defensiv und trotzdem outperformend.</div>

        <a name="sharpe-vertiefung"><h2>&#963; Sharpe-Ratio – Analyse-Vertiefung</h2></a>
        <p><b>Formel:</b> <code>Sharpe = (Rp − Rf) / σp × √252</code></p>
        <h3>Grenzen der Sharpe-Ratio</h3>
        <ul>
            <li><b>Normalverteilungs-Annahme:</b> Aufwärts- und Abwärtsvolatilität werden gleich behandelt</li>
            <li><b>Fat Tails:</b> Seltene extreme Verluste werden unterschätzt</li>
            <li><b>Zeitraum-Abhängigkeit:</b> Im Bullenmarkt sehen fast alle Aktien gut aus</li>
        </ul>
        <div class="tip"><b>Praxis-Tipp:</b> Vergleiche die Sharpe-Ratio immer innerhalb derselben Anlageklasse.</div>

        <a name="monte-carlo-vertiefung"><h2>&#127922; Monte Carlo – Vertiefung</h2></a>
        <h3>Was ist eine Monte Carlo Simulation?</h3>
        <p>Der Name kommt vom berühmten Spielkasino in Monaco – weil das Verfahren auf <b>Zufallszahlen</b>
        basiert, ähnlich wie ein Roulettekessel. Die Methode wurde in den 1940er-Jahren von Mathematikern
        für die Atomforschung entwickelt und wird heute in Finanz, Physik und Ingenieurwesen eingesetzt.</p>
        <p>In Stock Monitor berechnet die Simulation tausende mögliche Kurspfade für dein Portfolio –
        unter Verwendung des <b>Geometric Brownian Motion (GBM)</b> Modells, dem Industriestandard für
        Aktienkurssimulationen.</p>
        <h3>Wie funktioniert Geometric Brownian Motion?</h3>
        <p>Jeder Handelstag wird als kleiner Zufallsschritt simuliert. Die Richtung und Grösse des
        Schritts hängen von zwei Grössen ab:</p>
        <table>
            <tr><th>Parameter</th><th>Woher?</th><th>Bedeutung</th></tr>
            <tr><td><b>&#956; (Drift)</b></td><td>Historische Jahresrendite des Portfolios</td><td>Erwartete Richtung</td></tr>
            <tr><td><b>&#963; (Volatilität)</b></td><td>Historische Standardabweichung der Tagesrenditen</td><td>Schwankungsbreite</td></tr>
        </table>
        <p><b>Formel:</b> <code>S(t+1) = S(t) &times; exp( (&#956; &minus; &#189;&#963;&sup2;) &Delta;t + &#963; &radic;&Delta;t &times; Z )</code><br>
        wobei <code>Z</code> eine normalverteilte Zufallszahl ist und <code>&Delta;t = 1/252</code> (ein Handelstag).</p>
        <h3>Was zeigen die farbigen Bänder?</h3>
        <table>
            <tr><th>Band</th><th>Bedeutung</th></tr>
            <tr><td><b>10. Perzentil</b> (rot)</td><td>In 10% aller Szenarien war es schlechter als dieser Wert</td></tr>
            <tr><td><b>25. Perzentil</b> (orange)</td><td>Unteres Viertel der Szenarien</td></tr>
            <tr><td><b>50. Perzentil / Median</b> (blau)</td><td>Genau die Hälfte der Szenarien lag darüber, die Hälfte darunter</td></tr>
            <tr><td><b>75. Perzentil</b> (hellgrün)</td><td>Oberes Viertel der Szenarien</td></tr>
            <tr><td><b>90. Perzentil</b> (grün)</td><td>In 10% aller Szenarien war es besser als dieser Wert</td></tr>
        </table>
        <h3>Grenzen der Simulation</h3>
        <ul>
            <li><b>Vergangenheitsbasiert:</b> Drift und Volatilität stammen aus historischen Daten – die Zukunft kann anders sein</li>
            <li><b>Keine Krisen-Modellierung:</b> GBM unterschätzt seltene Extremereignisse (Fat Tails / Black Swans)</li>
            <li><b>Keine Korrelationen:</b> Die Simulation verwendet Portfolio-Gesamtrenditen, keine Einzeltitel-Korrelationen</li>
        </ul>
        <div class="tip"><b>Praxis-Tipp:</b> Nutze die Simulation für die <b>langfristige Perspektive</b> –
        10 Jahre zeigen sehr viel mehr Streuung als 1 Jahr. Das ist normal und zeigt, warum ein langer
        Anlagehorizont so wichtig ist: Der Median steigt, aber die Bänder werden breiter.</div>
        <div class="warning">&#9888; Die Monte Carlo Simulation ist ein <b>Planungshilfsmittel</b>, keine Prognose.
        Vergangene Volatilität garantiert keine zukünftige Entwicklung. Keine Anlageberatung.</div>

        <a name="ecy-vertiefung"><h2>&#128202; ECY – Vertiefung</h2></a>
        <h3>Was steckt hinter dem Excess CAPE Yield?</h3>
        <p>Der ECY wurde vom Ökonomen <b>Robert Shiller</b> (Nobelpreisträger 2013) und seinem Team entwickelt
        und im <i>Financial Analysts Journal</i> publiziert. Er kombiniert zwei bekannte Grössen:</p>
        <ul>
            <li><b>CAPE</b> (Cyclically Adjusted Price-to-Earnings Ratio, auch «Shiller-KGV»):
            Das Kurs-Gewinn-Verhältnis des S&amp;P 500, geglättet über <b>10 Jahre</b> inflationsbereinigter
            Gewinne. Glättet Konjunkturzyklen und kurzfristige Gewinnausschläge heraus.</li>
            <li><b>10J TIPS-Rendite</b> (Treasury Inflation-Protected Securities):
            Der <b>reale</b> (inflationsbereinigte) Zinssatz 10-jähriger US-Staatsanleihen –
            der «risikolose» Vergleichsmassstab.</li>
        </ul>
        <p>Die <b>Gewinnrendite</b> (1/CAPE × 100%) ist das Gegenteil des KGV: ein CAPE von 25 entspricht
        einer Gewinnrendite von 4%. Zieht man davon den realen Anleihezins ab, erhält man den <b>Excess</b>
        – die Mehrrendite, die Aktien gegenüber sicheren Anleihen bieten (oder eben nicht).</p>

        <h3>Wie lese ich die Ampel?</h3>
        <table>
            <tr><th>Signal</th><th>ECY-Bereich</th><th>Bedeutung</th></tr>
            <tr><td>🟢 Attraktiv</td><td>&gt; 3%</td><td>Aktien bieten eine deutliche Prämie über Anleihen. Historisch günstige Einstiegsphasen (z.B. 2009, 2012).</td></tr>
            <tr><td>🟡 Neutral</td><td>1–3%</td><td>Aktien sind leicht attraktiver als Anleihen. «Normale» Bewertungszone.</td></tr>
            <tr><td>🟠 Erhöht</td><td>0–1%</td><td>Aktien bieten kaum Prämie. Anleihen werden relativ interessanter.</td></tr>
            <tr><td>🔴 Teuer</td><td>&lt; 0%</td><td>Anleihen bieten mehr reale Rendite als Aktien. Historisch selten (zuletzt 2021–2022 kurz).</td></tr>
        </table>

        <h3>&#128721; Was der ECY <u>nicht</u> bedeutet – Panik vermeiden</h3>
        <div class="warning">
        Ein <b>negativer ECY</b> bedeutet <b>nicht</b>, dass der Markt morgen abstürzt – und ein positiver ECY
        ist kein Kaufbefehl. Der ECY ist ein <b>mittelfristiger Orientierungswert</b> (Horizont: 5–10 Jahre),
        kein kurzfristiger Timing-Indikator. Märkte können jahrelang «teuer» bleiben und weiter steigen.
        <br><br>
        <b>Beispiel:</b> Der ECY war von 2015 bis 2021 phasenweise niedrig oder negativ – dennoch stieg der
        S&amp;P 500 in dieser Zeit erheblich. Ein hoher ECY (wie 2009) signalisierte rückblickend einen
        günstigen Einstiegspunkt, aber niemand wusste das damals mit Sicherheit.
        </div>

        <h3>Für wen ist der ECY nützlich?</h3>
        <p>Der ECY ist besonders relevant für <b>langfristige Investoren</b>, die ihr Portfolio strategisch
        ausrichten möchten – zum Beispiel bei der Frage, ob eine Übergewichtung von Aktien vs. Anleihen
        sinnvoll ist. Für kurzfristiges Trading ist er ungeeignet.</p>
        <p>Zusammen mit der <b>Monte Carlo Simulation</b> ergibt sich ein rundes Bild: MC zeigt,
        <i>wie viel</i> dein Portfolio unter verschiedenen Szenarien wachsen könnte – ECY zeigt,
        <i>ob der Markt aktuell günstig oder teuer</i> für langfristige Anlagen ist.</p>
        <div class="tip"><b>Fazit:</b> ECY = ein weiteres Puzzlestück für informierte Entscheidungen.
        Kein Orakel, kein Alarmsignal – sondern ein nüchterner Vergleich zweier Anlageklassen.</div>


        <a name="gics-vertiefung"><h2>&#127981; GICS – Vertiefung</h2></a>
        <p><b>GICS</b> steht für <b>Global Industry Classification Standard</b> – ein weltweiter Standard zur Einteilung von börsenkotierten Unternehmen in Branchen. Entwickelt 1999 von <b>S&amp;P Global</b> und <b>MSCI</b>, wird er heute von Börsen, Fondsmanagern und Finanzmedien weltweit verwendet. Praktisch jede Aktie ist einem der <b>11 Sektoren</b> zugeordnet:</p>
        <table>
            <tr><th>Sektor</th><th>Was steckt dahinter?</th><th>Beispiele</th></tr>
            <tr><td><b>Information Technology</b></td><td>Software, Hardware, Halbleiter, IT-Dienste</td><td>Apple, Microsoft, NVIDIA, SAP</td></tr>
            <tr><td><b>Financials</b></td><td>Banken, Versicherungen, Vermögensverwaltung</td><td>JPMorgan, UBS, Allianz, Zurich</td></tr>
            <tr><td><b>Health Care</b></td><td>Pharma, Medtech, Biotechnologie, Krankenhäuser</td><td>Novartis, Roche, J&amp;J, Medtronic</td></tr>
            <tr><td><b>Consumer Discretionary</b></td><td>Nicht-lebensnotwendige Konsumgüter – Autos, Luxus, Handel</td><td>Amazon, Tesla, LVMH, BMW</td></tr>
            <tr><td><b>Industrials</b></td><td>Maschinenbau, Luft-/Raumfahrt, Transport, Rüstung</td><td>Siemens, Caterpillar, ABB, Boeing</td></tr>
            <tr><td><b>Communication Services</b></td><td>Telekommunikation, soziale Medien, Streaming</td><td>Alphabet, Meta, Netflix, Swisscom</td></tr>
            <tr><td><b>Consumer Staples</b></td><td>Lebensnotwendige Konsumgüter – Nahrung, Getränke, Haushalt</td><td>Nestlé, Procter &amp; Gamble, Coca-Cola</td></tr>
            <tr><td><b>Energy</b></td><td>Öl, Gas, erneuerbare Energien, Raffinerien</td><td>ExxonMobil, Shell, TotalEnergies</td></tr>
            <tr><td><b>Materials</b></td><td>Rohstoffe, Chemie, Bergbau, Papier</td><td>BASF, Rio Tinto, Glencore, Sika</td></tr>
            <tr><td><b>Real Estate</b></td><td>Immobilienfonds (REITs), Immobilienverwaltung</td><td>American Tower, Swiss Prime Site</td></tr>
            <tr><td><b>Utilities</b></td><td>Strom, Wasser, Gas – regulierte Versorger</td><td>NextEra Energy, BKW, E.ON</td></tr>
        </table>
        <h3>Warum ist Branchendiversifikation wichtig?</h3>
        <p>Verschiedene Sektoren reagieren unterschiedlich auf Konjunkturzyklen und Ereignisse. <b>Defensive Sektoren</b> (Consumer Staples, Health Care, Utilities) sind krisenresistenter – Menschen kaufen weiterhin Lebensmittel und Medikamente. <b>Zyklische Sektoren</b> (Consumer Discretionary, Industrials) laufen in Boomphasen besser, verlieren in Abschwüngen stärker. Wer z.B. 70% in Tech-Aktien hält, ist sehr gut aufgestellt wenn KI boomt – aber stark gefährdet wenn der Sektor korrigiert wie 2022.</p>
        <div class="tip"><b>Faustregel:</b> Kein einzelner Sektor sollte dauerhaft mehr als 30–35% des Portfolios ausmachen. Die Branchen-Ansicht in Stock Monitor macht Klumpenrisiken auf einen Blick sichtbar.</div>

        <a name="portfolio_branchen"><h2>&#127981; Branchen-Verteilung</h2></a>
        <p>Öffnen über <b>🏭 Branchen</b> in der Portfolio-Übersicht. Zeigt wie das Portfolio auf verschiedene Wirtschaftsbereiche verteilt ist – umschaltbar zwischen Gewichtung und Performance je Sektor.</p>
        <ul>
            <li>Kuchendiagramm mit Hover-Tooltip (Sektor, Anzahl Positionen, Anteil %)</li>
            <li>Umschalten auf Balkendiagramm zeigt Performance je Sektor im gewählten Zeitraum</li>
            <li>Krypto wird ausgeblendet (hat keinen GICS-Sektor)</li>
        </ul>
        <div class="tip">&#128270; <b>Vertiefung:</b> Was ist GICS, welche 11 Sektoren gibt es und warum ist Branchendiversifikation wichtig? &rarr; <a href="#gics-vertiefung">GICS – Vertiefung</a></div>

        <a name="portfolio_regionen"><h2>&#127758; Regionen-Verteilung</h2></a>
        <p>Öffnen über <b>🌍 Regionen</b> in der Portfolio-Übersicht. Zeigt die geographische Verteilung des Portfolios nach Kontinent und Firmenstandort (Hauptsitz des Unternehmens, nicht Börsenkotierung).</p>
        <ul>
            <li>Kreisdiagramm mit Hover-Tooltip (Region, Anzahl Positionen, Anteil %)</li>
            <li><b>Weltkarte im Browser:</b> Interaktive Karte zeigt Firmensitze als Pins – Klick öffnet Details</li>
        </ul>
        <div class="tip"><b>Tipp:</b> Viele Schweizer und europäische Anleger sind unbewusst stark US-lastig – US-Aktien dominieren die meisten Indizes. Die Regionen-Ansicht hilft, eine gewollte geographische Diversifikation zu kontrollieren.</div>

        <a name="indexvergleich"><h2>&#128202; Indexvergleich</h2></a>
        <div class="new">Feature: Weltweiter Börsenindex-Vergleich</div>
        <p>Öffnen über <b>📉 Indizes</b> in der Portfolio-Übersicht. Zeigt die Performance der <b>20 wichtigsten Börsenindizes</b> weltweit in einem übersichtlichen Balkendiagramm – optional ergänzt um die Performance des eigenen Portfolios.</p>
        <ul>
            <li><b>Enthaltene Indizes:</b>
                <ul>
                    <li><b>USA:</b> S&amp;P 500, NASDAQ 100, Dow Jones, Russell 2000</li>
                    <li><b>Europa:</b> SMI (Schweiz), DAX (Deutschland), EURO STOXX 50, FTSE 100 (UK), CAC 40 (Frankreich)</li>
                    <li><b>Asien/Pazifik:</b> Nikkei 225 (Japan), KOSPI (Südkorea), Hang Seng (Hongkong), Shanghai Composite (China), BSE SENSEX (Indien), ASX 200 (Australien)</li>
                    <li><b>Amerika:</b> Bovespa (Brasilien), TSX Composite (Kanada)</li>
                    <li><b>Global/Schwellenländer:</b> MSCI World, MSCI Emerging Markets, MSCI EM Asia</li>
                </ul>
            </li>
            <li><b>Zeitraum:</b> 1M / 3M / 6M / YTD / 1J / 2J / 5J / <b>10J</b> / Max – frei wählbar</li>
            <li><b>Eigenes Portfolio vergleichen:</b> Checkbox <i>📁 Portfolio anzeigen</i> blendet einen zusätzlichen <b>blauen Balken</b> für das geladene Portfolio ein. Die Performance wird als <b>gewichteter Durchschnitt</b> aller Positionen berechnet (Gewichtung nach aktuellem Marktwert). Checkbox aus = Portfolio ausgeblendet, kein erneuter Datenabruf nötig.</li>
            <li><b>Balkenfarben:</b> 🟢 Grün = positiv · 🔴 Rot = negativ · 🔵 Blau = eigenes Portfolio</li>
            <li>Hover-Tooltip zeigt exakten Prozentwert</li>
            <li>Statuszeile zeigt Anzahl Indizes im Plus/Minus sowie Portfolio-Performance</li>
            <li>Export als PDF / Excel / ODS möglich</li>
        </ul>
        <div class="tip"><b>Tipp:</b> Mit dem 10-Jahres-Zeitraum siehst du, welche Märkte langfristig am stärksten gewachsen sind – und ob dein Portfolio über einem Jahrzehnt besser abgeschnitten hat als der S&amp;P 500 oder MSCI World.</div>

        <a name="administration"><h2>&#9881; Administration</h2></a>
        <p>Zentrale Schaltstelle für alle Portfolio-Verwaltungsaufgaben.</p>
        <h3>Position hinzufügen</h3>
        <p>1. Symbol eingeben &rarr; 2. Kaufdatum &rarr; 3. Stückzahl &rarr; <b>Hinzufügen</b><br>
        Kaufkurs wird automatisch von Yahoo Finance geladen.</p>

        <a name="swissquote_import"><h2>&#128229; Swissquote Import</h2></a>
        <p>In Swissquote: <b>Depot &rarr; Transaktionen &rarr; Export als CSV</b></p>
        <ul>
            <li>Automatische Erkennung von Käufen und Verkäufen</li>
            <li>Verkäufe per <b>FIFO</b> von den ältesten Positionen abgezogen</li>
            <li>Duplikate werden automatisch übersprungen</li>
        </ul>

        <a name="generic_csv_import"><h2>&#128196; Generic CSV Import</h2></a>
        <p>Import von Depotauszügen <i>beliebiger Banken und Broker</i>.</p>
        <table>
            <tr><th>Bank / Broker</th><th>Besonderheit</th></tr>
            <tr><td><b>DeGiro</b></td><td>ISIN wird auto-konvertiert</td></tr>
            <tr><td><b>Flatex</b></td><td>ISIN wird auto-konvertiert</td></tr>
            <tr><td><b>Interactive Brokers</b></td><td>Direkte Ticker-Symbole</td></tr>
            <tr><td><b>Trading 212</b></td><td>Direkte Ticker-Symbole</td></tr>
            <tr><td><b>Jede andere Bank</b></td><td>Manuelles Spalten-Mapping</td></tr>
        </table>

        <a name="speichern__laden"><h2>&#128190; Speichern &amp; Laden</h2></a>
        <p><b>Auto-Speichern:</b> Beim Schließen automatisch &bull;
        <b>Manuell:</b> Speichern als &bull; <b>Laden:</b> Laden</p>

        <a name="verschlüsselung"><h2>&#128272; Verschlüsselung (AES-256-GCM)</h2></a>
        <p>Portfolio-Dateien werden mit <b>AES-256-GCM</b> verschlüsselt.</p>
        <ul>
            <li>Dateiformat: <code>.smpf</code> (Stock Monitor Portfolio File)</li>
            <li>Passwort-Ableitung via PBKDF2-HMAC-SHA256 (600'000 Iterationen)</li>
            <li>Die Daten verlassen deinen Computer nie – keine Cloud, kein Server</li>
        </ul>
        <div class="warning"><b>⚠ Passwort merken!</b> Es gibt keine Passwort-Wiederherstellung.</div>

        <a name="api-key"><h2>&#128273; API-Key (Gemini KI)</h2></a>
        <p>Für die KI-gestützte Portfolio-Analyse wird ein <b>Google Gemini API-Key</b> benötigt.</p>
        <ul>
            <li>Kostenlos registrieren: <code>aistudio.google.com</code></li>
            <li>Der Key wird lokal in <code>~/.stock_monitor_settings.json</code> gespeichert</li>
        </ul>

        <a name="bollinger-bänder"><h2>&#128200; Bollinger-Bänder (BB)</h2></a>
        <p><b>Aktivieren:</b> Checkbox <b>BB</b> im Zoom-Modus &rarr; drei Linien über dem Kurschart.</p>
        <div class="tip">&#128270; <b>Vertiefung:</b> &rarr; <a href="#bb-analyse">Bollinger-Bänder – Analyse-Vertiefung</a></div>

        <a name="drawdown"><h2>&#128201; Drawdown (DD)</h2></a>
        <p><b>Aktivieren:</b> Checkbox <b>DD</b> im Zoom-Modus &rarr; rotes Flächendiagramm unterhalb des Charts.</p>
        <div class="tip">&#128270; <b>Vertiefung:</b> &rarr; <a href="#dd-analyse">Drawdown – Analyse-Vertiefung</a></div>

        <a name="export_pdfexcelods"><h2>&#128190; Export (PDF / Excel / ODS)</h2></a>
        <table>
            <tr><th>Format</th><th>Inhalt</th><th>Benötigt</th></tr>
            <tr><td>PDF</td><td>Diagramm + Datentabelle</td><td>reportlab</td></tr>
            <tr><td>Excel (.xlsx)</td><td>Tabelle mit Formatierung + Diagramm</td><td>openpyxl</td></tr>
            <tr><td>ODS</td><td>OpenDocument-Tabelle für LibreOffice</td><td>odfpy</td></tr>
        </table>
        <p>Installation: <code>pip install reportlab openpyxl odfpy --break-system-packages</code></p>

        <a name="steuermodul"><h2>&#129534; Steuermodul</h2></a>
        <div class="new">Feature: Steuerauszug CH / DE / AT / UK / US inkl. Steuerformular-PDF</div>
        <p>Das Steuermodul erstellt einen steuerrelevanten Jahresauszug für das aktive Portfolio
        – separat für fünf Steuerjurisdiktionen.</p>
        <table>
            <tr><th>Land</th><th>Währung</th><th>Steuersystem</th></tr>
            <tr><td>&#127464;&#127469; Schweiz (CH)</td><td>CHF</td><td>Einkommens- + Vermögenssteuer</td></tr>
            <tr><td>&#127465;&#127466; Deutschland (DE)</td><td>EUR</td><td>Abgeltungsteuer 25 %</td></tr>
            <tr><td>&#127462;&#127481; Österreich (AT)</td><td>EUR</td><td>KESt 27,5 %</td></tr>
            <tr><td>&#127468;&#127463; Grossbritannien (UK)</td><td>GBP</td><td>Income Tax / CGT</td></tr>
            <tr><td>&#127482;&#127480; USA (US)</td><td>USD</td><td>Federal + State Tax</td></tr>
        </table>
        <div class="warning">&#9888; Das Steuermodul ist eine <b>Orientierungshilfe</b> – keine rechtsgültige Steuererklärung.
        Für die offizielle Abgabe immer den originalen Bankauszug und das Online-Portal des jeweiligen Landes verwenden.</div>

        <a name="internationale_börsen"><h2>&#127758; Internationale Börsen</h2></a>
        <p>Suffixe werden automatisch erkannt (13 unterstützte Börsen):</p>
        <table>
            <tr><th>Suffix</th><th>Börse / Land</th><th>Beispiel</th></tr>
            <tr><td>.SW</td><td>Schweiz (SIX)</td><td>NESN.SW</td></tr>
            <tr><td>.DE</td><td>Deutschland (XETRA)</td><td>BMW.DE</td></tr>
            <tr><td>.PA</td><td>Frankreich (Euronext)</td><td>AIR.PA</td></tr>
            <tr><td>.L</td><td>Grossbritannien (LSE)</td><td>SHEL.L</td></tr>
            <tr><td>.MI</td><td>Italien (Mailand)</td><td>ENI.MI</td></tr>
            <tr><td>.T</td><td>Japan (Tokyo)</td><td>7203.T</td></tr>
            <tr><td>.HK</td><td>Hongkong (HKEX)</td><td>0700.HK</td></tr>
        </table>
        <div class="tip"><b>Tipp:</b> Einfach das Symbol ohne Suffix eingeben – Stock Monitor erkennt die richtige Börse automatisch!</div>

        <a name="keyboard_shortcuts"><h2>&#9875; Keyboard Shortcuts</h2></a>
        <ul>
            <li><b>Strg+S:</b> Speichern &bull; <b>Strg+O:</b> Laden &bull; <b>Strg+Q:</b> Beenden</li>
        </ul>
"""

# ══════════════════════════════════════════════════════════════════════════════
# ENGLISH
# ══════════════════════════════════════════════════════════════════════════════
_HTML_EN = """
        <a name="überblick"><h2>&#128202; Overview</h2></a>
        <p>Stock Monitor is a professional trading app for simultaneously tracking
        stocks, ETFs, and cryptocurrencies &mdash; with portfolio management, risk metrics,
        AI analysis, and encrypted data storage.<br>
        <b>Platforms:</b> Linux (KDE Plasma, GNOME, ...) &bull; Windows (.exe download on GitHub)</p>
        <div class="tip"><b>Quick overview of main features:</b><br>
        <b>Top:</b> Administration &bull; Charts &bull; Portfolio view &bull; Analysis tools &bull; Export<br>
        <b>Center:</b> Live charts with technical analysis<br>
        <b>Bottom:</b> Total invested / current value / P&amp;L</div>

        <div class="new">&#127381; <b>Demo portfolio pre-loaded</b><br>
        Stock Monitor ships with a demo portfolio so you can explore all features right away.<br>
        <b>Password:</b> <code>Stock-Monitor 5.0</code></div>

        <a name="quickstart"><h2>&#128640; Quickstart – Up and Running in 5 Minutes</h2></a>
        <p>Never used Stock Monitor before? Here is the fastest way to get your first result:</p>
        <table>
            <tr><th>Step</th><th>Action</th><th>Where</th></tr>
            <tr><td><b>1</b></td><td>Launch the app – 4 empty charts appear</td><td>Main window</td></tr>
            <tr><td><b>2</b></td><td>Enter a symbol (e.g. <code>AAPL</code>, <code>NESN.SW</code>, <code>BTC-USD</code>) + Enter</td><td>Input field at top of chart</td></tr>
            <tr><td><b>3</b></td><td>Select a time period (1M / 6M / 1Y / 5Y / Max)</td><td>Dropdown in chart</td></tr>
            <tr><td><b>4</b></td><td>Add more symbols to the other charts</td><td>Each chart individually</td></tr>
            <tr><td><b>5</b></td><td>Change number of charts (4 / 6 / 8 / 12 / 16 &ndash; <i>16 only on 4K displays</i>)</td><td>Dropdown top-left in toolbar</td></tr>
            <tr><td><b>6</b></td><td>Double-click a chart for fullscreen with RSI, BB, Candlestick</td><td>Any chart</td></tr>
            <tr><td><b>7</b></td><td>Create a portfolio: ⚙ Administration → Add positions</td><td>Toolbar</td></tr>
            <tr><td><b>8</b></td><td>Save portfolio: 💾 Save (AES-256 encrypted)</td><td>Toolbar</td></tr>
        </table>
        <div class="tip"><b>Tip:</b> Enter symbols without the exchange suffix (e.g. <code>NESN</code> instead of <code>NESN.SW</code>) –
        Stock Monitor detects the correct exchange automatically.</div>
        <div class="tip"><b>Tip:</b> Your last session is saved automatically on close
        and restored on next launch – including the Watchlist.</div>

        <a name="zahlenformat"><h2>&#128290; Number Format</h2></a>
        <p>Use the <b>Format button</b> in the toolbar to change the number format for all displayed values.
        Three formats are available:</p>
        <table>
            <tr><th>Format</th><th>Region</th><th>Thousands separator</th><th>Decimal mark</th><th>Example</th></tr>
            <tr><td><b>CH</b></td><td>Switzerland</td><td>Apostrophe <code>'</code></td><td>Dot <code>.</code></td><td>1'234'567.89</td></tr>
            <tr><td><b>DE</b></td><td>Germany</td><td>Dot <code>.</code></td><td>Comma <code>,</code></td><td>1.234.567,89</td></tr>
            <tr><td><b>US</b></td><td>USA / International</td><td>Comma <code>,</code></td><td>Dot <code>.</code></td><td>1,234,567.89</td></tr>
        </table>
        <div class="tip"><b>Note:</b> The selected format applies to portfolio values, metrics, prices, and all
        numeric displays. After switching, values will be refreshed in the new format.</div>
        <div class="warning"><b>Important:</b> The number format only affects <i>display</i> – internally
        the app always uses English decimal notation. Inputs (e.g. purchase price, quantity) must
        still be entered with a dot as the decimal separator.</div>
        <div class="tip"><b>Stock chart axes:</b> The Y-axis labels in price charts (main charts,
        portfolio performance) always use the international standard with a dot as the decimal
        separator – regardless of the selected format. This follows the stock exchange standard.
        All calculated values (portfolio values, Alpha, Beta, Sharpe Ratio, etc.) follow the
        selected format.</div>

        <a name="datumsformat"><h2>&#128197; Date Format</h2></a>
        <p>Use the <b>📅 button</b> in the toolbar to change the date format for all displayed dates.
        Three formats are available:</p>
        <table>
            <tr><th>Format</th><th>Example</th><th>Usage</th></tr>
            <tr><td><b>EU</b></td><td>28.03.2026</td><td>German / Swiss / European</td></tr>
            <tr><td><b>ISO</b></td><td>2026-03-28</td><td>International / ISO 8601</td></tr>
            <tr><td><b>US</b></td><td>03/28/2026</td><td>USA / English</td></tr>
        </table>
        <div class="tip"><b>Note:</b> The selected date format applies to all date displays in the app –
        purchase dates, ex-dividend dates, chart axes, portfolio exports, and timestamps.
        The setting is saved permanently in <code>~/.stock_monitor_config.json</code>.</div>
        <div class="warning"><b>Important:</b> The date format only affects <i>display</i> –
        internally the app always stores dates in ISO format (<code>YYYY-MM-DD</code>).
        When entering purchase dates, all three formats are recognized automatically.</div>

        <a name="sprache"><h2>&#127760; Language / Sprache</h2></a>
        <p>The app language can be switched by <b>clicking the corresponding flag</b> in the toolbar.
        Currently supported languages: <b>German (DE)</b> and <b>English (EN)</b>.</p>
        <div class="tip"><b>Note:</b> The language setting applies to all UI labels, tooltips,
        and this help. It is saved permanently in <code>~/.stock_monitor_config.json</code>.</div>

        <a name="charts_erstellen"><h2>&#128200; Creating Charts</h2></a>
        <p>Click <b>&#128200; Upd.</b> in the header &rarr; enter a symbol &rarr; press Enter.</p>
        <ul>
            <li>Exchange suffixes are detected <b>automatically</b> (e.g. "NESN" &rarr; NESN.SW)</li>
            <li>Multiple layouts: 4 &bull; 6 &bull; 8 &bull; 12 &bull; 16 simultaneous charts &ndash; <i>16 charts (4&times;4) requires a 4K display</i></li>
            <li>Click a symbol in the portfolio overview &rarr; opens chart in new window</li>
        </ul>

        <a name="rsi-indikator"><h2>&#128200; RSI Indicator</h2></a>
        <p><b>Activate:</b> Checkbox <b>RSI</b> in zoom mode (fullscreen chart) &rarr; separate panel below the chart.</p>
        <table>
            <tr><th>Value</th><th>Signal</th><th>Rule of thumb</th></tr>
            <tr><td><b>&gt; 70</b></td><td style="color:#e74c3c">&#9650; Overbought</td><td>Possible pullback</td></tr>
            <tr><td><b>30–70</b></td><td style="color:#27ae60">&#9644; Neutral</td><td>Normal range</td></tr>
            <tr><td><b>&lt; 30</b></td><td style="color:#3498db">&#9660; Oversold</td><td>Possible recovery</td></tr>
        </table>
        <div class="tip">&#128270; <b>Deep dive:</b> Calculation, divergences, pitfalls &rarr;
        <a href="#rsi-analyse">RSI – Analysis deep dive</a></div>

        <a name="52w_hochtief"><h2>&#128200; 52W High / Low</h2></a>
        <div class="new">Feature: 52-week high/low lines</div>
        <p>In zoom mode (fullscreen chart), two horizontal reference lines can be shown:</p>
        <ul>
            <li><b>52W High:</b> Highest price of the last 52 weeks &ndash; green dashed line</li>
            <li><b>52W Low:</b> Lowest price of the last 52 weeks &ndash; red dashed line</li>
        </ul>
        <div class="tip"><b>Tip:</b> A price close to the 52W high means the stock is at its annual peak &ndash;
        some traders see this as a breakout signal, others as a warning. Close to the 52W low may indicate a buying opportunity.</div>

        <a name="kaufpreis-linie"><h2>&#128178; Purchase Price Line</h2></a>
        <div class="new">Feature: Personal cost basis line</div>
        <p>If the stock is in your portfolio, an <b>orange dashed line</b>
        is shown at your average purchase price (checkbox <b>Buy Price</b>).</p>
        <ul>
            <li>Shows your <b>weighted average purchase price</b></li>
            <li>At a glance: price above line = profit &bull; below = loss</li>
            <li>Only visible if the symbol exists in the active portfolio</li>
        </ul>

        <a name="stop-loss__zielkurs"><h2>&#128683; Stop-Loss &amp; &#127919; Personal Target Price</h2></a>
        <div class="new">Feature: Personal price alerts</div>
        <p>In zoom mode, personal price limits can be set for each stock:</p>
        <ul>
            <li><b>Stop-Loss (red):</b> Lower limit &ndash; if breached, a red warning appears in the chart</li>
            <li><b>Target price (green):</b> Upper limit &ndash; your personal price target</li>
        </ul>
        <p>Set: Click the <b>&#128683; SL / &#127919; TP</b> button in zoom mode &rarr; enter value &rarr; Save.<br>
        Values are stored permanently and are independent of analyst target prices.</p>
        <div class="tip"><b>Tip:</b> Stop-Loss and target price are also shown in the portfolio overview column view.</div>

        <h3>&#963; Sharpe Ratio (Zoom Mode)</h3>
        <p>In <b>zoom mode</b>, the checkbox <b>Show Sharpe Ratio</b> calculates the risk-return
        ratio for the displayed period.</p>
        <p><b>Formula:</b> Annualised Sharpe = (Return &minus; Risk-free rate) &divide; Volatility &times; &#8730;252<br>
        Risk-free rate: 5% p.a. (0.05/252 per day)</p>
        <table>
            <tr><th>Value</th><th>Colour</th><th>Assessment</th></tr>
            <tr><td>&ge; 1.0</td><td style="color:#27ae60">&#9632; Green</td><td>Good – strong risk-return ratio</td></tr>
            <tr><td>&ge; 0.5</td><td style="color:#e67e22">&#9632; Orange</td><td>Acceptable</td></tr>
            <tr><td>&ge; 0.0</td><td style="color:#7f8c8d">&#9632; Grey</td><td>Weak – little advantage over risk-free rate</td></tr>
            <tr><td>&lt; 0.0</td><td style="color:#e74c3c">&#9632; Red</td><td>Negative – return below risk-free rate</td></tr>
        </table>
        <div class="tip">&#128270; <b>Deep dive:</b> &rarr;
        <a href="#sharpe-vertiefung">Sharpe Ratio – Analysis deep dive</a></div>

        <h3>&#127869; Candlestick View (Zoom Mode)</h3>
        <p>In zoom mode, checkbox <b>&#127869; Candles</b> switches from line to candlestick view.</p>
        <ul>
            <li><b>Green candle:</b> Close &gt; Open (positive day)</li>
            <li><b>Red candle:</b> Close &lt; Open (negative day)</li>
            <li>The wick shows the daily high and low</li>
            <li>Available in zoom mode only</li>
        </ul>
        <div class="tip"><b>Tip:</b> Candlestick charts are best suited for short-term technical analysis (e.g. period 1D – 1M).</div>

        <a name="zeiträume"><h2>&#9200; Time Periods</h2></a>
        <p><b>Global:</b> Changes all charts at once &bull; <b>Per chart:</b> Individually selectable</p>
        <p>Available: <code>1D</code> &bull; <code>5D</code> &bull; <code>1M</code> &bull; <code>3M</code> &bull; <code>6M</code> &bull; <code>YTD</code> &bull; <code>1Y</code> &bull; <code>2Y</code> &bull; <code>5Y</code> &bull; <code>Max</code></p>
        <h3>&#10000; Crosshair &amp; Tooltip</h3>
        <p>In <b>zoom mode</b> a crosshair is activated:</p>
        <ul>
            <li>Crosshair follows the mouse and shows date + price as tooltip</li>
            <li>Disappears automatically when leaving the chart area</li>
            <li>Only one chart can be active at a time</li>
        </ul>

        <a name="eigener_zeitraum"><h2>&#128197; Custom Time Period</h2></a>
        <p>Selectable via <b>&#128197; Custom period</b> &mdash; start and end date freely adjustable (up to 10 years back).</p>
        <div class="tip"><b>Tip:</b> Ideal for analysing historical events (e.g. COVID crash March 2020).</div>

        <a name="moving_averages_ma"><h2>&#128201; Moving Averages (MA)</h2></a>
        <ul>
            <li><b>MA20:</b> Short-term trend (20 days)</li>
            <li><b>MA50:</b> Medium-term trend (50 days)</li>
            <li><b>MA200:</b> Long-term trend (200 days)</li>
        </ul>
        <div class="tip"><b>Trading tip:</b> <b>Golden Cross</b> = MA50 crosses MA200 upward = classic buy signal!</div>

        <a name="trendlinie"><h2>&#128208; Trend Line</h2></a>
        <p>Black dashed line = linear regression. Upward slope = uptrend.</p>

        <a name="beta-wert_chart"><h2>&#946; Beta (Chart)</h2></a>
        <p><b>Activate:</b> Checkbox <b>Beta</b> in zoom mode &rarr; value shown in chart.</p>
        <table>
            <tr><th>Beta</th><th>Meaning</th></tr>
            <tr><td><b>&beta; = 1.0</b></td><td>Moves with the S&amp;P 500</td></tr>
            <tr><td><b>&beta; &gt; 1.0</b></td><td>More volatile than the market</td></tr>
            <tr><td><b>&beta; &lt; 1.0</b></td><td>Defensive, lower volatility</td></tr>
            <tr><td><b>&beta; &lt; 0</b></td><td>Counter-cyclical (e.g. Gold)</td></tr>
        </table>
        <div class="tip">&#128270; <b>Deep dive:</b> &rarr; <a href="#beta-vertiefung">Beta – Analysis deep dive</a></div>

        <a name="alpha-wert_chart"><h2>&#945; Alpha (Chart)</h2></a>
        <p><b>Activate:</b> Checkbox <b>Alpha</b> in zoom mode.</p>
        <p>Jensen's Alpha = risk-adjusted excess return vs. S&amp;P 500. <b>Positive = outperformance</b>, negative = underperformance.
        Based on daily returns, annualised. Risk-free rate: 5% p.a.</p>
        <div class="tip">&#128270; <b>Deep dive:</b> &rarr; <a href="#alpha-vertiefung">Alpha – Analysis deep dive</a></div>

        <a name="zielkurs"><h2>&#127919; Analyst Target Price Line</h2></a>
        <p>Orange dashed line = average analyst target price (source: Yahoo Finance).</p>

        <a name="analysten-info"><h2>&#128678; Analyst Info</h2></a>
        <p>Click <b>i Info</b> in a chart:</p>
        <ul>
            <li>Analyst recommendation (5-level scale: Strong Buy to Strong Sell)</li>
            <li>Target price range (Min / Average / Max)</li>
            <li>Beta, Alpha, Sharpe Ratio at a glance</li>
            <li><b>News Score:</b> Automatic sentiment analysis of current headlines</li>
        </ul>

        <a name="firmeninfo"><h2>&#127970; Company Info</h2></a>
        <p>In the analyst dialog: <b>Company Info</b> &rarr; CEO, headcount, market cap,
        revenue, profit (TTM), company description.</p>
        <div class="tip">Exportable as PDF!</div>

        <a name="finanzdaten"><h2>&#128202; Financial Data</h2></a>
        <p>In the analyst dialog: <b>Financial Data</b> &rarr; P&amp;L, balance sheet, cash flow &mdash;
        switchable between <b>quarterly</b> and <b>annual</b>.</p>

        <a name="finment"><h2>&#128269; Finment</h2></a>
        <p>The <b>Finment</b> button opens an external stock analysis from
        <a href="https://finment.com">finment.com</a> for the currently displayed symbol.</p>
        <ul>
            <li>Opens in an <b>embedded browser window</b> directly in the app</li>
            <li>The correct page is <b>located automatically</b> based on the symbol</li>
        </ul>
        <div class="tip"><b>Tip:</b> Finment is particularly useful for German and European stocks.</div>
        <div class="warning"><b>Note:</b> Finment is an external service – the page may be empty for unknown symbols.</div>

        <a name="vergleich"><h2>&#9878; Comparison</h2></a>
        <p>Overlay multiple stocks for comparison &mdash; ideal for comparing relative performance.</p>

        <a name="performance-diagramm"><h2>&#128202; Performance Chart</h2></a>
        <p>All active charts as a bar chart. Hover tooltip shows symbol and percentage.</p>

        <a name="excel_export"><h2>&#128202; Excel Export (Charts)</h2></a>
        <p>Exports performance of all charts as an Excel file with colour-coded values and a native 3D column chart.</p>

        <a name="auto-refresh"><h2>&#128260; Auto-Refresh</h2></a>
        <p>Automatic updates: <b>Off &bull; 30 sec &bull; 1 min &bull; 5 min</b><br>
        Manual: Refresh-All button for immediate update of all charts.</p>

        <a name="favoriten"><h2>&#11088; Favourites</h2></a>
        <p><b>Add:</b> Add favourites in the header &bull;
        <b>Use:</b> Star button directly in the chart for quick symbol switching.</p>

        <a name="watchlist"><h2>&#128203; Watchlist</h2></a>
        <p>The Watchlist allows quick comparison of performance for up to <b>50 symbols</b> in a single bar chart.</p>
        <h3>Open</h3>
        <p>Main menu &rarr; <b>Watchlist</b> button in the toolbar.</p>
        <h3>Manage Symbols</h3>
        <ul>
            <li><b>Enter symbol + Enter</b> or <b>&#10133; Add</b></li>
            <li><b>&#128190; Save / &#128194; Load</b>: Save and load watchlist as JSON file</li>
        </ul>
        <h3>Calculate</h3>
        <p>Select time period &rarr; click <b>&#9654; Calculate</b>. All symbols are fetched in parallel.</p>
        <h3>Export</h3>
        <p><b>&#128228; Export</b>: Save results as PDF, Excel (.xlsx), or OpenDocument (.ods).</p>
        <div class="tip"><b>Tip:</b> The Watchlist is automatically saved and restored on next launch.</div>

        <a name="währungsrechner"><h2>&#128178; Currency Converter</h2></a>
        <ul>
            <li>23 fiat currencies incl. BTC, ETH, XRP, SOL</li>
            <li>Precious metals &amp; commodities: <b>XAU (Gold/oz), XAG (Silver/oz), XPT (Platinum/oz), XPD (Palladium/oz), XCU (Copper/lb)</b></li>
            <li>Real-time rates via Yahoo Finance (approx. 15 min delay)</li>
        </ul>

        <a name="portfolio_übersicht"><h2>&#128188; Portfolio Overview</h2></a>
        <p>All positions with real-time prices at a glance:</p>
        <ul>
            <li>Columns: Symbol &bull; Qty &bull; Avg. Buy Price &bull; Cost &bull; Current Price &bull; Current Value &bull; P&amp;L &bull; P&amp;L% &bull; Weight% &bull; Perf. Contribution% &bull; Sector Contribution% &bull; Sector &bull; Sub-Industry</li>
            <li>Display currency: <b>USD &bull; CHF &bull; EUR &bull; GBP</b></li>
            <li>Click symbol &rarr; opens chart in new window</li>
        </ul>

        <a name="rohstoffe"><h2>&#127775; Commodities</h2></a>
        <p>Stock Monitor supports <b>5 commodities</b> as a separate asset class alongside stocks and crypto.</p>
        <table>
            <tr><th>Symbol</th><th>Commodity</th><th>Unit</th></tr>
            <tr><td><code>XAU</code></td><td>Gold</td><td>Troy ounce (oz)</td></tr>
            <tr><td><code>XAG</code></td><td>Silver</td><td>Troy ounce (oz)</td></tr>
            <tr><td><code>XPT</code></td><td>Platinum</td><td>Troy ounce (oz)</td></tr>
            <tr><td><code>XPD</code></td><td>Palladium</td><td>Troy ounce (oz)</td></tr>
            <tr><td><code>XCU</code></td><td>Copper</td><td>Pound (lb)</td></tr>
        </table>

        <a name="portfolio_diagramme"><h2>&#128202; Portfolio Charts</h2></a>
        <p>Four different charts are accessible via the buttons in the Portfolio Overview:</p>
        <ul>
            <li><b>🥧 Positions / Weight per Stock:</b> Pie chart showing the percentage weight of each position. Hover tooltip shows symbol, value and share. Ideal for spotting concentration risk at a glance.</li>
            <li><b>📊 Perf. Compare / Performance Compare:</b> Bar chart of all positions sorted by performance. &rarr; <a href="#performance_vergleich">Performance Comparison</a></li>
            <li><b>🏭 Sectors / Sector Distribution:</b> Shows how the portfolio is spread across GICS sectors. &rarr; <a href="#portfolio_branchen">Sector Distribution</a></li>
            <li><b>🌍 Regions / Region Distribution:</b> Geographic distribution by continent. &rarr; <a href="#portfolio_regionen">Region Distribution</a></li>
            <li><b>📉 Indices / Index Comparison:</b> Performance of the 20 most important global stock indices as a bar chart. &rarr; <a href="#indexvergleich">Index Comparison</a></li>
        </ul>

        <a name="performance_vergleich"><h2>&#128202; Performance Comparison</h2></a>
        <p>Bar chart of all portfolio positions sorted by performance – green bars in profit, red bars in loss.</p>
        <ul>
            <li>Freely selectable time period (1M / 3M / 6M / YTD / 1Y / 2Y / 5Y / Max / Since Purchase)</li>
            <li>Hover tooltip shows company name; for bars on the right edge the tooltip appears on the left</li>
            <li>Crypto and commodities can be shown/hidden</li>
            <li><b>Annualized View (CAGR):</b> Switch to annualised return since purchase &mdash; time period is automatically set to <i>Since Purchase (Cost Basis)</i> and locked
                <ul>
                    <li><b>Filter ≥ 1 Year Held:</b> Appears only in Annualized View &mdash; hides positions held less than 1 year (CAGR under 1 year is not meaningful for comparison), active by default</li>
                    <li>Status bar shows positions <span style="color:green">in profit</span> and <span style="color:red">in loss</span>; with filter active: <i>X of Y Positions (≥1Y)</i></li>
                </ul>
            </li>
        </ul>
        <div class="tip"><b>Tip:</b> The Annualized View (CAGR) makes positions with different holding periods directly comparable – a stock with +200% over 4 years has ~31% p.a., while one with +50% in 6 months would be +125% p.a. annualised, but less meaningful.</div>

        <a name="portfolio_performance"><h2>&#128200; Portfolio Performance (TWR/MWR)</h2></a>
        <div class="new">Feature: Time-weighted return</div>
        <ul>
            <li><b>TWR:</b> Eliminates the impact of cash flows &mdash; shows pure investment performance</li>
            <li><b>MWR (XIRR):</b> Considers the timing of purchases &mdash; shows personal return</li>
            <li>Benchmark: S&amp;P 500, NASDAQ 100, MSCI World, SMI, DAX and others</li>
        </ul>

        <a name="monte-carlo"><h2>&#127922; Monte Carlo Simulation</h2></a>
        <div class="new">Feature: Portfolio future scenarios</div>
        <p>The Monte Carlo Simulation calculates <b>thousands of possible future scenarios</b> for your
        portfolio – based on the historical volatility and return of your positions.</p>
        <ul>
            <li><b>Time horizon:</b> 1, 3, 5, 10, 15, 20, 25 or 30 years</li>
            <li><b>Scenarios:</b> 500 to 10,000 simulations (Geometric Brownian Motion)</li>
            <li><b>Coloured bands:</b> 10th / 25th / 50th (median) / 75th / 90th percentile</li>
            <li><b>Table:</b> Portfolio value in USD per scenario at the end date</li>
        </ul>
        <div class="tip">&#128270; <b>Deep dive:</b> What exactly is a Monte Carlo Simulation? &rarr;
        <a href="#monte-carlo-vertiefung">Monte Carlo – Deep Dive</a></div>
        <div class="warning">&#9888; Not a forecast! The simulation is based on historical data and is <b>not investment advice</b>.</div>

        <a name="ecy"><h2>&#128202; Excess CAPE Yield (ECY)</h2></a>
        <div class="new">Feature: Market valuation indicator</div>
        <p>The <b>Excess CAPE Yield (ECY)</b> shows at a glance whether the US stock market (S&amp;P 500)
        is attractively or expensively valued compared to safe government bonds.</p>
        <ul>
            <li><b>Formula:</b> ECY = Earnings yield (1/CAPE × 100) − real 10Y bond yield (TIPS)</li>
            <li><b>Signal:</b> 🟢 &gt;3% attractive · 🟡 1–3% neutral · 🟠 0–1% elevated · 🔴 &lt;0% expensive</li>
            <li><b>Historical chart:</b> ECY since 1993 with colour-coded valuation zones</li>
            <li><b>Data source:</b> Yahoo Finance (^GSPC, ^TNX, RINF) – already integrated in the app, no API key needed</li>
        </ul>
        <div class="tip">&#128270; <b>Deep dive:</b> What does ECY mean in practice, and how do I read the signal? &rarr;
        <a href="#ecy-vertiefung">ECY – Deep Dive</a></div>
        <div class="warning">&#9888; ECY is a <b>market indicator</b>, not a portfolio indicator. It says nothing about your individual positions and is <b>not investment advice</b>.</div>


        <a name="alpha-analyse"><h2>&#945; Alpha Analysis</h2></a>
        <ul>
            <li>Jensen's Alpha for the <b>entire portfolio</b> (weighted by market value)</li>
            <li><b>Four sections:</b> Total &bull; Stocks/ETFs only &bull; Crypto only &bull; Commodities only</li>
        </ul>

        <a name="beta-analyse"><h2>&#946; Beta Analysis</h2></a>
        <ul>
            <li>Weighted portfolio beta (Total / Stocks / Crypto / Commodities)</li>
            <li><b>Gold typically has negative beta</b> – rises when stocks fall</li>
        </ul>

        <a name="sharpe-ratio"><h2>&#963; Sharpe Ratio</h2></a>
        <ul>
            <li>Return per unit of risk (standard deviation), annualised</li>
            <li>Rule of thumb: &gt; 1.0 = good &bull; &gt; 2.0 = excellent &bull; &lt; 0 = worse than risk-free investment</li>
        </ul>
        <div class="warning">All metrics are based on historical data. Not investment advice!</div>

        <a name="ai-balance"><h2>&#9878; AI Balance (Rebalancing)</h2></a>
        <p>Shows how the portfolio would look if position sizes followed performance.</p>
        <ul>
            <li>Selectable time period as performance basis</li>
            <li>Table: Rank &bull; Symbol &bull; Perf.% &bull; Score &bull; Current value &rarr; Target value &bull; Action</li>
            <li>Actions: Hold &bull; Buy +X shares &bull; Sell -X shares</li>
        </ul>
        <div class="warning">This is not investment advice. Past performance does not guarantee future results.</div>

        <a name="zielgerichtetes-rebalancing"><h2>&#127919; Targeted Rebalancing</h2></a>
        <p>The <b>🎯 Targeted</b> button and its accompanying checkbox restrict the AI Balance
        rebalancing to a specific subset of the portfolio – with optional target weighting
        per currency and sector.</p>
        <h3>Checkbox – Enable/Disable Filter</h3>
        <p>The <b>☑ Targeted</b> checkbox switches the filter on or off. The saved filter is
        retained even when the checkbox is deactivated – so you can temporarily disable the filter
        without losing it. The button appears <b style="color:#e67e22">orange</b> when the filter
        is active and enabled, <b style="color:#aaa">grey</b> when saved but disabled.</p>
        <h3>Filter Criteria</h3>
        <ul>
            <li><b>Currencies:</b> Only currencies present in the portfolio are offered (e.g. USD, CHF, EUR).
            An optional <b>target %</b> can be entered per currency.</li>
            <li><b>GICS Sectors (Level 1):</b> The GICS main sectors represented in the portfolio.
            An optional <b>target %</b> per sector as well.</li>
        </ul>
        <h3>Target % Weighting</h3>
        <p>The optional % field specifies how much of the filtered total capital should be allocated
        to a currency or sector. The sum per group should equal <b>100%</b> – the app shows the
        current sum in <span style="color:#27ae60">green</span> (=100%) or
        <span style="color:#e67e22">orange</span> (≠100%) and normalises automatically.</p>
        <table>
            <tr><th>Example</th><th>Effect</th></tr>
            <tr><td>USD 60%, CHF 40%</td><td>60% of capital in USD positions, 40% in CHF</td></tr>
            <tr><td>Technology 50%, Healthcare 50%</td><td>Equal split across two sectors</td></tr>
            <tr><td>No % entered</td><td>Even distribution by AI score</td></tr>
        </table>
        <h3>Logic</h3>
        <p>Only positions that fulfil <i>both</i> conditions are included: selected currency
        <b>AND</b> selected sector (AND logic). If both currency % and sector % are set,
        the average of both weightings is used for a symbol.</p>
        <h3>Storage</h3>
        <p>Filter settings are saved <b>per portfolio</b>. Use <b>↺ Reset</b> to remove all
        filters and include the full portfolio again.</p>
        <div class="tip"><b>Tip:</b> Want to increase your CHF allocation to 30%? Select CHF=30%,
        USD=70% for currencies – the rebalancing will then suggest how to achieve this target.</div>
        <div class="warning">A very narrow filter (e.g. only 1–2 positions) can lead to
        unbalanced rebalancing suggestions.</div>

        <a name="portfolio-vergleich"><h2>&#128202; Portfolio Comparison</h2></a>
        <div class="new">Feature: Compare portfolios visually</div>
        <p>Displays up to <b>4 saved portfolios</b> side by side – as a bar or line chart.
        This allows different investment strategies or time snapshots to be compared directly.</p>
        <h3>Usage</h3>
        <ul>
            <li><b>Add portfolios:</b> Select from the left list and add to the comparison list
            using the <b>+ Add</b> button. Each portfolio requires its password.</li>
            <li><b>Remove portfolios:</b> Select in the right list and remove with
            <b>– Remove</b>.</li>
            <li><b>Currency:</b> All values are converted to the selected currency (USD, CHF,
            EUR, GBP) so that portfolios are comparable.</li>
        </ul>
        <h3>Chart Types</h3>
        <ul>
            <li><b>📊 Bar chart:</b> Shows the current total value of each portfolio as a bar –
            ideal for a quick value comparison.</li>
            <li><b>📈 Line chart:</b> Shows value development over time – ideal for seeing which
            portfolio has performed better.</li>
        </ul>
        <h3>Export</h3>
        <p>Comparison data can be saved as Excel/CSV via the <b>📤 Export</b> button.</p>
        <div class="tip"><b>Tip:</b> Compare your current portfolio with a saved AI Balance
        suggestion – this shows concretely what would have changed.</div>
        <div class="warning">At least 2 saved portfolios (.smpf files) must exist to use
        the comparison.</div>

        <a name="dividenden"><h2>&#128181; Dividends</h2></a>
        <div class="new">Feature: Dividend overview</div>
        <p>Shows historical and projected dividends for all portfolio positions.</p>

        <a name="dividenden-details"><h2>&#128176; Dividend Details</h2></a>
        <p>Detailed view per stock with dividend history, CAGR, stability metric, and aristocrat titles.</p>

        <a name="ki-analyse"><h2>&#129504; AI Analysis</h2></a>
        <div class="new">Feature: AI-powered portfolio analysis</div>
        <p>Sends portfolio data to Google Gemini and receives a structured analysis.</p>
        <div class="warning">AI analyses are not investment advice and may contain errors.</div>

        <a name="rsi-analyse"><h2>&#128200; RSI – Analysis Deep Dive</h2></a>
        <p>The <b>Relative Strength Index (RSI)</b> was developed in 1978 by J. Welles Wilder.
        It measures the ratio of average gains to losses over the last <b>14 periods</b>,
        normalised to a scale of 0–100.</p>
        <p><b>Formula:</b> <code>RSI = 100 − (100 / (1 + RS))</code><br>
        where <code>RS = avg. gains over last 14 days / avg. losses over last 14 days</code></p>
        <div class="tip"><b>Practical tip:</b> RSI below 30 in a long-term uptrend is historically
        one of the most reliable entry points for long-term investors.</div>

        <a name="bb-analyse"><h2>&#128200; Bollinger Bands – Analysis Deep Dive</h2></a>
        <p><b>Bollinger Bands</b> surround the price chart with MA20 ± 2 standard deviations.</p>
        <table>
            <tr><th>Line</th><th>Calculation</th><th>Colour</th></tr>
            <tr><td>Middle line (SMA20)</td><td>20-day Simple Moving Average</td><td>Blue dashed</td></tr>
            <tr><td>Upper band</td><td>SMA20 + 2 × standard deviation</td><td>Cyan</td></tr>
            <tr><td>Lower band</td><td>SMA20 − 2 × standard deviation</td><td>Orange</td></tr>
        </table>
        <div class="tip"><b>Practical tip:</b> BB + RSI combined: price at the lower band <i>and</i> RSI below 30
        significantly improves accuracy over either indicator alone.</div>

        <a name="dd-analyse"><h2>&#128201; Drawdown – Analysis Deep Dive</h2></a>
        <p>The <b>drawdown</b> measures the percentage decline from the rolling high to the current trough.</p>
        <div class="tip"><b>Practical tip:</b> Before buying a position, look at the max drawdown over 5 years.
        Ask yourself: <i>Would I have held through a −50% drawdown?</i></div>

        <a name="alpha-vertiefung"><h2>&#945; Alpha – Analysis Deep Dive</h2></a>
        <p><b>Jensen's Alpha</b> measures whether an investment <b>generates more return than its risk warrants</b>.</p>
        <p><b>Formula:</b> <code>Alpha = Actual return − (Rf + β × (Rm − Rf))</code></p>
        <div class="tip"><b>Practical tip:</b> Positive alpha over 1–2 years may indicate a good stock pick
        – or overweighting in a sector that is currently trending.</div>

        <a name="beta-vertiefung"><h2>&#946; Beta – Analysis Deep Dive</h2></a>
        <p><b>Beta</b> measures a stock's sensitivity to market movements.</p>
        <p><b>Formula:</b> <code>&beta; = Covariance(Stock, Market) / Variance(Market)</code></p>
        <div class="tip"><b>Practical tip:</b> Beta &lt; 0.5 combined with positive alpha is the holy grail of
        stock selection – defensive yet outperforming.</div>

        <a name="sharpe-vertiefung"><h2>&#963; Sharpe Ratio – Analysis Deep Dive</h2></a>
        <p><b>Formula:</b> <code>Sharpe = (Rp − Rf) / σp × √252</code></p>
        <h3>Limitations of the Sharpe Ratio</h3>
        <ul>
            <li><b>Normality assumption:</b> Upside and downside volatility are treated equally</li>
            <li><b>Fat tails:</b> Rare extreme losses are underestimated</li>
            <li><b>Time dependency:</b> In a bull market almost all stocks look good</li>
        </ul>
        <div class="tip"><b>Practical tip:</b> Always compare the Sharpe Ratio within the same asset class.</div>

        <a name="monte-carlo-vertiefung"><h2>&#127922; Monte Carlo – Deep Dive</h2></a>
        <h3>What is a Monte Carlo Simulation?</h3>
        <p>The name comes from the famous casino in Monaco – because the method is based on <b>random numbers</b>,
        similar to a roulette wheel. It was developed by mathematicians in the 1940s for nuclear research and
        is now used in finance, physics and engineering.</p>
        <p>In Stock Monitor, the simulation calculates thousands of possible price paths for your portfolio
        using the <b>Geometric Brownian Motion (GBM)</b> model – the industry standard for stock price simulations.</p>
        <h3>How does Geometric Brownian Motion work?</h3>
        <p>Each trading day is simulated as a small random step. The direction and size of the step depend
        on two parameters:</p>
        <table>
            <tr><th>Parameter</th><th>Source</th><th>Meaning</th></tr>
            <tr><td><b>&#956; (Drift)</b></td><td>Historical annual return of the portfolio</td><td>Expected direction</td></tr>
            <tr><td><b>&#963; (Volatility)</b></td><td>Historical standard deviation of daily returns</td><td>Range of fluctuation</td></tr>
        </table>
        <p><b>Formula:</b> <code>S(t+1) = S(t) &times; exp( (&#956; &minus; &#189;&#963;&sup2;) &Delta;t + &#963; &radic;&Delta;t &times; Z )</code><br>
        where <code>Z</code> is a standard normal random variable and <code>&Delta;t = 1/252</code> (one trading day).</p>
        <h3>What do the coloured bands show?</h3>
        <table>
            <tr><th>Band</th><th>Meaning</th></tr>
            <tr><td><b>10th percentile</b> (red)</td><td>In 10% of all scenarios the outcome was worse than this value</td></tr>
            <tr><td><b>25th percentile</b> (orange)</td><td>Lower quarter of all scenarios</td></tr>
            <tr><td><b>50th percentile / Median</b> (blue)</td><td>Exactly half the scenarios ended above this, half below</td></tr>
            <tr><td><b>75th percentile</b> (light green)</td><td>Upper quarter of all scenarios</td></tr>
            <tr><td><b>90th percentile</b> (green)</td><td>In 10% of all scenarios the outcome was better than this value</td></tr>
        </table>
        <h3>Limitations of the simulation</h3>
        <ul>
            <li><b>History-based:</b> Drift and volatility come from historical data – the future may differ significantly</li>
            <li><b>No crisis modelling:</b> GBM underestimates rare extreme events (fat tails / black swans)</li>
            <li><b>No correlations:</b> The simulation uses total portfolio returns, not individual stock correlations</li>
        </ul>
        <div class="tip"><b>Practical tip:</b> Use the simulation for a <b>long-term perspective</b> –
        10 years show far more spread than 1 year. This is normal and illustrates why a long investment
        horizon matters so much: the median rises, but the bands widen.</div>
        <div class="warning">&#9888; The Monte Carlo Simulation is a <b>planning aid</b>, not a forecast.
        Past volatility does not guarantee future performance. Not investment advice.</div>

        <a name="ecy-vertiefung"><h2>&#128202; ECY – Deep Dive</h2></a>
        <h3>What is behind the Excess CAPE Yield?</h3>
        <p>The ECY was developed by economist <b>Robert Shiller</b> (Nobel Prize 2013) and published in the
        <i>Financial Analysts Journal</i>. It combines two well-known figures:</p>
        <ul>
            <li><b>CAPE</b> (Cyclically Adjusted Price-to-Earnings Ratio, also known as «Shiller P/E»):
            The price-to-earnings ratio of the S&amp;P 500, smoothed over <b>10 years</b> of
            inflation-adjusted earnings. Removes the effects of business cycles and short-term profit swings.</li>
            <li><b>10Y TIPS yield</b> (Treasury Inflation-Protected Securities):
            The <b>real</b> (inflation-adjusted) interest rate of 10-year US government bonds –
            the «risk-free» benchmark for comparison.</li>
        </ul>
        <p>The <b>earnings yield</b> (1/CAPE × 100%) is the inverse of the P/E ratio: a CAPE of 25 equals
        an earnings yield of 4%. Subtracting the real bond yield gives the <b>excess</b> –
        the additional return that stocks offer over safe bonds (or don't).</p>

        <h3>How do I read the signal?</h3>
        <table>
            <tr><th>Signal</th><th>ECY range</th><th>Meaning</th></tr>
            <tr><td>🟢 Attractive</td><td>&gt; 3%</td><td>Stocks offer a clear premium over bonds. Historically favourable entry phases (e.g. 2009, 2012).</td></tr>
            <tr><td>🟡 Neutral</td><td>1–3%</td><td>Stocks are slightly more attractive than bonds. «Normal» valuation zone.</td></tr>
            <tr><td>🟠 Elevated</td><td>0–1%</td><td>Stocks offer little premium. Bonds become relatively more interesting.</td></tr>
            <tr><td>🔴 Expensive</td><td>&lt; 0%</td><td>Bonds offer more real return than stocks. Historically rare (last seen briefly in 2021–2022).</td></tr>
        </table>

        <h3>&#128721; What ECY does <u>not</u> mean – avoiding panic</h3>
        <div class="warning">
        A <b>negative ECY</b> does <b>not</b> mean the market will crash tomorrow – and a positive ECY
        is not a buy signal. ECY is a <b>medium-term orientation value</b> (horizon: 5–10 years),
        not a short-term timing indicator. Markets can remain «expensive» for years and keep rising.
        <br><br>
        <b>Example:</b> The ECY was periodically low or negative from 2015 to 2021 – yet the S&amp;P 500
        rose substantially during that period. A high ECY (as in 2009) signalled a favourable entry point
        in hindsight, but nobody knew that with certainty at the time.
        </div>

        <h3>Who benefits from ECY?</h3>
        <p>ECY is particularly relevant for <b>long-term investors</b> who want to align their portfolio
        strategically – for example when deciding whether to overweight stocks vs. bonds.
        It is not suitable for short-term trading.</p>
        <p>Together with the <b>Monte Carlo Simulation</b>, it provides a complete picture: MC shows
        <i>how much</i> your portfolio could grow under various scenarios – ECY shows
        <i>whether the market is currently cheap or expensive</i> for long-term investments.</p>
        <div class="tip"><b>Bottom line:</b> ECY = one more piece of the puzzle for informed decisions.
        Not an oracle, not an alarm signal – but a sober comparison of two asset classes.</div>


        <a name="gics-vertiefung"><h2>&#127981; GICS – Deep Dive</h2></a>
        <p><b>GICS</b> stands for <b>Global Industry Classification Standard</b> – a worldwide standard for classifying listed companies into industries. Developed in 1999 by <b>S&amp;P Global</b> and <b>MSCI</b>, it is used today by stock exchanges, fund managers and financial media worldwide. Virtually every stock is assigned to one of <b>11 sectors</b>:</p>
        <table>
            <tr><th>Sector</th><th>What does it cover?</th><th>Examples</th></tr>
            <tr><td><b>Information Technology</b></td><td>Software, hardware, semiconductors, IT services</td><td>Apple, Microsoft, NVIDIA, SAP</td></tr>
            <tr><td><b>Financials</b></td><td>Banks, insurance, asset management</td><td>JPMorgan, UBS, Allianz, Zurich</td></tr>
            <tr><td><b>Health Care</b></td><td>Pharma, medtech, biotech, hospitals</td><td>Novartis, Roche, J&amp;J, Medtronic</td></tr>
            <tr><td><b>Consumer Discretionary</b></td><td>Non-essential goods – cars, luxury, retail</td><td>Amazon, Tesla, LVMH, BMW</td></tr>
            <tr><td><b>Industrials</b></td><td>Machinery, aerospace, transport, defense</td><td>Siemens, Caterpillar, ABB, Boeing</td></tr>
            <tr><td><b>Communication Services</b></td><td>Telecoms, social media, streaming</td><td>Alphabet, Meta, Netflix, Swisscom</td></tr>
            <tr><td><b>Consumer Staples</b></td><td>Essential goods – food, beverages, household</td><td>Nestlé, Procter &amp; Gamble, Coca-Cola</td></tr>
            <tr><td><b>Energy</b></td><td>Oil, gas, renewables, refineries</td><td>ExxonMobil, Shell, TotalEnergies</td></tr>
            <tr><td><b>Materials</b></td><td>Commodities, chemicals, mining, paper</td><td>BASF, Rio Tinto, Glencore, Sika</td></tr>
            <tr><td><b>Real Estate</b></td><td>Real estate funds (REITs), property management</td><td>American Tower, Swiss Prime Site</td></tr>
            <tr><td><b>Utilities</b></td><td>Electricity, water, gas – regulated suppliers</td><td>NextEra Energy, BKW, E.ON</td></tr>
        </table>
        <h3>Why does sector diversification matter?</h3>
        <p>Different sectors react differently to economic cycles and events. <b>Defensive sectors</b> (Consumer Staples, Health Care, Utilities) are more crisis-resistant – people keep buying food and medicine. <b>Cyclical sectors</b> (Consumer Discretionary, Industrials) perform better in boom phases but lose more in downturns. If 70% of your portfolio is in tech stocks, you are well positioned when AI booms – but heavily exposed if the sector corrects as it did in 2022.</p>
        <div class="tip"><b>Rule of thumb:</b> No single sector should permanently exceed 30–35% of the portfolio. The sector view in Stock Monitor makes concentration risks visible at a glance.</div>

        <a name="portfolio_branchen"><h2>&#127981; Sector Distribution</h2></a>
        <p>Open via <b>🏭 Sectors</b> in the Portfolio Overview. Shows how the portfolio is distributed across different industries – switchable between weighting and performance per sector.</p>
        <ul>
            <li>Pie chart with hover tooltip (sector, number of positions, share %)</li>
            <li>Switch to bar chart to see performance per sector for the selected time period</li>
            <li>Crypto is excluded (has no GICS sector)</li>
        </ul>
        <div class="tip">&#128270; <b>Deep Dive:</b> What is GICS, which 11 sectors exist and why does sector diversification matter? &rarr; <a href="#gics-vertiefung">GICS – Deep Dive</a></div>

        <a name="portfolio_regionen"><h2>&#127758; Regional Allocation</h2></a>
        <p>Open via <b>🌍 Regions</b> in the Portfolio Overview. Shows the geographic distribution of the portfolio by continent and company headquarters (where the company is based, not where it is listed).</p>
        <ul>
            <li>Donut chart with hover tooltip (region, number of positions, share %)</li>
            <li><b>Interactive world map in browser:</b> Shows company headquarters as pins – click for details</li>
        </ul>
        <div class="tip"><b>Tip:</b> Many European investors are unknowingly heavily weighted towards the US – US stocks dominate most indices. The regional view helps you keep your intended geographic diversification in check.</div>

        <a name="indexvergleich"><h2>&#128202; Index Comparison</h2></a>
        <div class="new">Feature: Global Stock Index Comparison</div>
        <p>Open via <b>📉 Indices</b> in the Portfolio Overview. Shows the performance of the <b>20 most important global stock indices</b> in a clear bar chart – optionally including your own portfolio's performance.</p>
        <ul>
            <li><b>Included indices:</b>
                <ul>
                    <li><b>USA:</b> S&amp;P 500, NASDAQ 100, Dow Jones, Russell 2000</li>
                    <li><b>Europe:</b> SMI (Switzerland), DAX (Germany), EURO STOXX 50, FTSE 100 (UK), CAC 40 (France)</li>
                    <li><b>Asia/Pacific:</b> Nikkei 225 (Japan), KOSPI (South Korea), Hang Seng (Hong Kong), Shanghai Composite (China), BSE SENSEX (India), ASX 200 (Australia)</li>
                    <li><b>Americas:</b> Bovespa (Brazil), TSX Composite (Canada)</li>
                    <li><b>Global/Emerging Markets:</b> MSCI World, MSCI Emerging Markets, MSCI EM Asia</li>
                </ul>
            </li>
            <li><b>Time period:</b> 1M / 3M / 6M / YTD / 1Y / 2Y / 5Y / <b>10Y</b> / Max – freely selectable</li>
            <li><b>Compare your own portfolio:</b> The <i>📁 Show portfolio</i> checkbox adds an extra <b>blue bar</b> for your loaded portfolio. Performance is calculated as a <b>weighted average</b> of all positions (weighted by current market value). Uncheck to hide the portfolio – no extra data fetch required.</li>
            <li><b>Bar colours:</b> 🟢 Green = positive · 🔴 Red = negative · 🔵 Blue = your portfolio</li>
            <li>Hover tooltip shows exact percentage value</li>
            <li>Status bar shows indices in the green/red plus portfolio performance</li>
            <li>Export as PDF / Excel / ODS available</li>
        </ul>
        <div class="tip"><b>Tip:</b> The 10-year view shows which markets have grown the most over the long term – and whether your portfolio has outperformed the S&amp;P 500 or MSCI World over a decade.</div>

        <a name="administration"><h2>&#9881; Administration</h2></a>
        <p>Central hub for all portfolio management tasks.</p>
        <h3>Add a position</h3>
        <p>1. Enter symbol &rarr; 2. Purchase date &rarr; 3. Quantity &rarr; <b>Add</b><br>
        Purchase price is loaded automatically from Yahoo Finance.</p>

        <a name="swissquote_import"><h2>&#128229; Swissquote Import</h2></a>
        <p>In Swissquote: <b>Depot &rarr; Transactions &rarr; Export as CSV</b></p>
        <ul>
            <li>Automatic detection of buys and sells</li>
            <li>Sells deducted from oldest positions via <b>FIFO</b></li>
            <li>Duplicates are skipped automatically</li>
        </ul>

        <a name="generic_csv_import"><h2>&#128196; Generic CSV Import</h2></a>
        <p>Import from <i>any bank or broker</i> depot export.</p>
        <table>
            <tr><th>Bank / Broker</th><th>Notes</th></tr>
            <tr><td><b>DeGiro</b></td><td>ISIN auto-converted</td></tr>
            <tr><td><b>Flatex</b></td><td>ISIN auto-converted</td></tr>
            <tr><td><b>Interactive Brokers</b></td><td>Direct ticker symbols</td></tr>
            <tr><td><b>Trading 212</b></td><td>Direct ticker symbols</td></tr>
            <tr><td><b>Any other bank</b></td><td>Manual column mapping</td></tr>
        </table>

        <a name="speichern__laden"><h2>&#128190; Save &amp; Load</h2></a>
        <p><b>Auto-save:</b> Automatically on close &bull;
        <b>Manual:</b> Save as &bull; <b>Load:</b> Load</p>

        <a name="verschlüsselung"><h2>&#128272; Encryption (AES-256-GCM)</h2></a>
        <p>Portfolio files are encrypted with <b>AES-256-GCM</b>.</p>
        <ul>
            <li>File format: <code>.smpf</code> (Stock Monitor Portfolio File)</li>
            <li>Key derivation via PBKDF2-HMAC-SHA256 (600,000 iterations)</li>
            <li>Your data never leaves your computer – no cloud, no server</li>
        </ul>
        <div class="warning"><b>⚠ Remember your password!</b> There is no password recovery.</div>

        <a name="api-key"><h2>&#128273; API Key (Gemini AI)</h2></a>
        <p>A <b>Google Gemini API key</b> is required for AI-powered portfolio analysis.</p>
        <ul>
            <li>Register for free at: <code>aistudio.google.com</code></li>
            <li>The key is stored locally in <code>~/.stock_monitor_settings.json</code></li>
        </ul>

        <a name="bollinger-bänder"><h2>&#128200; Bollinger Bands (BB)</h2></a>
        <p><b>Activate:</b> Checkbox <b>BB</b> in zoom mode &rarr; three lines over the price chart.</p>
        <div class="tip">&#128270; <b>Deep dive:</b> &rarr; <a href="#bb-analyse">Bollinger Bands – Analysis deep dive</a></div>

        <a name="drawdown"><h2>&#128201; Drawdown (DD)</h2></a>
        <p><b>Activate:</b> Checkbox <b>DD</b> in zoom mode &rarr; red area chart below the price chart.</p>
        <div class="tip">&#128270; <b>Deep dive:</b> &rarr; <a href="#dd-analyse">Drawdown – Analysis deep dive</a></div>

        <a name="export_pdfexcelods"><h2>&#128190; Export (PDF / Excel / ODS)</h2></a>
        <table>
            <tr><th>Format</th><th>Content</th><th>Requires</th></tr>
            <tr><td>PDF</td><td>Chart + data table</td><td>reportlab</td></tr>
            <tr><td>Excel (.xlsx)</td><td>Formatted table + chart</td><td>openpyxl</td></tr>
            <tr><td>ODS</td><td>OpenDocument spreadsheet</td><td>odfpy</td></tr>
        </table>
        <p>Install if needed: <code>pip install reportlab openpyxl odfpy --break-system-packages</code></p>

        <a name="steuermodul"><h2>&#129534; Tax Module</h2></a>
        <div class="new">Feature: Tax statement CH / DE / AT / UK / US incl. tax form PDF</div>
        <p>The tax module generates a tax-relevant annual statement for the active portfolio
        – separately for five tax jurisdictions.</p>
        <table>
            <tr><th>Country</th><th>Currency</th><th>Tax system</th></tr>
            <tr><td>&#127464;&#127469; Switzerland (CH)</td><td>CHF</td><td>Income tax + wealth tax</td></tr>
            <tr><td>&#127465;&#127466; Germany (DE)</td><td>EUR</td><td>Withholding tax 25%</td></tr>
            <tr><td>&#127462;&#127481; Austria (AT)</td><td>EUR</td><td>Capital gains tax 27.5%</td></tr>
            <tr><td>&#127468;&#127463; United Kingdom (UK)</td><td>GBP</td><td>Income Tax / CGT</td></tr>
            <tr><td>&#127482;&#127480; USA (US)</td><td>USD</td><td>Federal + State Tax</td></tr>
        </table>
        <div class="warning">&#9888; The tax module is a <b>guidance tool</b> – not a legally binding tax return.
        Always use your official bank statement and your country's online portal for the official submission.</div>

        <a name="internationale_börsen"><h2>&#127758; International Exchanges</h2></a>
        <p>Suffixes are detected automatically (13 supported exchanges):</p>
        <table>
            <tr><th>Suffix</th><th>Exchange / Country</th><th>Example</th></tr>
            <tr><td>.SW</td><td>Switzerland (SIX)</td><td>NESN.SW</td></tr>
            <tr><td>.DE</td><td>Germany (XETRA)</td><td>BMW.DE</td></tr>
            <tr><td>.PA</td><td>France (Euronext)</td><td>AIR.PA</td></tr>
            <tr><td>.L</td><td>UK (LSE)</td><td>SHEL.L</td></tr>
            <tr><td>.MI</td><td>Italy (Milan)</td><td>ENI.MI</td></tr>
            <tr><td>.T</td><td>Japan (Tokyo)</td><td>7203.T</td></tr>
            <tr><td>.HK</td><td>Hong Kong (HKEX)</td><td>0700.HK</td></tr>
        </table>
        <div class="tip"><b>Tip:</b> Just enter the symbol without the suffix – Stock Monitor detects the correct exchange automatically!</div>

        <a name="keyboard_shortcuts"><h2>&#9875; Keyboard Shortcuts</h2></a>
        <ul>
            <li><b>Ctrl+S:</b> Save &bull; <b>Ctrl+O:</b> Load &bull; <b>Ctrl+Q:</b> Quit</li>
        </ul>
"""

# ── Wrap HTML body into full document ────────────────────────────────────────
def _wrap(body: str, support: str) -> str:
    return f"<html><head>{_CSS}</head><body>{body}{support}{_DONATION_TABLE}</body></html>"


# ── TOC items ─────────────────────────────────────────────────────────────────
_TOC_DE = [
    "── 🚀 QUICKSTART ──",
    "Überblick",
    "── 📊 CHARTS ──",
    "Charts erstellen",
    "Zeiträume",
    "Moving Averages (MA)",
    "RSI-Indikator",
    "Bollinger-Bänder",
    "Trendlinie",
    "Candlestick",
    "Drawdown",
    "52W Hoch/Tief",
    "Kaufpreis-Linie",
    "Stop-Loss & Zielkurs",
    "Crosshair & Tooltip",
    "Auto-Refresh",
    "Favoriten",
    "Watchlist",
    "── 🔍 ANALYSE ──",
    "Alpha-Wert (Chart)",
    "Beta-Wert (Chart)",
    "Sharpe-Ratio",
    "Vergleich",
    "Analysten-Info",
    "Firmeninfo",
    "Finanzdaten",
    "Finment",
    "KI-Analyse",
    "RSI – Vertiefung",
    "Bollinger-Bänder – Vertiefung",
    "Drawdown – Vertiefung",
    "Alpha – Vertiefung",
    "Beta – Vertiefung",
    "Sharpe-Ratio – Vertiefung",
    "Monte Carlo – Vertiefung",
    "ECY – Vertiefung",
    "GICS – Vertiefung",
    "── 💼 PORTFOLIO ──",
    "Portfolio Übersicht",
    "Portfolio Diagramme",
    "Performance-Vergleich",
    "Portfolio Performance",
    "Monte Carlo Simulation",
    "Excess CAPE Yield (ECY)",
    "Alpha-Analyse",
    "Beta-Analyse",
    "AI-Balance",
    "Portfolio-Vergleich",
    "Dividenden",
    "Dividenden Details",
    "Rohstoffe",
    "Branchen-Verteilung",
    "Regionen-Verteilung",
    "Indexvergleich",
    "── 🧾 STEUER ──",
    "Steuermodul",
    "── 🗂 DATEN & IMPORT ──",
    "Administration",
    "Swissquote Import",
    "Generic CSV Import",
    "Internationale Börsen",
    "── ⚙️ SYSTEM ──",
    "Zahlenformat",
    "Datumsformat",
    "Sprache",
    "Speichern & Laden",
    "Verschlüsselung",
    "API-Key",
    "Export (PDF/Excel/ODS)",
    "Keyboard Shortcuts",
]

_TOC_EN = [
    "── 🚀 QUICKSTART ──",
    "Overview",
    "── 📊 CHARTS ──",
    "Creating Charts",
    "Time Periods",
    "Moving Averages (MA)",
    "RSI Indicator",
    "Bollinger Bands",
    "Trend Line",
    "Candlestick",
    "Drawdown",
    "52W High/Low",
    "Purchase Price Line",
    "Stop-Loss & Target Price",
    "Crosshair & Tooltip",
    "Auto-Refresh",
    "Favourites",
    "Watchlist",
    "── 🔍 ANALYSIS ──",
    "Alpha (Chart)",
    "Beta (Chart)",
    "Sharpe Ratio",
    "Comparison",
    "Analyst Info",
    "Company Info",
    "Financial Data",
    "Finment",
    "AI Analysis",
    "RSI – Deep Dive",
    "Bollinger Bands – Deep Dive",
    "Drawdown – Deep Dive",
    "Alpha – Deep Dive",
    "Beta – Deep Dive",
    "Sharpe Ratio – Deep Dive",
    "Monte Carlo – Deep Dive",
    "GICS – Deep Dive",
    "ECY – Deep Dive",
    "── 💼 PORTFOLIO ──",
    "Portfolio Overview",
    "Portfolio Charts",
    "Performance Comparison",
    "Portfolio Performance",
    "Monte Carlo Simulation",
    "Excess CAPE Yield (ECY)",
    "Alpha Analysis",
    "Beta Analysis",
    "AI Balance",
    "Portfolio Comparison",
    "Dividends",
    "Dividend Details",
    "Commodities",
    "Sector Distribution",
    "Region Distribution",
    "Index Comparison",
    "── 🧾 TAX ──",
    "Tax Module",
    "── 🗂 DATA & IMPORT ──",
    "Administration",
    "Swissquote Import",
    "Generic CSV Import",
    "International Exchanges",
    "── ⚙️ SYSTEM ──",
    "Number Format",
    "Date Format",
    "Language",
    "Save & Load",
    "Encryption",
    "API Key",
    "Export (PDF/Excel/ODS)",
    "Keyboard Shortcuts",
]

# ── Anchor maps ───────────────────────────────────────────────────────────────
# Maps TOC label (lowercase) → HTML anchor name
_ANCHOR_DE = {
    # Quickstart
    "überblick":                  "überblick",
    # Charts
    "charts erstellen":           "charts_erstellen",
    "zeiträume":                  "zeiträume",
    "moving averages (ma)":       "moving_averages_ma",
    "rsi-indikator":              "rsi-indikator",
    "bollinger-bänder":           "bollinger-bänder",
    "trendlinie":                 "trendlinie",
    "candlestick":                "stop-loss__zielkurs",
    "drawdown":                   "drawdown",
    "52w hoch/tief":              "52w_hochtief",
    "kaufpreis-linie":            "kaufpreis-linie",
    "stop-loss & zielkurs":       "stop-loss__zielkurs",
    "crosshair & tooltip":        "zeiträume",
    "auto-refresh":               "auto-refresh",
    "favoriten":                  "favoriten",
    "watchlist":                  "watchlist",
    # Analyse
    "alpha-wert (chart)":         "alpha-wert_chart",
    "beta-wert (chart)":          "beta-wert_chart",
    "sharpe-ratio":               "sharpe-ratio",
    "vergleich":                  "vergleich",
    "analysten-info":             "analysten-info",
    "firmeninfo":                 "firmeninfo",
    "finanzdaten":                "finanzdaten",
    "finment":                    "finment",
    "ki-analyse":                 "ki-analyse",
    "rsi – vertiefung":           "rsi-analyse",
    "bollinger-bänder – vertiefung": "bb-analyse",
    "drawdown – vertiefung":      "dd-analyse",
    "alpha – vertiefung":         "alpha-vertiefung",
    "beta – vertiefung":          "beta-vertiefung",
    "sharpe-ratio – vertiefung":  "sharpe-vertiefung",
    "monte carlo – vertiefung":   "monte-carlo-vertiefung",
    "ecy – vertiefung":           "ecy-vertiefung",
    "excess cape yield (ecy)":    "ecy",
    "ecy":                        "ecy",
    "gics – vertiefung":          "gics-vertiefung",
    # Portfolio
    "portfolio übersicht":        "portfolio_übersicht",
    "portfolio diagramme":        "portfolio_diagramme",
    "performance-vergleich":      "performance_vergleich",
    "portfolio performance":      "portfolio_performance",
    "monte carlo simulation":     "monte-carlo",
    "monte carlo – vertiefung":   "monte-carlo-vertiefung",
    "excess cape yield (ecy)":    "ecy",
    "ecy":                        "ecy",
    "alpha-analyse":              "alpha-analyse",
    "beta-analyse":               "beta-analyse",
    "ai-balance":                 "ai-balance",
    "zielgerichtetes-rebalancing": "zielgerichtetes-rebalancing",
    "targeted-rebalancing":        "zielgerichtetes-rebalancing",
    "portfolio-vergleich":        "portfolio-vergleich",
    "dividenden":                 "dividenden",
    "dividenden details":         "dividenden-details",
    "rohstoffe":                  "rohstoffe",
    "branchen-verteilung":        "portfolio_branchen",
    "regionen-verteilung":        "portfolio_regionen",
    "indexvergleich":              "indexvergleich",
    "portfolio branchen":         "portfolio_branchen",
    "portfolio regionen":         "portfolio_regionen",
    # Steuer
    "steuermodul":                "steuermodul",
    # Daten & Import
    "administration":             "administration",
    "swissquote import":          "swissquote_import",
    "generic csv import":         "generic_csv_import",
    "internationale börsen":      "internationale_börsen",
    # System
    "zahlenformat":               "zahlenformat",
    "datumsformat":               "datumsformat",
    "sprache":                    "sprache",
    "speichern & laden":          "speichern__laden",
    "verschlüsselung":            "verschlüsselung",
    "api-key":                    "api-key",
    "export (pdf/excel/ods)":     "export_pdfexcelods",
    "keyboard shortcuts":         "keyboard_shortcuts",
}

_ANCHOR_EN = {
    # Quickstart
    "overview":                   "überblick",
    # Charts
    "creating charts":            "charts_erstellen",
    "time periods":               "zeiträume",
    "moving averages (ma)":       "moving_averages_ma",
    "rsi indicator":              "rsi-indikator",
    "bollinger bands":            "bollinger-bänder",
    "trend line":                 "trendlinie",
    "candlestick":                "stop-loss__zielkurs",
    "drawdown":                   "drawdown",
    "52w high/low":               "52w_hochtief",
    "purchase price line":        "kaufpreis-linie",
    "stop-loss & target price":   "stop-loss__zielkurs",
    "crosshair & tooltip":        "zeiträume",
    "auto-refresh":               "auto-refresh",
    "favourites":                 "favoriten",
    "watchlist":                  "watchlist",
    # Analysis
    "alpha (chart)":              "alpha-wert_chart",
    "beta (chart)":               "beta-wert_chart",
    "sharpe ratio":               "sharpe-ratio",
    "comparison":                 "vergleich",
    "analyst info":               "analysten-info",
    "company info":               "firmeninfo",
    "financial data":             "finanzdaten",
    "finment":                    "finment",
    "ai analysis":                "ki-analyse",
    "rsi – deep dive":            "rsi-analyse",
    "bollinger bands – deep dive": "bb-analyse",
    "drawdown – deep dive":       "dd-analyse",
    "alpha – deep dive":          "alpha-vertiefung",
    "beta – deep dive":           "beta-vertiefung",
    "sharpe ratio – deep dive":   "sharpe-vertiefung",
    "monte carlo – deep dive":    "monte-carlo-vertiefung",
    "ecy – deep dive":            "ecy-vertiefung",
    "excess cape yield (ecy)":    "ecy",
    "ecy":                        "ecy",
    "gics – deep dive":           "gics-vertiefung",
    # Portfolio
    "portfolio overview":         "portfolio_übersicht",
    "portfolio charts":           "portfolio_diagramme",
    "performance comparison":     "performance_vergleich",
    "portfolio performance":      "portfolio_performance",
    "monte carlo simulation":     "monte-carlo",
    "monte carlo – deep dive":    "monte-carlo-vertiefung",
    "alpha analysis":             "alpha-analyse",
    "beta analysis":              "beta-analyse",
    "ai balance":                 "ai-balance",
    "portfolio comparison":       "portfolio-vergleich",
    "dividends":                  "dividenden",
    "dividend details":           "dividenden-details",
    "commodities":                "rohstoffe",
    "sector distribution":        "portfolio_branchen",
    "region distribution":        "portfolio_regionen",
    "index comparison":            "indexvergleich",
    "sector allocation":          "portfolio_branchen",
    "regional allocation":        "portfolio_regionen",
    # Tax
    "tax module":                 "steuermodul",
    # Data & Import
    "administration":             "administration",
    "swissquote import":          "swissquote_import",
    "generic csv import":         "generic_csv_import",
    "international exchanges":    "internationale_börsen",
    # System
    "number format":              "zahlenformat",
    "date format":                "datumsformat",
    "language":                   "sprache",
    "save & load":                "speichern__laden",
    "encryption":                 "verschlüsselung",
    "api key":                    "api-key",
    "export (pdf/excel/ods)":     "export_pdfexcelods",
    "keyboard shortcuts":         "keyboard_shortcuts",
}

# ══════════════════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════════════════
_DATA = {
    "DE": {
        "html":               _wrap(_HTML_DE, _SUPPORT_DE),
        "toc_items":          _TOC_DE,
        "anchor_map":         _ANCHOR_DE,
        "search_placeholder": "Suchen …",
        "window_title":       "Hilfe",
        "lang_label":         "Sprache:",
    },
    "EN": {
        "html":               _wrap(_HTML_EN, _SUPPORT_EN),
        "toc_items":          _TOC_EN,
        "anchor_map":         _ANCHOR_EN,
        "search_placeholder": "Search …",
        "window_title":       "Help",
        "lang_label":         "Language:",
    },
}


def get_help(lang: str = "DE") -> dict:
    """
    Return the help data dict for the given language.
    Falls back to DE if the language is not found.

    Returns a dict with keys:
        html, toc_items, anchor_map,
        search_placeholder, window_title, lang_label
    """
    return _DATA.get(lang, _DATA["DE"])
