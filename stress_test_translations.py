"""
stress_test_translations.py – Sprachmodul für stress_test.py (Stock Monitor)
=============================================================================
Enthält alle UI-Strings des Stresstest-Moduls.
Trennung von translations.py hält das Modul eigenständig und wartbar.

Verwendung in stress_test.py:
    from stress_test_translations import TRS
    dialog.setWindowTitle(TRS("title"))

Regeln:
  - DE-Texte sind immer das Original – nie ändern
  - EN: US English, Finance-Fachbegriffe beibehalten
  - Emojis bleiben immer gleich (sprachunabhängig)
  - f-String-Platzhalter {name} etc. müssen in beiden Sprachen vorhanden sein
"""

from __future__ import annotations

# ── Aktive Sprache (aus translations.py übernommen) ──────────────────────────
_CURRENT_LANG: str = "DE"


def set_stress_language(lang: str) -> None:
    """Setzt die aktive Sprache. Wird von translations.set_language() mitgerufen."""
    global _CURRENT_LANG
    if lang in STRESS_STRINGS:
        _CURRENT_LANG = lang


def get_stress_language() -> str:
    return _CURRENT_LANG


def TRS(key: str, **kwargs) -> str:
    """
    Gibt den übersetzten String aus dem Stresstest-Modul zurück.
    Fallback: erst DE, dann der Key selbst (damit nichts leer bleibt).
    kwargs werden als .format()-Argumente übergeben.
    """
    lang_dict = STRESS_STRINGS.get(_CURRENT_LANG, STRESS_STRINGS["DE"])
    text = lang_dict.get(key) or STRESS_STRINGS["DE"].get(key) or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


# ══════════════════════════════════════════════════════════════════════════════
# STRING-TABELLE
# Struktur: STRESS_STRINGS[LANG][key] = "Text"
# ══════════════════════════════════════════════════════════════════════════════

STRESS_STRINGS: dict[str, dict[str, str]] = {

    # ── DEUTSCH (Original – nie ändern) ──────────────────────────────────────
    "DE": {

        # ── Dialog / Tabs ─────────────────────────────────────────────────────
        "title":            "Stresstest",
        "tab_hist":         "Historische Ereignisse",
        "tab_custom":       "Eigenes Szenario",

        # ── Szenario-Kombination ──────────────────────────────────────────────
        "lbl_combine":      "Szenarien kombinieren",
        "rb_or":            "Schlechtestes (OR)",
        "rb_and":           "Kombiniert (AND)",
        "and_note":         "(gleichzeitig, kumulierter Effekt)",
        "or_note":          "(schlechtestes Einzelszenario)",
        "combined_name":    "Kombiniertes Szenario",

        # ── Lombardkredit ─────────────────────────────────────────────────────
        "lbl_lombard_grp":  "Lombardkredit",
        "lbl_amount":       "Kreditbetrag",
        "lbl_rate":         "Zinssatz (% p.a.)",
        "lbl_ltv":          "LTV-Limit (%)",

        # ── Buttons ───────────────────────────────────────────────────────────
        "btn_calc":         "▶  Berechnen",
        "btn_close":        "✖ Schliessen",
        "btn_help":         "❓ Hilfe",

        # ── Ergebnis-Labels ───────────────────────────────────────────────────
        "lbl_pf_value":     "Portfoliowert aktuell",
        "lbl_stressed":     "Im Stressfall",
        "lbl_loss":         "Verlust",
        "lbl_recovery":     "Erholung bis Ausgangsniveau",
        "lbl_mc_at":        "Margin Call bei",
        "lbl_mc_hit":       "Margin Call ausgelöst",
        "lbl_mc_buffer":    "Puffer bis Margin Call",
        "lbl_annual_cost":  "Jährl. Zinskosten",
        "yes":              "JA ⚠️",
        "no":               "Nein ✓",

        # ── Fehlermeldungen ───────────────────────────────────────────────────
        "err_no_scenario":  "Bitte mindestens ein Szenario auswählen.",
        "err_no_pf":        "Kein Portfolio geladen oder Portfoliowert = 0.",

        # ── Eigenes Szenario ──────────────────────────────────────────────────
        "lbl_dd":           "Drawdown (%)",
        "lbl_bear":         "Bärenmarkt-Dauer (Monate)",
        "lbl_rec":          "Erholung (Monate)",
        "lbl_name":         "Name (optional)",
        "chk_shock2":       "Zweiten Schock hinzufügen",
        "lbl_link":         "Verknüpfung",

        # ── Chart ─────────────────────────────────────────────────────────────
        "chart_title":      "Portfolio-Erholungskurve",
        "chart_x":          "Monate",
        "chart_y":          "Portfoliowert (%)",
        "bear_phase":       "Bärenmarkt",
        "rec_phase":        "Erholung",
        "lbl_breakeven":    "Ausgangswert (100 %)",
        "lbl_trough":       "Tiefpunkt",
        "lbl_mc":           "Margin Call",

        # ── Ergebnis-Tabellen-Spalten ─────────────────────────────────────────
        "lbl_bear_dur":     "Bärenmarkt",
        "lbl_rec_dur":      "Erholung",

        # ── Zeiteinheiten ─────────────────────────────────────────────────────
        "years":            "Jahre",
        "months_short":     "M",

        # ── Disclaimer ────────────────────────────────────────────────────────
        "disclaimer":       "⚠️  Keine Anlageberatung. Alle Szenarien basieren auf S&P-500-Daten "
                            "und sind keine Prognose für Ihr Portfolio.",

        # ── Szenario-Beschreibungen (historische Ereignisse) ──────────────────
        "desc_1907":        "Bankenpanik durch fehlgeschlagene Kupfer-Markt-Spekulation.",
        "desc_1929":        "Schwarzer Dienstag, Auslöser der Grossen Depression.",
        "desc_1937":        "Fed erhöhte Mindestreserven; Rezession nach kurzer Erholung.",
        "desc_1946":        "Nachkriegsanpassung, Inflation und Demobilisierungsängste.",
        "desc_1956":        "Konjunkturabschwung nach Suez-Krise und Geldpolitik-Straffung.",
        "desc_1962":        "Kuba-Krise und Korrektur nach starkem Bullenmarkt.",
        "desc_1966":        "Kreditklemme durch Fed-Straffung, Vietnam-Kriegskosten.",
        "desc_1970":        "Hightech-Blase platzt, Penn Central Bankrott, Stagflation.",
        "desc_1973":        "Ölembargo, Watergate-Skandal, Stagflation.",
        "desc_1980":        "Fed unter Volcker erhöhte Leitzins auf 20 % gegen Inflation.",
        "desc_1987":        "Schwarzer Montag: S&P 500 fiel an einem Tag um 20 %.",
        "desc_2000":        "Internet-Blase kollabiert, 9/11-Schock verstärkt den Absturz.",
        "desc_2007":        "Subprime-Krise, Lehman-Pleite, globaler Kreditkollaps.",
        "desc_2020":        "Schnellste Korrektur der Geschichte durch globale Pandemie.",
        "desc_2022":        "Fed-Zinserhöhungen zur Bekämpfung post-COVID-Inflation.",

        # ── Szenario-Namen ────────────────────────────────────────────────────
        "sc_1907":          "Panic von 1907",
        "sc_1929":          "Crash von 1929",
        "sc_1937":          "Fed Straffung 1937",
        "sc_1946":          "Crash nach 2. Weltkrieg",
        "sc_1956":          "Eisenhower-Rezession",
        "sc_1962":          "Flash-Crash von 1962",
        "sc_1966":          "Finanzkrise von 1966",
        "sc_1970":          "Tech-Crash von 1970",
        "sc_1973":          "Börsencrash 1973–1974",
        "sc_1980":          "Volcker-Straffung 1980",
        "sc_1987":          "Crash von 1987",
        "sc_2000":          "Platzen der Dotcom-Blase",
        "sc_2007":          "Finanzkrise 2007–2008",
        "sc_2020":          "Corona-Crash 2020",
        "sc_2022":          "Aktienmarktrückgang 2022",
    },

    # ── ENGLISH ───────────────────────────────────────────────────────────────
    "EN": {

        # ── Dialog / Tabs ─────────────────────────────────────────────────────
        "title":            "Stress Test",
        "tab_hist":         "Historical Events",
        "tab_custom":       "Custom Scenario",

        # ── Szenario-Kombination ──────────────────────────────────────────────
        "lbl_combine":      "Combine Scenarios",
        "rb_or":            "Worst Case (OR)",
        "rb_and":           "Combined (AND)",
        "and_note":         "(simultaneous, compounded effect)",
        "or_note":          "(worst single scenario)",
        "combined_name":    "Combined Scenario",

        # ── Lombardkredit ─────────────────────────────────────────────────────
        "lbl_lombard_grp":  "Lombard Credit",
        "lbl_amount":       "Loan Amount",
        "lbl_rate":         "Interest Rate (% p.a.)",
        "lbl_ltv":          "LTV Limit (%)",

        # ── Buttons ───────────────────────────────────────────────────────────
        "btn_calc":         "▶  Calculate",
        "btn_close":        "✖ Close",
        "btn_help":         "❓ Help",

        # ── Ergebnis-Labels ───────────────────────────────────────────────────
        "lbl_pf_value":     "Current Portfolio Value",
        "lbl_stressed":     "Stressed Value",
        "lbl_loss":         "Loss",
        "lbl_recovery":     "Recovery to Breakeven",
        "lbl_mc_at":        "Margin Call at",
        "lbl_mc_hit":       "Margin Call Triggered",
        "lbl_mc_buffer":    "Buffer to Margin Call",
        "lbl_annual_cost":  "Annual Interest Cost",
        "yes":              "YES ⚠️",
        "no":               "No ✓",

        # ── Fehlermeldungen ───────────────────────────────────────────────────
        "err_no_scenario":  "Please select at least one scenario.",
        "err_no_pf":        "No portfolio loaded or value is 0.",

        # ── Eigenes Szenario ──────────────────────────────────────────────────
        "lbl_dd":           "Drawdown (%)",
        "lbl_bear":         "Bear Market Duration (months)",
        "lbl_rec":          "Recovery (months)",
        "lbl_name":         "Name (optional)",
        "chk_shock2":       "Add Second Shock",
        "lbl_link":         "Link",

        # ── Chart ─────────────────────────────────────────────────────────────
        "chart_title":      "Portfolio Recovery Curve",
        "chart_x":          "Months",
        "chart_y":          "Portfolio Value (%)",
        "bear_phase":       "Bear Market",
        "rec_phase":        "Recovery",
        "lbl_breakeven":    "Breakeven (100%)",
        "lbl_trough":       "Trough",
        "lbl_mc":           "Margin Call",

        # ── Ergebnis-Tabellen-Spalten ─────────────────────────────────────────
        "lbl_bear_dur":     "Bear Market",
        "lbl_rec_dur":      "Recovery",

        # ── Zeiteinheiten ─────────────────────────────────────────────────────
        "years":            "years",
        "months_short":     "m",

        # ── Disclaimer ────────────────────────────────────────────────────────
        "disclaimer":       "⚠️  Not investment advice. All scenarios are based on S&P 500 data "
                            "and are not a forecast for your portfolio.",

        # ── Szenario-Beschreibungen ───────────────────────────────────────────
        "desc_1907":        "Banking panic triggered by failed copper market speculation.",
        "desc_1929":        "Black Tuesday, onset of the Great Depression.",
        "desc_1937":        "Fed raised reserve requirements during brief Depression recovery.",
        "desc_1946":        "Post-war adjustment, inflation and demobilization fears.",
        "desc_1956":        "Economic slowdown after Suez crisis and monetary tightening.",
        "desc_1962":        "Cuban Missile Crisis and correction after strong bull market.",
        "desc_1966":        "Credit crunch from Fed tightening amid Vietnam War spending.",
        "desc_1970":        "Tech bubble burst, Penn Central bankruptcy, stagflation onset.",
        "desc_1973":        "Oil embargo, Watergate scandal, stagflation.",
        "desc_1980":        "Volcker Fed raised rates to 20% to combat double-digit inflation.",
        "desc_1987":        "Black Monday: S&P 500 dropped 20% in a single session.",
        "desc_2000":        "Internet bubble collapse amplified by 9/11 shock.",
        "desc_2007":        "Subprime crisis, Lehman bankruptcy, global credit freeze.",
        "desc_2020":        "Fastest bear market in history triggered by global pandemic.",
        "desc_2022":        "Fed rate hikes to combat post-COVID inflation surge.",

        # ── Szenario-Namen ────────────────────────────────────────────────────
        "sc_1907":          "Panic of 1907",
        "sc_1929":          "Crash of 1929",
        "sc_1937":          "Fed Tightening 1937",
        "sc_1946":          "Post-WWII Crash",
        "sc_1956":          "Eisenhower Recession",
        "sc_1962":          "Flash Crash of 1962",
        "sc_1966":          "Credit Crunch 1966",
        "sc_1970":          "Tech Crash of 1970",
        "sc_1973":          "Crash of 1973–1974",
        "sc_1980":          "Volcker Tightening 1980",
        "sc_1987":          "Black Monday 1987",
        "sc_2000":          "Dot-com Bubble Burst",
        "sc_2007":          "Global Financial Crisis",
        "sc_2020":          "COVID-19 Crash",
        "sc_2022":          "Bear Market 2022",
    },
}
