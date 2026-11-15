#!/usr/bin/env python3
"""
realized_gains_translations.py – Texte für „Realisierte Gewinne“ (DE / EN).
Sprache folgt der App-Einstellung (translations.get_language()).
"""

STRINGS = {
    "DE": {
        "title":            "📈 Realisierte Gewinne",
        "info":             "Gewinne und Verluste aus verkauften Aktien. Pro Verkauf werden Kauf- und "
                            "Verkaufskurs, Haltedauer und Gewinn in Handelswährung und in {base} gezeigt. "
                            "Wo die Bank-CSV Beträge liefert (Swissquote-Import), sind Gebühren und der "
                            "echte Wechselkurs enthalten. Doppelklick auf einen Verkauf: Verkaufskurs korrigieren.",
        "lbl_year":         "Jahr:",
        "all_years":        "Alle Jahre",
        "btn_refresh":      "🔄 Aktualisieren",
        "tip_refresh":      "Fehlende Verkaufskurse und Wechselkurse von Yahoo Finance laden",
        "btn_close":        "Schliessen",
        "col_symbol":       "Symbol",
        "col_sell_date":    "Verkauf",
        "col_buy_date":     "Kauf",
        "col_qty":          "Stück",
        "col_buy_price":    "Kaufkurs",
        "col_sell_price":   "Verkaufskurs",
        "col_holding":      "Haltedauer",
        "col_gain_cur":     "Gewinn",
        "col_gain_base":    "Gewinn {base}",
        "col_pct":          "%",
        "col_source":       "Quelle",
        "src_bank":         "Bank",
        "src_price":        "Kurs",
        "tip_src_bank":     "Beträge aus der Bank-CSV (inkl. Gebühren und echtem Wechselkurs)",
        "tip_src_price":    "Berechnet aus Kurs × Stück, Wechselkurs von Yahoo Finance am Kauf-/Verkaufstag",
        "tip_est_price":    "Kein Verkaufskurs erfasst – Schlusskurs von Yahoo am Verkaufstag (≈).\n"
                            "Doppelklick, um den echten Verkaufskurs einzutragen.",
        "tip_staking":      "Staking-Ertrag (Einstandspreis 0)",
        "holding_days":     "{n} T.",
        "holding_years":    "{n} J.",
        "lbl_sum_gains":    "Realisierte Kursgewinne {period}: <b>{amount} {base}</b>  "
                            "<span style='color:{muted}'>(Gewinne {gains}, Verluste {losses}, {n} Verkäufe)</span>",
        "lbl_sum_divs":     "Dividenden {period} (netto): <b>{amount} {base}</b>",
        "lbl_sum_divs_none":"Dividenden: noch keine Daten – Dividendenkonto einmal öffnen und aktualisieren.",
        "lbl_sum_costs":    "Zinsen und Gebühren {period} (laut Bank): <b>{amount} {base}</b>",
        "lbl_sum_total":    "Gesamtertrag {period}: <b>{amount} {base}</b>",
        "lbl_after_tax":    "Gesamtertrag nach Steuern {period} (geschätzt, Steuerwohnsitz {res}): <b>{amount} {base}</b>",
        "after_tax_detail": "Steuern {tax} ({parts}).",
        "after_tax_gains":  "Kursgewinne {amount}",
        "after_tax_divs":   "Dividenden zusätzlich zur Quellensteuer {amount}",
        "after_tax_note_DE":"Abgeltungssteuer + Soli nach Sparerpauschbetrag, ohne Kirchensteuer. Bei einer deutschen Bank ist die Steuer evtl. schon im Konto abgezogen.",
        "after_tax_note_AT":"KESt 27,5 %, Altbestand steuerfrei, Verluste mit Dividenden verrechnet. Bei einer österreichischen Bank ist die KESt evtl. schon im Konto abgezogen.",
        "after_tax_note_UK":"CGT 18 % (Basic Rate) nach Freibetrag £3'000; Steuer auf Dividenden je nach Einkommen – nicht enthalten.",
        "after_tax_note_US":"Short-term 24 %, long-term 15 % (angenommene Sätze); Steuer auf Dividenden je nach Einkommen – nicht enthalten.",
        "after_tax_allow_ignored": "Freibetrag nicht berücksichtigt (kein Wechselkurs zur Portfoliowährung).",
        "lbl_after_tax_ch": "Nach Steuern (Steuerwohnsitz CH): Kursgewinne im Privatvermögen steuerfrei; die Einkommenssteuer auf Dividenden hängt von Kanton und Einkommen ab und wird nicht geschätzt.",
        "lbl_after_tax_none": "Nach Steuern: für den Steuerwohnsitz „{res}“ keine Schätzung möglich (Steuerwohnsitz im Dividendenkonto unter ⚙ ändern).",
        "lbl_by_year":      "Je Jahr: {items}",
        "period_all":       "gesamt",
        "period_year":      "{year}",
        "lbl_missing":      "⚠️ {n} Verkäufe ohne Kurs oder Wechselkurs – nicht in den Summen enthalten.",
        "lbl_empty":        "Noch keine Verkäufe erfasst. Verkäufe entstehen durch Teilverkauf (−) "
                            "oder beim Import aus der Bank-CSV.",
        "status_loading":   "Lade Kurs {sym} ({i}/{n}) …",
        "status_cur":       "Lade Währung {sym} …",
        "status_fx":        "Lade Wechselkurs {cur} → {base} …",
        "status_done":      "Aktualisiert.",
        "status_errors":    "Nicht geladen: {items}",
        "status_failed":    "Abruf fehlgeschlagen: {e}",
        "edit_title":       "Verkaufskurs korrigieren",
        "edit_label":       "<b>{sym}</b> – Verkauf vom {date}, {qty} Stück<br>"
                            "Verkaufskurs in {cur}:",
        "edit_hint_pence":  "Londoner Börse: Kurs in Pence (GBp), wie bei Yahoo.",
        "edit_hint_bank":   "Hinweis: Für diesen Verkauf liegt der Nettoerlös aus der Bank-CSV vor – "
                            "er hat Vorrang vor dem Kurs.",
        "btn_ok":           "OK",
        "btn_cancel":       "Abbrechen",
        "export_title":     "Realisierte Gewinne",
        "msg_title_error":  "Fehler",
    },
    "EN": {
        "title":            "📈 Realized gains",
        "info":             "Gains and losses from sold shares. For each sale: buy and sell price, holding "
                            "period and gain in trading currency and in {base}. Where the bank CSV provides "
                            "amounts (Swissquote import), fees and the actual exchange rate are included. "
                            "Double-click a sale to correct its sell price.",
        "lbl_year":         "Year:",
        "all_years":        "All years",
        "btn_refresh":      "🔄 Refresh",
        "tip_refresh":      "Load missing sell prices and exchange rates from Yahoo Finance",
        "btn_close":        "Close",
        "col_symbol":       "Symbol",
        "col_sell_date":    "Sold",
        "col_buy_date":     "Bought",
        "col_qty":          "Qty",
        "col_buy_price":    "Buy price",
        "col_sell_price":   "Sell price",
        "col_holding":      "Holding",
        "col_gain_cur":     "Gain",
        "col_gain_base":    "Gain {base}",
        "col_pct":          "%",
        "col_source":       "Source",
        "src_bank":         "Bank",
        "src_price":        "Price",
        "tip_src_bank":     "Amounts from the bank CSV (incl. fees and actual exchange rate)",
        "tip_src_price":    "Calculated as price × quantity, Yahoo Finance exchange rate on buy/sell date",
        "tip_est_price":    "No sell price recorded – Yahoo closing price on the sell date (≈).\n"
                            "Double-click to enter the actual sell price.",
        "tip_staking":      "Staking reward (cost basis 0)",
        "holding_days":     "{n} d",
        "holding_years":    "{n} y",
        "lbl_sum_gains":    "Realized capital gains {period}: <b>{amount} {base}</b>  "
                            "<span style='color:{muted}'>(gains {gains}, losses {losses}, {n} sales)</span>",
        "lbl_sum_divs":     "Dividends {period} (net): <b>{amount} {base}</b>",
        "lbl_sum_divs_none":"Dividends: no data yet – open and refresh the dividend account once.",
        "lbl_sum_costs":    "Interest and fees {period} (per bank): <b>{amount} {base}</b>",
        "lbl_sum_total":    "Total return {period}: <b>{amount} {base}</b>",
        "lbl_after_tax":    "Total return after taxes {period} (estimate, tax residence {res}): <b>{amount} {base}</b>",
        "after_tax_detail": "Taxes {tax} ({parts}).",
        "after_tax_gains":  "capital gains {amount}",
        "after_tax_divs":   "dividends in addition to withholding tax {amount}",
        "after_tax_note_DE":"Withholding tax + Soli after saver's allowance, without church tax. With a German bank the tax may already be deducted in the account.",
        "after_tax_note_AT":"KESt 27.5%, old holdings tax-free, losses offset against dividends. With an Austrian bank the KESt may already be deducted in the account.",
        "after_tax_note_UK":"CGT 18% (basic rate) after £3,000 allowance; tax on dividends depends on income – not included.",
        "after_tax_note_US":"Short-term 24%, long-term 15% (assumed rates); tax on dividends depends on income – not included.",
        "after_tax_allow_ignored": "Allowance not applied (no exchange rate to the portfolio currency).",
        "lbl_after_tax_ch": "After taxes (tax residence CH): capital gains on private assets are tax-free; income tax on dividends depends on canton and income and is not estimated.",
        "lbl_after_tax_none": "After taxes: no estimate possible for tax residence “{res}” (change the tax residence in the dividend account under ⚙).",
        "lbl_by_year":      "By year: {items}",
        "period_all":       "total",
        "period_year":      "{year}",
        "lbl_missing":      "⚠️ {n} sales without price or exchange rate – not included in totals.",
        "lbl_empty":        "No sales recorded yet. Sales are created by partial sell (−) "
                            "or when importing a bank CSV.",
        "status_loading":   "Loading price {sym} ({i}/{n}) …",
        "status_cur":       "Loading currency {sym} …",
        "status_fx":        "Loading exchange rate {cur} → {base} …",
        "status_done":      "Updated.",
        "status_errors":    "Not loaded: {items}",
        "status_failed":    "Download failed: {e}",
        "edit_title":       "Correct sell price",
        "edit_label":       "<b>{sym}</b> – sold on {date}, {qty} shares<br>"
                            "Sell price in {cur}:",
        "edit_hint_pence":  "London Stock Exchange: price in pence (GBp), as on Yahoo.",
        "edit_hint_bank":   "Note: the net proceeds from the bank CSV are available for this sale – "
                            "they take precedence over the price.",
        "btn_ok":           "OK",
        "btn_cancel":       "Cancel",
        "export_title":     "Realized gains",
        "msg_title_error":  "Error",
    },
}


def T(key: str, **kwargs) -> str:
    try:
        from translations import get_language
        lang = get_language()
    except Exception:
        lang = "DE"
    d = STRINGS.get(lang, STRINGS["DE"])
    text = d.get(key) or STRINGS["DE"].get(key) or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
