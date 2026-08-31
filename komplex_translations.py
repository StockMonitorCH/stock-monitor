"""
komplex_translations.py – Sprachmodul für komplex.py (Stock Monitor)
=====================================================================
Tab 1 – Faktorexposition
Tab 2 – Rollende Korrelation
Tab 3 – VaR / CVaR  (+ Calmar, Skewness, Kurtosis, Tail Ratio)
Tab 4 – Drawdown-Analyse
Tab 5 – Stress & Korrelation + Margin-Call

Verwendung in komplex.py:
    from komplex_translations import TRK
    dialog.setWindowTitle(TRK("title"))

Regeln:
  - DE-Texte sind immer das Original – nie ändern
  - EN: US English, Finance-Fachbegriffe beibehalten
  - f-String-Platzhalter {name} müssen in beiden Sprachen vorhanden sein
"""
from __future__ import annotations

_CURRENT_LANG: str = "DE"


def set_komplex_language(lang: str) -> None:
    global _CURRENT_LANG
    if lang in KOMPLEX_STRINGS:
        _CURRENT_LANG = lang


def get_komplex_language() -> str:
    return _CURRENT_LANG


def TRK(key: str, **kwargs) -> str:
    lang_dict = KOMPLEX_STRINGS.get(_CURRENT_LANG, KOMPLEX_STRINGS["DE"])
    text = lang_dict.get(key) or KOMPLEX_STRINGS["DE"].get(key) or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


KOMPLEX_STRINGS: dict[str, dict[str, str]] = {

    # ── DEUTSCH ───────────────────────────────────────────────────────────────
    "DE": {
        # Dialog
        "title":                "Komplex-Analyse",

        # Tabs
        "tab_factor":           "Faktorexposition",
        "tab_rolling":          "Rollende Korrelation",
        "tab_var":              "VaR / CVaR",
        "tab_drawdown":         "Drawdown-Analyse",
        "tab_stress":           "Stress-Korrelation",

        # Buttons
        "btn_refresh":          "↻  Aktualisieren",
        "btn_close":            "✖ Schliessen",
        "btn_help":             "❓ Hilfe",

        # Zeitraum
        "lbl_period":           "Zeitraum",
        "period_6mo":           "6 Monate",
        "period_1y":            "1 Jahr",
        "period_2y":            "2 Jahre",
        "period_3y":            "3 Jahre",

        # Ladezustand
        "lbl_loading":          "Kursdaten werden geladen …",
        "err_no_symbols":       "Kein Portfolio geladen.",
        "err_no_data":          "Daten konnten nicht geladen werden. Internetverbindung prüfen.",
        "err_no_pf_returns":    "Portfolio-Renditen konnten nicht berechnet werden (zu wenig Daten).",

        # Tab 1: Faktorexposition
        "lbl_factor_desc":      "Beta: Sensitivität gegenüber Benchmark (1.0 = identische Bewegung, "
                                "0 = unkorreliert). Tooltip auf Zelle zeigt R² (Erklärungsgrad).",
        "lbl_symbol":           "Symbol",
        "lbl_r2_tip":           "R² = {r2:.2f} – {r2pct:.0f}% der Kursbewegung durch diesen Benchmark erklärt",

        # Tab 2: Rollende Korrelation
        "lbl_benchmark":        "Benchmark",
        "chart_rolling_title":  "Rollende Korrelation: Portfolio vs. {bm}",
        "chart_rolling_y":      "Korrelation",
        "chart_rolling_x":      "Datum",
        "legend_30d":           "30 Tage",
        "legend_60d":           "60 Tage",
        "legend_90d":           "90 Tage",

        # Tab 3: VaR / CVaR
        "lbl_var_title":        "Value at Risk (historische Simulation)",
        "lbl_var_95":           "VaR 95 %",
        "lbl_var_99":           "VaR 99 %",
        "lbl_cvar_95":          "CVaR 95 %  (Expected Shortfall)",
        "lbl_cvar_99":          "CVaR 99 %  (Expected Shortfall)",
        "lbl_ann_vol":          "Volatilität (p.a.)",
        "lbl_ann_ret":          "Rendite (p.a.)",
        "lbl_max_dd":           "Max. Drawdown",
        "lbl_calmar":           "Calmar Ratio",
        "lbl_skewness":         "Schiefe (Skewness)",
        "lbl_kurtosis":         "Wölbung (excess Kurtosis)",
        "lbl_tail_ratio":       "Tail Ratio (P95/P5)",
        "chart_var_title":      "Tagesrenditen Portfolio",
        "chart_var_x":          "Tagesrendite",
        "chart_var_y":          "Häufigkeit (normiert)",
        "chart_var_95":         "VaR 95 %",
        "chart_var_99":         "VaR 99 %",

        # Tab 4: Drawdown-Analyse
        "dd_col_date":          "Beginn",
        "dd_col_dd":            "Drawdown",
        "dd_col_duration":      "Peak → Tief",
        "dd_col_recovery":      "Erholung",
        "lbl_days":             "Tage",
        "lbl_still_open":       "noch offen",
        "lbl_max_dd_dur":       "Max. DD Dauer (Peak → Tief)",
        "lbl_max_uw":           "Max. Underwater (bis Erholung)",
        "chart_underwater_title": "Portfolio unter Höchststand (Underwater-Chart)",
        "chart_underwater_y":   "Drawdown %",
        "lbl_underwater":       "Underwater",

        # Tab 5: Stress & Korrelation
        "stress_info":          "Krisenperioden: {n_crisis} von {n_total} Handelstagen "
                                "(SPY-Tagesrendite < −{thr:.1f} %)",
        "st_normal_corr":       "Norm. Korr.",
        "st_crisis_corr":       "Krisen-Korr.",
        "st_delta_corr":        "Δ Korr.",
        "st_normal_beta":       "Norm. β",
        "st_crisis_beta":       "Krisen-β",
        "st_delta_beta":        "Δ β",

        # Margin-Call Sektion (Tab 5)
        "lbl_mc_grp":           "Lombard-Kredit / Margin-Call-Distanz",
        "lbl_mc_loan":          "Kreditbetrag",
        "lbl_mc_ltv":           "LTV-Grenze",
        "lbl_mc_buffer":        "Puffer bis Margin Call",
        "lbl_mc_value":         "Margin Call bei Portfoliowert",
        "lbl_mc_ann_cost":      "Zinslast p.a.  (@ 3.5 %)",

        # Benchmark-Namen
        "bm_spy":               "S&P 500 (SPY)",
        "bm_agg":               "Anleihen (AGG)",
        "bm_gld":               "Gold (GLD)",
        "bm_vnq":               "Immob. (VNQ)",
        "bm_gsg":               "Rohstoffe (GSG)",

        # Tab 6: Sektor-Stresstest
        "tab_scenario":         "Sektor-Stresstest",
        "lbl_sc_select":        "Szenario",
        "btn_sc_load":          "▶ Laden",
        "btn_mode_hist":        "■ Historisch",
        "btn_mode_custom":      "✎ Benutzerdefiniert",
        "lbl_preset_select":    "Aus Szenario:",
        "sc_none":              "— Kein Szenario —",
        "btn_preset_apply":     "↩ Übernehmen",
        "btn_custom_calc":      "▶ Berechnen",
        "lbl_sector_shocks":    "Sektorschocks (in %):",
        "sc_custom_source":     "Benutzerdefinierte Sektorschocks",
        "custom_no_data_err":   "Keine Sektordaten – bitte zuerst Aktualisieren klicken.",
        "chart_no_data":        "Keine historischen Kursdaten für dieses Szenario verfügbar.",
        "sc_summary":           "Portfolio",
        "sc_col_sector":        "GICS-Sektor",
        "sc_col_n":             "Pos.",
        "sc_col_value":         "Marktwert",
        "sc_col_weight":        "Anteil",
        "sc_col_shock":         "Schock",
        "sc_col_stress_val":    "Stresswert",
        "sc_col_pnl":           "P&L",
        "sc_col_total":         "Portfolio Total",
        "sc_source_live":       "Datenquelle: Sektor-ETF-Renditen (yfinance, historische Daten)",
        "sc_source_est":        "Datenquelle: Historische Schätzwerte (kalibriert nach NBER/Shiller-Daten)",
        "chart_sector_title":   "Sektorverteilung: Aktuell vs. Stressszenario",

        # Tab 7: Historischer Chart
        "tab_hist_chart":        "Historischer Chart",
        "chart_hist_title":      "Krisenperiode {sc}  –  {ticker}  (indexiert auf 100)",
        "chart_hist_title_sim":  "Krisenperiode {sc}  –  Simuliert  (indexiert auf 100)",
        "chart_hist_index":      "Markt (indexiert)",
        "chart_hist_index_sim":  "Markt (simuliert)",
        "chart_hist_portfolio":  "Portfolio (geschätzt, β={beta:.2f})",
        "chart_hist_y":          "Wert (Basis 100)",
        "chart_hist_disclaimer": "⚠️  Portfoliokurve basiert auf dem aktuellen Beta vs. S&P 500 – "
                                  "nicht auf historischen Einzeltitel-Daten. Nur zur Orientierung.",
        "chart_synth_note":      "Simuliert – keine Marktdaten verfügbar\n"
                                  "Kurve aus Drawdown/Recovery-Parametern (kalibriert nach NBER/Shiller)",

        # Export
        "export_col_beta":      "Beta",
        "export_col_r2":        "R²",

        # Disclaimer
        "disclaimer":           "⚠️  Keine Anlageberatung. Berechnung auf Basis historischer Schlusskurse "
                                "(yfinance). Resultate sind keine Prognose. Benchmarks in USD.",
    },

    # ── ENGLISH ───────────────────────────────────────────────────────────────
    "EN": {
        # Dialog
        "title":                "Komplex Analysis",

        # Tabs
        "tab_factor":           "Factor Exposure",
        "tab_rolling":          "Rolling Correlation",
        "tab_var":              "VaR / CVaR",
        "tab_drawdown":         "Drawdown Analysis",
        "tab_stress":           "Stress-Correlation",

        # Buttons
        "btn_refresh":          "↻  Refresh",
        "btn_close":            "✖ Close",
        "btn_help":             "❓ Help",

        # Period
        "lbl_period":           "Period",
        "period_6mo":           "6 Months",
        "period_1y":            "1 Year",
        "period_2y":            "2 Years",
        "period_3y":            "3 Years",

        # Loading
        "lbl_loading":          "Loading price data …",
        "err_no_symbols":       "No portfolio loaded.",
        "err_no_data":          "Could not load data. Check your internet connection.",
        "err_no_pf_returns":    "Could not compute portfolio returns (insufficient data).",

        # Tab 1: Factor Exposure
        "lbl_factor_desc":      "Beta: sensitivity to benchmark (1.0 = identical movement, "
                                "0 = uncorrelated). Hover a cell to see R² (coefficient of determination).",
        "lbl_symbol":           "Symbol",
        "lbl_r2_tip":           "R² = {r2:.2f} – {r2pct:.0f}% of price movement explained by this benchmark",

        # Tab 2: Rolling Correlation
        "lbl_benchmark":        "Benchmark",
        "chart_rolling_title":  "Rolling Correlation: Portfolio vs. {bm}",
        "chart_rolling_y":      "Correlation",
        "chart_rolling_x":      "Date",
        "legend_30d":           "30 Days",
        "legend_60d":           "60 Days",
        "legend_90d":           "90 Days",

        # Tab 3: VaR / CVaR
        "lbl_var_title":        "Value at Risk (Historical Simulation)",
        "lbl_var_95":           "VaR 95%",
        "lbl_var_99":           "VaR 99%",
        "lbl_cvar_95":          "CVaR 95%  (Expected Shortfall)",
        "lbl_cvar_99":          "CVaR 99%  (Expected Shortfall)",
        "lbl_ann_vol":          "Volatility (p.a.)",
        "lbl_ann_ret":          "Return (p.a.)",
        "lbl_max_dd":           "Max. Drawdown",
        "lbl_calmar":           "Calmar Ratio",
        "lbl_skewness":         "Skewness",
        "lbl_kurtosis":         "Excess Kurtosis",
        "lbl_tail_ratio":       "Tail Ratio (P95/P5)",
        "chart_var_title":      "Portfolio Daily Returns",
        "chart_var_x":          "Daily Return",
        "chart_var_y":          "Frequency (normalized)",
        "chart_var_95":         "VaR 95%",
        "chart_var_99":         "VaR 99%",

        # Tab 4: Drawdown Analysis
        "dd_col_date":          "Start",
        "dd_col_dd":            "Drawdown",
        "dd_col_duration":      "Peak → Trough",
        "dd_col_recovery":      "Recovery",
        "lbl_days":             "days",
        "lbl_still_open":       "still open",
        "lbl_max_dd_dur":       "Max. DD Duration (Peak → Trough)",
        "lbl_max_uw":           "Max. Underwater (to Recovery)",
        "chart_underwater_title": "Portfolio Below Peak (Underwater Chart)",
        "chart_underwater_y":   "Drawdown %",
        "lbl_underwater":       "Underwater",

        # Tab 5: Stress & Correlation
        "stress_info":          "Crisis periods: {n_crisis} of {n_total} trading days "
                                "(SPY daily return < −{thr:.1f}%)",
        "st_normal_corr":       "Normal Corr.",
        "st_crisis_corr":       "Crisis Corr.",
        "st_delta_corr":        "Δ Corr.",
        "st_normal_beta":       "Normal β",
        "st_crisis_beta":       "Crisis β",
        "st_delta_beta":        "Δ β",

        # Margin-Call Section (Tab 5)
        "lbl_mc_grp":           "Lombard Loan / Margin-Call Distance",
        "lbl_mc_loan":          "Loan Amount",
        "lbl_mc_ltv":           "LTV Limit",
        "lbl_mc_buffer":        "Buffer to Margin Call",
        "lbl_mc_value":         "Margin Call at Portfolio Value",
        "lbl_mc_ann_cost":      "Annual Interest Cost  (@ 3.5%)",

        # Benchmark names
        "bm_spy":               "S&P 500 (SPY)",
        "bm_agg":               "Bonds (AGG)",
        "bm_gld":               "Gold (GLD)",
        "bm_vnq":               "Real Estate (VNQ)",
        "bm_gsg":               "Commodities (GSG)",

        # Tab 6: Sector Stress Test
        "tab_scenario":         "Sector Stress Test",
        "lbl_sc_select":        "Scenario",
        "btn_sc_load":          "▶ Load",
        "btn_mode_hist":        "■ Historical",
        "btn_mode_custom":      "✎ Custom",
        "lbl_preset_select":    "From Scenario:",
        "sc_none":              "— No Scenario —",
        "btn_preset_apply":     "↩ Apply",
        "btn_custom_calc":      "▶ Calculate",
        "lbl_sector_shocks":    "Sector Shocks (in %):",
        "sc_custom_source":     "Custom Sector Shocks",
        "custom_no_data_err":   "No sector data – please click Refresh first.",
        "chart_no_data":        "No historical price data available for this scenario.",
        "sc_summary":           "Portfolio",
        "sc_col_sector":        "GICS Sector",
        "sc_col_n":             "Pos.",
        "sc_col_value":         "Market Value",
        "sc_col_weight":        "Weight",
        "sc_col_shock":         "Shock",
        "sc_col_stress_val":    "Stress Value",
        "sc_col_pnl":           "P&L",
        "sc_col_total":         "Portfolio Total",
        "sc_source_live":       "Data source: Sector ETF returns (yfinance, historical data)",
        "sc_source_est":        "Data source: Historical estimates (calibrated from NBER/Shiller data)",
        "chart_sector_title":   "Sector Allocation: Current vs. Stress Scenario",

        # Tab 7: Historical Chart
        "tab_hist_chart":        "Historical Chart",
        "chart_hist_title":      "Crisis Period {sc}  –  {ticker}  (indexed to 100)",
        "chart_hist_title_sim":  "Crisis Period {sc}  –  Simulated  (indexed to 100)",
        "chart_hist_index":      "Market (indexed)",
        "chart_hist_index_sim":  "Market (simulated)",
        "chart_hist_portfolio":  "Portfolio (estimated, β={beta:.2f})",
        "chart_hist_y":          "Value (Base 100)",
        "chart_hist_disclaimer": "⚠️  Portfolio curve is based on the current beta vs. S&P 500 – "
                                  "not on historical individual stock data. For reference only.",
        "chart_synth_note":      "Simulated – no market data available\n"
                                  "Curve derived from drawdown/recovery parameters (calibrated from NBER/Shiller)",

        # Export
        "export_col_beta":      "Beta",
        "export_col_r2":        "R²",

        # Disclaimer
        "disclaimer":           "⚠️  Not investment advice. Calculated from historical closing prices "
                                "(yfinance). Results are not a forecast. Benchmarks denominated in USD.",
    },
}
