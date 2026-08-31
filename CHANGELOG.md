# Changelog

All notable changes to Stock Monitor are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
- Available for Windows (EXE), Linux (deb, rpm, Flatpak)
