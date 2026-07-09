"""
portfolio_analysis_extended.py — Erweiterte Portfolio-Synthese (Stufe 2)
Nutzt yfinance für Netzwerk-Metriken. Kein API-Key erforderlich.
"""
from __future__ import annotations
import math
import random
from typing import Optional

try:
    import yfinance as yf
    import numpy as np
    _HAS_DEPS = True
except ImportError:
    _HAS_DEPS = False

from portfolio_analysis_texts import (
    M1, M2, M3_drawdown, M3_rsi, M3_dd_perf,
    M4_ecy_mc, M4_sector_ecy, M4_mc_sl,
    M5_risks, M5_opportunities, M5_fazit,
)

_RISK_FREE = 0.045  # 4.5% approximate risk-free rate

_CRYPTO_SUFFIXES = ('-USD', '-EUR', '-CHF', '-BTC', '-USDT', '-USDC')
_COMMODITY_SYM   = frozenset(['XAU', 'XAG', 'XAUUSD', 'XAGUSD'])
_DEFENSIVE_SECS  = frozenset({
    'Consumer Staples', 'Health Care', 'Healthcare',
    'Utilities', 'Financials', 'Financial Services', 'Real Estate',
})


def _is_crypto(sym: str) -> bool:
    return any(sym.upper().endswith(s) for s in _CRYPTO_SUFFIXES)

def _is_commodity(sym: str) -> bool:
    return sym.upper() in _COMMODITY_SYM or sym.upper().startswith('XA')

def _to_yf_sym(sym: str) -> Optional[str]:
    if _is_crypto(sym):
        return sym.split('-')[0] + '-USD'
    if _is_commodity(sym):
        s = sym.upper()
        if 'XAU' in s: return 'GC=F'
        if 'XAG' in s: return 'SI=F'
        return None
    return sym


# ── Network fetch ─────────────────────────────────────────────────────────────

def _fetch_network_metrics(
    symbols_values: list[tuple[str, float]],
    period: str = '1y',
) -> dict:
    """
    Fetch yfinance data; compute beta, alpha, sharpe, max_drawdown,
    rsi, ecy, mc_positive_pct. Returns {} on failure.
    """
    if not _HAS_DEPS or not symbols_values:
        return {}

    total_val = sum(v for _, v in symbols_values)
    if total_val <= 0:
        return {}

    weights = {sym: val / total_val for sym, val in symbols_values}
    yf_map  = {sym: _to_yf_sym(sym) for sym, _ in symbols_values}
    yf_map  = {s: ys for s, ys in yf_map.items() if ys}

    all_tickers = list({ys for ys in yf_map.values()} | {'SPY'})

    try:
        raw = yf.download(
            all_tickers, period=period,
            auto_adjust=True, progress=False, threads=True,
        )
        if isinstance(raw.columns, type(None)) or raw.empty:
            return {}
        # Handle MultiIndex vs flat columns
        if hasattr(raw.columns, 'get_level_values'):
            try:
                close = raw['Close']
            except KeyError:
                close = raw
        else:
            close = raw
    except Exception:
        return {}

    if 'SPY' not in close.columns:
        return {}

    spy_r = close['SPY'].pct_change().dropna()
    if len(spy_r) < 30:
        return {}

    # Build per-symbol return series
    sym_returns: dict[str, tuple] = {}
    for sym, ys in yf_map.items():
        if ys in close.columns:
            sr = close[ys].pct_change().dropna()
            if len(sr) >= 30:
                sym_returns[sym] = (sr, weights[sym])

    if not sym_returns:
        return {}

    # Align on common dates
    common = spy_r.index
    for sr, _ in sym_returns.values():
        common = common.intersection(sr.index)
    if len(common) < 30:
        return {}

    spy_arr = np.array(spy_r.loc[common].values, dtype=float)

    # Weighted portfolio returns
    port_arr = np.zeros(len(common), dtype=float)
    for sym, (sr, w) in sym_returns.items():
        port_arr += np.array(sr.loc[common].values, dtype=float) * w

    # Beta
    cov = np.cov(port_arr, spy_arr)
    beta = cov[0, 1] / cov[1, 1] if cov[1, 1] > 1e-12 else 1.0

    # Annualised return
    port_ann = float(np.mean(port_arr)) * 252
    spy_ann  = float(np.mean(spy_arr))  * 252

    # Alpha (Jensen)
    alpha = port_ann - (_RISK_FREE + beta * (spy_ann - _RISK_FREE))

    # Sharpe
    std_ann = float(np.std(port_arr, ddof=1)) * math.sqrt(252)
    sharpe  = (port_ann - _RISK_FREE) / std_ann if std_ann > 1e-10 else 0.0

    # Max Drawdown
    cum        = np.cumprod(1 + port_arr)
    peak       = np.maximum.accumulate(cum)
    max_dd     = float(np.min((cum - peak) / peak)) * 100  # negative %

    # Median RSI(14) across all positions
    def _rsi14(prices: np.ndarray) -> float:
        if len(prices) < 16:
            return 50.0
        d  = np.diff(prices)
        ag = float(np.mean(np.where(d[-14:] > 0, d[-14:], 0.0)))
        al = float(np.mean(np.where(d[-14:] < 0, -d[-14:], 0.0)))
        if al < 1e-12:
            return 100.0
        return 100.0 - 100.0 / (1.0 + ag / al)

    rsi_vals = []
    for sym, ys in yf_map.items():
        if ys in close.columns:
            prices = close[ys].loc[common].values
            if len(prices) >= 16:
                rsi_vals.append(_rsi14(prices.astype(float)))
    median_rsi = float(np.median(rsi_vals)) if rsi_vals else 50.0

    # ECY (Excess CAPE Yield)
    ecy = None
    try:
        spy_info = yf.Ticker('SPY').info
        pe = spy_info.get('trailingPE') or spy_info.get('forwardPE')
        if pe and float(pe) > 0:
            ecy = (1.0 / float(pe) - _RISK_FREE) * 100
    except Exception:
        pass
    if ecy is None:
        ecy = 1.5  # fallback: fair market

    # Monte Carlo (500 paths × 252 days, parametric)
    mu  = float(np.mean(port_arr))
    sig = float(np.std(port_arr, ddof=1))
    rng = np.random.default_rng()
    sim_returns = rng.normal(mu, sig, (500, 252))
    end_vals    = np.prod(1 + sim_returns, axis=1)
    mc_pos_pct  = float(np.mean(end_vals > 1.0)) * 100

    return {
        'beta': beta,
        'alpha': alpha * 100,       # as %
        'sharpe': sharpe,
        'max_drawdown': max_dd,     # negative %
        'rsi': median_rsi,
        'ecy': ecy,
        'mc_positive_pct': mc_pos_pct,
        'n_days': len(common),
    }


# ── Local metrics ─────────────────────────────────────────────────────────────

def _compute_local_metrics(positions: list[dict], total_cost: float) -> dict:
    """RI-Faktor and performance contribution per position."""
    result = {}
    for p in positions:
        sym  = p['sym']
        val  = p.get('val',  0.0)
        cost = p.get('cost', 0.0)
        if total_cost > 0 and cost > 0:
            inv_share   = cost / total_cost
            ret_contrib = (val - cost) / total_cost
            ri          = ret_contrib / inv_share
            perf_c      = ret_contrib * 100
        else:
            ri = 0.0; perf_c = 0.0
        result[sym] = {'ri': ri, 'perf_contrib': perf_c}
    return result


# ── Classification helpers ────────────────────────────────────────────────────

def _classify_archetype(
    n_positions: int, hhi: float, crypto_pct: float,
    top_sec_pct: float, top_sector: str, has_defensive: bool, n_sectors: int,
    beta: float, alpha: float, sharpe: float, max_dd: float,
    local_metrics: dict,
) -> str:
    """Score 10 archetypes; return the winner."""
    sc: dict[str, int] = {
        'aggressive_growth': 0, 'speculative': 0, 'momentum_trend': 0,
        'balanced': 0, 'defensive': 0, 'diversified': 0,
        'dividends_income': 0, 'buy_and_hold': 0, 'high_risk': 0, 'retirement': 0,
    }
    ts = top_sector.lower()

    # aggressive_growth
    sc['aggressive_growth'] += (3 if beta > 1.2 else 1 if beta > 0.9 else 0)
    sc['aggressive_growth'] += (2 if alpha > 5 else 1 if alpha > 0 else 0)
    if not has_defensive:          sc['aggressive_growth'] += 1
    if crypto_pct < 20:            sc['aggressive_growth'] += 1
    if 'tech' in ts or 'information' in ts: sc['aggressive_growth'] += 2
    if 'discretionary' in ts:      sc['aggressive_growth'] += 1

    # speculative
    sc['speculative'] += (4 if crypto_pct > 30 else 2 if crypto_pct > 15 else 0)
    sc['speculative'] += (2 if n_positions <= 5 else 1 if n_positions <= 8 else 0)
    sc['speculative'] += (2 if hhi > 0.35 else 0)
    sc['speculative'] += (2 if beta > 1.4 else 0)
    sc['speculative'] += (2 if max_dd < -40 else 0)

    # momentum_trend — driven by 1-2 outperforming positions
    ri_top = sorted([v['ri'] for v in local_metrics.values() if v['ri'] > 0], reverse=True)
    pc_top = sorted([abs(v['perf_contrib']) for v in local_metrics.values()], reverse=True)
    sc['momentum_trend'] += (3 if ri_top and ri_top[0] > 3.0 else
                              1 if ri_top and ri_top[0] > 1.5 else 0)
    sc['momentum_trend'] += (2 if pc_top and pc_top[0] > 10 else 0)
    sc['momentum_trend'] += (1 if n_positions <= 8 else 0)
    sc['momentum_trend'] += (2 if hhi > 0.20 else 0)
    sc['momentum_trend'] += (1 if sharpe > 0.8 and alpha > 2 else 0)

    # balanced
    sc['balanced'] += (2 if 5 <= n_positions <= 15 else 0)
    sc['balanced'] += (2 if 0.6 <= beta <= 1.2 else 0)
    sc['balanced'] += (2 if n_sectors >= 4 else 0)
    sc['balanced'] += (2 if has_defensive else 0)
    sc['balanced'] += (2 if hhi < 0.15 else 0)
    sc['balanced'] += (1 if 0.3 <= sharpe <= 1.2 else 0)

    # defensive
    sc['defensive'] += (4 if beta < 0.7 else 2 if beta < 0.9 else 0)
    sc['defensive'] += (3 if has_defensive else 0)
    if 'staples' in ts or 'health' in ts or 'utilit' in ts:
        sc['defensive'] += 2
    sc['defensive'] += (2 if crypto_pct < 5 else 0)
    sc['defensive'] += (2 if max_dd > -15 else 0)

    # diversified
    sc['diversified'] += (4 if n_positions >= 12 else 2 if n_positions >= 8 else 0)
    sc['diversified'] += (3 if n_sectors >= 6 else 1 if n_sectors >= 4 else 0)
    sc['diversified'] += (3 if hhi < 0.10 else 1 if hhi < 0.15 else 0)
    sc['diversified'] += (2 if top_sec_pct < 30 else 0)

    # dividends_income
    sc['dividends_income'] += (3 if has_defensive and beta < 0.9 else 0)
    if 'staples' in ts or 'utilit' in ts or 'financ' in ts or 'real estate' in ts:
        sc['dividends_income'] += 2
    sc['dividends_income'] += (2 if crypto_pct < 5 else 0)
    sc['dividends_income'] += (2 if beta < 0.8 else 0)

    # buy_and_hold
    sc['buy_and_hold'] += (2 if 0.7 <= beta <= 1.15 else 0)
    sc['buy_and_hold'] += (2 if sharpe > 0.4 else 0)
    sc['buy_and_hold'] += (2 if alpha > 0 else 0)
    sc['buy_and_hold'] += (1 if hhi < 0.25 else 0)
    sc['buy_and_hold'] += (1 if crypto_pct <= 30 else 0)
    sc['buy_and_hold'] += (2 if max_dd > -30 else 0)
    sc['buy_and_hold'] += (1 if 3 <= n_sectors <= 8 else 0)
    sc['buy_and_hold'] += (1 if n_positions >= 5 else 0)

    # high_risk
    sc['high_risk'] += (4 if beta > 1.5 else 2 if beta > 1.2 else 0)
    sc['high_risk'] += (3 if max_dd < -35 else 1 if max_dd < -25 else 0)
    sc['high_risk'] += (3 if crypto_pct > 40 else 0)
    sc['high_risk'] += (2 if hhi > 0.40 else 0)
    sc['high_risk'] += (2 if n_positions <= 4 else 0)
    sc['high_risk'] += (2 if sharpe < 0.2 and alpha < 0 else 0)

    # retirement
    sc['retirement'] += (4 if beta < 0.6 else 2 if beta < 0.8 else 0)
    sc['retirement'] += (3 if max_dd > -10 else 1 if max_dd > -20 else 0)
    sc['retirement'] += (3 if crypto_pct < 3 else 1 if crypto_pct < 8 else 0)
    sc['retirement'] += (2 if has_defensive else 0)
    sc['retirement'] += (1 if n_positions >= 5 else 0)

    winner = max(sc, key=lambda k: sc[k])
    return winner


def _classify_all(
    total_pnl_pct: float, alpha: float, beta: float, sharpe: float,
    max_dd: float, ecy: float, mc_pct: float, rsi: float, top_sector: str,
) -> dict:
    """Map metric values to class strings for text lookup."""
    perf_class  = ('strong_pos' if total_pnl_pct >= 15 else
                   'pos'        if total_pnl_pct >= 3  else
                   'flat'       if total_pnl_pct >= -3 else 'loss')
    beta_class  = ('low' if beta < 0.75 else 'high' if beta > 1.25 else 'medium')
    sharpe_cls  = ('good' if sharpe > 0.8 else 'ok' if sharpe > 0.3 else 'poor')
    alpha_cls   = ('positive' if alpha > 2 else 'neutral' if alpha > -2 else 'negative')
    dd_class    = ('low' if max_dd > -15 else 'medium' if max_dd > -30 else 'high')
    rsi_class   = ('overbought' if rsi > 65 else 'oversold' if rsi < 35 else 'neutral')
    ecy_class   = ('cheap' if ecy > 3 else 'fair' if ecy > 1 else 'expensive')
    mc_class    = ('high' if mc_pct > 70 else 'medium' if mc_pct > 50 else 'low')
    ts = top_sector.lower()
    if 'tech' in ts or 'information' in ts:
        sector_type = 'tech_heavy'
    elif 'staples' in ts or 'utilit' in ts or 'health' in ts:
        sector_type = 'defensive_heavy'
    elif 'discretionary' in ts or 'growth' in ts:
        sector_type = 'growth_heavy'
    else:
        sector_type = 'balanced'

    return {
        'perf_class': perf_class, 'beta_class': beta_class,
        'sharpe_class': sharpe_cls, 'alpha_class': alpha_cls,
        'dd_class': dd_class, 'rsi_class': rsi_class,
        'ecy_class': ecy_class, 'mc_class': mc_class,
        'sector_type': sector_type,
    }


# ── Star ratings ──────────────────────────────────────────────────────────────

def _compute_star_ratings(
    total_pnl_pct: float, alpha: float, beta: float, max_dd: float,
    sharpe: float, sl_cov_pct: float, hhi: float,
    n_positions: int, n_sectors: int, local_metrics: dict,
) -> dict:
    """Return {category: 1-5} for 5 star categories."""

    def _clamp(v, lo=0, hi=100):
        return max(lo, min(hi, v))

    def _stars(raw):
        return max(1, min(5, round(_clamp(raw) / 100 * 4 + 1)))

    # Performance
    p = 50
    p += (40 if total_pnl_pct >= 20 else 25 if total_pnl_pct >= 10 else
          10 if total_pnl_pct >= 0  else -10 if total_pnl_pct >= -10 else -25)
    p += (20 if alpha > 5 else 10 if alpha > 0 else -15 if alpha < -5 else -5 if alpha < 0 else 0)

    # Sicherheit
    s = 50
    s += (20 if beta < 0.7 else 10 if beta < 1.0 else -20 if beta > 1.3 else -10 if beta > 1.1 else 0)
    s += (20 if max_dd > -10 else 10 if max_dd > -20 else -20 if max_dd < -35 else -10 if max_dd < -25 else 0)
    s += (15 if sl_cov_pct >= 80 else 5 if sl_cov_pct >= 50 else -15 if sl_cov_pct < 20 else 0)

    # Streuung
    d = 50
    d += (35 if hhi < 0.05 else 20 if hhi < 0.10 else 5 if hhi < 0.20 else
          -25 if hhi > 0.40 else -10 if hhi > 0.25 else 0)
    d += (20 if n_positions >= 15 else 10 if n_positions >= 10 else
          -20 if n_positions <= 3 else -10 if n_positions <= 5 else 0)
    d += (15 if n_sectors >= 7 else 5 if n_sectors >= 5 else -15 if n_sectors <= 2 else 0)

    # Stabilität
    st = 50
    st += (35 if sharpe > 1.5 else 20 if sharpe > 0.8 else 5 if sharpe > 0.3 else
           -20 if sharpe < 0 else 0)
    st += (15 if beta < 0.8 else -15 if beta > 1.3 else 0)
    st += (15 if max_dd > -15 else -15 if max_dd < -30 else 0)

    # Effizienz
    ri_vals = [v['ri'] for v in local_metrics.values() if v.get('ri', 0) != 0]
    avg_ri  = sum(ri_vals) / len(ri_vals) if ri_vals else 0.0
    e = 50
    e += (25 if sharpe > 1.5 else 15 if sharpe > 0.8 else 5 if sharpe > 0.3 else
          -20 if sharpe < 0 else 0)
    e += (20 if alpha > 5 else 10 if alpha > 0 else -15 if alpha < -5 else -5 if alpha < 0 else 0)
    e += (15 if avg_ri > 1.5 else 5 if avg_ri > 1.0 else -10 if avg_ri < 0 else 0)

    return {
        'performance': _stars(p), 'sicherheit': _stars(s),
        'streuung': _stars(d), 'stabilitaet': _stars(st),
        'effizienz': _stars(e),
    }


# ── Text composition ──────────────────────────────────────────────────────────

def _get_text(d: dict, key, lang: str, fallbacks=()) -> str:
    v = d.get(key)
    if v:
        return v.get(lang, v.get('DE', ''))
    for fk in fallbacks:
        v2 = d.get(fk)
        if v2:
            return v2.get(lang, v2.get('DE', ''))
    return ''


def _compose_text(
    archetype: str, classes: dict, top_sym: str, top_sector: str,
    counter_sector: str, mc_pct: float, sl_cov_pct: float, language: str,
) -> str:
    """Assemble 4-5 prose paragraphs from text modules."""
    lang = language
    cls  = classes

    def _fill(t):
        return (t.replace('{top_sym}', top_sym)
                 .replace('{sector}', top_sector)
                 .replace('{counter_sector}', counter_sector)
                 .replace('{mc_pct}', f'{mc_pct:.0f}'))

    paras = []

    # P1 – Portfolio character (M1)
    p1 = _get_text(M1, (archetype, cls['perf_class']), lang, [
        (archetype, 'pos'), ('balanced', cls['perf_class']), ('balanced', 'pos'),
    ])
    if p1:
        paras.append(_fill(p1))

    # P2 – Risk/return (M2)
    p2 = _get_text(M2, (cls['beta_class'], cls['sharpe_class'], cls['alpha_class']), lang, [
        (cls['beta_class'], cls['sharpe_class'], 'neutral'),
        (cls['beta_class'], 'ok', 'neutral'),
        ('medium', 'ok', 'neutral'),
    ])
    if p2:
        paras.append(_fill(p2))

    # P3 – What happened (M3 drawdown + RSI, optional dd_perf combo)
    p3a = _get_text(M3_drawdown, (cls['dd_class'], cls['beta_class']), lang, [
        (cls['dd_class'], 'medium'), ('medium', cls['beta_class']),
    ])
    p3b = _get_text(M3_rsi, cls['rsi_class'], lang)
    p3c = _get_text(M3_dd_perf, (cls['dd_class'], cls['perf_class']), lang)
    p3_parts = [x for x in [p3a, p3b, p3c] if x]
    if p3_parts:
        paras.append(_fill(' '.join(p3_parts)))

    # P4 – Market context (M4 ecy/mc + sector/ecy + mc/sl)
    p4a = _get_text(M4_ecy_mc, (cls['ecy_class'], cls['mc_class']), lang, [
        (cls['ecy_class'], 'medium'), ('fair', cls['mc_class']), ('fair', 'medium'),
    ])
    p4b = _get_text(M4_sector_ecy, (cls['sector_type'], cls['ecy_class']), lang, [
        (cls['sector_type'], 'fair'), ('balanced', 'any'),
    ])
    sl_class = 'good' if sl_cov_pct >= 60 else 'poor'
    p4c = _get_text(M4_mc_sl, (cls['mc_class'], sl_class), lang)
    p4_parts = [x for x in [p4a, p4b, p4c] if x]
    if p4_parts:
        paras.append(_fill(' '.join(p4_parts)))

    # P5 – Risks + opportunities + conclusion (M5)
    risk_priority = []
    if cls['dd_class'] == 'high' and cls['beta_class'] == 'high':
        risk_priority.append('high_beta_unprotected')
    if cls['sector_type'] == 'tech_heavy':
        risk_priority.append('sector_concentration')
    if archetype in ('speculative', 'high_risk'):
        risk_priority.append('high_crypto')
    risk_priority += [
        'position_concentration', 'sector_concentration', 'no_defensive',
        'expensive_market_growth', 'no_stop_loss', 'high_beta_unprotected',
    ]
    p5a = ''
    for rk in risk_priority:
        if rk in M5_risks:
            p5a = _get_text(M5_risks, rk, lang)
            if p5a:
                break

    opp_priority = []
    if archetype in ('aggressive_growth', 'speculative', 'high_risk', 'momentum_trend'):
        opp_priority.append('protect_momentum')
    if cls['alpha_class'] == 'positive':
        opp_priority.append('leverage_alpha')
    if cls['ecy_class'] == 'cheap':
        opp_priority.append('cheap_market_opportunity')
    opp_priority += [
        'rebalance_concentration', 'add_defensive', 'add_stop_loss', 'reduce_crypto',
    ]
    p5b = ''
    for ok_ in opp_priority:
        if ok_ in M5_opportunities:
            p5b = _get_text(M5_opportunities, ok_, lang)
            if p5b:
                break

    fazit_key = 'mixed'
    if archetype in ('balanced', 'buy_and_hold') and cls['perf_class'] in ('strong_pos', 'pos'):
        fazit_key = 'solid'
    elif archetype == 'defensive' and cls['perf_class'] != 'loss':
        fazit_key = 'defensive_stable'
    elif archetype in ('diversified',) and cls['beta_class'] == 'low':
        fazit_key = 'well_structured'
    elif cls['perf_class'] == 'strong_pos' and cls['alpha_class'] == 'positive':
        fazit_key = 'strong'
    elif archetype in ('speculative', 'high_risk') and cls['perf_class'] == 'strong_pos':
        fazit_key = 'speculative_winning'
    elif cls['perf_class'] == 'loss' and cls['dd_class'] == 'high':
        fazit_key = 'critical'
    elif cls['perf_class'] == 'loss':
        fazit_key = 'needs_work'

    p5c = _get_text(M5_fazit, fazit_key, lang)
    p5_parts = [x for x in [p5a, p5b, p5c] if x]
    if p5_parts:
        paras.append(_fill(' '.join(p5_parts)))

    return ''.join(
        f"<p style='margin:0 0 14px;line-height:1.75;font-size:14px'>{p}</p>"
        for p in paras
    )


# ── Star HTML ─────────────────────────────────────────────────────────────────

def _render_stars_html(stars: dict, dark_mode: bool, language: str) -> str:
    is_de      = (language == 'DE')
    text_col   = '#e0e0e0' if dark_mode else '#2c3e50'
    bg_col     = '#1e2a1e' if dark_mode else '#fffdf0'
    border_col = '#3a5040' if dark_mode else '#e0d060'

    labels = {
        'performance': "Performance",
        'sicherheit':  "Sicherheit"       if is_de else "Safety",
        'streuung':    "Streuung"          if is_de else "Diversification",
        'stabilitaet': "Stabilität"       if is_de else "Stability",
        'effizienz':   "Effizienz"        if is_de else "Efficiency",
    }
    rows = []
    for key, label in labels.items():
        n = stars.get(key, 3)
        star_html = (
            f"<span style='color:#f1c40f;font-size:20px'>{'★' * n}</span>"
            f"<span style='color:#555;font-size:20px'>{'☆' * (5 - n)}</span>"
        )
        rows.append(
            f"<tr><td style='padding:5px 16px 5px 6px;font-size:14px;"
            f"color:{text_col};font-weight:bold;white-space:nowrap'>{label}</td>"
            f"<td style='padding:5px 0'>{star_html}</td></tr>"
        )

    title = "Portfolio-Rating" if is_de else "Portfolio Rating"
    return (
        f"<div style='background:{bg_col};border:1px solid {border_col};"
        f"border-radius:10px;padding:14px 20px;margin:0 0 16px'>"
        f"<div style='font-size:15px;font-weight:bold;color:{text_col};"
        f"margin-bottom:10px'>⭐ {title}</div>"
        f"<table style='border-spacing:0'>{''.join(rows)}</table>"
        f"</div>"
    )


# ── Main entry point ──────────────────────────────────────────────────────────

def analyze_extended(
    portfolio_data: dict,
    price_cache: dict,
    sector_cache: dict,
    limits: dict,
    language: str = 'DE',
    dark_mode: bool = False,
    period: str = '1y',
) -> dict:
    """
    Extended portfolio synthesis (Stage 2).
    Fetches yfinance data; returns {'html': str, 'error': str|None}.
    """
    if not _HAS_DEPS:
        msg = (
            "yfinance oder numpy nicht installiert. "
            "Bitte 'pip install yfinance numpy' ausführen."
            if language == 'DE' else
            "yfinance or numpy not installed. "
            "Please run 'pip install yfinance numpy'."
        )
        return {'html': f'<p style="color:#e74c3c;padding:12px">{msg}</p>', 'error': msg}

    is_de = (language == 'DE')
    pc  = price_cache  or {}
    sc  = sector_cache or {}
    lm  = limits       or {}

    # ── Rebuild positions ─────────────────────────────────────────────────
    positions  = []
    total_val  = 0.0
    total_cost = 0.0

    for sym, pos_list in portfolio_data.items():
        if '=' in sym:
            continue
        d    = pc.get(sym, {})
        val  = d.get('value_usd', 0.0) if isinstance(d, dict) else 0.0
        cost = d.get('cost_usd',  0.0) if isinstance(d, dict) else 0.0
        if val <= 0:
            val  = sum(p.get('quantity', 0) * p.get('buy_price', 0) for p in pos_list)
            cost = val
        sector = sc.get(sym, '')
        stop   = lm.get(sym, {}).get('stop')
        total_val  += val
        total_cost += cost
        positions.append({
            'sym': sym, 'val': val, 'cost': cost, 'sector': sector,
            'is_crypto': _is_crypto(sym), 'is_commodity': _is_commodity(sym),
            'stop': stop,
        })

    if not positions or total_val <= 0:
        msg = "Keine Daten verfügbar." if is_de else "No data available."
        return {'html': f'<p style="color:#e74c3c;padding:12px">{msg}</p>', 'error': msg}

    positions.sort(key=lambda x: x['val'], reverse=True)
    for p in positions:
        p['weight'] = p['val'] / total_val

    total_pnl_pct = (total_val - total_cost) / total_cost * 100 if total_cost > 0 else 0.0
    hhi           = sum(p['weight'] ** 2 for p in positions)
    n_positions   = len(positions)
    top_sym       = positions[0]['sym']

    crypto_val  = sum(p['val'] for p in positions if p['is_crypto'])
    crypto_pct  = crypto_val / total_val * 100

    sector_vals: dict[str, float] = {}
    stock_base = sum(p['val'] for p in positions if not p['is_crypto'])
    for p in positions:
        if not p['is_crypto'] and p['sector']:
            sector_vals[p['sector']] = sector_vals.get(p['sector'], 0.0) + p['val']

    if stock_base > 0 and sector_vals:
        sec_w       = {s: v / stock_base for s, v in sector_vals.items()}
        top_sector  = max(sec_w, key=lambda k: sec_w[k])
        top_sec_pct = sec_w[top_sector] * 100
        has_def     = any(s in _DEFENSIVE_SECS for s in sec_w)
        n_sectors   = len(sector_vals)
    else:
        sec_w = {}; top_sector = ''; top_sec_pct = 0.0; has_def = False; n_sectors = 0

    protected_val = sum(p['val'] for p in positions if p['stop'] is not None)
    sl_cov_pct    = protected_val / total_val * 100

    from portfolio_analysis import _COUNTER_DE, _COUNTER_EN
    counter_sector = (
        (_COUNTER_DE if is_de else _COUNTER_EN)
        .get(top_sector, 'weitere Sektoren' if is_de else 'other sectors')
    )

    local_metrics = _compute_local_metrics(positions, total_cost)

    # ── Network metrics ───────────────────────────────────────────────────
    sym_vals = [(p['sym'], p['val']) for p in positions]
    net = _fetch_network_metrics(sym_vals, period=period)

    beta   = net.get('beta',             1.0)
    alpha  = net.get('alpha',            0.0)
    sharpe = net.get('sharpe',           0.5)
    max_dd = net.get('max_drawdown',   -20.0)
    rsi    = net.get('rsi',             50.0)
    ecy    = net.get('ecy',              1.5)
    mc_pct = net.get('mc_positive_pct', 55.0)

    # ── Classify ──────────────────────────────────────────────────────────
    archetype = _classify_archetype(
        n_positions, hhi, crypto_pct, top_sec_pct, top_sector,
        has_def, n_sectors, beta, alpha, sharpe, max_dd, local_metrics,
    )

    classes = _classify_all(
        total_pnl_pct, alpha, beta, sharpe,
        max_dd, ecy, mc_pct, rsi, top_sector,
    )

    stars = _compute_star_ratings(
        total_pnl_pct, alpha, beta, max_dd, sharpe,
        sl_cov_pct, hhi, n_positions, n_sectors, local_metrics,
    )

    # ── Compose HTML ──────────────────────────────────────────────────────
    text_col   = '#d8e0e8' if dark_mode else '#2c3e50'
    bg_col     = '#1a2030' if dark_mode else '#f4f7fb'
    border_col = '#2e4060' if dark_mode else '#c0cfe0'

    archetype_labels = {
        'aggressive_growth': "Aggressiver Wachstumsinvestor" if is_de else "Aggressive Growth Investor",
        'speculative':       "Spekulativer Opportunist"       if is_de else "Speculative Opportunist",
        'momentum_trend':    "Momentum- & Trend-Investor"     if is_de else "Momentum & Trend Investor",
        'balanced':          "Ausgewogener Langfristinvestor"  if is_de else "Balanced Long-Term Investor",
        'defensive':         "Defensiver Stabilitätsinvestor"  if is_de else "Defensive Stability Investor",
        'diversified':       "Diversifizierter Allrounder"     if is_de else "Diversified All-Rounder",
        'dividends_income':  "Dividenden- & Einkommensinvestor" if is_de else "Dividend & Income Investor",
        'buy_and_hold':      "Solider Buy-and-Hold-Investor"   if is_de else "Solid Buy-and-Hold Investor",
        'high_risk':         "Hochrisiko-Investor"             if is_de else "High-Risk Investor",
        'retirement':        "Vorsichtiger Altersvorsorge-Aufbauer" if is_de else "Cautious Retirement Builder",
    }
    archetype_label = archetype_labels.get(archetype, archetype)
    pf_type_lbl     = "Portfolio-Typ" if is_de else "Portfolio Type"
    analysis_title  = "Erweiterte Portfolio-Analyse" if is_de else "Extended Portfolio Analysis"

    subtitle_col = '#a0aabb' if dark_mode else '#4a5568'
    header_html = (
        f"<div style='background:{bg_col};border:1px solid {border_col};"
        f"border-radius:10px;padding:14px 18px;margin:0 0 12px'>"
        f"<div style='font-size:15px;font-weight:bold;color:{text_col};"
        f"margin-bottom:4px'>🔍 {analysis_title}</div>"
        f"<div style='font-size:13px;color:{subtitle_col}'>"
        f"{pf_type_lbl}: <b style='color:{text_col}'>{archetype_label}</b></div>"
        f"</div>"
    )

    stars_html = _render_stars_html(stars, dark_mode, language)

    prose_html = _compose_text(
        archetype, classes, top_sym, top_sector,
        counter_sector, mc_pct, sl_cov_pct, language,
    )
    prose_block = (
        f"<div style='background:{bg_col};border:1px solid {border_col};"
        f"border-radius:10px;padding:16px 20px;margin:0 0 14px;color:{text_col}'>"
        + prose_html
        + "</div>"
    )

    return {'html': header_html + stars_html + prose_block, 'error': None}
