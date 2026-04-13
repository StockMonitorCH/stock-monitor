"""
tax_translations.py – Sprachmodul für tax_module.py (Stock Monitor)
====================================================================
Enthält alle UI-Strings des Steuermoduls.
Trennung von translations.py, damit das Steuermodul (jährlich aktualisierbar)
eigenständig bleibt.

Verwendung in tax_module.py:
    from tax_translations import TRT
    dlg.setWindowTitle(TRT("tax_loading_title"))

Regeln:
  - DE-Texte sind immer das Original – nie ändern
  - EN: US English, Finance-Fachbegriffe beibehalten
  - Emojis bleiben immer gleich (sprachunabhängig)
  - f-String-Platzhalter {name} etc. müssen in beiden Sprachen vorhanden sein
"""

from __future__ import annotations

# ── Aktive Sprache (aus translations.py übernommen) ──────────────────────────
_CURRENT_LANG: str = "DE"


def set_tax_language(lang: str) -> None:
    """Setzt die aktive Sprache. Wird von translations.set_language() mitgerufen."""
    global _CURRENT_LANG
    if lang in TAX_STRINGS:
        _CURRENT_LANG = lang


def get_tax_language() -> str:
    return _CURRENT_LANG


def TRT(key: str, **kwargs) -> str:
    """
    Gibt den übersetzten String aus dem Steuermodul zurück.
    Fallback: erst DE, dann der Key selbst (damit nichts leer bleibt).
    kwargs werden als .format()-Argumente übergeben.
    """
    lang_dict = TAX_STRINGS.get(_CURRENT_LANG, TAX_STRINGS["DE"])
    text = lang_dict.get(key) or TAX_STRINGS["DE"].get(key) or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


# ══════════════════════════════════════════════════════════════════════════════
# STRING-TABELLE
# Struktur: TAX_STRINGS[LANG][key] = "Text"
# ══════════════════════════════════════════════════════════════════════════════

TAX_STRINGS: dict[str, dict[str, str]] = {

    # ── DEUTSCH (Original – nie ändern) ──────────────────────────────────────
    "DE": {

        # ── Lade-Dialog ───────────────────────────────────────────────────────
        "tax_loading_title":            "Steuerauszug wird berechnet…",
        "tax_loading_header":           "<b>Lade Dividendendaten…</b>",
        "tax_loading_status":           "{i} / {n} Symbole abgerufen",
        "tax_loading_symbol":           "↻  {sym}",
        "tax_loading_calculating":      "{n} / {n} Symbole – berechne Steuer…",

        # ── Haupt-Dialog Titel ────────────────────────────────────────────────
        "tax_main_title":               "{flag}  Steuerauszug {name}  –  {year}",
        "tax_main_heading":             "<b>{flag}  Steuerauszug {name}  –  Steuerjahr {year}</b>",

        # ── Buttons (Haupt-Dialog) ────────────────────────────────────────────
        "tax_btn_update":               "🔄  Update Steuerregeln",
        "tax_btn_save":                 "💾  Steuerauszug speichern",
        "tax_btn_load":                 "📂  Steuerauszug laden",
        "tax_btn_export":               "📤  Exportieren",
        "tax_btn_form":                 "📋  Steuerformular",
        "tax_btn_close":                "✖  Schliessen",
        "tax_btn_help":                 "❓  Hilfe",

        # ── Tooltips (Haupt-Dialog) ───────────────────────────────────────────
        "tax_tip_update":               (
            "Steuerregeln werden jährlich aktualisiert.\n"
            "Online-Update wird nach Homepage-Launch verfügbar sein."
        ),
        "tax_tip_export":               "Als PDF, Excel oder ODS exportieren",
        "tax_tip_form_main": (
            "Steuerformular-PDF exportieren\n"
            "CH: Wertschriftenverzeichnis (DA-1) mit Kantonsauswahl\n"
            "DE: Anlage KAP (Kapitalerträge)\n"
            "AT: E1kv-Nachweis (Kapitalerträge-Beilage)"
        ),
        "tax_tip_form_disabled":        "Steuerformular-Export nur für CH, DE, AT, UK und US verfügbar",
        "tax_tip_help":                 "Hilfe zum Steuermodul anzeigen",

        # ── Tabellen-Spalten ──────────────────────────────────────────────────
        "tax_col_ticker":               "Ticker",
        "tax_col_name":                 "Name",
        "tax_col_qty":                  "Stück",
        "tax_col_price":                "Kurs",
        "tax_col_market_val":           "Marktwert",
        "tax_col_div":                  "Dividende/J.",
        "tax_col_vst":                  "Verrechnungssteuer",
        "tax_col_foreign_tax":          "Ausländische QSt.",
        "tax_col_note":                 "Hinweis",
        "tax_col_unrealised":           "Nicht realisierter Gewinn",
        "tax_col_withholding":          "Quellensteuer",
        "tax_col_dba":                  "DBA-Satz",
        # Kurz-Varianten für Export-Tabellen (PDF/XLSX/ODS)
        "tax_col_kest_div_short":       "KESt Div.",
        "tax_col_vst_short":            "VSt (35%)",
        "tax_col_foreign_short":        "Ausländ. QSt",
        "tax_col_rate":                 "Satz",
        "tax_col_unrealised_short":     "Nicht real. Gewinn",
        "tax_lbl_summary":              "Zusammenfassung",
        "tax_lbl_tax_statement":        "Steuerauszug",

        # ── Zusammenfassung – Labels ──────────────────────────────────────────
        "tax_sum_market_val":           "Gesamter Marktwert:",
        "tax_sum_gross_div":            "Gesamte Brutto-Dividenden:",
        # AT
        "tax_sum_kest_div":             "KESt 27,5 % auf Dividenden:",
        "tax_sum_foreign_tax":          "Ausländische Quellensteuern (anrechenbar):",
        "tax_sum_kest_gain":            "KESt auf nicht real. Kursgewinne (Schätzung):",
        "tax_sum_total_tax":            "Gesamtsteuer (geschätzt):",
        "tax_sum_net_div_kest":         "Netto-Dividenden (nach KESt / QSt, geschätzt):",
        "tax_sum_verlustausgleich":     "ℹ  Verlustausgleich:",
        # CH
        "tax_sum_vst":                  "Verrechnungssteuer (CH, rückforderbar):",
        "tax_sum_foreign_tax_est":      "Ausländische Quellensteuern (geschätzt):",
        "tax_sum_total_tax_ch":         "Gesamtsteuer:",
        "tax_sum_net_div_ch":           "Netto-Dividenden (nach Steuer, geschätzt):",
        "tax_sum_wealth_tax":           "⚠  Vermögenssteuer:",
        # DE
        "tax_sum_freistellung":         "Freistellungsauftrag:",
        "tax_sum_taxable_div":          "Steuerpflichtige Dividenden:",
        "tax_sum_abgeltung":            "Abgeltungssteuer (25 %):",
        "tax_sum_soli":                 "Solidaritätszuschlag (5,5 % auf AbgSt):",
        "tax_sum_total_tax_de":         "Gesamtsteuer:",
        "tax_sum_net_div_de":           "Netto-Dividenden:",
        # UK
        "tax_sum_div_allowance":        "Dividend Allowance (£500):",
        "tax_sum_taxable_div_uk":       "Steuerpflichtige Dividenden:",
        "tax_sum_div_tax_basic":        "Dividendensteuer (Basic Rate 8,75 %):",
        "tax_sum_net_div_uk":           "Netto-Dividenden:",
        # US
        "tax_sum_total_tax_us":         "Quellensteuer gesamt:",
        "tax_sum_net_div_us":           "Netto-Dividenden (nach QSt):",

        # ── Wash Sale Hinweis (US) ────────────────────────────────────────────
        "tax_wash_sale_text": (
            "<b>Wash Sale Rule (IRC § 1091):</b> Verluste sind steuerlich NICHT "
            "abzugsfähig, wenn dieselbe Aktie innerhalb von 30 Tagen vor oder nach "
            "dem Verkauf zurückgekauft wurde. Diese Regel wird hier nicht automatisch "
            "berechnet. Bitte prüfen Sie Ihren Broker-Auszug (1099-B) auf "
            "'Wash Sale Loss Disallowed'-Einträge."
        ),

        # ── Globaler Disclaimer ───────────────────────────────────────────────
        "tax_disclaimer_global": (
            "Bitte verwenden Sie für Ihre Steuererklärung den originalen Bankauszug. "
            "Dieses Portfolio kann bis zu ca. 2 % vom tatsächlichen Bankwert abweichen "
            "(Bankrundungen, Devisenkurse). Gebühren, Lombardkredite und sonstige "
            "Bankkosten sind nicht berücksichtigt. Keine Steuerberatung."
        ),

        # ── Export-Format Dialog ──────────────────────────────────────────────
        "tax_export_title":             "📤  Exportieren",
        "tax_export_heading":           "<b>Steuerauszug {name} exportieren</b>",
        "tax_export_format_label":      "Format wählen:",
        "tax_export_rb_pdf":            "📄  PDF",
        "tax_export_rb_xlsx":           "📊  Excel (.xlsx)",
        "tax_export_rb_ods":            "📋  OpenDocument (.ods)",
        "tax_export_btn_save":          "💾  Speichern…",
        "tax_export_btn_cancel":        "Abbrechen",
        "tax_export_save_dialog":       "Datei speichern",
        "tax_export_default_filename":  "Steuerauszug_{country}",
        "tax_export_success_title":     "Exportiert",
        "tax_export_success_msg":       "✅  Gespeichert:\n{path}",
        "tax_export_error_title":       "Fehler",
        "tax_export_error_msg":         "Export fehlgeschlagen:\n{error}",

        # ── Keine Daten Warnung ───────────────────────────────────────────────
        "tax_no_data_title":            "Keine Daten",
        "tax_no_data_msg":              "Bitte zuerst den Steuerauszug laden (Dialog öffnen und warten).",

        # ── Passwort setzen Dialog ────────────────────────────────────────────
        "tax_pw_set_title":             "🔐  Passwort setzen",
        "tax_pw_set_heading":           "<b>Passwort für Steuerauszug setzen</b>",
        "tax_pw_set_hint": (
            "<small style='color:#666'>Mindestens 12 Zeichen. Die .smtx-Datei kann<br>"
            "damit auf jedem PC geöffnet werden.</small>"
        ),
        "tax_pw_label":                 "Passwort:",
        "tax_pw_placeholder":           "Mindestens 12 Zeichen…",
        "tax_pw_confirm_label":         "Passwort bestätigen:",
        "tax_pw_confirm_placeholder":   "Wiederholen…",
        "tax_pw_show_cb":               "Passwort anzeigen",
        "tax_pw_btn_cancel":            "Abbrechen",
        "tax_pw_btn_save":              "🔐  Speichern",
        "tax_pw_err_short":             "⚠ Passwort muss mindestens 12 Zeichen haben.",
        "tax_pw_err_mismatch":          "⚠ Passwörter stimmen nicht überein.",
        # Passwort-Stärke Labels
        "tax_pw_strength_weak":         "Schwach",
        "tax_pw_strength_medium":       "Mittel",
        "tax_pw_strength_strong":       "Stark",
        "tax_pw_strength_very_strong":  "Sehr stark",
        # Speichern-Dialoge
        "tax_save_dialog_title":        "Steuerauszug speichern",
        "tax_save_success_title":       "Gespeichert",
        "tax_save_success_msg":         "✅  Steuerauszug gespeichert:\n{path}\n🔐  AES-256-GCM verschlüsselt",
        "tax_save_success_unenc_msg":   "✅  Steuerauszug gespeichert (unverschlüsselt – 'cryptography' fehlt):\n{path}",
        "tax_save_error_title":         "Fehler",
        "tax_save_error_msg":           "Speichern fehlgeschlagen:\n{error}",

        # ── Passwort eingeben Dialog (Laden) ──────────────────────────────────
        "tax_pw_enter_title":           "🔐  Passwort eingeben",
        "tax_pw_enter_for_file":        "<b>Passwort für:</b><br><small>{filename}</small>",
        "tax_pw_enter_placeholder":     "Passwort eingeben…",
        "tax_pw_enter_btn_open":        "🔓  Öffnen",
        "tax_pw_enter_btn_cancel":      "Abbrechen",
        "tax_pw_wrong_title":           "Fehler",
        "tax_pw_wrong_msg":             "Falsches Passwort oder beschädigte Datei.",
        # Laden-Dialoge
        "tax_load_dialog_title":        "Steuerauszug laden",
        "tax_load_error_title":         "Fehler",
        "tax_load_error_msg":           "Datei konnte nicht gelesen werden:\n{error}",
        "tax_load_success_title":       "Geladen",
        "tax_load_success_msg": (
            "✅  Steuerauszug geladen:\n{filename}\n"
            "(Anzeige zeigt weiterhin aktuelle Portfolio-Daten)"
        ),

        # ── Hilfe-Dialog ──────────────────────────────────────────────────────
        "tax_help_title":               "Hilfe – Steuermodul {name}",
        "tax_help_btn_close":           "✖  Schliessen",
        "tax_help_no_text":             "<p>Für dieses Land ist noch kein Hilfetext verfügbar.</p>",
        "tax_help_lang_label":          "Sprache:",

        # ── Steuerformular-Export Dialog ──────────────────────────────────────
        "tax_form_title":               "📋  Steuerformular exportieren",
        "tax_form_btn_export":          "📋  PDF exportieren",
        "tax_form_btn_cancel":          "Abbrechen",
        # CH
        "tax_form_ch_heading":          "🇨🇭  Wertschriftenverzeichnis – Schweiz",
        "tax_form_ch_info": (
            "Exportiert ein ausgefülltes Wertschriftenverzeichnis (Formular DA-1) "
            "als Orientierungshilfe. Kurse per 31.12., Währungsumrechnung via SNB/Yahoo Finance."
        ),
        "tax_form_ch_region_label":     "Kanton:",
        "tax_form_ch_stichtag":         "Stichtag Kurse: 31.12.{year}  |  Währungskurse: SNB-Jahresendkurs {year}",
        "tax_form_ch_disc": (
            "Orientierungshilfe – kein offizielles Steuerformular. "
            "Bitte mit dem originalen Bankauszug und dem kantonalen Online-Portal vergleichen. "
            "Wertschriftenverzeichnis / Formular DA-1 (Steuerjahr {year})."
        ),
        "tax_form_ch_save_dialog":      "Wertschriftenverzeichnis speichern",
        "tax_form_ch_default_filename": "Wertschriftenverzeichnis_{canton}_{year}.pdf",
        "tax_form_ch_success_title":    "Export erfolgreich",
        "tax_form_ch_success_msg":      "Wertschriftenverzeichnis ({canton_name}) exportiert:\n{path}",
        "tax_form_ch_error_title":      "Fehler",
        "tax_form_ch_error_msg":        "Export fehlgeschlagen:\n{error}",
        # DE
        "tax_form_de_heading":          "🇩🇪  Anlage KAP – Deutschland",
        "tax_form_de_info": (
            "Exportiert eine ausgefüllte Anlage KAP (Kapitalerträge) als Orientierungshilfe. "
            "Inkl. Freistellungsauftrag-Berechnung, Abgeltungsteuer und Soli. "
            "Kurse per 31.12., Währungsumrechnung via Bundesbank/Yahoo Finance."
        ),
        "tax_form_de_region_label":     "Bundesland (für Kirchensteuer-Hinweis):",
        "tax_form_de_stichtag":         "Stichtag Kurse: 31.12.{year}  |  Währungskurse: Bundesbank-Jahresendkurs {year}",
        "tax_form_de_disc": (
            "Orientierungshilfe – kein offizielles ELSTER-Formular. "
            "Bitte mit der Jahressteuerbescheinigung der Depotbank vergleichen. "
            "Anlage KAP (Steuerjahr {year})."
        ),
        "tax_form_de_save_dialog":      "Anlage KAP speichern",
        "tax_form_de_default_filename": "Anlage_KAP_{year}.pdf",
        "tax_form_de_success_title":    "Export erfolgreich",
        "tax_form_de_success_msg":      "Anlage KAP ({bl_name}) exportiert:\n{path}",
        "tax_form_de_error_title":      "Fehler",
        "tax_form_de_error_msg":        "Export fehlgeschlagen:\n{error}",
        # AT
        "tax_form_at_heading":          "🇦🇹  E1kv-Nachweis – Österreich",
        "tax_form_at_info": (
            "Exportiert einen Nachweis für ausländische Kapitalerträge (E1kv-Beilage) "
            "als Orientierungshilfe. Hilft bei der Rückforderung ausländischer Quellensteuern. "
            "Kurse per 31.12., Währungsumrechnung via OeNB/Yahoo Finance."
        ),
        "tax_form_at_region_label":     "Finanzamt-Region (optional):",
        "tax_form_at_stichtag":         "Stichtag Kurse: 31.12.{year}  |  Währungskurse: OeNB-Jahresendkurs {year}",
        "tax_form_at_disc": (
            "Orientierungshilfe – kein offizielles FinanzOnline-Formular. "
            "KESt wird bei österreichischem Depot automatisch durch die Depotbank abgeführt. "
            "E1kv-Nachweis für QSt-Rückforderung (Steuerjahr {year})."
        ),
        "tax_form_at_save_dialog":      "E1kv-Nachweis speichern",
        "tax_form_at_default_filename": "E1kv_Nachweis_{year}.pdf",
        "tax_form_at_success_title":    "Export erfolgreich",
        "tax_form_at_success_msg":      "E1kv-Nachweis exportiert:\n{path}",
        "tax_form_at_error_title":      "Fehler",
        "tax_form_at_error_msg":        "Export fehlgeschlagen:\n{error}",
        # UK
        "tax_form_uk_heading":          "🇬🇧  Capital Gains & Dividends – United Kingdom",
        "tax_form_uk_info": (
            "Exports a Capital Gains Tax / Dividend Tax summary (SA108 / SA100 guidance) "
            "as an orientation aid. Dividend Allowance £500, CGT Annual Exempt £3,000 (2024/25). "
            "Prices at 5 April (UK tax year end), FX via Yahoo Finance."
        ),
        "tax_form_uk_region_label":     "UK Nation (für Steuerhinweis):",
        "tax_form_uk_stichtag":         "Tax year end: 5 April {year}  |  FX rates: Yahoo Finance",
        "tax_form_uk_disc": (
            "Orientation aid – not an official HMRC form. "
            "Please compare with your broker's annual tax statement (e.g. Consolidated Tax Certificate). "
            "Self Assessment SA100 / SA108 (tax year {year}/{year_plus1})."
        ),
        "tax_form_uk_save_dialog":      "SA108 Summary speichern",
        "tax_form_uk_default_filename": "UK_Tax_Summary_{year}.pdf",
        "tax_form_uk_success_title":    "Export successful",
        "tax_form_uk_success_msg":      "UK Tax Summary ({nation_name}) exported:\n{path}",
        "tax_form_uk_error_title":      "Error",
        "tax_form_uk_error_msg":        "Export failed:\n{error}",
        # US
        "tax_form_us_heading":          "🇺🇸  Schedule B / Form 1040 – United States",
        "tax_form_us_info": (
            "Exports a dividend & withholding tax summary (Schedule B / 1099-DIV guidance) "
            "as an orientation aid. For non-US persons: 30 % / DBA 15 % withholding. "
            "For US residents: Qualified Dividends 0/15/20 %."
        ),
        "tax_form_us_region_label":     "Investor-Status:",
        "tax_form_us_stichtag":         "Tax year: {year}  |  Form 1040 / Schedule B / 1099-DIV",
        "tax_form_us_disc": (
            "Orientation aid – not an official IRS form. "
            "Please compare with your broker's 1099-DIV / 1042-S statement. "
            "Wash Sale Rule (30-day window) is NOT calculated automatically – "
            "check your broker's 1099-B for disallowed losses."
        ),
        "tax_form_us_state_label":      "Bundesstaat (State Tax):",
        "tax_form_us_state_note":       "State Income Tax wird im PDF als Hinweis ausgewiesen (Schätzung).",
        "tax_form_us_filing_label":     "Filing Status:",
        "tax_form_us_filing_note":      "Bestimmt die Einkommensschwellen für Qualified Dividend Rates.",
        "tax_form_us_save_dialog":      "US Tax Summary speichern",
        "tax_form_us_default_filename": "US_Tax_Summary_{year}.pdf",
        "tax_form_us_success_title":    "Export erfolgreich",
        "tax_form_us_success_msg":      "US Tax Summary gespeichert:\n{path}",
        "tax_form_us_error_title":      "Fehler",
        "tax_form_us_error_msg":        "Export fehlgeschlagen:\n{error}",

        # ── AT FA_REGIONEN Dropdown ───────────────────────────────────────────
        "tax_fa_alle":                  "Alle / Nicht spezifiziert",

        # ── US_TYPES Dropdown ─────────────────────────────────────────────────
        "tax_us_type_ch":               "Schweizer / DBA CH-US (15 % QSt)",
        "tax_us_type_de":               "Deutsch / DBA DE-US (15 % QSt)",
        "tax_us_type_at":               "Österreicher / DBA AT-US (15 % QSt)",
        "tax_us_type_nra":              "Nicht-US-Person ohne DBA (30 % QSt)",
        "tax_us_type_res":              "US-Resident (Qualified Dividends / LTCG)",

        # ── Dateidialoge / Filter ─────────────────────────────────────────────
        "tax_file_save_default":        "Steuerauszug_{country}_{year}",
        "tax_file_filter_smtx":         "Steuerauszug (*.smtx)",
        "tax_file_filter_all":          "Alle Dateien (*)",

    },

    # ── ENGLISH (US) ─────────────────────────────────────────────────────────
    "EN": {

        # ── Lade-Dialog ───────────────────────────────────────────────────────
        "tax_loading_title":            "Calculating tax statement…",
        "tax_loading_header":           "<b>Loading dividend data…</b>",
        "tax_loading_status":           "{i} / {n} symbols retrieved",
        "tax_loading_symbol":           "↻  {sym}",
        "tax_loading_calculating":      "{n} / {n} symbols – calculating taxes…",

        # ── Haupt-Dialog Titel ────────────────────────────────────────────────
        "tax_main_title":               "{flag}  Tax Statement {name}  –  {year}",
        "tax_main_heading":             "<b>{flag}  Tax Statement {name}  –  Tax Year {year}</b>",

        # ── Buttons (Haupt-Dialog) ────────────────────────────────────────────
        "tax_btn_update":               "🔄  Update Tax Rules",
        "tax_btn_save":                 "💾  Save Tax Statement",
        "tax_btn_load":                 "📂  Load Tax Statement",
        "tax_btn_export":               "📤  Export",
        "tax_btn_form":                 "📋  Tax Form",
        "tax_btn_close":                "✖  Close",
        "tax_btn_help":                 "❓  Help",

        # ── Tooltips (Haupt-Dialog) ───────────────────────────────────────────
        "tax_tip_update": (
            "Tax rules are updated annually.\n"
            "Online update will be available after homepage launch."
        ),
        "tax_tip_export":               "Export as PDF, Excel or ODS",
        "tax_tip_form_main": (
            "Export tax form PDF\n"
            "CH: Securities Schedule (DA-1) with canton selection\n"
            "DE: Anlage KAP (capital income)\n"
            "AT: E1kv declaration (capital income supplement)"
        ),
        "tax_tip_form_disabled":        "Tax form export available for CH, DE, AT, UK and US only",
        "tax_tip_help":                 "Show help for tax module",

        # ── Tabellen-Spalten ──────────────────────────────────────────────────
        "tax_col_ticker":               "Ticker",
        "tax_col_name":                 "Name",
        "tax_col_qty":                  "Shares",
        "tax_col_price":                "Price",
        "tax_col_market_val":           "Market Value",
        "tax_col_div":                  "Dividend/Y.",
        "tax_col_vst":                  "Withholding Tax",
        "tax_col_foreign_tax":          "Foreign WHT",
        "tax_col_note":                 "Note",
        "tax_col_unrealised":           "Unrealized Gain",
        "tax_col_withholding":          "Withholding Tax",
        "tax_col_dba":                  "Treaty Rate",
        # Short variants for export tables (PDF/XLSX/ODS)
        "tax_col_kest_div_short":       "WHT Div.",
        "tax_col_vst_short":            "WHT (35%)",
        "tax_col_foreign_short":        "Foreign WHT",
        "tax_col_rate":                 "Rate",
        "tax_col_unrealised_short":     "Unrealized Gain",
        "tax_lbl_summary":              "Summary",
        "tax_lbl_tax_statement":        "Tax Statement",

        # ── Zusammenfassung – Labels ──────────────────────────────────────────
        "tax_sum_market_val":           "Total Market Value:",
        "tax_sum_gross_div":            "Total Gross Dividends:",
        # AT
        "tax_sum_kest_div":             "KESt 27.5 % on dividends:",
        "tax_sum_foreign_tax":          "Foreign withholding taxes (creditable):",
        "tax_sum_kest_gain":            "KESt on unrealized capital gains (est.):",
        "tax_sum_total_tax":            "Total tax (estimated):",
        "tax_sum_net_div_kest":         "Net dividends (after KESt / WHT, est.):",
        "tax_sum_verlustausgleich":     "ℹ  Loss offset:",
        # CH
        "tax_sum_vst":                  "Withholding tax (CH, reclaimable):",
        "tax_sum_foreign_tax_est":      "Foreign withholding taxes (estimated):",
        "tax_sum_total_tax_ch":         "Total tax:",
        "tax_sum_net_div_ch":           "Net dividends (after tax, est.):",
        "tax_sum_wealth_tax":           "⚠  Wealth tax:",
        # DE
        "tax_sum_freistellung":         "Exemption order (Freistellungsauftrag):",
        "tax_sum_taxable_div":          "Taxable dividends:",
        "tax_sum_abgeltung":            "Withholding tax (Abgeltungssteuer 25 %):",
        "tax_sum_soli":                 "Solidarity surcharge (5.5 % on WHT):",
        "tax_sum_total_tax_de":         "Total tax:",
        "tax_sum_net_div_de":           "Net dividends:",
        # UK
        "tax_sum_div_allowance":        "Dividend Allowance (£500):",
        "tax_sum_taxable_div_uk":       "Taxable dividends:",
        "tax_sum_div_tax_basic":        "Dividend tax (Basic Rate 8.75 %):",
        "tax_sum_net_div_uk":           "Net dividends:",
        # US
        "tax_sum_total_tax_us":         "Total withholding tax:",
        "tax_sum_net_div_us":           "Net dividends (after WHT):",

        # ── Wash Sale Hinweis (US) ────────────────────────────────────────────
        "tax_wash_sale_text": (
            "<b>Wash Sale Rule (IRC § 1091):</b> Losses are NOT tax-deductible "
            "if the same security is repurchased within 30 days before or after "
            "the sale. This rule is not calculated automatically here. "
            "Please check your broker statement (1099-B) for "
            "'Wash Sale Loss Disallowed' entries."
        ),

        # ── Globaler Disclaimer ───────────────────────────────────────────────
        "tax_disclaimer_global": (
            "Please use your official bank statement for your tax return. "
            "This portfolio may deviate by up to approx. 2 % from the actual bank value "
            "(bank rounding, exchange rates). Fees, margin loans and other "
            "bank costs are not included. Not tax advice."
        ),

        # ── Export-Format Dialog ──────────────────────────────────────────────
        "tax_export_title":             "📤  Export",
        "tax_export_heading":           "<b>Export Tax Statement {name}</b>",
        "tax_export_format_label":      "Choose format:",
        "tax_export_rb_pdf":            "📄  PDF",
        "tax_export_rb_xlsx":           "📊  Excel (.xlsx)",
        "tax_export_rb_ods":            "📋  OpenDocument (.ods)",
        "tax_export_btn_save":          "💾  Save…",
        "tax_export_btn_cancel":        "Cancel",
        "tax_export_save_dialog":       "Save file",
        "tax_export_default_filename":  "TaxStatement_{country}",
        "tax_export_success_title":     "Exported",
        "tax_export_success_msg":       "✅  Saved:\n{path}",
        "tax_export_error_title":       "Error",
        "tax_export_error_msg":         "Export failed:\n{error}",

        # ── Keine Daten Warnung ───────────────────────────────────────────────
        "tax_no_data_title":            "No Data",
        "tax_no_data_msg":              "Please open the tax statement dialog first and wait for data to load.",

        # ── Passwort setzen Dialog ────────────────────────────────────────────
        "tax_pw_set_title":             "🔐  Set Password",
        "tax_pw_set_heading":           "<b>Set password for tax statement</b>",
        "tax_pw_set_hint": (
            "<small style='color:#666'>At least 12 characters. The .smtx file can<br>"
            "be opened on any PC with this password.</small>"
        ),
        "tax_pw_label":                 "Password:",
        "tax_pw_placeholder":           "At least 12 characters…",
        "tax_pw_confirm_label":         "Confirm password:",
        "tax_pw_confirm_placeholder":   "Repeat…",
        "tax_pw_show_cb":               "Show password",
        "tax_pw_btn_cancel":            "Cancel",
        "tax_pw_btn_save":              "🔐  Save",
        "tax_pw_err_short":             "⚠ Password must be at least 12 characters.",
        "tax_pw_err_mismatch":          "⚠ Passwords do not match.",
        # Passwort-Stärke Labels
        "tax_pw_strength_weak":         "Weak",
        "tax_pw_strength_medium":       "Fair",
        "tax_pw_strength_strong":       "Strong",
        "tax_pw_strength_very_strong":  "Very strong",
        # Speichern-Dialoge
        "tax_save_dialog_title":        "Save Tax Statement",
        "tax_save_success_title":       "Saved",
        "tax_save_success_msg":         "✅  Tax statement saved:\n{path}\n🔐  AES-256-GCM encrypted",
        "tax_save_success_unenc_msg":   "✅  Tax statement saved (unencrypted – 'cryptography' missing):\n{path}",
        "tax_save_error_title":         "Error",
        "tax_save_error_msg":           "Save failed:\n{error}",

        # ── Passwort eingeben Dialog (Laden) ──────────────────────────────────
        "tax_pw_enter_title":           "🔐  Enter Password",
        "tax_pw_enter_for_file":        "<b>Password for:</b><br><small>{filename}</small>",
        "tax_pw_enter_placeholder":     "Enter password…",
        "tax_pw_enter_btn_open":        "🔓  Open",
        "tax_pw_enter_btn_cancel":      "Cancel",
        "tax_pw_wrong_title":           "Error",
        "tax_pw_wrong_msg":             "Wrong password or corrupted file.",
        # Laden-Dialoge
        "tax_load_dialog_title":        "Load Tax Statement",
        "tax_load_error_title":         "Error",
        "tax_load_error_msg":           "Could not read file:\n{error}",
        "tax_load_success_title":       "Loaded",
        "tax_load_success_msg": (
            "✅  Tax statement loaded:\n{filename}\n"
            "(Display still shows current portfolio data)"
        ),

        # ── Hilfe-Dialog ──────────────────────────────────────────────────────
        "tax_help_title":               "Help – Tax Module {name}",
        "tax_help_btn_close":           "✖  Close",
        "tax_help_no_text":             "<p>No help text available for this country yet.</p>",
        "tax_help_lang_label":          "Language:",

        # ── Steuerformular-Export Dialog ──────────────────────────────────────
        "tax_form_title":               "📋  Export Tax Form",
        "tax_form_btn_export":          "📋  Export PDF",
        "tax_form_btn_cancel":          "Cancel",
        # CH
        "tax_form_ch_heading":          "🇨🇭  Securities Schedule – Switzerland",
        "tax_form_ch_info": (
            "Exports a completed securities schedule (Form DA-1) "
            "as an orientation aid. Prices at Dec 31, FX via SNB/Yahoo Finance."
        ),
        "tax_form_ch_region_label":     "Canton:",
        "tax_form_ch_stichtag":         "Reference date: Dec 31, {year}  |  FX rates: SNB year-end {year}",
        "tax_form_ch_disc": (
            "Orientation aid – not an official tax form. "
            "Please compare with your original bank statement and the cantonal online portal. "
            "Securities schedule / Form DA-1 (tax year {year})."
        ),
        "tax_form_ch_save_dialog":      "Save Securities Schedule",
        "tax_form_ch_default_filename": "SecuritiesSchedule_{canton}_{year}.pdf",
        "tax_form_ch_success_title":    "Export successful",
        "tax_form_ch_success_msg":      "Securities schedule ({canton_name}) exported:\n{path}",
        "tax_form_ch_error_title":      "Error",
        "tax_form_ch_error_msg":        "Export failed:\n{error}",
        # DE
        "tax_form_de_heading":          "🇩🇪  Anlage KAP – Germany",
        "tax_form_de_info": (
            "Exports a completed Anlage KAP (capital income) as an orientation aid. "
            "Incl. exemption order, withholding tax and solidarity surcharge. "
            "Prices at Dec 31, FX via Bundesbank/Yahoo Finance."
        ),
        "tax_form_de_region_label":     "Federal state (for church tax note):",
        "tax_form_de_stichtag":         "Reference date: Dec 31, {year}  |  FX rates: Bundesbank year-end {year}",
        "tax_form_de_disc": (
            "Orientation aid – not an official ELSTER form. "
            "Please compare with your broker's annual tax certificate. "
            "Anlage KAP (tax year {year})."
        ),
        "tax_form_de_save_dialog":      "Save Anlage KAP",
        "tax_form_de_default_filename": "Anlage_KAP_{year}.pdf",
        "tax_form_de_success_title":    "Export successful",
        "tax_form_de_success_msg":      "Anlage KAP ({bl_name}) exported:\n{path}",
        "tax_form_de_error_title":      "Error",
        "tax_form_de_error_msg":        "Export failed:\n{error}",
        # AT
        "tax_form_at_heading":          "🇦🇹  E1kv Declaration – Austria",
        "tax_form_at_info": (
            "Exports a declaration for foreign capital income (E1kv supplement) "
            "as an orientation aid. Helps with reclaiming foreign withholding taxes. "
            "Prices at Dec 31, FX via OeNB/Yahoo Finance."
        ),
        "tax_form_at_region_label":     "Tax office region (optional):",
        "tax_form_at_stichtag":         "Reference date: Dec 31, {year}  |  FX rates: OeNB year-end {year}",
        "tax_form_at_disc": (
            "Orientation aid – not an official FinanzOnline form. "
            "KESt is automatically withheld by the Austrian custodian bank. "
            "E1kv declaration for WHT reclaim (tax year {year})."
        ),
        "tax_form_at_save_dialog":      "Save E1kv Declaration",
        "tax_form_at_default_filename": "E1kv_Declaration_{year}.pdf",
        "tax_form_at_success_title":    "Export successful",
        "tax_form_at_success_msg":      "E1kv declaration exported:\n{path}",
        "tax_form_at_error_title":      "Error",
        "tax_form_at_error_msg":        "Export failed:\n{error}",
        # UK
        "tax_form_uk_heading":          "🇬🇧  Capital Gains & Dividends – United Kingdom",
        "tax_form_uk_info": (
            "Exports a Capital Gains Tax / Dividend Tax summary (SA108 / SA100 guidance) "
            "as an orientation aid. Dividend Allowance £500, CGT Annual Exempt £3,000 (2024/25). "
            "Prices at 5 April (UK tax year end), FX via Yahoo Finance."
        ),
        "tax_form_uk_region_label":     "UK Nation (for tax note):",
        "tax_form_uk_stichtag":         "Tax year end: 5 April {year}  |  FX rates: Yahoo Finance",
        "tax_form_uk_disc": (
            "Orientation aid – not an official HMRC form. "
            "Please compare with your broker's annual tax statement (e.g. Consolidated Tax Certificate). "
            "Self Assessment SA100 / SA108 (tax year {year}/{year_plus1})."
        ),
        "tax_form_uk_save_dialog":      "Save SA108 Summary",
        "tax_form_uk_default_filename": "UK_Tax_Summary_{year}.pdf",
        "tax_form_uk_success_title":    "Export successful",
        "tax_form_uk_success_msg":      "UK Tax Summary ({nation_name}) exported:\n{path}",
        "tax_form_uk_error_title":      "Error",
        "tax_form_uk_error_msg":        "Export failed:\n{error}",
        # US
        "tax_form_us_heading":          "🇺🇸  Schedule B / Form 1040 – United States",
        "tax_form_us_info": (
            "Exports a dividend & withholding tax summary (Schedule B / 1099-DIV guidance) "
            "as an orientation aid. For non-US persons: 30 % / treaty 15 % withholding. "
            "For US residents: Qualified Dividends 0/15/20 %."
        ),
        "tax_form_us_region_label":     "Investor status:",
        "tax_form_us_stichtag":         "Tax year: {year}  |  Form 1040 / Schedule B / 1099-DIV",
        "tax_form_us_disc": (
            "Orientation aid – not an official IRS form. "
            "Please compare with your broker's 1099-DIV / 1042-S statement. "
            "Wash Sale Rule (30-day window) is NOT calculated automatically – "
            "check your broker's 1099-B for disallowed losses."
        ),
        "tax_form_us_state_label":      "State (State Tax):",
        "tax_form_us_state_note":       "State income tax is shown as an estimate in the PDF.",
        "tax_form_us_filing_label":     "Filing Status:",
        "tax_form_us_filing_note":      "Determines the income thresholds for Qualified Dividend rates.",
        "tax_form_us_save_dialog":      "Save US Tax Summary",
        "tax_form_us_default_filename": "US_Tax_Summary_{year}.pdf",
        "tax_form_us_success_title":    "Export successful",
        "tax_form_us_success_msg":      "US Tax Summary exported:\n{path}",
        "tax_form_us_error_title":      "Error",
        "tax_form_us_error_msg":        "Export failed:\n{error}",

        # ── AT FA_REGIONEN Dropdown ───────────────────────────────────────────
        "tax_fa_alle":                  "All / Not specified",

        # ── US_TYPES Dropdown ─────────────────────────────────────────────────
        "tax_us_type_ch":               "Swiss / Treaty CH-US (15 % WHT)",
        "tax_us_type_de":               "German / Treaty DE-US (15 % WHT)",
        "tax_us_type_at":               "Austrian / Treaty AT-US (15 % WHT)",
        "tax_us_type_nra":              "Non-US person, no treaty (30 % WHT)",
        "tax_us_type_res":              "US Resident (Qualified Dividends / LTCG)",

        # ── Dateidialoge / Filter ─────────────────────────────────────────────
        "tax_file_save_default":        "TaxStatement_{country}_{year}",
        "tax_file_filter_smtx":         "Tax Statement (*.smtx)",
        "tax_file_filter_all":          "All Files (*)",

    },
}
