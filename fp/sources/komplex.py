"""
komplex.py – Portfolio Komplex-Analyse für Stock Monitor
=========================================================
Tab 1 – Faktorexposition       : Beta vs. 5 Benchmarks
Tab 2 – Rollende Korrelation   : Portfolio vs. Benchmark über Zeit
Tab 3 – VaR / CVaR             : Historische Simulation + Kennzahlen
Tab 4 – Drawdown-Analyse       : Underwater-Chart, Top-5-Drawdowns, Dauer/Erholung
Tab 5 – Stress & Korrelation   : Korrelations-Breakdown + Stress-Beta + Margin-Call
Tab 6 – Sektor-Stresstest      : GICS-Sektoraufschlüsselung unter hist. Szenario
Tab 7 – Historischer Chart     : Bloomberg-Style Krisenperiodenchart mit Annotationen

Datenabruf via yfinance, max. 6 Threads.
Alle UI-Strings: komplex_translations.py (TRK).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from collections import OrderedDict

from komplex_translations import TRK

# ── Benchmarks / Perioden ─────────────────────────────────────────────────────
BENCHMARKS: OrderedDict = OrderedDict([
    ("SPY", "bm_spy"),
    ("AGG", "bm_agg"),
    ("GLD", "bm_gld"),
    ("VNQ", "bm_vnq"),
    ("GSG", "bm_gsg"),
])

PERIODS: OrderedDict = OrderedDict([
    ("6mo", "period_6mo"),
    ("1y",  "period_1y"),
    ("2y",  "period_2y"),
    ("3y",  "period_3y"),
])

_CRISIS_THRESHOLD = -0.015   # SPY-Tagesrendite < -1.5 % → Krisentag

# ── Szenarien (Tab 6 + 7) ──────────────────────────────────────────────────────

# Krisenperioden: {scenario_id: (chart_ticker, start, end)}
_SCENARIO_WINDOWS: dict = {
    "1907": ("^DJI",  "1906-07-01", "1908-12-31"),
    "1929": ("^DJI",  "1929-09-01", "1932-12-31"),
    "1937": ("^DJI",  "1937-03-01", "1938-12-31"),
    "1946": ("^DJI",  "1946-05-01", "1947-12-31"),
    "1956": ("^DJI",  "1956-04-01", "1957-12-31"),
    "1962": ("^DJI",  "1962-01-01", "1963-06-30"),
    "1966": ("^GSPC", "1966-01-01", "1967-06-30"),
    "1970": ("^GSPC", "1969-12-01", "1971-06-30"),
    "1973": ("^GSPC", "1973-01-01", "1975-06-30"),
    "1980": ("^GSPC", "1980-01-01", "1982-12-31"),
    "1987": ("^GSPC", "1987-08-01", "1988-06-30"),
    "2000": ("SPY",   "2000-03-01", "2002-12-31"),
    "2007": ("SPY",   "2007-10-01", "2009-06-30"),
    "2020": ("SPY",   "2020-02-01", "2020-09-30"),
    "2022": ("SPY",   "2022-01-01", "2023-06-30"),
}

# Sektor-ETFs (für live-Datenabgleich bei Szenarien ab 1998)
_SECTOR_ETFS: dict = {
    "Communication Services": "XLC",    # ab 2018-06
    "Consumer Discretionary":  "XLY",   # ab 1998-12
    "Consumer Staples":        "XLP",   # ab 1998-12
    "Energy":                  "XLE",   # ab 1998-12
    "Financials":              "XLF",   # ab 1998-12
    "Health Care":             "XLV",   # ab 1998-12
    "Industrials":             "XLI",   # ab 1998-12
    "Information Technology":  "XLK",   # ab 1998-12
    "Materials":               "XLB",   # ab 1998-12
    "Real Estate":             "XLRE",  # ab 2015-10
    "Utilities":               "XLU",   # ab 1998-12
}

# Sektormultiplikatoren relativ zum Gesamt-Marktdrawdown (1.0 = wie Markt)
# Kalibriert nach historischen Aufzeichnungen (NBER / Shiller-Daten)
_SECTOR_MULTIPLIERS: dict = {
    "1907": {
        "Communication Services": 0.90, "Consumer Discretionary": 1.10,
        "Consumer Staples": 0.50,       "Energy": 0.85,
        "Financials": 1.65,            "Health Care": 0.60,
        "Industrials": 1.20,           "Information Technology": 0.95,
        "Materials": 1.10,             "Real Estate": 1.40,
        "Utilities": 0.70,             "Unknown": 1.00,
    },
    "1929": {
        "Communication Services": 1.05, "Consumer Discretionary": 1.35,
        "Consumer Staples": 0.65,       "Energy": 1.00,
        "Financials": 1.60,            "Health Care": 0.75,
        "Industrials": 1.30,           "Information Technology": 1.15,
        "Materials": 1.25,             "Real Estate": 1.50,
        "Utilities": 0.90,             "Unknown": 1.10,
    },
    "1937": {
        "Communication Services": 0.90, "Consumer Discretionary": 1.10,
        "Consumer Staples": 0.55,       "Energy": 0.90,
        "Financials": 1.45,            "Health Care": 0.65,
        "Industrials": 1.30,           "Information Technology": 1.05,
        "Materials": 1.15,             "Real Estate": 1.20,
        "Utilities": 0.80,             "Unknown": 1.00,
    },
    "1946": {
        "Communication Services": 0.85, "Consumer Discretionary": 1.30,
        "Consumer Staples": 0.50,       "Energy": 0.80,
        "Financials": 1.10,            "Health Care": 0.55,
        "Industrials": 1.25,           "Information Technology": 0.90,
        "Materials": 1.10,             "Real Estate": 1.00,
        "Utilities": 0.65,             "Unknown": 0.95,
    },
    "1956": {
        "Communication Services": 0.90, "Consumer Discretionary": 1.15,
        "Consumer Staples": 0.55,       "Energy": 0.85,
        "Financials": 1.10,            "Health Care": 0.60,
        "Industrials": 1.15,           "Information Technology": 0.95,
        "Materials": 1.05,             "Real Estate": 1.00,
        "Utilities": 0.70,             "Unknown": 0.95,
    },
    "1962": {
        "Communication Services": 0.95, "Consumer Discretionary": 1.10,
        "Consumer Staples": 0.60,       "Energy": 0.85,
        "Financials": 1.15,            "Health Care": 0.65,
        "Industrials": 1.10,           "Information Technology": 1.20,
        "Materials": 1.00,             "Real Estate": 1.05,
        "Utilities": 0.70,             "Unknown": 1.00,
    },
    "1966": {
        "Communication Services": 0.90, "Consumer Discretionary": 1.15,
        "Consumer Staples": 0.55,       "Energy": 0.80,
        "Financials": 1.40,            "Health Care": 0.65,
        "Industrials": 1.10,           "Information Technology": 1.05,
        "Materials": 1.00,             "Real Estate": 1.20,
        "Utilities": 0.70,             "Unknown": 1.00,
    },
    "1970": {
        "Communication Services": 1.10, "Consumer Discretionary": 1.15,
        "Consumer Staples": 0.55,       "Energy": 0.75,
        "Financials": 1.20,            "Health Care": 0.70,
        "Industrials": 1.10,           "Information Technology": 1.60,
        "Materials": 1.00,             "Real Estate": 1.05,
        "Utilities": 0.70,             "Unknown": 1.05,
    },
    "1973": {
        "Communication Services": 1.00, "Consumer Discretionary": 1.35,
        "Consumer Staples": 0.65,       "Energy": -0.10,
        "Financials": 1.20,            "Health Care": 0.70,
        "Industrials": 1.15,           "Information Technology": 1.25,
        "Materials": 1.05,             "Real Estate": 1.30,
        "Utilities": 0.85,             "Unknown": 1.05,
    },
    "1980": {
        "Communication Services": 0.85, "Consumer Discretionary": 1.25,
        "Consumer Staples": 0.55,       "Energy": -0.15,
        "Financials": 1.45,            "Health Care": 0.60,
        "Industrials": 1.20,           "Information Technology": 1.00,
        "Materials": 1.05,             "Real Estate": 1.40,
        "Utilities": 0.95,             "Unknown": 1.00,
    },
    "1987": {
        "Communication Services": 0.95, "Consumer Discretionary": 1.10,
        "Consumer Staples": 0.70,       "Energy": 0.85,
        "Financials": 1.25,            "Health Care": 0.75,
        "Industrials": 1.05,           "Information Technology": 1.20,
        "Materials": 1.00,             "Real Estate": 1.00,
        "Utilities": 0.75,             "Unknown": 1.00,
    },
    # 2000, 2007, 2020, 2022 → live via Sektor-ETFs
}

# Schlüssel-Ereignis-Annotationen für den historischen Chart
_SCENARIO_ANNOTATIONS: dict = {
    "1929": [("1929-10-24", "Black\nThursday"), ("1929-10-29", "Black\nTuesday"),
             ("1932-07-08", "Tief −89%")],
    "1987": [("1987-10-19", "Black Monday\n−22.6%")],
    "2000": [("2000-03-10", "NASDAQ\nPeak"), ("2001-09-11", "9/11"),
             ("2002-10-09", "Tief −49%")],
    "2007": [("2008-09-15", "Lehman\nBrothers"), ("2008-10-03", "TARP"),
             ("2009-03-09", "Tief −57%")],
    "2020": [("2020-02-19", "Peak"), ("2020-03-23", "Tief\n−34%"),
             ("2020-08-18", "Neue Hochs")],
    "2022": [("2022-01-03", "Fed Zins-\nerhöhung"), ("2022-10-12", "Jahrestief"),
             ("2023-01-13", "Trendwende")],
    "1973": [("1973-10-17", "OPEC-\nEmbargo"), ("1974-12-06", "Tief −48%")],
    "1980": [("1980-06-01", "Volcker\n20%"), ("1982-08-12", "Tief")],
}


# ── Datenabruf ────────────────────────────────────────────────────────────────

def _fetch_prices(tickers: list[str], period: str) -> dict[str, pd.Series]:
    import yfinance as yf
    from concurrent.futures import ThreadPoolExecutor

    def _one(t: str) -> tuple[str, pd.Series | None]:
        try:
            df = yf.download(t, period=period, auto_adjust=True, progress=False)
            if df is None or df.empty:
                return t, None
            close = df["Close"].squeeze().dropna()
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0].dropna()
            if len(close) > 30:
                return t, close
        except Exception:
            pass
        return t, None

    out: dict[str, pd.Series] = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for ticker, series in ex.map(_one, tickers):
            if series is not None:
                out[ticker] = series
    return out


def _fetch_sectors(symbols: list[str]) -> dict[str, str]:
    """Holt den GICS-Sektor jedes Symbols via yfinance."""
    import yfinance as yf
    from concurrent.futures import ThreadPoolExecutor

    def _one(sym: str) -> tuple[str, str]:
        try:
            info = yf.Ticker(sym).info
            return sym, info.get("sector") or "Unknown"
        except Exception:
            return sym, "Unknown"

    sectors: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for sym, sec in ex.map(_one, symbols):
            sectors[sym] = sec
    return sectors


def _fetch_scenario_shocks(scenario_id: str) -> tuple[dict[str, float], str]:
    """
    Liefert (sector_shocks, source) für ein Szenario.
    Für 2000+: live via Sektor-ETFs; sonst: vordefinierte Multiplikatoren.
    """
    import yfinance as yf
    from concurrent.futures import ThreadPoolExecutor

    try:
        from stress_test import SCENARIOS as _ST
        sc = next((s for s in _ST if s["id"] == scenario_id), None)
        mkt_dd = sc["drawdown"] if sc else -0.30
    except Exception:
        mkt_dd = -0.30

    if scenario_id in _SECTOR_MULTIPLIERS:
        mults = _SECTOR_MULTIPLIERS[scenario_id]
        shocks = {sec: max(-0.99, mkt_dd * mults.get(sec, 1.0)) for sec in _SECTOR_ETFS}
        shocks["Unknown"] = mkt_dd
        return shocks, "legacy"

    if scenario_id not in _SCENARIO_WINDOWS:
        return {}, "no_data"
    _, start, end = _SCENARIO_WINDOWS[scenario_id]

    def _etf_return(item):
        sec, etf = item
        try:
            df = yf.download(etf, start=start, end=end,
                             auto_adjust=True, progress=False)
            if df is None or df.empty:
                return sec, None
            close = df["Close"].squeeze().dropna()
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0].dropna()
            if len(close) < 5:
                return sec, None
            return sec, float(close.iloc[-1] / close.iloc[0] - 1)
        except Exception:
            return sec, None

    shocks: dict[str, float] = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for sec, ret in ex.map(_etf_return, _SECTOR_ETFS.items()):
            if ret is not None:
                shocks[sec] = ret

    for sec in _SECTOR_ETFS:
        if sec not in shocks:
            shocks[sec] = mkt_dd
    shocks["Unknown"] = mkt_dd
    return shocks, "live"


def _fetch_crisis_chart(scenario_id: str) -> pd.Series | None:
    """Holt Indexdaten für die Krisenperiode (Tab 7)."""
    import yfinance as yf
    if scenario_id not in _SCENARIO_WINDOWS:
        return None
    ticker, start, end = _SCENARIO_WINDOWS[scenario_id]
    try:
        df = yf.download(ticker, start=start, end=end,
                         auto_adjust=True, progress=False)
        if df is None or df.empty:
            return None
        close = df["Close"].squeeze().dropna()
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0].dropna()
        return close if len(close) > 20 else None
    except Exception:
        return None


# ── Mathematik ────────────────────────────────────────────────────────────────

def _to_returns(prices: dict[str, pd.Series]) -> dict[str, pd.Series]:
    return {t: s.pct_change().dropna() for t, s in prices.items()}


def _portfolio_returns(rets: dict[str, pd.Series],
                       symbols: list[str],
                       weights: dict[str, float]) -> pd.Series | None:
    valid = [s for s in symbols if s in rets and weights.get(s, 0) > 0]
    if not valid:
        return None
    df = pd.concat([rets[s].rename(s) for s in valid], axis=1).dropna()
    if len(df) < 30:
        return None
    tot = sum(weights[s] for s in valid)
    w = np.array([weights[s] / tot for s in valid])
    return pd.Series(df.values @ w, index=df.index, name="portfolio")


def _ols(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    x_m, y_m = x.mean(), y.mean()
    cov = ((x - x_m) * (y - y_m)).sum()
    var = ((x - x_m) ** 2).sum()
    if var < 1e-12:
        return 0.0, 0.0, 0.0
    beta  = cov / var
    alpha = y_m - beta * x_m
    y_hat = alpha + beta * x
    ss_res = ((y - y_hat) ** 2).sum()
    ss_tot = ((y - y_m)  ** 2).sum()
    r2 = max(0.0, 1.0 - ss_res / ss_tot) if ss_tot > 1e-12 else 0.0
    return beta, r2, alpha * 252


def _factor_table(rets: dict[str, pd.Series],
                  symbols: list[str]) -> dict[str, dict[str, tuple]]:
    rows: dict[str, dict] = {}
    for sym in symbols:
        if sym not in rets:
            continue
        rows[sym] = {}
        for bm in BENCHMARKS:
            if bm not in rets:
                continue
            aligned = pd.concat([rets[sym], rets[bm]], axis=1).dropna()
            if len(aligned) < 30:
                continue
            beta, r2, alpha = _ols(aligned.iloc[:, 1].values,
                                   aligned.iloc[:, 0].values)
            rows[sym][bm] = (beta, r2, alpha)
    return rows


def _rolling_corr(pf_ret: pd.Series,
                  rets: dict[str, pd.Series],
                  windows: tuple = (30, 60, 90)) -> dict:
    out: dict = {}
    for bm in BENCHMARKS:
        if bm not in rets:
            continue
        comb = pd.concat([pf_ret, rets[bm]], axis=1).dropna()
        comb.columns = ["pf", "bm"]
        out[bm] = {w: comb["pf"].rolling(w).corr(comb["bm"]) for w in windows}
    return out


def _var_cvar(pf_ret: pd.Series) -> dict:
    arr = pf_ret.values
    out: dict = {}
    for cl in (95, 99):
        q    = np.percentile(arr, 100 - cl)
        tail = arr[arr <= q]
        out[cl] = {"var": q, "cvar": tail.mean() if len(tail) else q}
    ann_ret = arr.mean() * 252
    ann_vol = arr.std() * np.sqrt(252)
    cum  = np.cumprod(1 + arr)
    peak = np.maximum.accumulate(cum)
    mdd  = ((cum - peak) / peak).min()
    mu, sigma = arr.mean(), arr.std()
    skew  = float(np.mean(((arr - mu) / sigma) ** 3)) if sigma > 0 else 0.0
    kurt  = float(np.mean(((arr - mu) / sigma) ** 4) - 3) if sigma > 0 else 0.0
    p95, p05 = np.percentile(arr, 95), np.percentile(arr, 5)
    tail_ratio = abs(p95 / p05) if abs(p05) > 1e-8 else 0.0
    calmar = abs(ann_ret / mdd) if abs(mdd) > 1e-8 else 0.0
    out.update({"ann_vol": ann_vol, "ann_ret": ann_ret, "max_dd": mdd,
                "calmar": calmar, "skewness": skew, "kurtosis": kurt,
                "tail_ratio": tail_ratio, "returns": arr})
    return out


def _drawdown_details(pf_ret: pd.Series) -> dict:
    arr = pf_ret.values
    idx = pf_ret.index
    cum  = np.cumprod(1 + arr)
    peak = np.maximum.accumulate(cum)
    dd   = (cum - peak) / peak
    underwater = pd.Series(dd * 100.0, index=idx)
    periods: list[dict] = []
    i, n = 0, len(dd)
    while i < n:
        if dd[i] < -1e-6:
            start_i = i; trough_i = i; trough_v = dd[i]
            while i < n and dd[i] < -1e-6:
                if dd[i] < trough_v:
                    trough_v = dd[i]; trough_i = i
                i += 1
            end_i = i if i < n else None
            periods.append({
                "start": idx[start_i], "trough": idx[trough_i],
                "end": idx[end_i] if end_i is not None and end_i < n else None,
                "drawdown_pct": trough_v * 100.0,
                "days_to_trough": trough_i - start_i,
                "days_recovery": (end_i - start_i) if end_i is not None and end_i < n else None,
            })
        else:
            i += 1
    periods.sort(key=lambda x: x["drawdown_pct"])
    worst = periods[0] if periods else {}
    return {"underwater": underwater, "periods": periods[:5],
            "max_dd": dd.min() * 100.0,
            "max_dd_duration": worst.get("days_to_trough", 0),
            "max_underwater": worst.get("days_recovery")}


def _stress_analysis(pf_ret: pd.Series, rets: dict[str, pd.Series]) -> dict:
    spy = rets.get("SPY")
    if spy is None:
        return {}
    result: dict = {"threshold": _CRISIS_THRESHOLD, "benchmarks": {}}
    spy_aligned = spy.dropna()
    result["n_crisis"] = int((spy_aligned < _CRISIS_THRESHOLD).sum())
    result["n_total"]  = len(spy_aligned)
    for bm in BENCHMARKS:
        if bm not in rets:
            continue
        comb = pd.concat([pf_ret.rename("pf"), rets[bm].rename("bm"), spy.rename("spy")],
                         axis=1).dropna()
        if len(comb) < 40:
            continue
        crisis_m = comb["spy"] < _CRISIS_THRESHOLD
        normal_m = ~crisis_m

        def _sc(mask):
            return float(comb.loc[mask, "pf"].corr(comb.loc[mask, "bm"])) if mask.sum() > 10 else None
        def _sb(mask):
            return float(_ols(comb.loc[mask, "bm"].values,
                              comb.loc[mask, "pf"].values)[0]) if mask.sum() > 10 else None
        n_c, c_c = _sc(normal_m), _sc(crisis_m)
        n_b, c_b = _sb(normal_m), _sb(crisis_m)
        result["benchmarks"][bm] = {
            "n_normal": int(normal_m.sum()), "n_crisis": int(crisis_m.sum()),
            "normal_corr": n_c, "crisis_corr": c_c,
            "corr_delta": (c_c - n_c) if (n_c is not None and c_c is not None) else None,
            "normal_beta": n_b, "crisis_beta": c_b,
            "beta_delta": (c_b - n_b) if (n_b is not None and c_b is not None) else None,
        }
    return result


def _compute_sector_stress(symbols_values: list[tuple],
                            sectors: dict[str, str],
                            shocks: dict[str, float]) -> dict:
    """Berechnet Stressimpact nach GICS-Sektor."""
    from collections import defaultdict
    sg: dict = defaultdict(lambda: {"symbols": [], "value": 0.0})
    total = sum(v for _, v in symbols_values)
    for sym, val in symbols_values:
        sec = sectors.get(sym, "Unknown")
        sg[sec]["symbols"].append(sym)
        sg[sec]["value"] += val

    fallback = shocks.get("Unknown", -0.30)
    total_stress = sum(
        sg[s]["value"] * (1 + shocks.get(s, fallback)) for s in sg
    )

    rows = []
    for sec, data in sorted(sg.items()):
        val   = data["value"]
        shock = shocks.get(sec, fallback)
        sv    = val * (1 + shock)
        rows.append({
            "sector":       sec,
            "symbols":      data["symbols"],
            "n":            len(data["symbols"]),
            "value":        val,
            "weight":       val / total if total > 0 else 0,
            "shock":        shock,
            "stress_val":   sv,
            "pnl":          sv - val,
            "stress_weight": sv / total_stress if total_stress > 0 else 0,
        })
    return {
        "rows": rows, "total": total, "total_stress": total_stress,
        "total_pnl": total_stress - total,
        "total_pnl_pct": (total_stress / total - 1) if total > 0 else 0,
    }


# ── Charts ────────────────────────────────────────────────────────────────────

def _ax_style(ax, fig, bg, fg, grid):
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.tick_params(colors=fg, labelsize=8)
    for sp in ax.spines.values():
        sp.set_edgecolor(grid)
    ax.grid(True, color=grid, linewidth=0.5, alpha=0.55)


def _draw_rolling(fig, rolling: dict, bm: str, dark: bool) -> None:
    fig.clear()
    bg, fg, grid = (("#1e1e2e", "#cdd6f4", "#333355") if dark
                    else ("#ffffff", "#2c3e50", "#e0e0e0"))
    ax = fig.add_subplot(111)
    _ax_style(ax, fig, bg, fg, grid)
    palette = {30: "#e74c3c", 60: "#f39c12", 90: "#2980b9"}
    leg_keys = {30: "legend_30d", 60: "legend_60d", 90: "legend_90d"}
    for w, color in palette.items():
        if w in rolling.get(bm, {}):
            s = rolling[bm][w].dropna()
            ax.plot(s.index, s.values, color=color, linewidth=1.6,
                    label=TRK(leg_keys[w]), alpha=0.9)
    ax.axhline(0,    color=fg,        lw=0.9, ls="--", alpha=0.45)
    ax.axhline( 0.5, color="#27ae60", lw=0.7, ls=":",  alpha=0.5)
    ax.axhline(-0.5, color="#27ae60", lw=0.7, ls=":",  alpha=0.5)
    ax.set_title(TRK("chart_rolling_title", bm=TRK(BENCHMARKS[bm])),
                 fontsize=10, fontweight="bold", color=fg)
    ax.set_xlabel(TRK("chart_rolling_x"), fontsize=9, color=fg)
    ax.set_ylabel(TRK("chart_rolling_y"), fontsize=9, color=fg)
    ax.set_ylim(-1.05, 1.05)
    ax.legend(fontsize=8, loc="upper right", facecolor=bg, edgecolor=grid, labelcolor=fg)
    try:
        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        fig.autofmt_xdate(rotation=28, ha="right")
    except Exception:
        pass
    fig.tight_layout(pad=1.2)


def _draw_var(fig, var_data: dict, dark: bool) -> None:
    fig.clear()
    bg, fg, grid = (("#1e1e2e", "#cdd6f4", "#333355") if dark
                    else ("#ffffff", "#2c3e50", "#e0e0e0"))
    ax = fig.add_subplot(111)
    _ax_style(ax, fig, bg, fg, grid)
    arr = var_data.get("returns", np.array([]))
    if not len(arr):
        return
    ax.hist(arr, bins=70, color="#2980b9", alpha=0.60, edgecolor=bg, density=True)
    mu, sigma = arr.mean(), arr.std()
    if sigma > 0:
        x   = np.linspace(arr.min(), arr.max(), 400)
        pdf = np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
        ax.plot(x, pdf, color=fg, lw=1.4, ls="--", alpha=0.65, label="Normal")
    for cl, color, lk in ((95, "#f39c12", "chart_var_95"), (99, "#e74c3c", "chart_var_99")):
        v = var_data[cl]["var"]
        ax.axvline(v, color=color, lw=2.0, label=f"{TRK(lk)}: {v:.2%}", zorder=5)
    ax.set_title(TRK("chart_var_title"), fontsize=10, fontweight="bold", color=fg)
    ax.set_xlabel(TRK("chart_var_x"), fontsize=9, color=fg)
    ax.set_ylabel(TRK("chart_var_y"), fontsize=9, color=fg)
    ax.legend(fontsize=8, loc="upper left", facecolor=bg, edgecolor=grid, labelcolor=fg)
    fig.tight_layout(pad=1.2)


def _draw_underwater(fig, dd_data: dict, dark: bool) -> None:
    fig.clear()
    bg, fg, grid = (("#1e1e2e", "#cdd6f4", "#333355") if dark
                    else ("#ffffff", "#2c3e50", "#e0e0e0"))
    ax = fig.add_subplot(111)
    _ax_style(ax, fig, bg, fg, grid)
    uw: pd.Series = dd_data.get("underwater", pd.Series(dtype=float))
    if not len(uw):
        return
    ax.fill_between(uw.index, uw.values, 0.0, alpha=0.65, color="#e74c3c")
    ax.plot(uw.index, uw.values, color="#c0392b", lw=0.9, alpha=0.9)
    ax.axhline(0, color=fg, lw=0.9, ls="-", alpha=0.55)
    ax.set_title(TRK("chart_underwater_title"), fontsize=10, fontweight="bold", color=fg)
    ax.set_xlabel(TRK("chart_rolling_x"), fontsize=9, color=fg)
    ax.set_ylabel(TRK("chart_underwater_y"), fontsize=9, color=fg)
    try:
        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        fig.autofmt_xdate(rotation=28, ha="right")
    except Exception:
        pass
    fig.tight_layout(pad=1.2)


def _draw_sector_bars(fig, stress_data: dict, currency_sym: str, dark: bool) -> None:
    """Horizontales Balkendiagramm: Aktueller Wert vs. Stresswert je Sektor."""
    fig.clear()
    bg, fg, grid = (("#1e1e2e", "#cdd6f4", "#333355") if dark
                    else ("#ffffff", "#2c3e50", "#e0e0e0"))
    rows = stress_data.get("rows", [])
    if not rows:
        return
    ax = fig.add_subplot(111)
    _ax_style(ax, fig, bg, fg, grid)
    labels    = [r["sector"][:22] for r in rows]
    orig_vals = [r["value"]      / 1000 for r in rows]
    stress_v  = [r["stress_val"] / 1000 for r in rows]
    y = range(len(labels))
    bar_h = 0.38
    ax.barh([i + bar_h/2 for i in y], orig_vals, height=bar_h,
            color="#2980b9", alpha=0.80, label=TRK("sc_col_value"))
    ax.barh([i - bar_h/2 for i in y], stress_v,  height=bar_h,
            color="#e74c3c", alpha=0.80, label=TRK("sc_col_stress_val"))
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=8, color=fg)
    ax.set_xlabel(f"{TRK('sc_col_value')} ({currency_sym}k)", fontsize=9, color=fg)
    ax.set_title(TRK("chart_sector_title"), fontsize=10, fontweight="bold", color=fg)
    ax.legend(fontsize=8, loc="lower right", facecolor=bg, edgecolor=grid, labelcolor=fg)
    fig.tight_layout(pad=1.2)


def _synthetic_crisis_chart(scenario_id: str) -> "pd.Series | None":
    """Erzeugt eine synthetische Krisenperiodenkurve aus SCENARIOS-Parametern.

    Fallback wenn yfinance keine Echtdaten liefert (z. B. ^DJI vor 1985).
    Bear-Phase: leicht beschleunigte Kurve (t^1.4); Recovery: schnell anlaufend (t^0.55).
    """
    try:
        from stress_test import SCENARIOS as _ST
    except ImportError:
        return None
    sc = next((s for s in _ST if s["id"] == scenario_id), None)
    if sc is None:
        return None

    drawdown      = float(sc["drawdown"])
    bear_months   = int(sc["bear_months"])
    rec_real      = int(sc.get("recovery_months", 60))
    rec_shown     = min(rec_real, 120)   # max 10 Jahre im Chart anzeigen

    start_year = int(scenario_id)
    total_pts  = bear_months + rec_shown + 1
    dates = pd.date_range(f"{start_year}-01-01", periods=total_pts, freq="MS")
    trough = 100.0 * (1.0 + drawdown)

    values: list[float] = []
    for i in range(total_pts):
        if i <= bear_months:
            t = i / bear_months if bear_months > 0 else 1.0
            v = 100.0 + (trough - 100.0) * (t ** 1.4)   # leicht beschleunigte Kurve
        else:
            rec_i = i - bear_months
            # Basis ist rec_real – zeigen nur Ausschnitt wenn rec_real > 120
            t = min(1.0, rec_i / rec_real) if rec_real > 0 else 1.0
            v = trough + (100.0 - trough) * (t ** 0.55)  # schneller Anfang, langsam auslaufend
        values.append(v)

    return pd.Series(values, index=dates, dtype=float)


def _draw_crisis_chart(fig, prices: pd.Series, scenario_id: str,
                        pf_beta: float, dark: bool,
                        synthetic: bool = False) -> None:
    """Bloomberg-Style Krisenperiodenchart. synthetic=True: Kurve aus Parametern, kein Echtdatensatz."""
    import matplotlib.dates as mdates
    fig.clear()
    bg, fg, grid = (("#1e1e2e", "#cdd6f4", "#333355") if dark
                    else ("#ffffff", "#2c3e50", "#e0e0e0"))
    ax = fig.add_subplot(111)
    _ax_style(ax, fig, bg, fg, grid)

    norm = prices / prices.iloc[0] * 100.0
    trough_i  = int(np.argmin(norm.values))
    trough_dt = norm.index[trough_i]
    trough_v  = float(norm.iloc[trough_i])
    dd_pct    = trough_v - 100.0

    # Roter Fill für Drawdown
    ax.fill_between(norm.index, norm.values, 100.0,
                    where=(norm.values < 100.0),
                    alpha=0.30, color="#e74c3c")

    # Marktlinie: bei synthetischer Kurve gestrichelt und gedämpfte Farbe
    mkt_color = ("#7ecfef" if dark else "#4a8ab5") if synthetic else ("#4fc3f7" if dark else "#1565c0")
    mkt_ls    = "--" if synthetic else "-"
    mkt_lbl   = TRK("chart_hist_index_sim") if synthetic else TRK("chart_hist_index")
    ax.plot(norm.index, norm.values, color=mkt_color, lw=1.8, ls=mkt_ls,
            alpha=0.85, label=mkt_lbl)

    # Geschätzte Portfolio-Linie (beta-skaliert, gestrichelt)
    if abs(pf_beta) > 0.05:
        pf_path = 100.0 + (norm.values - 100.0) * pf_beta
        ax.plot(norm.index, pf_path, color="#f39c12", lw=1.6, ls="--",
                alpha=0.85, label=TRK("chart_hist_portfolio", beta=pf_beta))

    ax.axhline(100.0, color=fg, lw=0.8, ls="--", alpha=0.40)

    # Tief-Annotation
    ax.annotate(f"{dd_pct:+.1f} %",
                xy=(trough_dt, trough_v),
                xytext=(0, -22), textcoords="offset points",
                fontsize=9, color="#e74c3c", fontweight="bold", ha="center",
                arrowprops=dict(arrowstyle="->", color="#e74c3c", lw=1.2))

    # Ereignis-Annotationen (nur bei Echtdaten; synthetisch hat keine exakten Daten)
    if not synthetic:
        annots = _SCENARIO_ANNOTATIONS.get(scenario_id, [])
        for dt_str, label in annots:
            try:
                dt = pd.Timestamp(dt_str)
                closest = norm.index[np.argmin(np.abs((norm.index - dt).days.astype(float)))]
                val = float(norm.loc[closest])
                ax.axvline(closest, color="#aaaaaa", lw=0.8, ls=":", alpha=0.6)
                ax.text(closest, val + 3, label, fontsize=7, color=fg,
                        ha="center", va="bottom",
                        bbox=dict(boxstyle="round,pad=0.2", fc=bg, ec="#888", alpha=0.75))
            except Exception:
                pass

    # "Simuliert"-Hinweis als Textbox im Chart
    if synthetic:
        ax.text(0.98, 0.97, TRK("chart_synth_note"),
                transform=ax.transAxes, fontsize=7.5,
                color="#f39c12" if dark else "#8b6914",
                ha="right", va="top",
                bbox=dict(boxstyle="round,pad=0.4",
                          fc="#2a2000" if dark else "#fffbe6",
                          ec="#c8a800", alpha=0.88))

    if synthetic:
        title = TRK("chart_hist_title_sim", sc=scenario_id)
    else:
        ticker_lbl = _SCENARIO_WINDOWS.get(scenario_id, ("",))[0]
        title = TRK("chart_hist_title", sc=scenario_id, ticker=ticker_lbl)
    ax.set_title(title, fontsize=10, fontweight="bold", color=fg)
    ax.set_xlabel(TRK("chart_rolling_x"), fontsize=9, color=fg)
    ax.set_ylabel(TRK("chart_hist_y"), fontsize=9, color=fg)
    ax.legend(fontsize=8, loc="lower left", facecolor=bg, edgecolor=grid, labelcolor=fg)
    try:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
        fig.autofmt_xdate(rotation=28, ha="right")
    except Exception:
        pass
    fig.tight_layout(pad=1.2)


# ── Haupt-Dialog ──────────────────────────────────────────────────────────────

def show_komplex_dialog(parent,
                        symbols_values: list[tuple[str, float]],
                        currency: str = "USD") -> None:
    from PyQt6.QtWidgets import (
        QApplication, QDialog, QVBoxLayout, QHBoxLayout,
        QTabWidget, QWidget, QLabel, QPushButton, QComboBox, QFrame,
        QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView,
        QStackedWidget, QDoubleSpinBox, QGroupBox, QMessageBox,
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QPalette, QBrush, QColor, QFont, QFontDatabase
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.figure import Figure

    if not symbols_values:
        QMessageBox.information(parent, TRK("title"), TRK("err_no_symbols"))
        return

    symbols  = [s for s, _ in symbols_values]
    weights  = {s: v for s, v in symbols_values}
    pf_total = sum(weights.values())

    _dm    = QApplication.palette().color(QPalette.ColorRole.Window).lightness() < 128
    _red   = "#e74c3c"
    _green = "#27ae60"
    _muted = "#aaa" if _dm else "#666"
    sym_fmt = {"USD": "$", "EUR": "€", "CHF": "CHF ", "GBP": "£"}.get(currency, currency + " ")

    def _fv(v: float) -> str:
        return f"{sym_fmt}{abs(v):,.0f}"

    def _ef(btn) -> None:
        af = QFontDatabase.families()
        for fc in ("Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji"):
            if fc in af:
                btn.setFont(QFont(fc, 10)); return

    # ── Dialog ────────────────────────────────────────────────────────────────
    dialog = QDialog(parent)
    dialog.setWindowTitle(TRK("title"))
    dialog.setWindowFlag(Qt.WindowType.Window, True)
    screen = (parent.screen() or QApplication.primaryScreen()).availableGeometry()
    dlg_w  = min(int(screen.width()  * 0.96), 1800)
    dlg_h  = min(int(screen.height() * 0.92), 1050)
    dialog.resize(dlg_w, dlg_h)
    dialog.move(screen.x() + (screen.width()  - dlg_w) // 2,
                screen.y() + (screen.height() - dlg_h) // 2)

    outer = QVBoxLayout(dialog); outer.setSpacing(6); outer.setContentsMargins(12, 8, 12, 8)

    # ── Toolbar ───────────────────────────────────────────────────────────────
    toolbar = QHBoxLayout(); toolbar.setSpacing(6)
    toolbar.addWidget(QLabel(TRK("lbl_period") + ":"))
    period_combo = QComboBox()
    for key, lk in PERIODS.items():
        period_combo.addItem(TRK(lk), key)
    period_combo.setCurrentIndex(1)
    toolbar.addWidget(period_combo)

    refresh_btn = QPushButton(TRK("btn_refresh"))
    refresh_btn.setMinimumHeight(30)
    refresh_btn.setStyleSheet("font-weight:bold; padding:2px 14px;")
    toolbar.addWidget(refresh_btn)
    toolbar.addStretch()

    _export_data: list = [None]
    main_win = next((w for w in QApplication.topLevelWidgets()
                     if hasattr(w, "_make_export_btn")), None)
    if main_win is not None:
        export_btn = main_win._make_export_btn(lambda: _export_data[0], TRK("title"))
        export_btn.setMinimumHeight(30); export_btn.setEnabled(False)
        toolbar.addWidget(export_btn)
    else:
        export_btn = None

    def _show_help() -> None:
        for w in QApplication.topLevelWidgets():
            if hasattr(w, "show_help"):
                w.show_help(anchor="komplex", parent_widget=dialog); break

    help_btn = QPushButton(TRK("btn_help"))
    help_btn.setMinimumHeight(30); help_btn.setStyleSheet("padding:2px 12px;")
    help_btn.clicked.connect(_show_help); _ef(help_btn)
    toolbar.addWidget(help_btn)

    close_btn = QPushButton(TRK("btn_close"))
    close_btn.setMinimumHeight(30); close_btn.setStyleSheet("padding:2px 12px;")
    close_btn.clicked.connect(dialog.close)
    toolbar.addWidget(close_btn)
    outer.addLayout(toolbar)

    # ── Stack ─────────────────────────────────────────────────────────────────
    stack = QStackedWidget(); outer.addWidget(stack, stretch=1)
    loading_page = QWidget()
    ll = QVBoxLayout(loading_page); ll.setAlignment(Qt.AlignmentFlag.AlignCenter)
    ll_lbl = QLabel(TRK("lbl_loading"))
    ll_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    ll_lbl.setStyleSheet("font-size:14px; color:#888;")
    ll.addWidget(ll_lbl); stack.addWidget(loading_page)
    content_page = QWidget()
    cl = QVBoxLayout(content_page); cl.setSpacing(0); cl.setContentsMargins(0, 0, 0, 0)
    stack.addWidget(content_page)

    tabs = QTabWidget(); cl.addWidget(tabs, stretch=1)

    # ─── Tab 1: Faktorexposition ──────────────────────────────────────────────
    tab1 = QWidget(); t1l = QVBoxLayout(tab1)
    t1l.setSpacing(4); t1l.setContentsMargins(8, 8, 8, 8)
    desc1 = QLabel(TRK("lbl_factor_desc")); desc1.setWordWrap(True)
    desc1.setStyleSheet(f"color:{_muted}; font-size:10px; padding:2px 0 6px 0;")
    t1l.addWidget(desc1)
    ftable = QTableWidget(); ftable.setAlternatingRowColors(True)
    ftable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    ftable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    ftable.verticalHeader().setVisible(False); ftable.setSortingEnabled(True)
    t1l.addWidget(ftable); tabs.addTab(tab1, TRK("tab_factor"))

    # ─── Tab 2: Rollende Korrelation ──────────────────────────────────────────
    tab2 = QWidget(); t2l = QVBoxLayout(tab2)
    t2l.setSpacing(6); t2l.setContentsMargins(8, 8, 8, 8)
    t2ctrl = QHBoxLayout(); t2ctrl.addWidget(QLabel(TRK("lbl_benchmark") + ":"))
    bm_combo = QComboBox()
    for bk, lk in BENCHMARKS.items(): bm_combo.addItem(TRK(lk), bk)
    t2ctrl.addWidget(bm_combo); t2ctrl.addStretch(); t2l.addLayout(t2ctrl)
    fig2 = Figure(figsize=(9, 5), dpi=96); cvs2 = FigureCanvasQTAgg(fig2)
    t2l.addWidget(cvs2, stretch=1); tabs.addTab(tab2, TRK("tab_rolling"))

    # ─── Tab 3: VaR / CVaR ───────────────────────────────────────────────────
    tab3 = QWidget(); t3l = QHBoxLayout(tab3)
    t3l.setSpacing(12); t3l.setContentsMargins(8, 8, 8, 8)
    t3_left = QFrame(); t3_left.setFrameShape(QFrame.Shape.StyledPanel); t3_left.setMaximumWidth(310)
    t3f = QFormLayout(t3_left); t3f.setSpacing(7); t3f.setContentsMargins(14, 14, 14, 14)

    def _vlbl(color="", bold=False):
        lbl = QLabel("—")
        s = (f"color:{color};" if color else "") + ("font-weight:bold; font-size:13px;" if bold else "")
        if s: lbl.setStyleSheet(s)
        return lbl

    def _sep():
        s = QFrame(); s.setFrameShape(QFrame.Shape.HLine); return s

    lbl_v95  = _vlbl(color=_red, bold=True);  lbl_v99  = _vlbl(color=_red, bold=True)
    lbl_cv95 = _vlbl(color=_red);             lbl_cv99 = _vlbl(color=_red)
    lbl_vol  = _vlbl(); lbl_ret = _vlbl(); lbl_mdd = _vlbl(color=_red)
    lbl_cal  = _vlbl(); lbl_skew = _vlbl(); lbl_kurt = _vlbl(); lbl_tail = _vlbl()
    t3f.addRow(f"<b>{TRK('lbl_var_95')}:</b>",   lbl_v95)
    t3f.addRow(f"<b>{TRK('lbl_var_99')}:</b>",   lbl_v99); t3f.addRow(_sep())
    t3f.addRow(f"{TRK('lbl_cvar_95')}:", lbl_cv95)
    t3f.addRow(f"{TRK('lbl_cvar_99')}:", lbl_cv99); t3f.addRow(_sep())
    t3f.addRow(f"{TRK('lbl_ann_vol')}:", lbl_vol)
    t3f.addRow(f"{TRK('lbl_ann_ret')}:", lbl_ret)
    t3f.addRow(f"{TRK('lbl_max_dd')}:",  lbl_mdd)
    t3f.addRow(f"{TRK('lbl_calmar')}:",  lbl_cal); t3f.addRow(_sep())
    t3f.addRow(f"{TRK('lbl_skewness')}:",  lbl_skew)
    t3f.addRow(f"{TRK('lbl_kurtosis')}:",  lbl_kurt)
    t3f.addRow(f"{TRK('lbl_tail_ratio')}:", lbl_tail)
    t3l.addWidget(t3_left)
    fig3 = Figure(figsize=(7, 5), dpi=96); cvs3 = FigureCanvasQTAgg(fig3)
    t3l.addWidget(cvs3, stretch=1); tabs.addTab(tab3, TRK("tab_var"))

    # ─── Tab 4: Drawdown-Analyse ──────────────────────────────────────────────
    tab4 = QWidget(); t4l = QHBoxLayout(tab4)
    t4l.setSpacing(10); t4l.setContentsMargins(8, 8, 8, 8)
    t4_left = QFrame(); t4_left.setFrameShape(QFrame.Shape.StyledPanel); t4_left.setMinimumWidth(380)
    t4lv = QVBoxLayout(t4_left); t4lv.setContentsMargins(10, 10, 10, 10); t4lv.setSpacing(6)
    dd_table = QTableWidget(); dd_table.setAlternatingRowColors(True)
    dd_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    dd_table.verticalHeader().setVisible(False); dd_table.setColumnCount(4)
    dd_table.setHorizontalHeaderLabels([TRK("dd_col_date"), TRK("dd_col_dd"),
                                        TRK("dd_col_duration"), TRK("dd_col_recovery")])
    dd_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    dd_table.horizontalHeader().setStretchLastSection(True)
    dd_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    t4lv.addWidget(dd_table)
    dd_sf = QFormLayout(); dd_sf.setSpacing(6)
    lbl_mdd_dur = _vlbl(); lbl_mdd_uw = _vlbl()
    dd_sf.addRow(f"{TRK('lbl_max_dd_dur')}:", lbl_mdd_dur)
    dd_sf.addRow(f"{TRK('lbl_max_uw')}:",     lbl_mdd_uw)
    t4lv.addLayout(dd_sf); t4l.addWidget(t4_left)
    fig4 = Figure(figsize=(8, 5), dpi=96); cvs4 = FigureCanvasQTAgg(fig4)
    t4l.addWidget(cvs4, stretch=1); tabs.addTab(tab4, TRK("tab_drawdown"))

    # ─── Tab 5: Stress & Korrelation ─────────────────────────────────────────
    tab5 = QWidget(); t5l = QVBoxLayout(tab5)
    t5l.setSpacing(8); t5l.setContentsMargins(8, 8, 8, 8)
    stress_info_lbl = QLabel(""); stress_info_lbl.setStyleSheet(f"color:{_muted}; font-size:10px;")
    t5l.addWidget(stress_info_lbl)
    stress_table = QTableWidget(); stress_table.setAlternatingRowColors(True)
    stress_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    stress_table.verticalHeader().setVisible(False); stress_table.setColumnCount(7)
    stress_table.setHorizontalHeaderLabels([
        TRK("lbl_benchmark"),
        TRK("st_normal_corr"), TRK("st_crisis_corr"), TRK("st_delta_corr"),
        TRK("st_normal_beta"), TRK("st_crisis_beta"), TRK("st_delta_beta"),
    ])
    stress_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
    for c in range(1, 7):
        stress_table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.Stretch)
    t5l.addWidget(stress_table, stretch=1)
    mc_grp = QGroupBox(TRK("lbl_mc_grp")); mc_grp.setCheckable(True); mc_grp.setChecked(False)
    mc_form = QFormLayout(mc_grp); mc_form.setSpacing(6); mc_form.setContentsMargins(10, 8, 10, 8)
    loan_spin = QDoubleSpinBox(); loan_spin.setRange(0, 1e9); loan_spin.setValue(0)
    loan_spin.setGroupSeparatorShown(True); loan_spin.setSuffix(f"  {currency}"); loan_spin.setSingleStep(10_000)
    ltv_spin  = QDoubleSpinBox(); ltv_spin.setRange(10.0, 95.0); ltv_spin.setValue(70.0)
    ltv_spin.setSuffix(" %"); ltv_spin.setSingleStep(5.0)
    mc_form.addRow(TRK("lbl_mc_loan"), loan_spin)
    mc_form.addRow(TRK("lbl_mc_ltv"),  ltv_spin)
    mc_res = QFormLayout()
    lbl_mc_buf = _vlbl(color=_green); lbl_mc_val = _vlbl(color=_red); lbl_mc_cost = _vlbl()
    mc_res.addRow(f"{TRK('lbl_mc_buffer')}:",   lbl_mc_buf)
    mc_res.addRow(f"{TRK('lbl_mc_value')}:",    lbl_mc_val)
    mc_res.addRow(f"{TRK('lbl_mc_ann_cost')}:", lbl_mc_cost)
    mc_form.addRow(mc_res); t5l.addWidget(mc_grp)
    tabs.addTab(tab5, TRK("tab_stress"))

    # ─── Tab 6: Sektor-Stresstest ─────────────────────────────────────────────
    tab6 = QWidget(); t6l = QVBoxLayout(tab6)
    t6l.setSpacing(6); t6l.setContentsMargins(8, 8, 8, 8)

    # Modus-Umschalter
    t6mode_row = QHBoxLayout(); t6mode_row.setSpacing(4)
    btn_mode_hist   = QPushButton(TRK("btn_mode_hist"))
    btn_mode_custom = QPushButton(TRK("btn_mode_custom"))
    _tog_style = ("QPushButton{padding:2px 10px; border:1px solid #888; border-radius:3px;}"
                  "QPushButton:checked{font-weight:bold; border:2px solid #4a90d9;}")
    for _b in (btn_mode_hist, btn_mode_custom):
        _b.setCheckable(True); _b.setMinimumHeight(26); _b.setStyleSheet(_tog_style)
    btn_mode_hist.setChecked(True)
    t6mode_row.addWidget(btn_mode_hist); t6mode_row.addWidget(btn_mode_custom)
    t6mode_row.addStretch(); t6l.addLayout(t6mode_row)

    # ── ctrl_stack: Seite 0 = Historisch, Seite 1 = Benutzerdefiniert
    ctrl_stack6 = QStackedWidget(); t6l.addWidget(ctrl_stack6)

    # Seite 0: Historisch
    hist_panel = QWidget(); hist_lay = QHBoxLayout(hist_panel)
    hist_lay.setContentsMargins(0, 0, 0, 0); hist_lay.setSpacing(8)
    hist_lay.addWidget(QLabel(TRK("lbl_sc_select") + ":"))
    sc_combo = QComboBox(); sc_combo.setMinimumWidth(240)
    try:
        from stress_test import SCENARIOS as _ST_SC
        from stress_test_translations import TRS as _TRS
        for sc in _ST_SC:
            sc_combo.addItem(_TRS(f"sc_{sc['id']}"), sc["id"])
    except Exception:
        sc_combo.addItem("2007", "2007"); sc_combo.addItem("2020", "2020")
        _TRS = lambda k: k
    hist_lay.addWidget(sc_combo)
    sc_load_btn = QPushButton(TRK("btn_sc_load"))
    sc_load_btn.setMinimumHeight(28); sc_load_btn.setStyleSheet("padding:2px 12px; font-weight:bold;")
    hist_lay.addWidget(sc_load_btn); hist_lay.addStretch()
    t6_info = QLabel(""); t6_info.setStyleSheet(f"color:{_muted}; font-size:10px;")
    hist_lay.addWidget(t6_info)
    ctrl_stack6.addWidget(hist_panel)

    # Seite 1: Benutzerdefiniert
    custom_panel = QWidget(); custom_lay = QVBoxLayout(custom_panel)
    custom_lay.setContentsMargins(0, 2, 0, 2); custom_lay.setSpacing(4)

    # Preset-Zeile
    preset_row = QHBoxLayout(); preset_row.setSpacing(8)
    preset_row.addWidget(QLabel(TRK("lbl_preset_select")))
    preset_combo = QComboBox(); preset_combo.setMinimumWidth(200)
    preset_combo.addItem(TRK("sc_none"), "")
    try:
        from stress_test import SCENARIOS as _ST_SC_P
        from stress_test_translations import TRS as _TRS_P
        for sc in _ST_SC_P:
            preset_combo.addItem(_TRS_P(f"sc_{sc['id']}"), sc["id"])
    except Exception:
        preset_combo.addItem("2007", "2007")
    preset_row.addWidget(preset_combo)
    preset_apply_btn = QPushButton(TRK("btn_preset_apply"))
    preset_apply_btn.setMinimumHeight(26)
    preset_row.addWidget(preset_apply_btn); preset_row.addStretch()
    t6_custom_info = QLabel(""); t6_custom_info.setStyleSheet(f"color:{_muted}; font-size:10px;")
    preset_row.addWidget(t6_custom_info)
    custom_lay.addLayout(preset_row)

    # Sektor-Spin-Boxes (11 Sektoren, 2 Spalten)
    _sector_spins: dict[str, "QDoubleSpinBox"] = {}
    spin_grid = QHBoxLayout(); spin_grid.setSpacing(16)
    left_form  = QFormLayout(); left_form.setSpacing(3); left_form.setHorizontalSpacing(8)
    right_form = QFormLayout(); right_form.setSpacing(3); right_form.setHorizontalSpacing(8)
    _SECTOR_ORDER = list(_SECTOR_ETFS.keys())
    _SHORT_SEC = {
        "Communication Services": "Comm. Services",
        "Consumer Discretionary":  "Cons. Discretionary",
        "Consumer Staples":        "Cons. Staples",
        "Energy":                  "Energy",
        "Financials":              "Financials",
        "Health Care":             "Health Care",
        "Industrials":             "Industrials",
        "Information Technology":  "IT",
        "Materials":               "Materials",
        "Real Estate":             "Real Estate",
        "Utilities":               "Utilities",
    }
    for i, sec in enumerate(_SECTOR_ORDER):
        sp = QDoubleSpinBox()
        sp.setRange(-100.0, 100.0); sp.setSingleStep(1.0)
        sp.setSuffix(" %"); sp.setDecimals(1); sp.setValue(0.0)
        sp.setMinimumWidth(110)
        _sector_spins[sec] = sp
        lbl_s = QLabel(_SHORT_SEC.get(sec, sec) + ":")
        lbl_s.setFixedWidth(130)
        (left_form if i < 6 else right_form).addRow(lbl_s, sp)
    spin_grid.addLayout(left_form); spin_grid.addLayout(right_form); spin_grid.addStretch()
    custom_lay.addLayout(spin_grid)

    # Berechnen-Zeile
    calc_row = QHBoxLayout()
    calc_btn = QPushButton(TRK("btn_custom_calc"))
    calc_btn.setMinimumHeight(28); calc_btn.setStyleSheet("padding:2px 16px; font-weight:bold;")
    calc_row.addWidget(calc_btn); calc_row.addStretch()
    custom_lay.addLayout(calc_row)
    ctrl_stack6.addWidget(custom_panel)

    # Modus-Umschalt-Logik
    def _set_t6_mode(hist: bool) -> None:
        ctrl_stack6.setCurrentIndex(0 if hist else 1)
        btn_mode_hist.setChecked(hist); btn_mode_custom.setChecked(not hist)

    btn_mode_hist.clicked.connect(lambda: _set_t6_mode(True))
    btn_mode_custom.clicked.connect(lambda: _set_t6_mode(False))

    # Gemeinsame Untersektion: Zusammenfassung + Tabelle + Chart
    t6_summary = QLabel(""); t6_summary.setStyleSheet("font-size:12px; font-weight:bold; padding:4px 0;")
    t6l.addWidget(t6_summary)

    t6split = QHBoxLayout(); t6split.setSpacing(8)
    sc_frame = QFrame(); sc_frame.setFrameShape(QFrame.Shape.StyledPanel); sc_frame.setMinimumWidth(600)
    sc_fv = QVBoxLayout(sc_frame); sc_fv.setContentsMargins(6, 6, 6, 6)
    sc_table = QTableWidget(); sc_table.setAlternatingRowColors(True)
    sc_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    sc_table.verticalHeader().setVisible(False); sc_table.setSortingEnabled(False)
    sc_cols = [TRK("sc_col_sector"), TRK("sc_col_n"), TRK("sc_col_value"),
               TRK("sc_col_weight"), TRK("sc_col_shock"),
               TRK("sc_col_stress_val"), TRK("sc_col_pnl")]
    sc_table.setColumnCount(len(sc_cols)); sc_table.setHorizontalHeaderLabels(sc_cols)
    for c in range(len(sc_cols)):
        sc_table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
    sc_table.horizontalHeader().setStretchLastSection(False)
    sc_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    sc_fv.addWidget(sc_table)
    sc_source_lbl = QLabel(""); sc_source_lbl.setStyleSheet(f"color:{_muted}; font-size:9px; padding:2px 0;")
    sc_fv.addWidget(sc_source_lbl)
    t6split.addWidget(sc_frame)
    fig6 = Figure(figsize=(7, 5), dpi=96); cvs6 = FigureCanvasQTAgg(fig6)
    t6split.addWidget(cvs6, stretch=1); t6l.addLayout(t6split, stretch=1)
    tabs.addTab(tab6, TRK("tab_scenario"))

    # ─── Tab 7: Historischer Chart ────────────────────────────────────────────
    tab7 = QWidget(); t7l = QVBoxLayout(tab7)
    t7l.setSpacing(6); t7l.setContentsMargins(8, 8, 8, 8)
    t7ctrl = QHBoxLayout(); t7ctrl.setSpacing(8)
    t7ctrl.addWidget(QLabel(TRK("lbl_sc_select") + ":"))
    sc_combo7 = QComboBox(); sc_combo7.setMinimumWidth(240)
    try:
        from stress_test import SCENARIOS as _ST_SC2
        from stress_test_translations import TRS as _TRS2
        for sc in _ST_SC2:
            sc_combo7.addItem(_TRS2(f"sc_{sc['id']}"), sc["id"])
    except Exception:
        sc_combo7.addItem("2007", "2007"); sc_combo7.addItem("2020", "2020")
    t7ctrl.addWidget(sc_combo7)
    t7load_btn = QPushButton(TRK("btn_sc_load"))
    t7load_btn.setMinimumHeight(28); t7load_btn.setStyleSheet("padding:2px 12px; font-weight:bold;")
    t7ctrl.addWidget(t7load_btn); t7ctrl.addStretch(); t7l.addLayout(t7ctrl)
    fig7 = Figure(figsize=(11, 5.5), dpi=96); cvs7 = FigureCanvasQTAgg(fig7)
    t7l.addWidget(cvs7, stretch=1)
    t7_disc = QLabel(TRK("chart_hist_disclaimer"))
    t7_disc.setWordWrap(True); t7_disc.setStyleSheet(f"color:{_muted}; font-size:9px;")
    t7l.addWidget(t7_disc)
    tabs.addTab(tab7, TRK("tab_hist_chart"))

    # ── Footer ────────────────────────────────────────────────────────────────
    disc = QLabel(TRK("disclaimer")); disc.setWordWrap(True)
    disc.setStyleSheet(
        f"color:{_muted}; font-size:10px; font-style:italic; "
        f"padding:4px 0; border-top:1px solid {'#444' if _dm else '#ddd'};"
    )
    outer.addWidget(disc)

    # ── State ─────────────────────────────────────────────────────────────────
    _rolling_cache: list = [None]
    _workers: list = []
    _sectors_cache: list = [{}]
    _pf_spy_beta:   list = [1.0]
    _cached = {"factor": {}, "dd": {}, "stress": {}}

    # ── Farb-Helfer ───────────────────────────────────────────────────────────

    def _beta_brush(v: float) -> QBrush:
        t = min(1.0, abs(v) / 2.0)
        if _dm:
            return (QBrush(QColor(int(t*30), int(t*50), int(40+t*100))) if v >= 0 else
                    QBrush(QColor(int(40+t*100), int(t*30), int(t*30))))
        if v >= 0: c = int(235 - t*130); return QBrush(QColor(c, c, 255))
        c = int(235 - t*130); return QBrush(QColor(255, c, c))

    def _delta_brush(v):
        if v is None: return None
        t = min(1.0, abs(v) / 0.5)
        if _dm:
            return (QBrush(QColor(int(40+t*100), int(t*30), int(t*30))) if v > 0 else
                    QBrush(QColor(int(t*30), int(40+t*80), int(t*30))))
        if v > 0: c = int(235-t*100); return QBrush(QColor(255, c, c))
        c = int(235-t*100); return QBrush(QColor(c, 255, c))

    def _shock_brush(v: float) -> QBrush:
        if v >= 0:
            return QBrush(QColor(180, 230, 180) if not _dm else QColor(40, 100, 40))
        sev = min(1.0, abs(v) / 0.6)
        if not _dm:
            return QBrush(QColor(int(255-sev*75), int(220-sev*140), 80))
        return QBrush(QColor(int(80+sev*80), 20, 20))

    # ── Tab-Füllfunktionen ────────────────────────────────────────────────────

    def _fill_factor(fd: dict) -> None:
        bm_keys = list(BENCHMARKS.keys())
        headers = [TRK("lbl_symbol")] + [TRK(BENCHMARKS[bm]) for bm in bm_keys]
        ftable.setColumnCount(len(headers)); ftable.setHorizontalHeaderLabels(headers)
        ftable.setRowCount(len(fd))
        for row, (sym, bm_data) in enumerate(fd.items()):
            i0 = QTableWidgetItem(sym)
            i0.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            ftable.setItem(row, 0, i0)
            for col, bm in enumerate(bm_keys, start=1):
                if bm in bm_data:
                    beta, r2, _ = bm_data[bm]
                    item = QTableWidgetItem(f"{beta:+.2f}")
                    item.setData(Qt.ItemDataRole.UserRole, float(beta))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setBackground(_beta_brush(beta))
                    item.setToolTip(TRK("lbl_r2_tip", r2=r2, r2pct=r2*100))
                else:
                    item = QTableWidgetItem("—")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                ftable.setItem(row, col, item)
        ftable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        for c in range(1, ftable.columnCount()):
            ftable.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.Stretch)

    def _fill_var(vd: dict) -> None:
        lbl_v95.setText(f"{vd[95]['var']:.2%}"); lbl_v99.setText(f"{vd[99]['var']:.2%}")
        lbl_cv95.setText(f"{vd[95]['cvar']:.2%}"); lbl_cv99.setText(f"{vd[99]['cvar']:.2%}")
        lbl_vol.setText(f"{vd['ann_vol']:.2%}")
        ret = vd["ann_ret"]; lbl_ret.setText(f"{ret:+.2%}")
        lbl_ret.setStyleSheet(f"color:{'#27ae60' if ret >= 0 else '#e74c3c'};")
        lbl_mdd.setText(f"{vd['max_dd']:.2%}"); lbl_cal.setText(f"{vd['calmar']:.2f}")
        sk = vd["skewness"]; lbl_skew.setText(f"{sk:+.2f}")
        lbl_skew.setStyleSheet(f"color:{'#e74c3c' if sk < -0.5 else ''};")
        ku = vd["kurtosis"]; lbl_kurt.setText(f"{ku:+.2f}")
        lbl_kurt.setStyleSheet(f"color:{'#e74c3c' if ku > 1 else ''};")
        lbl_tail.setText(f"{vd['tail_ratio']:.2f}")
        _draw_var(fig3, vd, _dm); cvs3.draw()

    def _fill_drawdown(dd: dict) -> None:
        periods = dd.get("periods", []); dd_table.setRowCount(len(periods))
        for row, p in enumerate(periods):
            st = p["start"].strftime("%d.%m.%Y") if hasattr(p["start"], "strftime") else str(p["start"])[:10]
            du = f"{p['days_to_trough']} {TRK('lbl_days')}"
            rc = (f"{p['days_recovery']} {TRK('lbl_days')}"
                  if p["days_recovery"] is not None else TRK("lbl_still_open"))
            for col, text in enumerate([st, f"{p['drawdown_pct']:.1f} %", du, rc]):
                item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 1: item.setForeground(QColor(_red))
                dd_table.setItem(row, col, item)
        lbl_mdd_dur.setText(f"{dd.get('max_dd_duration', 0)} {TRK('lbl_days')}")
        uw = dd.get("max_underwater")
        lbl_mdd_uw.setText(f"{uw} {TRK('lbl_days')}" if uw is not None else TRK("lbl_still_open"))
        _draw_underwater(fig4, dd, _dm); cvs4.draw()

    def _fill_stress(sd: dict) -> None:
        n_cr = sd.get("n_crisis", 0); n_tot = sd.get("n_total", 1)
        thr  = abs(sd.get("threshold", _CRISIS_THRESHOLD)) * 100
        stress_info_lbl.setText(TRK("stress_info", n_crisis=n_cr, n_total=n_tot, thr=thr))
        bms = sd.get("benchmarks", {}); stress_table.setRowCount(len(bms))
        for row, (bm, d) in enumerate(bms.items()):
            bm_i = QTableWidgetItem(TRK(BENCHMARKS[bm]))
            bm_i.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            stress_table.setItem(row, 0, bm_i)
            for col, (val, fmt, is_d) in enumerate([
                (d["normal_corr"], "{:.2f}", False), (d["crisis_corr"], "{:.2f}", False),
                (d["corr_delta"],  "{:+.2f}", True),
                (d["normal_beta"], "{:.2f}", False), (d["crisis_beta"], "{:.2f}", False),
                (d["beta_delta"],  "{:+.2f}", True),
            ], start=1):
                text = fmt.format(val) if val is not None else "—"
                item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if is_d and val is not None:
                    br = _delta_brush(val)
                    if br: item.setBackground(br)
                stress_table.setItem(row, col, item)

    def _update_mc() -> None:
        if not mc_grp.isChecked(): return
        loan = loan_spin.value(); ltv = ltv_spin.value() / 100.0
        if loan <= 0 or ltv <= 0: return
        mc_val  = loan / ltv
        buf_pct = (pf_total - mc_val) / pf_total * 100.0 if pf_total > 0 else 0
        ann_cost = loan * 3.5 / 100.0
        lbl_mc_buf.setText(f"{buf_pct:.1f} %")
        lbl_mc_buf.setStyleSheet(f"color:{'#27ae60' if buf_pct > 20 else '#e74c3c'}; font-weight:bold;")
        lbl_mc_val.setText(f"{_fv(mc_val)} ({mc_val/pf_total*100:.1f} %)" if pf_total > 0 else _fv(mc_val))
        lbl_mc_cost.setText(f"{_fv(ann_cost)} p.a.")

    loan_spin.valueChanged.connect(_update_mc)
    ltv_spin.valueChanged.connect(_update_mc)
    mc_grp.toggled.connect(_update_mc)

    def _update_rolling() -> None:
        if _rolling_cache[0] is None: return
        try:
            _draw_rolling(fig2, _rolling_cache[0], bm_combo.currentData(), _dm); cvs2.draw()
        except RuntimeError:
            pass

    bm_combo.currentIndexChanged.connect(_update_rolling)

    def _fill_sector(sr: dict, source: str) -> None:
        rows = sr.get("rows", [])
        tot  = sr.get("total", 0); tot_s = sr.get("total_stress", 0)
        pnl_pct = sr.get("total_pnl_pct", 0)
        t6_summary.setText(
            f"{TRK('sc_summary')}: {sym_fmt}{tot:,.0f} → {sym_fmt}{tot_s:,.0f}  ({pnl_pct:+.1%})"
        )
        t6_summary.setStyleSheet(
            f"font-size:12px; font-weight:bold; padding:4px 0; "
            f"color:{'#e74c3c' if pnl_pct < 0 else '#27ae60'};"
        )
        sc_table.setRowCount(len(rows) + 1)

        def _ci(r, c, text, color=None, bold=False, bg=None):
            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if color: item.setForeground(QColor(color))
            if bold:  item.setFont(QFont("", -1, QFont.Weight.Bold))
            if bg:    item.setBackground(bg)
            sc_table.setItem(r, c, item)

        for row, r in enumerate(rows):
            ni = QTableWidgetItem(r["sector"])
            ni.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            sc_table.setItem(row, 0, ni)
            _ci(row, 1, str(r["n"]))
            _ci(row, 2, f"{sym_fmt}{r['value']:,.0f}")
            _ci(row, 3, f"{r['weight']:.1%}")
            _ci(row, 4, f"{r['shock']:+.1%}",
                color="white",
                bg=_shock_brush(r["shock"]))
            _ci(row, 5, f"{sym_fmt}{r['stress_val']:,.0f}")
            _ci(row, 6, f"{r['pnl']:+,.0f}", color="#e74c3c" if r["pnl"] < 0 else "#27ae60")

        tr = len(rows)
        ti = QTableWidgetItem(TRK("sc_col_total"))
        ti.setFont(QFont("", -1, QFont.Weight.Bold))
        ti.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        sc_table.setItem(tr, 0, ti)
        _ci(tr, 1, str(sum(r["n"] for r in rows)), bold=True)
        _ci(tr, 2, f"{sym_fmt}{tot:,.0f}", bold=True)
        _ci(tr, 3, "100.0 %", bold=True)
        _ci(tr, 4, f"{pnl_pct:+.1%}", bold=True, color="#e74c3c" if pnl_pct < 0 else "#27ae60")
        _ci(tr, 5, f"{sym_fmt}{tot_s:,.0f}", bold=True)
        _ci(tr, 6, f"{sr['total_pnl']:+,.0f}", bold=True,
            color="#e74c3c" if pnl_pct < 0 else "#27ae60")

        sc_source_lbl.setText({"live": TRK("sc_source_live"),
                                "legacy": TRK("sc_source_est"),
                                "custom": TRK("sc_custom_source")}.get(source, ""))
        _draw_sector_bars(fig6, sr, sym_fmt.strip(), _dm); cvs6.draw()

    def _fill_crisis_chart(prices: "pd.Series | None", sc_id: str) -> None:
        if prices is None:
            synth = _synthetic_crisis_chart(sc_id)
            if synth is not None:
                _draw_crisis_chart(fig7, synth, sc_id, _pf_spy_beta[0], _dm,
                                   synthetic=True)
                cvs7.draw()
                return
            # Auch kein synthetischer Fallback möglich
            fig7.clear()
            ax7 = fig7.add_subplot(111)
            ax7.text(0.5, 0.5, TRK("chart_no_data"), transform=ax7.transAxes,
                     ha="center", va="center", fontsize=11,
                     color="#888888" if not _dm else "#777777")
            ax7.axis("off")
            fig7.patch.set_facecolor("#1e1e1e" if _dm else "#ffffff")
            cvs7.draw()
            return
        _draw_crisis_chart(fig7, prices, sc_id, _pf_spy_beta[0], _dm); cvs7.draw()

    # ── Export ────────────────────────────────────────────────────────────────

    def _update_export(fd, dd, sd):
        idx = tabs.currentIndex()
        if idx == 3:
            hdrs = [TRK("dd_col_date"), TRK("dd_col_dd"),
                    TRK("dd_col_duration"), TRK("dd_col_recovery")]
            rows = []
            for p in dd.get("periods", []):
                s = p["start"].strftime("%d.%m.%Y") if hasattr(p["start"], "strftime") else str(p["start"])[:10]
                rc = f"{p['days_recovery']} {TRK('lbl_days')}" if p["days_recovery"] is not None else TRK("lbl_still_open")
                rows.append([s, f"{p['drawdown_pct']:.1f}%",
                             f"{p['days_to_trough']} {TRK('lbl_days')}", rc])
            _export_data[0] = {"title": TRK("tab_drawdown"), "headers": hdrs, "rows": rows, "fig": fig4}
        elif idx == 4:
            hdrs = [TRK("lbl_benchmark"),
                    TRK("st_normal_corr"), TRK("st_crisis_corr"), TRK("st_delta_corr"),
                    TRK("st_normal_beta"), TRK("st_crisis_beta"), TRK("st_delta_beta")]
            def _fs(v, fmt="{:+.2f}"): return fmt.format(v) if v is not None else "—"
            rows = [[TRK(BENCHMARKS[bm]),
                    _fs(d["normal_corr"], "{:.2f}"), _fs(d["crisis_corr"], "{:.2f}"),
                    _fs(d["corr_delta"]),
                    _fs(d["normal_beta"], "{:.2f}"), _fs(d["crisis_beta"], "{:.2f}"),
                    _fs(d["beta_delta"])]
                   for bm, d in sd.get("benchmarks", {}).items()]
            _export_data[0] = {"title": TRK("tab_stress"), "headers": hdrs, "rows": rows, "fig": fig2}
        elif idx in (5, 6):
            _export_data[0] = {"title": TRK("tab_scenario") if idx == 5 else TRK("tab_hist_chart"),
                               "headers": [], "rows": [], "fig": fig6 if idx == 5 else fig7}
        else:
            bm_keys = list(BENCHMARKS.keys())
            hdrs = [TRK("lbl_symbol")] + [TRK(BENCHMARKS[bm]) for bm in bm_keys]
            rows = [[sym] + [f"{fd[sym][bm][0]:+.2f}" if bm in fd.get(sym, {}) else "—"
                            for bm in bm_keys] for sym in fd]
            _export_data[0] = {"title": TRK("tab_factor"), "headers": hdrs, "rows": rows, "fig": fig2}

    tabs.currentChanged.connect(lambda _: _update_export(_cached["factor"], _cached["dd"], _cached["stress"]))

    # ── Haupt-Loader ──────────────────────────────────────────────────────────
    class _Loader(QThread):
        done  = pyqtSignal(object)
        error = pyqtSignal(str)
        def __init__(self, period): super().__init__(); self.period = period
        def run(self):
            try:
                all_t = list(dict.fromkeys(symbols + list(BENCHMARKS.keys())))
                prices = _fetch_prices(all_t, self.period)
                if not prices: self.error.emit(TRK("err_no_data")); return
                secs = _fetch_sectors(symbols)
                self.done.emit({"rets": _to_returns(prices), "sectors": secs})
            except Exception as exc:
                self.error.emit(str(exc))

    def _on_done(result: dict) -> None:
        try:
            if not dialog.isVisible(): return
        except RuntimeError:
            return
        rets = result["rets"]; sectors = result["sectors"]
        _sectors_cache[0] = sectors
        stack.setCurrentIndex(1); refresh_btn.setEnabled(True)
        fd = _factor_table(rets, symbols); _fill_factor(fd); _cached["factor"] = fd
        pf_ret = _portfolio_returns(rets, symbols, weights)
        if pf_ret is not None:
            if "SPY" in rets:
                comb = pd.concat([pf_ret, rets["SPY"]], axis=1).dropna()
                if len(comb) > 30:
                    _pf_spy_beta[0] = float(_ols(comb.iloc[:, 1].values,
                                                  comb.iloc[:, 0].values)[0])
            _rolling_cache[0] = _rolling_corr(pf_ret, rets); _update_rolling()
            _fill_var(_var_cvar(pf_ret))
            dd = _drawdown_details(pf_ret); _fill_drawdown(dd); _cached["dd"] = dd
            sd = _stress_analysis(pf_ret, rets); _fill_stress(sd); _cached["stress"] = sd
        _update_export(fd, _cached["dd"], _cached["stress"])
        if export_btn is not None: export_btn.setEnabled(True)

    def _on_error(msg: str) -> None:
        try:
            if not dialog.isVisible(): return
        except RuntimeError:
            return
        stack.setCurrentIndex(1); refresh_btn.setEnabled(True)
        QMessageBox.warning(dialog, TRK("title"), msg)

    # ── Szenario-Loader (Tab 6 + 7) ───────────────────────────────────────────
    class _ScenarioLoader(QThread):
        done6  = pyqtSignal(object, str)   # (sector_result, source)
        done7  = pyqtSignal(object, str)   # (prices, sc_id)
        error6 = pyqtSignal(str)
        def __init__(self, sc_id: str):
            super().__init__(); self.sc_id = sc_id
        def run(self):
            try:
                shocks, src = _fetch_scenario_shocks(self.sc_id)
                sr = _compute_sector_stress(symbols_values, _sectors_cache[0], shocks)
                self.done6.emit(sr, src)
            except Exception as exc:
                self.error6.emit(str(exc))
            try:
                px = _fetch_crisis_chart(self.sc_id)
                if px is not None: self.done7.emit(px, self.sc_id)
            except Exception:
                pass

    class _ChartLoader(QThread):
        done = pyqtSignal(object, str)
        def __init__(self, sc_id: str):
            super().__init__(); self.sc_id = sc_id
        def run(self):
            try:
                px = _fetch_crisis_chart(self.sc_id)
                if px is not None: self.done.emit(px, self.sc_id)
            except Exception:
                pass

    def _start_scenario_load() -> None:
        sc_id = sc_combo.currentData()
        sc_load_btn.setEnabled(False); t6_info.setText("")
        w = _ScenarioLoader(sc_id)
        w.done6.connect(lambda sr, src: _fill_sector(sr, src))
        w.done7.connect(lambda px, sid: _fill_crisis_chart(px, sid))
        w.error6.connect(lambda msg: t6_info.setText(f"Fehler: {msg}"))
        def _sc_finished():
            sc_load_btn.setEnabled(True)
            if w in _workers: _workers.remove(w)
        w.finished.connect(_sc_finished)
        _workers.append(w); w.start()

    def _start_chart_load() -> None:
        sc_id = sc_combo7.currentData()
        t7load_btn.setEnabled(False)
        w = _ChartLoader(sc_id)
        _got_data = [False]
        def _on_chart_done(px, sid):
            _got_data[0] = True
            _fill_crisis_chart(px, sid)
        def _chart_finished():
            t7load_btn.setEnabled(True)
            if not _got_data[0]:
                _fill_crisis_chart(None, sc_id)
            if w in _workers: _workers.remove(w)
        w.done.connect(_on_chart_done)
        w.finished.connect(_chart_finished)
        _workers.append(w); w.start()

    def _fill_sector_custom() -> None:
        if not _sectors_cache[0]:
            t6_custom_info.setText(TRK("custom_no_data_err"))
            return
        t6_custom_info.setText("")
        shocks: dict[str, float] = {sec: sp.value() / 100.0
                                     for sec, sp in _sector_spins.items()}
        active = [v for v in shocks.values() if v != 0.0]
        avg_shock = (sum(active) / len(active)) if active else 0.0
        shocks["Unknown"] = avg_shock
        sr = _compute_sector_stress(symbols_values, _sectors_cache[0], shocks)
        _fill_sector(sr, "custom")

    calc_btn.clicked.connect(_fill_sector_custom)

    class _PresetLoader(QThread):
        done  = pyqtSignal(object)
        error = pyqtSignal(str)
        def __init__(self, sc_id: str):
            super().__init__(); self.sc_id = sc_id
        def run(self):
            try:
                shocks, _ = _fetch_scenario_shocks(self.sc_id)
                self.done.emit(shocks)
            except Exception as exc:
                self.error.emit(str(exc))

    def _apply_preset_to_custom() -> None:
        sc_id = preset_combo.currentData()
        if not sc_id:
            for sp in _sector_spins.values():
                sp.setValue(0.0)
            t6_custom_info.setText("")
            return
        preset_apply_btn.setEnabled(False)
        t6_custom_info.setText(TRK("lbl_loading"))
        w = _PresetLoader(sc_id)
        def _on_preset_done(shocks: dict):
            for sec, sp in _sector_spins.items():
                if sec in shocks:
                    sp.setValue(round(shocks[sec] * 100.0, 1))
        def _preset_finished():
            preset_apply_btn.setEnabled(True)
            t6_custom_info.setText("")
            if w in _workers: _workers.remove(w)
        w.done.connect(_on_preset_done)
        w.error.connect(lambda msg: t6_custom_info.setText(f"Fehler: {msg}"))
        w.finished.connect(_preset_finished)
        _workers.append(w); w.start()

    preset_apply_btn.clicked.connect(_apply_preset_to_custom)

    sc_load_btn.clicked.connect(_start_scenario_load)
    t7load_btn.clicked.connect(_start_chart_load)

    def _start_load() -> None:
        stack.setCurrentIndex(0); refresh_btn.setEnabled(False)
        if export_btn is not None: export_btn.setEnabled(False)
        w = _Loader(period_combo.currentData())
        w.done.connect(_on_done); w.error.connect(_on_error)
        w.finished.connect(lambda: _workers.remove(w) if w in _workers else None)
        _workers.append(w); w.start()

    refresh_btn.clicked.connect(_start_load)
    _start_load()
    dialog.exec()
