# Changelog

All notable changes to Stock Monitor are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
