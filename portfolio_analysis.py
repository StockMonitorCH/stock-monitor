"""
portfolio_analysis.py — Regelbasierte Portfolio-Bewertung für Stock Monitor
Keine API-Keys erforderlich. Alle Analysen basieren auf gecachten lokalen Daten.
"""
from __future__ import annotations

CRYPTO_SUFFIXES = ('-USD', '-EUR', '-CHF', '-BTC')

def _is_crypto(sym: str) -> bool:
    return any(sym.upper().endswith(s) for s in CRYPTO_SUFFIXES)

_COMMODITY_SYMS = frozenset(['XAU', 'XAG', 'XAUUSD', 'XAGUSD'])

def _is_commodity(sym: str) -> bool:
    return sym.upper() in _COMMODITY_SYMS or sym.upper().startswith('XA')


# ── Sector sets ───────────────────────────────────────────────────────────────

DEFENSIVE_SECTORS = frozenset({
    'Consumer Staples', 'Health Care', 'Healthcare',
    'Utilities', 'Financials', 'Financial Services', 'Real Estate',
})

# ── Counter-sector recommendations ───────────────────────────────────────────

_COUNTER_DE = {
    'Technology':             'Konsumgüter (Consumer Staples), Gesundheitswesen, Versorger',
    'Information Technology': 'Konsumgüter (Consumer Staples), Gesundheitswesen, Versorger',
    'Communication Services': 'Konsumgüter (Consumer Staples), Gesundheitswesen, Finanzwerte',
    'Consumer Discretionary': 'Konsumgüter (Consumer Staples), Versorger, Gesundheitswesen',
    'Energy':                 'Technologie, Konsumgüter (Consumer Staples), Gesundheitswesen',
    'Materials':              'Technologie, Gesundheitswesen, Konsumgüter (Consumer Staples)',
    'Industrials':            'Gesundheitswesen, Konsumgüter (Consumer Staples), Technologie',
    'Financials':             'Technologie, Gesundheitswesen, Konsumgüter (Consumer Staples)',
    'Financial Services':     'Technologie, Gesundheitswesen, Konsumgüter (Consumer Staples)',
    'Real Estate':            'Technologie, Konsumgüter (Consumer Staples), Gesundheitswesen',
    'Health Care':            'Technologie, Finanzwerte, Konsumgüter (Consumer Staples)',
    'Healthcare':             'Technologie, Finanzwerte, Konsumgüter (Consumer Staples)',
    'Consumer Staples':       'Technologie, Gesundheitswesen, Finanzwerte',
    'Utilities':              'Technologie, Finanzwerte, Konsumgüter (Consumer Staples)',
}

_COUNTER_EN = {
    'Technology':             'Consumer Staples, Health Care, Utilities',
    'Information Technology': 'Consumer Staples, Health Care, Utilities',
    'Communication Services': 'Consumer Staples, Health Care, Financials',
    'Consumer Discretionary': 'Consumer Staples, Utilities, Health Care',
    'Energy':                 'Technology, Consumer Staples, Health Care',
    'Materials':              'Technology, Health Care, Consumer Staples',
    'Industrials':            'Health Care, Consumer Staples, Technology',
    'Financials':             'Technology, Health Care, Consumer Staples',
    'Financial Services':     'Technology, Health Care, Consumer Staples',
    'Real Estate':            'Technology, Consumer Staples, Health Care',
    'Health Care':            'Technology, Financials, Consumer Staples',
    'Healthcare':             'Technology, Financials, Consumer Staples',
    'Consumer Staples':       'Technology, Health Care, Financials',
    'Utilities':              'Technology, Financials, Consumer Staples',
}


def analyze_portfolio(
    portfolio_data: dict,
    price_cache: dict,
    sector_cache: dict,
    limits: dict,
    language: str = 'DE',
    dark_mode: bool = False,
) -> dict:
    """
    Führt eine regelbasierte Portfolio-Bewertung durch.

    Returns dict:
        html          — fertiger HTML-String für QTextEdit
        overall_score — int 0–100
        overall_label — str
        overall_color — str
    """
    pc   = price_cache or {}
    sc   = sector_cache or {}
    lm   = limits or {}
    is_de = (language == 'DE')

    # ── Collect positions ─────────────────────────────────────────────
    positions = []
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
        is_cr  = _is_crypto(sym)
        is_com = _is_commodity(sym)
        stop   = lm.get(sym, {}).get('stop')
        total_val  += val
        total_cost += cost
        positions.append({
            'sym': sym, 'val': val, 'cost': cost,
            'sector': sector, 'is_crypto': is_cr, 'is_commodity': is_com,
            'stop': stop,
        })

    if not positions or total_val <= 0:
        msg = ("Keine Kurs-Daten vorhanden. Bitte zuerst das Portfolio aktualisieren."
               if is_de else
               "No price data available. Please refresh the portfolio first.")
        return {
            'html': f'<p style="color:#e74c3c;font-size:13px;padding:20px">{msg}</p>',
            'overall_score': 0,
            'overall_label': '—',
            'overall_color': '#888',
        }

    positions.sort(key=lambda x: x['val'], reverse=True)

    # ── Core metrics ──────────────────────────────────────────────────
    total_pnl_pct = (total_val - total_cost) / total_cost * 100 if total_cost > 0 else 0.0
    n_positions   = len(positions)

    for p in positions:
        p['weight'] = p['val'] / total_val

    hhi           = sum(p['weight'] ** 2 for p in positions)
    top_pos       = positions[0]
    top3_weight   = sum(p['weight'] for p in positions[:3])
    top3_names    = ", ".join(p['sym'] for p in positions[:3])

    winners = sum(1 for p in positions if p['cost'] > 0 and p['val'] > p['cost'])
    losers  = sum(1 for p in positions if p['cost'] > 0 and p['val'] < p['cost'])

    # Asset mix
    crypto_val    = sum(p['val'] for p in positions if p['is_crypto'])
    commodity_val = sum(p['val'] for p in positions if p['is_commodity'])
    stock_val     = total_val - crypto_val - commodity_val
    crypto_pct    = crypto_val    / total_val * 100
    commodity_pct = commodity_val / total_val * 100
    stock_pct     = stock_val     / total_val * 100

    # Sector analysis (stocks + commodities only)
    sector_vals: dict[str, float] = {}
    stock_base = sum(p['val'] for p in positions if not p['is_crypto'])
    for p in positions:
        if not p['is_crypto'] and p['sector']:
            sector_vals[p['sector']] = sector_vals.get(p['sector'], 0.0) + p['val']

    if stock_base > 0 and sector_vals:
        sec_w         = {s: v / stock_base for s, v in sector_vals.items()}
        top_sector    = max(sec_w, key=lambda k: sec_w[k])
        top_sec_pct   = sec_w[top_sector] * 100
        has_defensive = any(s in DEFENSIVE_SECTORS for s in sec_w)
        n_sectors     = len(sector_vals)
    else:
        sec_w         = {}
        top_sector    = ''
        top_sec_pct   = 0.0
        has_defensive = False
        n_sectors     = 0

    # Stop-loss
    protected_val   = sum(p['val'] for p in positions if p['stop'] is not None)
    sl_cov_pct      = protected_val / total_val * 100
    n_without_sl    = sum(1 for p in positions if p['stop'] is None)
    top_unprotected = [p for p in positions if p['stop'] is None][:3]

    # ── Scores ────────────────────────────────────────────────────────

    # Position HHI → concentration score
    if   hhi < 0.05: pos_score = 100
    elif hhi < 0.10: pos_score = 90
    elif hhi < 0.20: pos_score = 70
    elif hhi < 0.35: pos_score = 50
    elif hhi < 0.50: pos_score = 30
    else:            pos_score = 15

    # Sector top weight → sector score
    if   not sec_w:         sec_score = 60
    elif top_sec_pct < 30:  sec_score = 100
    elif top_sec_pct < 40:  sec_score = 80
    elif top_sec_pct < 50:  sec_score = 60
    elif top_sec_pct < 60:  sec_score = 40
    else:                   sec_score = 20

    # Stop-loss coverage
    if   sl_cov_pct >= 80: sl_score = 100
    elif sl_cov_pct >= 60: sl_score = 75
    elif sl_cov_pct >= 40: sl_score = 55
    elif sl_cov_pct >= 20: sl_score = 35
    else:                  sl_score = 15

    # Number of positions
    if   n_positions >= 10: npos_score = 100
    elif n_positions >= 7:  npos_score = 80
    elif n_positions >= 5:  npos_score = 60
    elif n_positions >= 3:  npos_score = 40
    else:                   npos_score = 20

    # Crypto concentration
    if   crypto_pct <= 10: cry_score = 100
    elif crypto_pct <= 20: cry_score = 80
    elif crypto_pct <= 35: cry_score = 60
    elif crypto_pct <= 50: cry_score = 40
    else:                  cry_score = 20

    # Performance (informational)
    if   total_pnl_pct >= 20:  perf_score = 100
    elif total_pnl_pct >= 10:  perf_score = 85
    elif total_pnl_pct >= 0:   perf_score = 70
    elif total_pnl_pct >= -10: perf_score = 50
    else:                      perf_score = 25

    # Weighted overall
    overall_score = int(
        pos_score  * 0.25 +
        sec_score  * 0.20 +
        sl_score   * 0.20 +
        npos_score * 0.15 +
        cry_score  * 0.10 +
        perf_score * 0.10
    )

    if   overall_score >= 80:
        ov_label = "Gut aufgestellt"  if is_de else "Well Positioned"
        ov_color = "#27ae60"
    elif overall_score >= 65:
        ov_label = "Solide"           if is_de else "Solid"
        ov_color = "#2ecc71"
    elif overall_score >= 50:
        ov_label = "Ausgewogen"       if is_de else "Balanced"
        ov_color = "#f39c12"
    elif overall_score >= 35:
        ov_label = "Verbesserungsbedarf" if is_de else "Needs Improvement"
        ov_color = "#e67e22"
    else:
        ov_label = "Hohes Risiko"     if is_de else "High Risk"
        ov_color = "#e74c3c"

    # ── Theme ─────────────────────────────────────────────────────────
    if dark_mode:
        th = {
            'section_bg':  '#252d25',
            'section_alt': '#25252d',
            'action_bg':   '#2d2d14',
            'border':      '#484848',
            'title':       '#e8f4e8',
            'body':        '#d0dcd0',
            'subtext':     '#a0b4a0',
            'ov_sub':      '#909090',
        }
    else:
        th = {
            'section_bg':  '#f8f9fa',
            'section_alt': '#f8f9fa',
            'action_bg':   '#fef9e7',
            'border':      '#d0d8e0',
            'title':       '#1a2a3a',
            'body':        '#243040',
            'subtext':     '#4a5a6a',
            'ov_sub':      '#606878',
        }

    # Pre-assign theme values used inside f-strings (avoids nested-quote SyntaxError)
    _th_border  = th['border']
    _th_title   = th['title']
    _th_body    = th['body']
    _th_subtext = th['subtext']
    _th_act_bg  = th['action_bg']

    # ── Section helpers ───────────────────────────────────────────────

    def _score_bar(score: int, color: str) -> str:
        filled = round(score / 10)
        return (
            f"<span style='font-family:monospace;font-size:15px;color:{color}'>"
            f"{'█' * filled}{'░' * (10 - filled)}"
            f"</span> <b style='font-size:14px;color:{color}'>{score}/100</b>"
        )

    def _section(icon, title, score, color, bg, body) -> str:
        score_part = f" &nbsp;—&nbsp; {_score_bar(score, color)}" if score is not None else ""
        bg_eff     = th['section_bg'] if dark_mode else bg
        return (
            f"<div style='background:{bg_eff};border-radius:10px;"
            f"border:1px solid {_th_border};margin:10px 0;padding:16px 20px'>"
            f"<div style='font-size:14px;font-weight:bold;color:{_th_title};margin-bottom:10px'>"
            f"{icon} {title}{score_part}"
            f"</div>"
            f"<div style='font-size:14px;color:{_th_body};line-height:1.75'>{body}</div>"
            f"</div>"
        )

    parts = []

    # ── Overall header ────────────────────────────────────────────────
    ov_title  = "Portfolio-Gesamtbewertung" if is_de else "Portfolio Overall Rating"
    _ov_sub   = th['ov_sub']

    if is_de:
        _scale_0   = "0 = maximales Risiko, kaum Struktur"
        _scale_100 = "100 = optimal aufgestellt"
        _scale_mid = "50 = Verbesserungsbedarf"
        _ov_hint   = "Regelbasierte Bewertung ohne API-Key · nur lokale Daten"
    else:
        _scale_0   = "0 = maximum risk, little structure"
        _scale_100 = "100 = optimally positioned"
        _scale_mid = "50 = needs improvement"
        _ov_hint   = "Rule-based rating without API key · local data only"

    parts.append(
        f"<div style='text-align:center;padding:22px 0 26px'>"
        f"<div style='font-size:58px;font-weight:bold;color:{ov_color};line-height:1'>{overall_score}</div>"
        f"<div style='font-size:21px;font-weight:bold;color:{ov_color};margin-top:4px'>{ov_label}</div>"
        f"<div style='font-size:12px;color:{_ov_sub};margin-top:6px'>{ov_title}</div>"
        f"<div style='font-size:11px;color:{_ov_sub};margin-top:8px;"
        f"border-top:1px solid {_th_border};padding-top:8px;display:inline-block'>"
        f"<span title='{_scale_0}'>0</span>"
        f"&nbsp;·&nbsp;<b>──────</b>&nbsp;·&nbsp;"
        f"<span title='{_scale_mid}'>50</span>"
        f"&nbsp;·&nbsp;<b>──────</b>&nbsp;·&nbsp;"
        f"<span title='{_scale_100}'>100</span>"
        f"</div>"
        f"<div style='font-size:11px;color:{_ov_sub};margin-top:4px'>"
        f"{_scale_0} &nbsp;·&nbsp; {_scale_100}"
        f"</div>"
        f"<div style='font-size:10px;color:{_ov_sub};margin-top:6px;font-style:italic'>{_ov_hint}</div>"
        f"</div>"
    )

    # ── 1. Gesamtüberblick ────────────────────────────────────────────
    if is_de:
        direction = "Plus" if total_pnl_pct >= 0 else "Minus"
        pnl_text  = (
            f"Das Portfolio liegt aktuell <b>{total_pnl_pct:+.1f}%</b> im {direction} "
            f"(investiert: ${total_cost:,.0f} | aktuell: ${total_val:,.0f}). "
        )
        if   total_pnl_pct >= 20: pnl_text += "Starke Outperformance – regelmässige Gewinnmitnahmen können sinnvoll sein."
        elif total_pnl_pct >= 5:  pnl_text += "Das Portfolio entwickelt sich positiv."
        elif total_pnl_pct >= 0:  pnl_text += "Leicht positiv – noch wenig Polster vorhanden."
        elif total_pnl_pct >= -10: pnl_text += "Im Verlust – prüfen, ob stark verlustbringende Positionen weiter gehalten werden sollten."
        else:                      pnl_text += "Deutliche Verluste – kritische Überprüfung aller Positionen empfohlen."
        win_str   = f"{winners} von {n_positions} Positionen im Plus"
        if losers: win_str += f", {losers} im Minus"
        body = f"{pnl_text}<br><br>📊 {win_str}. Portfolio umfasst {n_positions} Positionen in {n_sectors} Sektoren."
    else:
        direction = "profit" if total_pnl_pct >= 0 else "loss"
        pnl_text  = (
            f"The portfolio is currently <b>{total_pnl_pct:+.1f}%</b> in {direction} "
            f"(invested: ${total_cost:,.0f} | current: ${total_val:,.0f}). "
        )
        if   total_pnl_pct >= 20:  pnl_text += "Strong outperformance – consider taking partial profits regularly."
        elif total_pnl_pct >= 5:   pnl_text += "Portfolio is developing positively."
        elif total_pnl_pct >= 0:   pnl_text += "Slightly positive – little cushion yet."
        elif total_pnl_pct >= -10: pnl_text += "In loss – consider whether strongly losing positions should be held."
        else:                       pnl_text += "Significant losses – critical review of all positions recommended."
        win_str = f"{winners} of {n_positions} positions in profit"
        if losers: win_str += f", {losers} at a loss"
        body = f"{pnl_text}<br><br>📊 {win_str}. Portfolio has {n_positions} positions across {n_sectors} sectors."

    parts.append(_section('📈',
        "Gesamtüberblick" if is_de else "Overview",
        perf_score,
        '#27ae60' if total_pnl_pct >= 0 else '#e74c3c',
        '#f0fff4' if total_pnl_pct >= 0 else '#fff5f5',
        body))

    # ── 2. Positionskonzentration ─────────────────────────────────────
    if is_de:
        if pos_score >= 80:
            body = (f"Die Positionsstreuung ist <b>gut</b>. Grösste Position: {top_pos['sym']} "
                    f"({top_pos['weight']*100:.1f}%). Top-3 ({top3_names}): {top3_weight*100:.1f}%.")
        elif pos_score >= 50:
            body = (f"Moderate Konzentration – grösste Position: <b>{top_pos['sym']} ({top_pos['weight']*100:.1f}%)</b>. "
                    f"Top-3 ({top3_names}): {top3_weight*100:.1f}%. Bei Gelegenheit weiter diversifizieren.")
        else:
            body = (f"⚠️ <b>Hohe Konzentration</b> – grösste Position: <b>{top_pos['sym']} ({top_pos['weight']*100:.1f}%)</b>. "
                    f"Top-3 ({top3_names}): {top3_weight*100:.1f}%. Klumpenrisiko: "
                    f"ein starker Rückgang dieser Positionen belastet das gesamte Portfolio massiv.")
            if top_pos['weight'] > 0.20:
                body += (f" Bei einem 30%-Rückgang von {top_pos['sym']} allein verlöre das Portfolio "
                         f"ca. {top_pos['weight']*30:.1f}%.")
    else:
        if pos_score >= 80:
            body = (f"Position spread is <b>good</b>. Largest position: {top_pos['sym']} "
                    f"({top_pos['weight']*100:.1f}%). Top-3 ({top3_names}): {top3_weight*100:.1f}%.")
        elif pos_score >= 50:
            body = (f"Moderate concentration – largest position: <b>{top_pos['sym']} ({top_pos['weight']*100:.1f}%)</b>. "
                    f"Top-3 ({top3_names}): {top3_weight*100:.1f}%. Diversify further when possible.")
        else:
            body = (f"⚠️ <b>High concentration</b> – largest position: <b>{top_pos['sym']} ({top_pos['weight']*100:.1f}%)</b>. "
                    f"Top-3 ({top3_names}): {top3_weight*100:.1f}%. Cluster risk: "
                    f"a sharp drop in these positions will heavily impact the entire portfolio.")
            if top_pos['weight'] > 0.20:
                body += (f" A 30% drop in {top_pos['sym']} alone would reduce the portfolio "
                         f"by approx. {top_pos['weight']*30:.1f}%.")

    parts.append(_section('⚖️',
        "Positionskonzentration" if is_de else "Position Concentration",
        pos_score,
        '#27ae60' if pos_score >= 80 else ('#f39c12' if pos_score >= 50 else '#e74c3c'),
        '#f9f9f9', body))

    # ── 3. Sektorverteilung ────────────────────────────────────────────
    if sec_w:
        sorted_secs = sorted(sec_w.items(), key=lambda x: x[1], reverse=True)
        sec_list = " &nbsp;|&nbsp; ".join(f"{s}: {w*100:.0f}%" for s, w in sorted_secs[:6])
        if is_de:
            counter = _COUNTER_DE.get(top_sector, 'weitere Sektoren')
            if sec_score >= 80:
                body = (f"Sektorverteilung ist <b>ausgewogen</b>. Kein Sektor dominiert übermässig.<br>"
                        f"<span style='font-size:12px;color:{_th_subtext}'>{sec_list}</span>")
            elif sec_score >= 50:
                body = (f"<b>{top_sector}</b> dominiert mit {top_sec_pct:.0f}% des Nicht-Krypto-Anteils.<br>"
                        f"<span style='font-size:12px;color:{_th_subtext}'>{sec_list}</span><br>"
                        f"Als Gegengewicht bieten sich an: {counter}.")
                if not has_defensive:
                    body += " ⚠️ Keine defensiven Sektoren – erhöhte Schwankungsanfälligkeit in Abschwüngen."
            else:
                body = (f"⚠️ <b>Starke Sektorkonzentration</b> – {top_sector} macht "
                        f"<b>{top_sec_pct:.0f}%</b> des Nicht-Krypto-Anteils aus.<br>"
                        f"<span style='font-size:12px;color:{_th_subtext}'>{sec_list}</span><br>"
                        f"Empfohlene Gegengewichte: {counter}.")
                if not has_defensive:
                    body += "<br>⛔ <b>Keine defensiven Sektoren vorhanden</b> – Consumer Staples, Healthcare und Utilities bieten in Krisen wichtigen Schutz."
        else:
            counter = _COUNTER_EN.get(top_sector, 'other sectors')
            if sec_score >= 80:
                body = (f"Sector allocation is <b>well balanced</b>. No single sector dominates excessively.<br>"
                        f"<span style='font-size:12px;color:{_th_subtext}'>{sec_list}</span>")
            elif sec_score >= 50:
                body = (f"<b>{top_sector}</b> dominates at {top_sec_pct:.0f}% of the non-crypto portion.<br>"
                        f"<span style='font-size:12px;color:{_th_subtext}'>{sec_list}</span><br>"
                        f"Recommended counterweights: {counter}.")
                if not has_defensive:
                    body += " ⚠️ No defensive sectors – increased vulnerability during market downturns."
            else:
                body = (f"⚠️ <b>Heavy sector concentration</b> – {top_sector} accounts for "
                        f"<b>{top_sec_pct:.0f}%</b> of the non-crypto portion.<br>"
                        f"<span style='font-size:12px;color:{_th_subtext}'>{sec_list}</span><br>"
                        f"Recommended counterweights: {counter}.")
                if not has_defensive:
                    body += "<br>⛔ <b>No defensive sectors present</b> – Consumer Staples, Healthcare and Utilities provide crucial downside protection during crises."
    else:
        body = ("Keine Sektordaten verfügbar – bitte das Portfolio aktualisieren."
                if is_de else
                "No sector data available – please refresh the portfolio.")

    parts.append(_section('🏭',
        "Sektorverteilung" if is_de else "Sector Allocation",
        sec_score,
        '#27ae60' if sec_score >= 80 else ('#f39c12' if sec_score >= 50 else '#e74c3c'),
        '#f9f9f9', body))

    # ── 4. Asset-Mix ──────────────────────────────────────────────────
    if is_de:
        mix_parts = [f"Aktien/ETF: <b>{stock_pct:.0f}%</b>"]
        if crypto_pct > 0:    mix_parts.append(f"Krypto: <b>{crypto_pct:.0f}%</b>")
        if commodity_pct > 0: mix_parts.append(f"Rohstoffe: <b>{commodity_pct:.0f}%</b>")
        body = " &nbsp;|&nbsp; ".join(mix_parts) + ".<br>"
        if   crypto_pct > 50: body += ("⛔ Über die Hälfte des Portfolios in Krypto – extremes Volatilitätsrisiko. "
                                        "Breite Diversifikation in traditionelle Anlagen ist dringend empfohlen.")
        elif crypto_pct > 30: body += ("⚠️ Hoher Krypto-Anteil. Kryptowährungen sind stark volatil und korrelieren "
                                        "in Krisen oft mit risikoreichen Aktien. Anteil unter 20% wird empfohlen.")
        elif crypto_pct > 10: body += "Krypto-Anteil im moderaten Bereich. Höhere Volatilität im Vergleich zu Aktien beachten."
        elif crypto_pct > 0:  body += "Ausgewogener Asset-Mix. Der geringe Krypto-Anteil hält das Volatilitätsrisiko in Grenzen."
        else:                  body += "Fokus auf Aktien/ETF – konservativ und wertstabil."
    else:
        mix_parts = [f"Stocks/ETF: <b>{stock_pct:.0f}%</b>"]
        if crypto_pct > 0:    mix_parts.append(f"Crypto: <b>{crypto_pct:.0f}%</b>")
        if commodity_pct > 0: mix_parts.append(f"Commodities: <b>{commodity_pct:.0f}%</b>")
        body = " &nbsp;|&nbsp; ".join(mix_parts) + ".<br>"
        if   crypto_pct > 50: body += ("⛔ More than half the portfolio in crypto – extreme volatility risk. "
                                        "Broad diversification into traditional assets is strongly recommended.")
        elif crypto_pct > 30: body += ("⚠️ High crypto allocation. Crypto is highly volatile and often correlates "
                                        "with risky equities during crises. Allocation below 20% recommended.")
        elif crypto_pct > 10: body += "Crypto allocation in moderate range. Note higher volatility compared to stocks."
        elif crypto_pct > 0:  body += "Balanced asset mix. The low crypto share keeps volatility risk in check."
        else:                  body += "Focus on stocks/ETFs – conservative and value-stable."

    parts.append(_section('🎯',
        "Asset-Mix",
        cry_score,
        '#27ae60' if cry_score >= 80 else ('#f39c12' if cry_score >= 50 else '#e74c3c'),
        '#f9f9f9', body))

    # ── 5. Stop-Loss-Schutz ───────────────────────────────────────────
    if is_de:
        if sl_cov_pct >= 80:
            body = (f"<b>{sl_cov_pct:.0f}%</b> des Portfolio-Wertes sind durch Stop-Loss geschützt. "
                    "Ausgezeichneter Schutz bei Markteinbrüchen.")
        elif sl_cov_pct >= 50:
            body = (f"<b>{sl_cov_pct:.0f}%</b> des Portfolio-Wertes sind durch Stop-Loss geschützt. "
                    f"{n_without_sl} Positionen ohne Schutz.")
            if top_unprotected:
                body += f" Grösste ungeschützte Positionen: {', '.join(p['sym'] for p in top_unprotected)}."
        else:
            body = (f"⚠️ Nur <b>{sl_cov_pct:.0f}%</b> des Portfolio-Wertes durch Stop-Loss geschützt – "
                    f"{n_without_sl} von {n_positions} Positionen ohne Schutz.")
            if top_unprotected:
                body += (f"<br>Grösste ungeschützte Positionen: "
                         f"<b>{', '.join(p['sym'] for p in top_unprotected)}</b>. "
                         "Stop-Loss-Orders schützen vor grossen Verlusten bei unerwarteten Kurseinbrüchen.")
    else:
        if sl_cov_pct >= 80:
            body = (f"<b>{sl_cov_pct:.0f}%</b> of portfolio value is protected by stop-loss orders. "
                    "Excellent downside protection.")
        elif sl_cov_pct >= 50:
            body = (f"<b>{sl_cov_pct:.0f}%</b> of portfolio value is protected by stop-loss orders. "
                    f"{n_without_sl} positions without protection.")
            if top_unprotected:
                body += f" Largest unprotected positions: {', '.join(p['sym'] for p in top_unprotected)}."
        else:
            body = (f"⚠️ Only <b>{sl_cov_pct:.0f}%</b> of portfolio value protected by stop-loss – "
                    f"{n_without_sl} of {n_positions} positions without protection.")
            if top_unprotected:
                body += (f"<br>Largest unprotected positions: "
                         f"<b>{', '.join(p['sym'] for p in top_unprotected)}</b>. "
                         "Stop-loss orders protect against major losses during unexpected market drops.")

    parts.append(_section('🛡️',
        "Stop-Loss-Schutz" if is_de else "Stop-Loss Protection",
        sl_score,
        '#27ae60' if sl_score >= 80 else ('#f39c12' if sl_score >= 50 else '#e74c3c'),
        '#f9f9f9', body))

    # ── 6. Handlungsempfehlungen ──────────────────────────────────────
    actions = []

    if is_de:
        if pos_score < 50 and top_pos['weight'] > 0.25:
            actions.append(f"🔴 <b>Grösse von {top_pos['sym']} reduzieren</b> – "
                           f"derzeit {top_pos['weight']*100:.0f}% (Empfehlung: max. 20%)")
        elif pos_score < 80 and top_pos['weight'] > 0.15:
            actions.append(f"🟡 Position {top_pos['sym']} beobachten – "
                           f"{top_pos['weight']*100:.0f}% ist erhöht, Ziel: unter 15%")

        if sec_score < 50 and top_sector:
            counter = _COUNTER_DE.get(top_sector, 'weitere Sektoren')
            actions.append(f"🔴 <b>Sektorkonzentration {top_sector} abbauen</b> – "
                           f"Gegengewicht aufbauen in: {counter}")
        elif sec_score < 80 and not has_defensive:
            actions.append("🟡 Defensive Positionen hinzufügen – Consumer Staples oder Healthcare als Puffer in Abschwungphasen")

        if sl_score < 50:
            unp = ", ".join(p['sym'] for p in top_unprotected[:2])
            actions.append(f"🔴 <b>Stop-Loss setzen</b> – insbesondere für {unp}")
        elif sl_score < 80 and top_unprotected:
            unp = ", ".join(p['sym'] for p in top_unprotected[:2])
            actions.append(f"🟡 Stop-Loss für {unp} in Betracht ziehen")

        if   crypto_pct > 35: actions.append(f"🔴 Krypto-Anteil von {crypto_pct:.0f}% reduzieren – Ziel: unter 20%")
        elif crypto_pct > 20: actions.append(f"🟡 Krypto-Anteil ({crypto_pct:.0f}%) im Auge behalten")

        if n_positions < 5:
            actions.append(f"🟡 Portfolio mit nur {n_positions} Positionen stärker diversifizieren")

        if total_pnl_pct >= 20 and pos_score < 70:
            actions.append(f"🟡 Bei {total_pnl_pct:.0f}% Gewinn: Teilgewinne sichern und Portfolio neu ausbalancieren")

        if not actions:
            actions.append("✅ Das Portfolio ist solide aufgestellt. Regelmässige Überprüfung empfohlen.")

        intro = "Basierend auf der Analyse werden folgende Massnahmen empfohlen:"
        rec_title = "Handlungsempfehlungen"
    else:
        if pos_score < 50 and top_pos['weight'] > 0.25:
            actions.append(f"🔴 <b>Reduce {top_pos['sym']} position size</b> – "
                           f"currently {top_pos['weight']*100:.0f}% (recommendation: max. 20%)")
        elif pos_score < 80 and top_pos['weight'] > 0.15:
            actions.append(f"🟡 Monitor {top_pos['sym']} – "
                           f"{top_pos['weight']*100:.0f}% is elevated, target: below 15%")

        if sec_score < 50 and top_sector:
            counter = _COUNTER_EN.get(top_sector, 'other sectors')
            actions.append(f"🔴 <b>Reduce {top_sector} concentration</b> – "
                           f"build counterweight in: {counter}")
        elif sec_score < 80 and not has_defensive:
            actions.append("🟡 Add defensive positions – Consumer Staples or Healthcare as a buffer during downturns")

        if sl_score < 50:
            unp = ", ".join(p['sym'] for p in top_unprotected[:2])
            actions.append(f"🔴 <b>Set stop-loss orders</b> – especially for {unp}")
        elif sl_score < 80 and top_unprotected:
            unp = ", ".join(p['sym'] for p in top_unprotected[:2])
            actions.append(f"🟡 Consider stop-loss for {unp}")

        if   crypto_pct > 35: actions.append(f"🔴 Reduce crypto allocation from {crypto_pct:.0f}% – target: below 20%")
        elif crypto_pct > 20: actions.append(f"🟡 Monitor crypto allocation ({crypto_pct:.0f}%)")

        if n_positions < 5:
            actions.append(f"🟡 Diversify further – only {n_positions} positions")

        if total_pnl_pct >= 20 and pos_score < 70:
            actions.append(f"🟡 With {total_pnl_pct:.0f}% gains: consider taking partial profits and rebalancing")

        if not actions:
            actions.append("✅ Portfolio is well structured. Regular review recommended.")

        intro = "Based on the analysis, the following actions are recommended:"
        rec_title = "Action Recommendations"
    action_body = (
        f"<p style='color:{_th_subtext};margin:0 0 6px'>{intro}</p>"
        f"<ul style='margin:4px 0 4px 18px;padding:0'>"
        + "".join(f"<li style='margin:7px 0'>{a}</li>" for a in actions)
        + "</ul>"
    )
    parts.append(_section('💡', rec_title, None, '#2c3e50', _th_act_bg, action_body))

    return {
        'html':          "\n".join(parts),
        'overall_score': overall_score,
        'overall_label': ov_label,
        'overall_color': ov_color,
    }
