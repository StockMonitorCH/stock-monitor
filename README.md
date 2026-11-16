# 📈 Stock Monitor

**Professional stock portfolio management for Windows, macOS and Linux**

Stock Monitor is a free, open-source desktop application for tracking and analysing your investment portfolio. Monitor stocks, ETFs, cryptocurrencies and commodities across all major global exchanges — all in one place, without any cloud or subscription.

![Stock Monitor Dashboard](screenshots/dashboard_EN.png)

---

## ✨ Features

### 📊 Charts & Technical Analysis
- Up to **16 simultaneous live charts** (4 / 6 / 8 / 12 / 16)
- Time periods: 1D · 1W · 1M · 3M · 6M · 1Y · 5Y · Max
- Moving averages: MA 20 / 50 / 200
- RSI indicator, Bollinger Bands, Trendline, Candlestick, Drawdown
- Crosshair with detailed tooltip
- Double-click any chart for fullscreen zoom mode
- Auto-Refresh: 30 sec / 1 min / 5 min

### 💼 Portfolio Management
- Stocks, ETFs, cryptocurrencies and commodities in one portfolio
- Multi-currency support: USD · CHF · EUR · GBP
- Import from **Swissquote** and **Generic CSV**
- AES-256-GCM encrypted portfolio files (`.smpf`)
- Auto-save on close, auto-restore on next launch

![Portfolio Overview](screenshots/portfolio_EN.png)

### 🏦 Account & Realized Gains
- Complete cash account: buys and sells come automatically from the portfolio, plus deposits/withdrawals, currency exchanges, interest and fees
- Multi-currency account: balance per currency and total balance in the portfolio currency
- **Realized gains per lot** – buy/sell price, holding period, gain in trading and portfolio currency
- Total return = capital gains + dividends − interest and fees, plus an after-tax estimate
- Swissquote import with account movements and reconciliation

![Account – Realized Gains](screenshots/konto_EN.png)

### 🔍 Portfolio Analysis
- **Performance comparison** – all positions as bar chart
- **Sector distribution** – GICS sector breakdown
- **Region distribution** – geographic allocation on world map
- **Sharpe Ratio, Alpha, Beta** analysis
- **Monte Carlo Simulation** – thousands of future scenarios

![Monte Carlo Simulation](screenshots/montecarlo_EN.png)

### 🧠 Komplex Analysis
Institutional-grade risk analysis in 7 tabs:
- **Factor exposure** – beta & R² against 5 benchmarks (S&P 500, bonds, gold, real estate, commodities)
- **Rolling correlation** (30/60/90 days) – shows when diversification breaks down in a crisis
- **VaR / CVaR**, Calmar Ratio, skewness, kurtosis, Tail Ratio
- **Drawdown analysis** – underwater chart and the 5 worst drawdown periods
- **Sector stress test** – 15 historical scenarios or fully custom

![Komplex Analysis](screenshots/komplex_EN.png)

### 🔎 Stock Screener
- Filter **18 indices** (S&P 500, Nasdaq 100, DAX, SMI, CAC 40, FTSE 100, Nikkei 225, Russell 2000 and more) by 1-year performance and P/E
- Add results directly to favorites / watchlist or open the zoom chart

![Stock Screener](screenshots/screener_EN.png)

### ⭐ Stock Rating
- Overall rating from **6 weighted categories**: performance, risk, technical, trading suitability, long-term suitability, analyst recommendation
- Up to 5 stars per category – a quick read, not a buy recommendation

![Stock Rating](screenshots/bewertung_EN.png)

### 🤖 AI Features
- **AI Balance** – rebalancing proposals weighted by analyst consensus and news sentiment
- **AI Analysis** – Google Gemini AI-powered portfolio analysis (API key required)

![AI Balance](screenshots/ai-balance_EN.png)

### 🌍 World Map
- Interactive map showing geographic distribution of all holdings
- Position size proportional to portfolio weight

![World Map](screenshots/worldmap_EN.png)

### 🧾 Tax Module
- Tax reports for **CH · DE · AT · UK · US**
- Dividend withholding tax calculation
- Export as PDF, XLSX or ODS

![Tax Module](screenshots/tax_EN.png)

### 📤 Export
- **PDF** – charts and portfolio data
- **Excel (XLSX)** – with colour-coded values and 3D bar chart
- **ODS** – LibreOffice compatible
- **Watchlist** – compare up to 50 symbols in a single chart

---

## 💻 Download & Installation

All downloads are on the **[latest release page](https://github.com/StockMonitorCH/stock-monitor/releases/latest)**.

### Windows (Portable)
1. Download `stock_monitor.zip`
2. Extract to any folder
3. Run `stock_monitor.exe` — no installation required

[⬇ Download for Windows](https://github.com/StockMonitorCH/stock-monitor/releases/latest/download/stock_monitor.zip)

### macOS
Download the `.dmg` file from the [latest release](https://github.com/StockMonitorCH/stock-monitor/releases/latest), open it and drag Stock Monitor into the Applications folder.

### Linux (Flatpak)

**Option 1 – One-click install (recommended)**

Click the link below — your software centre (GNOME Software, KDE Discover) opens automatically and installs Stock Monitor including automatic future updates:

[⬇ Install via Flatpak](https://StockMonitorCH.github.io/stock-monitor/StockMonitor.flatpakref)

Or from the terminal:
```bash
flatpak remote-add --user stockmonitor https://StockMonitorCH.github.io/stock-monitor/repo
flatpak install stockmonitor ch.stockmonitor.StockMonitor
```

**Option 2 – Direct download**

Download the `.flatpak` file from the [latest release](https://github.com/StockMonitorCH/stock-monitor/releases/latest), then:

```bash
flatpak install StockMonitor-*.flatpak
```

### Run from source
```bash
pip install PyQt6 yfinance pandas matplotlib pyqtgraph cryptography
python stock_monitor.py
```

---

## 🚀 Getting Started

Stock Monitor launches with a **pre-loaded Demo portfolio** — no password required. Explore all features immediately, then create your own portfolio via ⚙ Administration.

**Quick start:**
1. Enter a symbol (e.g. `AAPL`, `NESN.SW`, `BTC-USD`) in any chart → Enter
2. Select a time period (1M / 6M / 1Y / 5Y)
3. Double-click a chart for fullscreen with RSI, Bollinger Bands, Candlestick
4. Create a portfolio: ⚙ Administration → Add positions → 💾 Save

---

## 🔒 Privacy

- **No cloud, no server, no account** — all data stays on your computer
- Portfolio files are encrypted with **AES-256-GCM**
- Market data is fetched directly from Yahoo Finance

---

## 🌐 Links

- **Website:** [stock-monitor.ch](https://www.stock-monitor.ch)
- **Support:** [info@stock-monitor.ch](mailto:info@stock-monitor.ch)

---

## ❤️ Support the Project

Stock Monitor is free and developed in spare time. If you enjoy it, any donation is appreciated:

**PayPal:** [paypal.me/StockMonitor](https://paypal.me/StockMonitor)

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
