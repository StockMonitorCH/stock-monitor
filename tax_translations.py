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
        "tax_main_title":               "Steuerauszug {name}  –  {year}",
        "tax_main_heading":             "<b>Steuerauszug {name}  –  Steuerjahr {year}</b>",

        # ── Buttons (Haupt-Dialog) ────────────────────────────────────────────
        "tax_btn_update":               "🔄  Update Steuerregeln",
        "tax_btn_save":                 "💾  Steuerauszug speichern",
        "tax_btn_load":                 "📂  Steuerauszug laden",
        "tax_btn_export":               "📤  Exportieren",
        "tax_btn_form":                 "📋  Steuerformular",
        "tax_btn_close":                "✖  Schliessen",
        "tax_btn_help":                 "❓  Hilfe",
        "tax_btn_reload":               "🔄  Neu laden",
        "tax_tip_reload":               "Dividenden, Wechselkurse und realisierte Gewinne neu von Yahoo laden.\nSonst werden die Daten pro Tag nur einmal geladen (Stand: {time}).",

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
        "tax_col_age":                  "AGE",
        "tax_col_kest_age":             "KESt AGE",
        "tax_sum_age":                  "Ausschüttungsgleiche Erträge (AGE, manuell):",
        "tax_sum_kest_age":             "KESt 27,5 % auf AGE (abzgl. anrechenbarer QSt):",
        "tax_btn_age":                  "📝 AGE erfassen",
        "tax_tip_age":                  "Ausschüttungsgleiche Erträge thesaurierender Fonds aus der OeKB-Meldung eintragen",
        "tax_age_title":                "Ausschüttungsgleiche Erträge {year}",
        "tax_age_info":                 "Thesaurierende Fonds schütten nicht aus, in Österreich sind die "
                                        "<b>ausschüttungsgleichen Erträge (AGE)</b> trotzdem jährlich KESt-pflichtig. "
                                        "Die Werte je Anteil stehen in der Steuermeldung des Fonds bei der OeKB "
                                        "(<a href='https://my.oekb.at'>my.oekb.at</a> → Fonds-Steuerdaten, Suche nach ISIN). "
                                        "Übernehmen Sie für {year}: <i>Ausschüttungsgleiche Erträge</i>, "
                                        "<i>anrechenbare ausländische Quellensteuer</i> und das Zuflussdatum "
                                        "(massgebend ist Ihr Bestand an diesem Tag). Beträge in Fondswährung. "
                                        "Leer lassen (0) = keine AGE. Angezeigt werden nur Fonds/ETFs – bei Aktien ist nichts einzutragen. "
                                        "Die Währung ist die Fondswährung laut OeKB-Meldung (kann von der Börsenwährung abweichen).",
        "tax_age_col_age":              "AGE je Anteil",
        "tax_age_col_qst":              "Anrechenb. QSt je Anteil",
        "tax_age_col_date":             "Zuflussdatum",
        "tax_age_btn_save":             "Speichern",
        "tax_age_btn_cancel":           "Abbrechen",
        "tax_age_col_cur":              "Währung (OeKB)",
        "tax_age_no_funds":             "In diesem Portfolio wurden keine Fonds oder ETFs gefunden. "
                                        "Ausschüttungsgleiche Erträge gibt es nur bei Fonds – für Aktien "
                                        "ist nichts einzutragen.",
        "tax_age_show_all":             "Alle Positionen anzeigen (falls ein Fonds nicht erkannt wurde)",
        "tax_fx_note":                  "Alle Beträge in {cur}: Dividenden zum Kurs am Ex-Tag, "
                                        "Kurse und Marktwerte zum aktuellen Kurs umgerechnet.",
        "tax_fx_missing":               "Kein Wechselkurs verfügbar für: {syms} (nicht umgerechnet).",
        # Kurz-Varianten für Export-Tabellen (PDF/XLSX/ODS)
        "tax_col_kest_div_short":       "KESt Div.",
        "tax_col_vst_short":            "VSt (35%)",
        "tax_col_foreign_short":        "Ausländ. QSt",
        "tax_col_rate":                 "Satz",
        "tax_col_unrealised_short":     "Nicht real. Gewinn",
        "tax_lbl_summary":              "Zusammenfassung",
        "tax_lbl_note":                 "Hinweis:",
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

        # ── v5.10.0: Kontosaldo + realisierte Gewinne ──
        "tax_loading_gains":            "Realisierte Gewinne und Kontosaldo werden geladen …",
        "tax_loading_fx_cash":          "Wechselkurs {cur} für den Kontosaldo …",
        "tax_tab_positions":            "Positionen und Dividenden",
        "tax_tab_gains":                "Realisierte Gewinne ({n})",
        "tax_cash_head_final":          "Kontosaldo per {date}",
        "tax_cash_head_today":          "Kontosaldo per {date} (Stand heute – das Steuerjahr ist noch nicht abgeschlossen)",
        "tax_cash_line":                "{cur} {amt} × {rate}:",
        "tax_cash_line_same":           "{cur}:",
        "tax_cash_total":               "Kontoguthaben total:",
        "tax_cash_fx_missing":          "Kein Wechselkurs für {items} – nicht im Total enthalten.",
        "tax_cash_not_setup":           "Kontosaldo: Im Konto (💰) die Ansicht „Alles“ einrichten, dann erscheint hier das Guthaben per 31.12. für die Vermögenssteuer.",
        "tax_ch_wealth_total":          "Steuerwert Wertschriften + Konto:",
        "tax_ch_wealth_note":           "Vermögenssteuer: Freibetrag und Steuersatz sind kantonal, besteuert wird das gesamte Reinvermögen (inkl. übrige Konten, abzüglich Schulden).",
        "tax_g_none":                   "Keine Verkäufe vom {lo} bis {hi}.",
        "tax_g_head":                   "Realisierte Gewinne {lo} – {hi} ({n} Verkäufe)",
        "tax_g_gains":                  "Kursgewinne:",
        "tax_g_losses":                 "Kursverluste:",
        "tax_g_net":                    "Realisierter Gewinn netto:",
        "tax_g_ch_free":                "Kapitalgewinne im Privatvermögen sind steuerfrei (Ausnahme: gewerbsmässiger Wertschriftenhandel). Verluste sind nicht abziehbar. Nur zur Information.",
        "tax_g_de_stock_net":           "Gewinne/Verluste Wertpapiere (ohne Krypto):",
        "tax_g_de_frei_left":           "davon durch Rest-Sparerpauschbetrag gedeckt:",
        "tax_g_de_taxable":             "Steuerpflichtige Kursgewinne:",
        "tax_g_de_tax":                 "Abgeltungssteuer + Soli auf Kursgewinne:",
        "tax_g_de_total_all":           "Steuer gesamt (Dividenden + Kursgewinne):",
        "tax_g_de_loss_carry":          "Verlustvortrag (ins Folgejahr):",
        "tax_g_de_crypto":              "Krypto (privates Veräusserungsgeschäft, § 23 EStG): {short} {cur} mit Haltedauer bis 1 Jahr – steuerpflichtig zum persönlichen Steuersatz, Freigrenze {frei} {cur}; {long} {cur} nach mehr als 1 Jahr – steuerfrei.",
        "tax_g_de_note":                "Anlage KAP. Aktienverluste sind nur mit Aktiengewinnen verrechenbar; die Depotbank führt die Verlustverrechnungstöpfe. Kirchensteuer nicht berücksichtigt.",
        "tax_g_at_net_new":             "Gewinne/Verluste Neuvermögen:",
        "tax_g_at_old_free":            "Altbestand (steuerfrei):",
        "tax_g_at_kest":                "KESt 27,5 % auf realisierte Kursgewinne:",
        "tax_g_at_loss_credit":         "Verlustausgleich (Gutschrift KESt auf Dividenden):",
        "tax_g_at_note":                "Altbestand: Aktien/Fonds gekauft vor 1.1.2011, Krypto vor 1.3.2021. Bei österreichischem Depot führt die Bank KESt und Verlustausgleich automatisch durch.",
        "tax_g_uk_allowance":           "CGT Annual Exempt Amount:",
        "tax_g_uk_taxable":             "Steuerpflichtiger Gewinn (CGT):",
        "tax_g_uk_basic":               "CGT bei Basic Rate (18 %):",
        "tax_g_uk_higher":              "CGT bei Higher Rate (24 %):",
        "tax_g_uk_loss":                "Verluste können gemeldet und in Folgejahre vorgetragen werden.",
        "tax_g_uk_note":                "UK-Steuerjahr 6. April – 5. April. HMRC verlangt Same-Day-, 30-Tage- und Section-104-Pool-Regeln; hier wird je Kauf-Lot (FIFO) gerechnet – Ergebnis kann abweichen.",
        "tax_g_us_short":               "Short-term (bis 1 Jahr):",
        "tax_g_us_long":                "Long-term (mehr als 1 Jahr):",
        "tax_g_us_st_taxable":          "Short-term steuerpflichtig (ordentlicher Satz):",
        "tax_g_us_lt_tax":              "Long-term Steuer (Schätzung 15 %):",
        "tax_g_us_loss_deduct":         "Verlust abziehbar vom Einkommen (max. $3'000):",
        "tax_g_us_loss_carry":          "Verlustvortrag (Capital Loss Carryover):",
        "tax_g_us_wash":                "Mögliche Wash Sales ({n}, Rückkauf innert 30 Tagen) – Verlust evtl. nicht abziehbar:",
        "tax_g_us_note":                "Form 8949 / Schedule D. Massgebend ist das 1099-B des Brokers (inkl. Wash-Sale-Korrekturen).",
        "tax_g_missing":                "{n} Verkäufe ohne Verkaufskurs oder Wechselkurs – nicht in den Summen enthalten.",
        "tax_g_est":                    "{n} Verkäufe mit Yahoo-Schlusskurs (≈) statt echtem Verkaufskurs – im Konto unter „Realisierte Gewinne“ per Doppelklick korrigieren.",
        "tax_g_errors":                 "Daten fehlen für: {items}",
        "tax_g_col_buy":                "Kauf",
        "tax_g_col_sell":               "Verkauf",
        "tax_g_col_days":               "Tage",
        "tax_g_col_cost":               "Kosten ({cur})",
        "tax_g_col_proceeds":           "Erlös ({cur})",
        "tax_g_col_gain":               "Gewinn ({cur})",
        "tax_g_note_est":               "≈ Schlusskurs",
        "tax_g_note_staking":           "Staking",
        "tax_g_note_long":              "long-term",
        "tax_g_note_short":             "short-term",
        "tax_g_note_wash":              "Wash Sale? (Kauf {date})",
        "tax_g_note_old":               "Altbestand – steuerfrei",
        "tax_g_note_crypto_free":       "Krypto > 1 Jahr – steuerfrei",
        "tax_g_note_crypto_tax":        "Krypto ≤ 1 Jahr – § 23 EStG",
        "tax_g_note_crypto":            "Krypto",
        "tax_g_note_missing":           "Kurs fehlt",
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
            "dem Verkauf zurückgekauft wurde. Mögliche Wash Sales werden im Reiter "
            "„Realisierte Gewinne“ markiert, aber nicht herausgerechnet. Bitte prüfen Sie Ihren Broker-Auszug (1099-B) auf "
            "'Wash Sale Loss Disallowed'-Einträge."
        ),

        # ── Globaler Disclaimer ───────────────────────────────────────────────
        "tax_disclaimer_global": (
            "Bitte verwenden Sie für Ihre Steuererklärung den originalen Bankauszug. "
            "Dieses Portfolio kann bis zu ca. 3 % vom tatsächlichen Bankwert abweichen "
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
        "tax_form_ch_heading":          "Wertschriftenverzeichnis – Schweiz",
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
        "tax_form_de_heading":          "Anlage KAP – Deutschland",
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
        "tax_form_at_heading":          "E1kv-Nachweis – Österreich",
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
        "tax_form_uk_heading":          "Capital Gains & Dividends – United Kingdom",
        "tax_form_uk_info": (
            "Exports a Capital Gains Tax / Dividend Tax summary (SA108 / SA100 guidance) "
            "as an orientation aid. Dividend Allowance £500, CGT Annual Exempt £3,000 ({year}/{year_plus1})."
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
        "tax_form_us_heading":          "Schedule B / Form 1040 – United States",
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
        "tax_main_title":               "Tax Statement {name}  –  {year}",
        "tax_main_heading":             "<b>Tax Statement {name}  –  Tax Year {year}</b>",

        # ── Buttons (Haupt-Dialog) ────────────────────────────────────────────
        "tax_btn_update":               "🔄  Update Tax Rules",
        "tax_btn_save":                 "💾  Save Tax Statement",
        "tax_btn_load":                 "📂  Load Tax Statement",
        "tax_btn_export":               "📤  Export",
        "tax_btn_form":                 "📋  Tax Form",
        "tax_btn_close":                "✖  Close",
        "tax_btn_help":                 "❓  Help",
        "tax_btn_reload":               "🔄  Reload",
        "tax_tip_reload":               "Reload dividends, exchange rates and realized gains from Yahoo.\nOtherwise the data is loaded only once per day (as of {time}).",

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
        "tax_col_age":                  "Deemed dist.",
        "tax_col_kest_age":             "KESt deemed",
        "tax_sum_age":                  "Deemed distributed income (AGE, manual):",
        "tax_sum_kest_age":             "KESt 27.5 % on AGE (less creditable WHT):",
        "tax_btn_age":                  "📝 Enter AGE",
        "tax_tip_age":                  "Enter deemed distributed income of accumulating funds from the OeKB report",
        "tax_age_title":                "Deemed distributed income {year}",
        "tax_age_info":                 "Accumulating funds do not pay out, but in Austria their "
                                        "<b>deemed distributed income (ausschüttungsgleiche Erträge, AGE)</b> is still "
                                        "subject to KESt every year. The per-unit figures are in the fund's tax report "
                                        "at OeKB (<a href='https://my.oekb.at'>my.oekb.at</a> → fund tax data, search by ISIN). "
                                        "Enter for {year}: <i>deemed distributed income</i>, <i>creditable foreign "
                                        "withholding tax</i> and the inflow date (your holding on that day counts). "
                                        "Leave empty (0) = no AGE. Only funds/ETFs are listed – nothing to enter for shares. "
                                        "Currency = fund currency as reported by OeKB (may differ from the trading currency).",
        "tax_age_col_age":              "AGE per unit",
        "tax_age_col_qst":              "Creditable WHT per unit",
        "tax_age_col_date":             "Inflow date",
        "tax_age_btn_save":             "Save",
        "tax_age_btn_cancel":           "Cancel",
        "tax_age_col_cur":              "Currency (OeKB)",
        "tax_age_no_funds":             "No funds or ETFs were found in this portfolio. "
                                        "Deemed distributed income only exists for funds – "
                                        "nothing to enter for shares.",
        "tax_age_show_all":             "Show all positions (if a fund was not recognised)",
        "tax_fx_note":                  "All amounts in {cur}: dividends converted at the ex-date rate, "
                                        "prices and market values at the current rate.",
        "tax_fx_missing":               "No exchange rate available for: {syms} (not converted).",
        # Short variants for export tables (PDF/XLSX/ODS)
        "tax_col_kest_div_short":       "WHT Div.",
        "tax_col_vst_short":            "WHT (35%)",
        "tax_col_foreign_short":        "Foreign WHT",
        "tax_col_rate":                 "Rate",
        "tax_col_unrealised_short":     "Unrealized Gain",
        "tax_lbl_summary":              "Summary",
        "tax_lbl_note":                 "Note:",
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

        # ── v5.10.0: account balance + realized gains ──
        "tax_loading_gains":            "Loading realized gains and account balance …",
        "tax_loading_fx_cash":          "Exchange rate {cur} for the account balance …",
        "tax_tab_positions":            "Positions and dividends",
        "tax_tab_gains":                "Realized gains ({n})",
        "tax_cash_head_final":          "Account balance as of {date}",
        "tax_cash_head_today":          "Account balance as of {date} (today – the tax year is not over yet)",
        "tax_cash_line":                "{cur} {amt} × {rate}:",
        "tax_cash_line_same":           "{cur}:",
        "tax_cash_total":               "Total cash balance:",
        "tax_cash_fx_missing":          "No exchange rate for {items} – not included in the total.",
        "tax_cash_not_setup":           "Account balance: set up the view “All” in the account (💰) to show the balance as of Dec 31 for wealth tax here.",
        "tax_ch_wealth_total":          "Tax value securities + account:",
        "tax_ch_wealth_note":           "Wealth tax: allowance and rate depend on the canton; tax is levied on total net assets (incl. other accounts, minus debts).",
        "tax_g_none":                   "No sales from {lo} to {hi}.",
        "tax_g_head":                   "Realized gains {lo} – {hi} ({n} sales)",
        "tax_g_gains":                  "Capital gains:",
        "tax_g_losses":                 "Capital losses:",
        "tax_g_net":                    "Net realized gain:",
        "tax_g_ch_free":                "Capital gains on private assets are tax-free (exception: professional securities trading). Losses are not deductible. For information only.",
        "tax_g_de_stock_net":           "Gains/losses securities (excl. crypto):",
        "tax_g_de_frei_left":           "of which covered by remaining saver's allowance:",
        "tax_g_de_taxable":             "Taxable capital gains:",
        "tax_g_de_tax":                 "Withholding tax + Soli on capital gains:",
        "tax_g_de_total_all":           "Total tax (dividends + capital gains):",
        "tax_g_de_loss_carry":          "Loss carryforward (to next year):",
        "tax_g_de_crypto":              "Crypto (private sale, § 23 EStG): {short} {cur} held up to 1 year – taxable at personal rate, exemption limit {frei} {cur}; {long} {cur} held more than 1 year – tax-free.",
        "tax_g_de_note":                "Anlage KAP. Stock losses can only be offset against stock gains; the custodian bank keeps the loss pots. Church tax not included.",
        "tax_g_at_net_new":             "Gains/losses new assets:",
        "tax_g_at_old_free":            "Old holdings (tax-free):",
        "tax_g_at_kest":                "KESt 27.5% on realized capital gains:",
        "tax_g_at_loss_credit":         "Loss offset (KESt credit on dividends):",
        "tax_g_at_note":                "Old holdings: stocks/funds bought before Jan 1, 2011, crypto before Mar 1, 2021. With an Austrian custodian, the bank handles KESt and loss offset automatically.",
        "tax_g_uk_allowance":           "CGT Annual Exempt Amount:",
        "tax_g_uk_taxable":             "Taxable gain (CGT):",
        "tax_g_uk_basic":               "CGT at basic rate (18%):",
        "tax_g_uk_higher":              "CGT at higher rate (24%):",
        "tax_g_uk_loss":                "Losses can be reported and carried forward to later years.",
        "tax_g_uk_note":                "UK tax year April 6 – April 5. HMRC requires same-day, 30-day and Section 104 pool matching; this calculation uses purchase lots (FIFO) – results may differ.",
        "tax_g_us_short":               "Short-term (up to 1 year):",
        "tax_g_us_long":                "Long-term (more than 1 year):",
        "tax_g_us_st_taxable":          "Short-term taxable (ordinary rate):",
        "tax_g_us_lt_tax":              "Long-term tax (estimate 15%):",
        "tax_g_us_loss_deduct":         "Loss deductible from income (max. $3,000):",
        "tax_g_us_loss_carry":          "Capital loss carryover:",
        "tax_g_us_wash":                "Possible wash sales ({n}, repurchase within 30 days) – loss may be disallowed:",
        "tax_g_us_note":                "Form 8949 / Schedule D. The broker's 1099-B (incl. wash sale adjustments) is authoritative.",
        "tax_g_missing":                "{n} sales without sell price or exchange rate – not included in the totals.",
        "tax_g_est":                    "{n} sales use the Yahoo closing price (≈) instead of the actual sell price – correct them by double-click in Account → Realized gains.",
        "tax_g_errors":                 "Data missing for: {items}",
        "tax_g_col_buy":                "Bought",
        "tax_g_col_sell":               "Sold",
        "tax_g_col_days":               "Days",
        "tax_g_col_cost":               "Cost ({cur})",
        "tax_g_col_proceeds":           "Proceeds ({cur})",
        "tax_g_col_gain":               "Gain ({cur})",
        "tax_g_note_est":               "≈ closing price",
        "tax_g_note_staking":           "Staking",
        "tax_g_note_long":              "long-term",
        "tax_g_note_short":             "short-term",
        "tax_g_note_wash":              "Wash sale? (bought {date})",
        "tax_g_note_old":               "Old holding – tax-free",
        "tax_g_note_crypto_free":       "Crypto > 1 year – tax-free",
        "tax_g_note_crypto_tax":        "Crypto ≤ 1 year – § 23 EStG",
        "tax_g_note_crypto":            "Crypto",
        "tax_g_note_missing":           "Price missing",
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
            "the sale. Possible wash sales are flagged in the “Realized gains” tab "
            "but not deducted. "
            "Please check your broker statement (1099-B) for "
            "'Wash Sale Loss Disallowed' entries."
        ),

        # ── Globaler Disclaimer ───────────────────────────────────────────────
        "tax_disclaimer_global": (
            "Please use your official bank statement for your tax return. "
            "This portfolio may deviate by up to approx. 3 % from the actual bank value "
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
        "tax_form_ch_heading":          "Securities Schedule – Switzerland",
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
        "tax_form_de_heading":          "Anlage KAP – Germany",
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
        "tax_form_at_heading":          "E1kv Declaration – Austria",
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
        "tax_form_uk_heading":          "Capital Gains & Dividends – United Kingdom",
        "tax_form_uk_info": (
            "Exports a Capital Gains Tax / Dividend Tax summary (SA108 / SA100 guidance) "
            "as an orientation aid. Dividend Allowance £500, CGT Annual Exempt £3,000 ({year}/{year_plus1})."
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
        "tax_form_us_heading":          "Schedule B / Form 1040 – United States",
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
