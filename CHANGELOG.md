# Changelog

All notable changes to Stock Monitor are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [5.10.0] – 2026-11-16

### Added

- **Portfolio saved automatically** – after "Save as" or loading a portfolio (password entered), every change (buys, sells, imports, account, notes, stop-loss/target prices, AI balance targets) is saved automatically and encrypted in the portfolio – previously only on "Save as". The password is not stored, only the derived key in memory; after a restart the portfolio is "🔒 locked" and is reconnected with a click on "Unlock". Stop-loss/target prices and AI balance targets now belong to the portfolio and come along when loading (also on another PC). **Backups:** automatic and encrypted (session start, before import, before overwrite, otherwise hourly); kept are the last 10, one per day (30 days) and one per month (12 months). New button **"🕘 Backups"** in the administration: list with date, reason and – after entering the password – number of symbols/positions, restore by double-click (the current state is backed up first). File names include the portfolio name (`Timm_2026-11-15_194200_import.smpf`). After an import, the note "The previous state was backed up" appears. **After a CSV import**, "Save as" appears right away (or the question whether to save into the open portfolio). *(Requested by a user)*
- **💰 Account with all movements** – the dividend account becomes a complete cash account, without a second account. A switch at the top selects the view: **"Dividends only"** shows exactly the previous dividend account (unchanged), **"Everything"** additionally shows buys (debit), sells (credit), deposits/withdrawals, currency exchanges, interest and fees – per currency with balance and total balance in the portfolio currency. Buys and sells come automatically from the portfolio and follow every change. New button **"💰 Account"** in the portfolio overview (4K: directly below "Dividends"; Full HD: directly next to "Dividends"); the existing button in the dividend window opens "Dividends only". When switching to "Everything" for the first time, a setup asks for the start date, the opening balance per currency and whether earlier withdrawals went to the bank or were invested in shares (otherwise they would be deducted twice). Deposits/withdrawals belong to the view in which they were recorded. *(Requested by a user)*
- **📈 Realized gains** – new tab in the account ("Everything" view): for every sold lot the buy and sell price, quantity, holding period, gain in trading currency and in the portfolio currency (exchange rate on the buy and sell date), percentage and source (bank/price). Year filter, totals per year (gains, losses) and **total return = capital gains + dividends − interest and fees** (e.g. margin loan interest). Export to PDF/XLSX/ODS. For older sales without a recorded sell price, the Yahoo closing price of the sale date is used and marked with "≈"; a double-click lets you enter the actual price. New files: `realized_gains.py`, `realized_gains_translations.py`. *(Requested by a user)*
- **Tax statement: account balance and realized gains** – new tab "Realized gains" with all sales of the tax period (holding period, cost, proceeds, gain in the statement currency at the rate on the buy/sell date) and a second summary column. **CH:** account balance as of Dec 31 (per currency at the year-end rate, "Everything" view) is added to the tax value for wealth tax; gains as information only (tax-free on private assets). **DE:** stock gains after the remaining saver's allowance with withholding tax + Soli, loss carryforward; crypto separately (≤ 1 year taxable, > 1 year tax-free). **AT:** KESt 27.5 % on realized gains of new assets (old holdings tax-free), loss offset against dividend KESt. **UK:** CGT in the UK tax year (6 April – 5 April), £3,000 allowance, 18 % / 24 %. **US:** short-term/long-term, $3,000 loss deduction, carryover; possible **wash sales** (repurchase within 30 days after a loss) are flagged. Included in the PDF/XLSX/ODS export and in the tax form PDF with form fields (e.g. Anlage KAP line 20, E1kv, SA108, Schedule D line 7/15).
- **Total return after taxes (estimate)** – the "Realized gains" tab additionally shows the return after taxes below the total return, depending on the tax residence of the dividend account: DE withholding tax + Soli after saver's allowance, AT KESt 27.5 % (old holdings tax-free), each on capital gains and dividends minus withholding tax already deducted; UK CGT 18 % after allowance; US short-term 24 % / long-term 15 % (assumed rates). CH: note instead of an estimate (capital gains tax-free, income tax cantonal). Pure performance and performance after taxes side by side; the account balance stays unchanged.
- **Swissquote import: account movements and reconciliation** – new option "Import account movements": deposits/withdrawals, payments, currency exchanges, interest (incl. debit/margin interest), custody and exchange fees as well as the dividends as booked by the bank (gross, withholding tax, reversals) are taken over into the account. Within the period of the CSV, the "Everything" view uses the actual bank dividends instead of the Yahoo calculation. The account compares its balance with the Swissquote balance and shows "✔ Matches" or the difference per currency. Dividend symbols are matched to the portfolio symbol via the ISIN (`SAAB^B` → `SAAB-B.ST`).
- **Import: fees and net amounts** – the Swissquote and generic imports store the fees, the net amount and (Swissquote) the amount in account currency for every buy and sell, so realized gains and account entries match the bank exactly. Can be disabled via "Import fees and net amounts". The generic import has new optional columns "Fees" and "Net amount" in the column dialog.
- **Import crypto staking** – Swissquote books staking rewards as "Crypto Deposit"; these were ignored, so ETH/SOL quantities were too low. The Swissquote import now shows – only if such entries exist – a checkbox "Import staking rewards (x ETH, y SOL)". The coins are added with a cost basis of 0, the reward appears as a gain of the position. Warning for unusually large single entries (could be a wallet transfer). The generic import offers the new option "As staking reward" for unknown transaction types.
- **Comparison: shares outside the charts** – in the "Compare charts" window, the new button "➕ More shares…" opens the company search. The selected share appears in italics as an additional checkbox and is compared immediately, without replacing one of the charts. Up to 4 additional shares; they are stored in `config.json` and available the next time. Remove with a right-click. The charts in the main window remain unchanged.
- **Adjust the purchase price by hand** – when adding a position, the automatically loaded closing price appears in a confirmation window and can be overwritten, e.g. if the share fluctuated strongly on the purchase day. Shows the currency (incl. a pence note for London) and the day range low–high; if the entered price is more than 10 % outside, Stock Monitor asks again (typo protection). "↺ Closing price" restores the automatic price. **Additional buy (+) and partial sale (−):** date, quantity and price in one window; the closing price is reloaded when the date changes, a manually changed price is kept. Without a Yahoo price, a price can be entered by hand for an additional buy. The sell price is stored on partial sale and evaluated in "Realized gains"; fees and amounts of the remaining lot are reduced proportionally. Replaces the previous "Trading day adjusted" message. *(Requested by a user)*
- **Indices in the chart** – index names such as "SMI", "SPI", "S&P 500", "Nikkei", "Euro Stoxx 50" can be entered directly in the symbol field and are converted to the Yahoo symbol (SMI → `^SSMI`, SPI → `^SSHI` etc., about 30 indices). In the company search the index appears as the first hit. Short names that are also a security on Yahoo (DAX = Global X DAX ETF, DOW = Dow Inc., CAC, HSI) are only offered as an index in the company search, not on direct input.
- **Watchlist: symbol check with suggestions** – symbols are checked for price data on Yahoo before they are added (in parallel, about 1–2 s). Unknown symbols are no longer added but stay in the input field for correction. For typos, clickable suggestions from the screener index lists appear (NVAD → NVDA, APPL → AAPL, TSAL → TSLA); swapped letters count as one error, well-known securities are preferred. Symbols without an exchange are completed (NESN → NESN.SW). Without internet, the symbol is added anyway.

### Changed

- **Import: protection against accidental replacement** – if a CSV contains sales whose purchase is not in the file (e.g. a statement of the last few days only), the import warns that the file covers only part of the period and recommends "Merge"; "Replace" then requires an additional confirmation. When merging, sales already in the portfolio (overlapping periods) are no longer deducted twice – previously this applied only to buys. Swissquote and generic import.
- **Account and tax statement: no reload when opening and switching** – dividends and exchange rates are loaded from Yahoo only once per day. Reopening the account on the same day (via "Dividends" or "💰 Account") shows the values immediately ("As of today HH:MM"), also after a restart. Data is reloaded only when the positions change, on the next day or via 🔄 Refresh. Switching between "Dividends only" and "Everything" no longer recalculates anything – at most a missing exchange rate is loaded, and a rate Yahoo does not deliver is not retried on every switch. The trading currencies for realized gains are remembered for the session. **Tax statement as well:** dividends per share, exchange rates and the realized-gains data are loaded once per day (cache file `.stock_monitor_tax_cache.json`, valid until midnight, also after a restart) – opening it a second time takes a moment instead of several seconds (test with 4 securities: 3.0 s → 0.1 s). Holdings on the ex-date are always recalculated, so buys/sells in between are taken into account immediately; failed requests are not cached. New button **"🔄 Reload"** in the tax statement reloads fresh data on demand (tooltip shows the time of the data; on narrow screens only 🔄). Both columns of the summary scroll, so nothing is cut off with little height (e.g. Full HD at 150 % scaling).
- **Update dialog: countdown stops while reading** – as soon as you scroll, click or press a key in the update window, it no longer closes automatically after 10 seconds. The update function itself is unchanged.
- **Company search: list of hits instead of a single hit** – the search (⌕ in the chart and in the watchlist) shows all hits as a list with symbol, exchange and name. The most likely hit is at the top, bold with ★ and preselected; take it over with a double-click, Enter or "Apply". Previously only one hit could be selected, alternatives were shown as non-clickable text.
- **Company search: only hits with price data** – futures and options are hidden; every hit is checked for price data in advance (max. 6 parallel requests). Indian dual listings: `.BO` is hidden if the same share is listed on the NSE (`.NS`). Note "(x without price data hidden)".
- **Company search: home exchange instead of secondary listing** – if the first Yahoo hit is only a secondary listing (Frankfurt, Munich, Vienna, London IOB …), the same company on its home exchange is preferred, Swiss exchange first. Example: "Mobimo" → `MOBN.SW` instead of `M1H.F`.
- **Chart: understandable message for incomplete Yahoo data** – instead of the technical yfinance error "Dividends events are out-of-range…" a note with a tip appears (other exchange, shorter period).
- **Overview on Full HD: new button arrangement** – "💰 Account" is in row 1 directly next to "Dividends", "Correlation" moves to row 2 after "Sharpe". Row 1 becomes slightly narrower and now also fits at 125 % Windows scaling (previously slightly too wide). 4K unchanged.
- **Account: columns sized by content** – the account columns get the width of their content, the remaining space is distributed (previously all equally wide). On Full HD at 125 % scaling, headers such as "Deposits/Withdrawals" were cut off; the "Everything" view now needs about 840 instead of 1,155 px (EN 800 instead of 1,317 px).
- **Portfolio performance on small screens** – if the header does not fit on the screen (e.g. Full HD at 150 % scaling, 1280 px), Calculate, Monte Carlo, ECY, Export and Close move to a second row. At 100 %/125 % and larger, unchanged in one row.
- **Komplex: toggle in the sector stress test** – "Historical"/"Custom" were cut off at the end when active (bold font). The width now accounts for the bold font.
- **Chart: "Hold." replaces "Finment" for ETFs and funds** – for ETFs/funds the "Hold." button (holdings) now appears instead of "Finment" rather than in addition. Previously the buttons in the "Analysis:" row were cut off, and Finment has hardly any analyses for funds anyway. Stocks unchanged: "Finment" and "Info".
- **Dark mode: checkboxes and radio buttons clearly visible** – in dark mode, checkboxes (chart, zoom, settings …) and radio buttons (e.g. PDF/XLSX/ODS when exporting) were hard to see: the border was barely lighter than the background. Now fixed centrally for the whole program: lighter border, checked = blue with a white check mark or dot. Light mode unchanged. The tooltip of the portfolio name line (overview/administration) was blue on dark in dark mode and hard to read – now in the normal tooltip colors.
- **"Remove all" only clears the overview** – new dialog "Clear overview" with a clear description: the saved portfolio stays unchanged and can be opened again via "Load". If the overview has not been saved yet, a warning offers "Save first…". Account and notes are now cleared as well (previously they remained and were mixed with the next portfolio). Translated buttons instead of "Yes/No".
- **Administration: help button and buttons no longer cut off** – new button "❓ Help" (jumps to the administration section with an overview of all buttons). "🗑 Delete portfolio" is now called "🗑 Clear overview" (the saved portfolio is not deleted). The window opens wide enough for all buttons (4K: one row, previously labels were cut off); if the screen is too narrow (e.g. Full HD at 125 %), the buttons are arranged in two rows.
- **Continue the demo portfolio as your own portfolio** – after "Save as" under your own name, the demo banner and "sample portfolio" watermark disappear immediately – previously only after a restart. The name "Demo" is reserved so the sample portfolio cannot be overwritten with a password (it could no longer be opened otherwise). The demo itself is not saved automatically; the tooltip of the name line explains this.
- **Comparison window wider** – 95 % instead of 82 % of the screen width; the counter "Select at least 2" is no longer cut off (width based on the longest text, also EN). **Full HD and WQHD (up to 2560 px):** the period selector is now at the top next to the counter, the additional stocks and "➕ More shares…" have their own row below the charts (indented below the first checkbox); the chart checkboxes wrap when needed. Previously, with 16 charts plus additional stocks the window became wider than the screen (at 125 % scaling already with 16 charts and no additional stocks), so the last checkboxes and the period selector could not be reached.
- **Help extended** – new sections "Account" (views, setup, columns, reconciliation with the bank) and "Realized gains"; tax module with "Account balance and realized gains" (table per country); Swissquote import with import options and "Replace or merge?"; generic import with the new columns. New section "Company search" incl. indices (table of short names); "Comparison" described in detail (additional shares, limit, right-click); watchlist with symbol check and suggestions (DE/EN).

### Fixed

- **Austrian tax statement: KESt on unrealized gains** – the AT statement estimated KESt on *unrealized* price gains of the open positions and added it to the total tax. KESt is only due on realization; it is now calculated from the actual sales of the tax year.
- **Import: sales matched to the wrong purchases** – the Swissquote CSV is sorted by date in descending order, and sales were processed in that order: a later sale "used up" the oldest purchases, and an earlier sale was then matched with purchases made only after the sale. For securities traded several times, the remaining open positions (purchase date, cost price) were therefore wrong. Sales are now processed chronologically and only against purchases up to the sale date (FIFO), also in the generic CSV import. Affected portfolios: import the Swissquote CSV again ("Replace").
- **Import: buys and parts of sales wrongly discarded as duplicates** – two genuine buys with the same date and quantity in the same file (e.g. twice 1 Samsung on the same day) were treated as duplicates and the second was missing. Parts of sales were also lost if a purchase was sold in several orders on the same day (e.g. DELL 23 + 8 shares) – the positions were correct, but the sales history was incomplete. Only entries that were already in the portfolio before the import now count as duplicates. Swissquote and generic import; please re-import affected portfolios.
- **Company search: OK did nothing** – typing a name and pressing OK directly returned to the chart without a result, because a symbol was only set after "Search". Enter in the search field also closed the dialog. Now "Apply" without hits starts the search, Enter in the search field only searches.
- **Comparison: "nan%" for individual shares** – if Yahoo delivered empty closing prices (e.g. `000660.KS` SK hynix), the comparison showed "nan%" and a broken line. Empty prices are now removed before the calculation (comparison and export).
- **Swissquote import: Swiss small caps not found** – Swissquote partly uses shorter tickers than SIX (`MOB` instead of `MOBN` for Mobimo), which resulted in the non-existent `MOB.SW`. If a symbol delivers no prices, it is now looked up via the ISIN from the CSV (`CH0011108872` → `MOBN.SW`), with the exchange matching the trading currency. Positions already imported with a wrong symbol (e.g. `MOB.SW`) remain and must be re-imported or corrected by hand.
- **Swissquote import: wrong symbols for short tickers** – Kinross Gold (`K`) was imported as the KOSPI index (`^KS11`) because the Yahoo search returned the index first. Symbol resolution no longer accepts indices, currencies or futures; imports only take over exact hits.
- **Swissquote import: exchange from trading currency** – the suffix is now derived from the trading currency (CAD → `.TO`, CHF → `.SW`, GBP → `.L`, JPY → `.T`, SEK → `.ST`, HKD, AUD, NOK, DKK). Kinross in CAD thus becomes `K.TO`. Securities traded in USD with a foreign ISIN (e.g. Garmin, Chubb) no longer get a wrong `.SW`/`.L`. Share classes such as `SAAB^B` become `SAAB-B.ST`.
- **Swissquote import: London shares missing** – Swissquote writes LSE tickers with a trailing dot (`RR.` = Rolls-Royce), which resulted in the invalid symbol `RR.`. Now becomes `RR.L`. GBP prices from the CSV are also converted to pence (Yahoo quotes LSE in GBp), and the historical FX rate uses `GBPCHF=X` instead of the non-existent `GBpCHF=X`.
- **Swissquote import: US shares bought in EUR** – with trading currency EUR, a European exchange is preferred (e.g. `NVD` → `NVD.DE` instead of the US ETF of the same name, `WMT` → `WMT.MU`, `ASML` → `ASML.AS`). Identical tickers in different currencies are no longer mixed up.
- **Mac App Store: files only readable/writable in "Downloads"** – in the App Store version, CSV import and all exports (Excel, PDF, ODS …) outside the "Downloads" folder failed with "Operation not permitted", even though the file had been selected in the dialog. Cause: inside the app sandbox, Qt manages the access grant for the selected file itself, so Python no longer had access. The selected file now stays accessible to the app – import and export work in any folder (e.g. Documents, Desktop). The DMG, Windows and Linux versions were not affected.
- **Windows: focus after CSV import** – after the import (and the following save prompt), Windows brought the Explorer window of the CSV selection to the front instead of Stock Monitor. Focus now returns directly to the main window, as with the other dialogs.

---

## [5.9.0] – 2026-11-08

### Added

- **Logarithmic price axis** – new "Log" checkbox in the zoom view (line and candlesticks). Equal percentage changes appear equally high – ideal for long periods (5Y, Max). Clearly readable axis labels; crosshair and Bollinger Bands are scaled correctly; the setting is saved. *(Requested in an App Store review)*
- **Dividend account** – new multi-currency account in the dividend window (button "💰 Dividend account"). Dividends are automatically credited on the ex-date, with the holdings at that time, to the account of their currency; withholding tax depends on the company's country of domicile and your own tax residence (CH/DE/AT/UK/US, W-8BEN). Gross/net toggle, total balance in the portfolio currency, double-click shows all bookings of an account with running balance. Manual deposits/withdrawals, dividends can be corrected, export to PDF/XLSX/ODS. Stored encrypted together with the portfolio. New files: `dividend_account.py`, `dividend_account_translations.py`. While loading, the familiar dollar bill with progress indicator appears.
- **Austrian tax report: accumulated income (AGE)** – new button "📝 Enter AGE": manually enter the values of accumulating funds from the OeKB report (AGE and creditable withholding tax per unit, inflow date). KESt on AGE is calculated with the holdings on the inflow date and appears in separate columns, in the summary, in the total tax and in all exports. The dialog shows only funds/ETFs (option "Show all positions"); the currency of the OeKB report can be selected and is converted at the rate on the inflow date. Alternating light/grey rows (also with hidden rows and in dark mode); OeKB link readable in dark mode.
- **Sales history** – sales (manual partial sale, broker import) are stored internally with their date. The main view still shows only open positions, but the dividend account and tax report know the holdings on every ex-date – even for positions sold completely (they appear in the tax report of the year of sale with quantity 0). The partial sale dialog now also asks for the sale date (also retroactively; default = last trading day; weekends are rejected, on holidays of the respective exchange a warning appears with "Use this date anyway?"; crypto 24/7). Stored encrypted together with the portfolio.

### Changed

- **Help extended** – new sections on log scale, dividend account and tax module (currency, country of domicile & withholding tax, AT AGE); Austrian tax help with the new columns and AGE instructions (DE/EN).
- **Tax report: window size** – opens wide enough for all buttons to be fully visible (max. 95 % of the screen), centred. On small screens (e.g. Full HD at 150 % scaling) a compact header and a lower table.
- **Monte Carlo (portfolio and scenarios): legend** – legend bar above the charts instead of a legend inside the chart; on Full HD the curves are no longer covered. The gap to the title is measured and identical at every resolution/scaling. In comparison mode a single shared Y-axis label instead of two overlapping ones.
- **Exchange calendar** – holidays are now calculated from fixed rules (Easter, "3rd Monday in January", substitute days) instead of being maintained by hand, for 2024–2028. New with holidays: Vienna, Milan, Madrid, Lisbon, Stockholm, Oslo, Copenhagen, Helsinki, Johannesburg, Mexico, São Paulo, NZX, CME. Used for the exchange hours display and in the partial sale dialog.
- **yfinance 1.8.0** – data library updated to the latest version.

### Fixed

- **Monte Carlo Scenarios: result table unreadable in dark mode** – light row colours with light text; now a dark palette as in the portfolio view. Better contrast for green/red in light mode as well. Grid lines of both Monte Carlo tables clearly visible in dark mode. Column lines of header and table no longer offset by 1 pixel on scaled screens (125 % and above, e.g. 4K).
- **Help: table of contents** – "Candlestick" jumped to "Stop-Loss & Target Price", "News" (EN) led nowhere.
- **Tax help: price information** – described "price as of 31 Dec (year-end price)", but the report uses the current price; texts corrected.
- **Monte Carlo: axis label** – "Portfolio value (USD) (USD)", or for CHF portfolios "Portfolio value (USD) (CHF)"; now only the actual currency.
- **Tax report: country of domicile of securities** – the country of domicile was never detected (positions store no country): in the CH report every foreign share was treated as a US share, in the AT report as an Austrian one. The country is now determined from Yahoo company data (Apple stays US, even on the Frankfurt exchange), for ETFs from the fund name (UCITS → IE/LU without withholding tax, "(CH)" → Swiss withholding tax), otherwise from the exchange suffix. The result is cached.
- **Tax report CH/AT: correct treaty rates** – new table with the residual rates per country (UK, HK, SG, UCITS funds 0 %; FR 12.8 %; JP/FI 10 %; mostly 15 %). Fixed among others: UK dividends in AT wrongly with 15 % withholding tax, Austrian shares in the CH report with a flat 30 %, unknown exchanges in the AT report treated as Austrian, UCITS ETFs on SIX with 35 % Swiss withholding tax.
- **Tax report: UK dividends 100× too high** – Yahoo delivers dividends of London shares in pence; they were counted as pounds. Now converted correctly (also ZAc, ILA).
- **Tax report: mixed currencies** – dividends and prices in USD, GBP, CHF etc. were added without conversion and shown as EUR/CHF. Now everything is in the report currency (AT/DE EUR, CH CHF, UK GBP, US USD): dividends at the rate on the ex-date, prices/market values at the current rate. Note in the report if a rate is missing.
- **Tax report: current price** – the purchase price was always shown as the current price (price cache read incorrectly); market value and the KESt estimate on capital gains were therefore wrong.
- **Tax report: sale on the ex-date** – positions sold on the ex-date wrongly lost their dividend entitlement; positions bought on the ex-date were wrongly counted. Now the same rule as in the dividend account (bought before the ex-date, not sold before the ex-date).
- **Exchange hours: wrong holidays 2027** – Easter 2027 was stored as 25 April instead of 28 March; Good Friday/Easter Monday (all exchanges) and Ascension/Whit Monday (SIX) were wrong. Further corrections: SIX without a substitute day for 1 August, Berchtold's Day added; Toronto Civic Holiday added; ASX/Toronto substitute days at Christmas; Tokyo substitute and bridge holidays.
- **Dividend Kings / Aristocrats updated (as of November 2026)** – the list had not been maintained since 2025 and contained errors: among others 3M and V.F. Corp (dividend cut) still listed as Kings, AT&T, Walgreens, Ventas and others wrongly as Aristocrats. New among others: Carlisle, McDonald's, MGE Energy, Pentair, ADM, RLI, United Bankshares (Kings); Erie, Eversource, FactSet, Brown-Forman, Cardinal Health, West Pharmaceutical and others (Aristocrats). Renamings taken into account (Marzetti MZTI, H2O America HTO).
- **Austrian tax report: notes column missing** – the table had one column too few, so the treaty notes were never shown; the column titles "Withholding tax/treaty rate" did not match the values (KESt / foreign withholding tax).
- **macOS: digits with wide spacing** – in labels and buttons containing emoji (e.g. ECY row "4 1 . 0", Monte Carlo Scenarios "± 1 0 % limit") "Apple Color Emoji" was used as the main font, whose digits are wide keycap glyphs. Now the system font with the emoji font as fallback.

---

## [5.8.0] – 2026-11-02

### Added
- **Double-click to zoom:** In the portfolio overview, a double-click on any chart opens it in zoom mode; a second double-click closes it again (feature request from a user in Australia)

### Changed
- **Tax data updated to 2026** for all five supported countries:
  - 🇬🇧 UK: Dividend Tax raised by 2 pp to **10.75 % / 35.75 % / 39.35 %** (Basic / Higher / Additional), effective 6 April 2026
  - 🇬🇧 UK: CGT rates unchanged at **18 % (Basic) / 24 % (Higher)**, Annual Exempt Amount £3,000
  - 🇨🇭 CH: Verrechnungssteuer 35 % — unchanged
  - 🇩🇪 DE: Abgeltungsteuer 25 % + Soli 5.5 % — unchanged; Freistellungsauftrag €1,000
  - 🇦🇹 AT: KESt 27.5 % — unchanged
  - 🇺🇸 USA: Long-Term Capital Gains 0 / 15 / 20 % — unchanged
- Tax module version string updated to `2026-01`
- UK tax year label in info text now dynamic (`{year}/{year_plus1}`) — no longer hardcoded

---

## [5.7.4] – 2026-10-30

### Changed
- Monte Carlo Scenarios: Y-axes in dual-chart mode synchronised (same scale top/bottom)

### Fixed
- Candlestick chart: doji candles (Open = Close) no longer create tall spike bars — minimum body height is now price-based (`5 % of median bar range`) instead of time-based (`candle_w × 0.05` in seconds), which caused bodies up to 9 CHF/USD tall on 5-minute charts

---

## [5.7.3] – 2026-10-17

### Fixed
- AI Balance: replaced `ticker.news` (broken in yfinance ≥ 1.7.0 with HTTP 500) with direct Yahoo Finance v1 API — same fix already applied to chart news
- AI Balance + Chart News: fallback to company-name search when symbol search returns no results (affects non-US tickers like ABBN.SW, SIE.DE, SREN.SW)

---

## [5.7.2] – 2026-10-14

### Fixed
- Stock Rating: QThread cleanup via `finished` signal, `RuntimeError` caught safely when closing quickly
- Screener: `finished` signal renamed to `done` (resolved Qt internal signal name conflict), thread cleanup improved
- Zoom chart: `UrlFinderThread` safe cleanup on close (macOS crash fix)

---

## [5.7.1] – 2026-10-11

### Fixed
- macOS ≥ 14 / Flatpak: `RLIMIT_NOFILE` raised to 10240 at startup to prevent file-descriptor crashes
- Performance dialog: parent window and window flags set correctly (macOS rendering fix)
- Screen geometry: `self.screen()` fallback for multi-monitor setups
- Thread pool: maximum 6 workers enforced consistently everywhere (avoids Yahoo rate limiting)
- Screener help (DE/EN): all 18 indices now documented

---

## [5.7.0] – 2026-10-02

### Added
- **Monte Carlo Scenarios** (accessible from portfolio overview): scenario editor with full Monte Carlo simulation, comparison against the real portfolio, export as PDF/XLSX/ODS
- **Quick Search** in Stock Screener: pre-computed daily data for instant filtering without a new download
- Help: new sections for Monte Carlo Scenarios and Quick Search; keyword index updated

---

## [5.6.0] – 2026-08-31

### Added
- **Stress Test** (Correlation window): new button runs the portfolio through 15 historical crisis scenarios (Dotcom, 2008, COVID, …)
- **Advanced Analysis – 7 tabs** (accessible from the stress test dialog):
  - Tab 1 – Factor Exposure: Beta + R² against 5 benchmarks (SPY, AGG, GLD, VNQ, GSG)
  - Tab 2 – Rolling Correlation: 30/60/90-day windows, portfolio vs. benchmark
  - Tab 3 – VaR / CVaR: historical simulation, Calmar Ratio, Skewness, Kurtosis, Tail Ratio
  - Tab 4 – Drawdown Analysis: underwater chart, top-5 drawdowns, peak→trough, recovery time
  - Tab 5 – Stress & Correlation: normal vs. crisis periods, Lombard credit calculator
  - Tab 6 – Sector Stress Test: GICS breakdown for 15 historical scenarios (historical + custom)
  - Tab 7 – Historical Chart: crisis-period chart with portfolio overlay, synthetic data back to 1907
- **Stock Screener** (accessible from the watchlist): 12 indices (S&P 500, Nasdaq 100, Nasdaq Extra, DAX, SMI, CAC 40, FTSE 100, Nikkei 225, TSX, ASX 200, Russell 2000), filter by 1-year performance band and max. P/E ratio, AND/OR logic, direct chart access from results
- **Stock Rating** in zoom chart: 1–5 star rating (half-star precision), 6 categories (Performance, Risk, Technical, Suitable for Trading, Long-term Suitability, Analyst Recommendation), overall rating as weighted average
- macOS: automatic update via DMG (`_do_macos_update`), update dialog now supports DMG URL

### Changed
- AI analysis model updated to `gemini-3.5-flash-lite`
- yfinance updated to 1.7.0
- World map tile service switched from CARTO to Esri World Light Gray (CARTO now requires an API key; OSM blocks desktop apps without a Referer header)

### Fixed
- Dividends: total amount in the dividend details window now correctly formatted (e.g. CHF 1,870 instead of wrong format)
- Sector stress test: first dropdown entry «— No scenario —» resets all sector values to 0%
- Advanced Analysis: no crash when closing the dialog before the data loader thread finishes (`_on_done`, `_on_error`, `_update_rolling` now check whether the dialog is still open)
- Correlation window (Windows): main window is explicitly brought to the foreground after closing so Windows does not focus a browser window instead
- Watchlist dialog: correct centering on Full HD displays — two root causes fixed: Qt's `adjustPosition` centering on parent instead of screen, and screener button inflating toolbar min-width before `move()` was called
- All dialogs (28 locations in `stock_monitor.py`, 1 each in `komplex.py` and `stress_test.py`): use `self.screen()` instead of `QApplication.primaryScreen()` so dialogs always appear on the monitor that contains the main window

---

## [5.5.0] – 2026-07-29

### Added
- Sortino Ratio in zoom chart (new «So» checkbox next to the Sharpe checkbox)
- Portfolio Sortino Ratio dialog accessible from the Sharpe dialog

### Fixed
- Watchlist: last available closing price is now used when the market is closed, instead of showing «no data»
- Favourites: clicking the chart star dropdown adds the stock directly if it is not yet in the favourites list

### Changed
- Help section expanded with a Sortino deep-dive, extended Favourites and Watchlist sections
- yfinance updated to 1.5.2

---

## [5.4.4] – 2026-07-09

### Added
- Zoom chart now saves its own indicator settings (MA, Trend, Beta etc.) independently per stock — settings are preserved across sessions

### Changed
- Global settings now also apply to the currently open zoom chart
- Zoom chart indicator state is restored when reopening a chart

### Fixed
- Windows: loading stocks with maximum time range (e.g. McDonald's, Coca-Cola) no longer fails with Errno 22

---

## [5.4.3] – 2026-06-22

### Fixed
- Dark mode: company info box and AI assessment box are now readable (hard-coded background color removed)
- RI-Factor tooltip text corrected: left-click (not right-click) opens the detail view

---

## [5.4.2] – 2026-06-16

### Fixed
- Company name now appears correctly in the portfolio overview tooltip on Full HD displays (1920×1080)

---

## [5.4.1] – 2026-06-02

### Fixed
- Critical crash (SIGABRT / Signal 6) when opening the portfolio or closing the app while portfolio data was loading. Caused by unsafe thread termination (`pthread_cancel` on Python threads) and a race condition in the update worker. Workers now use cooperative cancellation (`requestInterruption`) and `finished.connect(deleteLater)` for safe shutdown.
- Sorting by the G/V column in the portfolio overview now correctly uses CHF-based gain/loss values. Previously, positions losing in CHF (due to USD/CHF currency effects) could appear among the winners.
- Sorting by the Performance Contribution column now correctly uses CHF-based values when CHF is selected. Same USD-vs-CHF root cause as the G/V sort fix.
- Linux (RPM): Library installation (yfinance etc.) no longer requires root privileges. The launcher now installs packages directly into `~/.local/share/stock-monitor/lib`, making installation via Discover and other graphical package managers fully reliable.

---

## [5.4.0] – 2026-05-25

### Added
- Portfolio correlation matrix: shows how strongly securities move in relation to each other. Time period selectable (1 month to 5 years). Accessible from the portfolio overview.

### Fixed
- Dark mode: various UI corrections
- CSV import: fix for edge cases
- RI-Factor help now opens with a left-click on the ✅/⚠️ symbol (no right-click required)

### Changed
- Chart labels (Beta, Alpha, Sharpe Ratio) and update dialog now use the translation system (available in English)

---

## [5.0.3] – 2026-04-23

### Fixed
- Sharpe Ratio: minus sign was missing in explanation text for negative values
- Several translation errors in German UI corrected
- Window title now shows the correct version number dynamically
- yfinance update: new version is now active immediately after restart
- yfinance update crash on Linux (deb/rpm) caused by Qt thread-safety violation
- Restart dialog wording made consistent across platforms

### Changed
- Currency calculator remembers the last selected currency pair across sessions
- Restart dialog now offers "Restart now" and "Restart later" consistently on all platforms

---

## [5.0.2] – 2026-04-21

### Fixed
- Exchange status indicators (open/closed lights) now rendered as colored dots instead of emoji — fixes rendering issues on some Linux desktop environments
- Gemini AI: graceful error message when API returns HTTP 503
- Translations: several keys were missing or untranslated in Flatpak environment
- SyntaxError in translations.py caused by non-ASCII quotation marks
- £ (GBP) and ¥ (JPY) currency symbols missing in AI balance target dialog
- MIT license restored — metainfo had incorrectly listed GPL-3.0
- App downloaded update files to ~/Downloads (KDE auto-opened the folder); changed to ~/.cache

### Added
- "Open folder" button in error log hint dialog for easier log access

---

## [5.0.1] – 2026-04-19

### Added
- **Self-update for Windows EXE**: app detects new releases on GitHub and updates itself automatically — no manual download required
- yfinance update button in update dialog — installs newer versions directly from within the app
- Portable mode for Windows: all data stored next to the executable when run from a portable location
- Demo portfolio included in Windows EXE build (no login required)
- First-start layout: 12 charts at Full HD, 16 charts at 4K automatically

### Fixed
- Update check now only shows "update available" notification when a genuinely newer version exists
- SSL certificate handling for update check in PyInstaller EXE
- Admin window opens centered instead of at fixed screen position (100, 100)
- Several data path issues when running as packaged EXE on Windows

### Changed
- Help section expanded with update instructions and Flatpak-specific notes

---

## [5.0.0] – 2026-04-13

Initial public release of Stock Monitor v5.

### Features
- Real-time and historical stock/ETF/fund price charts via yfinance
- Multi-portfolio management with password protection
- Dividend tracking and tax module (Switzerland, Germany, Austria)
- AI-powered portfolio analysis (Google Gemini)
- Currency converter with live rates
- World market map
- Export to Excel, PDF, ODS
- Full German and English UI
- Available for Windows (EXE), Linux (deb, Flatpak)
