# Changelog

All notable changes to Stock Monitor are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
