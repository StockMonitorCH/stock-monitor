"""
stress_test.py – Historischer Stresstest für Stock Monitor
Portfolioauswirkungen historischer Börsencrashs und eigener Szenarien.
Basis: S&P 500 historische Daten.

Alle UI-Strings kommen aus stress_test_translations.py (TRS).
"""
from __future__ import annotations

from stress_test_translations import TRS

# ── Historische Szenarien ─────────────────────────────────────────────────────
# Nur numerische Daten – Namen und Beschreibungen kommen aus TRS("sc_<id>") /
# TRS("desc_<id>") in stress_test_translations.py.
#
# drawdown:         Peak-to-Trough (negativ, z.B. -0.57 = -57 %)
# bear_months:      Dauer Bärenmarkt in Monaten
# recovery_months:  Monate vom Tief zurück zum Ausgangsniveau (historisch geschätzt)
SCENARIOS: list[dict] = [
    {"id": "1907", "drawdown": -0.48, "bear_months": 12, "recovery_months": 30},
    {"id": "1929", "drawdown": -0.86, "bear_months": 32, "recovery_months": 266},
    {"id": "1937", "drawdown": -0.60, "bear_months": 61, "recovery_months": 96},
    {"id": "1946", "drawdown": -0.30, "bear_months": 36, "recovery_months": 60},
    {"id": "1956", "drawdown": -0.22, "bear_months": 14, "recovery_months": 18},
    {"id": "1962", "drawdown": -0.28, "bear_months":  6, "recovery_months": 12},
    {"id": "1966", "drawdown": -0.22, "bear_months":  7, "recovery_months": 18},
    {"id": "1970", "drawdown": -0.36, "bear_months": 17, "recovery_months": 30},
    {"id": "1973", "drawdown": -0.48, "bear_months": 20, "recovery_months": 96},
    {"id": "1980", "drawdown": -0.27, "bear_months": 20, "recovery_months": 30},
    {"id": "1987", "drawdown": -0.34, "bear_months":  3, "recovery_months": 24},
    {"id": "2000", "drawdown": -0.49, "bear_months": 30, "recovery_months": 61},
    {"id": "2007", "drawdown": -0.57, "bear_months": 17, "recovery_months": 48},
    {"id": "2020", "drawdown": -0.34, "bear_months":  1, "recovery_months": 5},
    {"id": "2022", "drawdown": -0.25, "bear_months":  9, "recovery_months": 15},
]


# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

def _fmt_val(value: float, currency: str) -> str:
    sym = {"USD": "$", "EUR": "€", "CHF": "CHF ", "GBP": "£"}.get(currency, currency + " ")
    return f"{sym}{value:,.0f}"


def _fmt_months(months: int) -> str:
    if months >= 24:
        years = months / 12
        return f"~{years:.0f} {TRS('years')} ({months} {TRS('months_short')})"
    return f"{months} {TRS('months_short')}"


# ── Kern-Berechnung ───────────────────────────────────────────────────────────

def _compute_scenario(
    scenarios: list[dict],
    mode: str,        # "OR" | "AND"
    portfolio: float,
    lombard_on: bool,
    loan: float,
    rate_pa: float,   # % per year
    ltv_limit: float, # % e.g. 70.0
) -> dict:
    """Berechnet den Stresstest-Effekt aufs Portfolio."""
    if not scenarios:
        return {}

    if len(scenarios) == 1 or mode == "OR":
        sc = min(scenarios, key=lambda s: s["drawdown"])
        mode_note = TRS("or_note") if len(scenarios) > 1 else ""
    else:
        # AND: kumulierter Drawdown (gleichzeitig)
        compound = 1.0
        for s in scenarios:
            compound *= (1.0 + s["drawdown"])
        sc = {
            "id":              None,
            "name":            TRS("combined_name"),
            "drawdown":        compound - 1.0,
            "bear_months":     max(s["bear_months"]     for s in scenarios),
            "recovery_months": max(s["recovery_months"] for s in scenarios),
        }
        mode_note = TRS("and_note")

    drawdown = sc["drawdown"]
    stressed = portfolio * (1.0 + drawdown)
    loss     = portfolio - stressed

    result = {
        "scenario":        sc,
        "mode_note":       mode_note,
        "drawdown":        drawdown,
        "bear_months":     sc["bear_months"],
        "recovery_months": sc["recovery_months"],
        "stressed_value":  stressed,
        "loss":            loss,
        "loss_pct":        drawdown * 100.0,
        "mc_value":        None,
        "mc_pct":          None,
        "mc_hit":          False,
        "mc_buffer":       None,
        "annual_cost":     0.0,
    }

    if lombard_on and loan > 0 and ltv_limit > 0:
        # Margin Call wenn: Kredit / Portfolio_Stressiert >= ltv_limit/100
        mc_value = loan / (ltv_limit / 100.0)
        result.update({
            "mc_value":    mc_value,
            "mc_pct":      mc_value / portfolio * 100.0,
            "mc_hit":      stressed <= mc_value,
            "mc_buffer":   max(0.0, portfolio - mc_value),
            "annual_cost": loan * rate_pa / 100.0,
        })

    return result


# ── Chart ─────────────────────────────────────────────────────────────────────

def _draw_chart(fig, result: dict, dark_mode: bool) -> None:
    """Zeichnet die Erholungskurve in das matplotlib-Figure."""
    fig.clear()

    bg   = "#1e1e2e" if dark_mode else "#ffffff"
    fg   = "#cdd6f4" if dark_mode else "#2c3e50"
    grid = "#333355" if dark_mode else "#e0e0e0"

    fig.patch.set_facecolor(bg)
    ax = fig.add_subplot(111)
    ax.set_facecolor(bg)

    drawdown        = result["drawdown"]
    bear_months     = result["bear_months"]
    recovery_months = result["recovery_months"]
    trough_pct      = (1.0 + drawdown) * 100.0

    N      = 200
    t_bear = [i * bear_months / N for i in range(N + 1)]
    t_rec  = [bear_months + i * recovery_months / N for i in range(N + 1)]

    # Exponentieller Verlauf (realistischer als linear)
    v_bear = [
        100.0 * ((1.0 + drawdown) ** (t / bear_months)) if bear_months > 0
        else trough_pct
        for t in t_bear
    ]
    v_rec = [
        trough_pct * ((100.0 / trough_pct) ** ((t - bear_months) / recovery_months))
        if recovery_months > 0 else 100.0
        for t in t_rec
    ]

    all_t = t_bear + t_rec[1:]
    all_v = v_bear + v_rec[1:]

    ax.fill_between(t_bear, trough_pct * 0.5, v_bear,
                    alpha=0.18, color="#e74c3c", label=TRS("bear_phase"))
    ax.fill_between(t_rec,  trough_pct * 0.5, v_rec,
                    alpha=0.18, color="#27ae60", label=TRS("rec_phase"))
    ax.plot(all_t, all_v, color="#2980b9", linewidth=2.2, zorder=5)

    ax.axhline(y=100, color=fg, linestyle="--", linewidth=1, alpha=0.6)
    ax.text(bear_months * 0.05, 101.5, TRS("lbl_breakeven"),
            fontsize=8, color=fg, alpha=0.8)

    ax.axvline(x=bear_months, color="#e74c3c", linestyle=":", linewidth=1, alpha=0.5)
    offset_x = (bear_months + recovery_months) * 0.03
    ax.annotate(
        f"{TRS('lbl_trough')}: {drawdown * 100:.0f}%",
        xy=(bear_months, trough_pct),
        xytext=(bear_months + offset_x, trough_pct + 4),
        fontsize=8, color="#e74c3c",
        arrowprops=dict(arrowstyle="-", color="#e74c3c", alpha=0.5),
    )

    mc_pct = result.get("mc_pct")
    if mc_pct is not None:
        ax.axhline(y=mc_pct, color="#e74c3c", linestyle="--",
                   linewidth=1.8, alpha=0.9, zorder=6)
        mid_x = (bear_months + recovery_months) * 0.5
        ax.text(mid_x, mc_pct + 1.5, TRS("lbl_mc"),
                fontsize=8, color="#e74c3c", fontweight="bold")

    total_months = bear_months + recovery_months
    y_min = max(0, trough_pct - 18)
    if mc_pct is not None:
        y_min = min(y_min, mc_pct - 10)

    ax.set_xlabel(TRS("chart_x"), fontsize=9, color=fg)
    ax.set_ylabel(TRS("chart_y"), fontsize=9, color=fg)
    ax.set_title(TRS("chart_title"), fontsize=10, fontweight="bold", color=fg)
    ax.set_xlim(0, total_months * 1.04)
    ax.set_ylim(max(0, y_min), 115)
    ax.tick_params(colors=fg, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(grid)
    ax.grid(True, color=grid, linewidth=0.6, alpha=0.7)
    ax.legend(fontsize=8, loc="lower right",
              facecolor=bg, edgecolor=grid, labelcolor=fg)

    fig.tight_layout(pad=1.2)


# ── Haupt-Dialog ──────────────────────────────────────────────────────────────

def show_stress_test_dialog(parent, portfolio_value: float, currency: str = "USD") -> None:
    """Öffnet den Stresstest-Dialog.

    portfolio_value: Gesamtwert in der Anzeige-Währung (currency).
    """
    from PyQt6.QtWidgets import (
        QApplication, QDialog, QVBoxLayout, QHBoxLayout, QSplitter,
        QTabWidget, QWidget, QScrollArea, QFrame, QCheckBox, QLabel,
        QPushButton, QRadioButton, QButtonGroup, QGroupBox, QFormLayout,
        QDoubleSpinBox, QSpinBox, QLineEdit, QMessageBox,
    )
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPalette
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.figure import Figure

    if portfolio_value <= 0:
        QMessageBox.information(parent, TRS("title"), TRS("err_no_pf"))
        return

    _dm    = QApplication.palette().color(QPalette.ColorRole.Window).lightness() < 128
    _muted = "#aaa" if _dm else "#666"
    _red   = "#e74c3c"
    _green = "#27ae60"

    # ── Dialog ────────────────────────────────────────────────────────────────
    dialog = QDialog(parent)
    dialog.setWindowTitle(TRS("title"))
    dialog.setWindowFlag(Qt.WindowType.Window, True)
    screen = (parent.screen() or QApplication.primaryScreen()).availableGeometry()
    dlg_w  = min(int(screen.width()  * 0.82), 1350)
    dlg_h  = min(int(screen.height() * 0.86), 920)
    dialog.resize(dlg_w, dlg_h)
    dialog.move(screen.x() + (screen.width()  - dlg_w) // 2,
                screen.y() + (screen.height() - dlg_h) // 2)

    outer = QVBoxLayout(dialog)
    outer.setSpacing(6)
    outer.setContentsMargins(12, 8, 12, 8)

    # ── Emoji-Font Helper (wie self._ef in stock_monitor) ────────────────────
    def _apply_emoji_font(btn) -> None:
        from PyQt6.QtGui import QFontDatabase, QFont
        af = QFontDatabase.families()
        for fc in ('Segoe UI Emoji', 'Noto Color Emoji', 'Apple Color Emoji'):
            if fc in af:
                btn.setFont(QFont(fc, 10))
                return

    # ── Toolbar (oben) ────────────────────────────────────────────────────────
    toolbar = QHBoxLayout()
    toolbar.setSpacing(6)

    calc_btn = QPushButton(TRS("btn_calc"))
    calc_btn.setMinimumHeight(30)
    calc_btn.setStyleSheet("font-weight:bold; padding:2px 18px;")
    toolbar.addWidget(calc_btn)
    toolbar.addStretch()

    # Export-Button (wird nach _compute befüllt)
    _export_data: list = [None]

    def _get_export_data():
        return _export_data[0]

    main_win = next((w for w in QApplication.topLevelWidgets() if hasattr(w, '_make_export_btn')), None)
    if main_win is not None:
        export_btn = main_win._make_export_btn(_get_export_data, TRS("title"))
        export_btn.setMinimumHeight(30)
        export_btn.setEnabled(False)
        toolbar.addWidget(export_btn)
    else:
        export_btn = None

    def _open_komplex() -> None:
        mw = next((w for w in QApplication.topLevelWidgets()
                   if hasattr(w, '_get_symbols_values_for_risk')), None)
        if mw is None:
            return
        from komplex import show_komplex_dialog
        cur = getattr(mw, '_ov_currency', 'USD') or 'USD'
        fx  = mw._ov_fx.get(cur, 1.0) if hasattr(mw, '_ov_fx') else 1.0
        svr = [(s, v * fx) for s, v in mw._get_symbols_values_for_risk()]
        show_komplex_dialog(dialog, svr, cur)

    komplex_btn = QPushButton("▦ Komplex")
    komplex_btn.setMinimumHeight(30)
    komplex_btn.setStyleSheet("padding:2px 14px;")
    komplex_btn.clicked.connect(_open_komplex)
    toolbar.addWidget(komplex_btn)

    def _show_help() -> None:
        for w in QApplication.topLevelWidgets():
            if hasattr(w, 'show_help'):
                w.show_help(anchor="stresstest", parent_widget=dialog)
                break

    help_btn = QPushButton(TRS("btn_help"))
    help_btn.setMinimumHeight(30)
    help_btn.setStyleSheet("padding:2px 12px;")
    help_btn.clicked.connect(_show_help)
    _apply_emoji_font(help_btn)
    toolbar.addWidget(help_btn)

    close_btn = QPushButton(TRS("btn_close"))
    close_btn.setMinimumHeight(30)
    close_btn.setStyleSheet("padding:2px 12px;")
    close_btn.clicked.connect(dialog.close)
    toolbar.addWidget(close_btn)

    outer.addLayout(toolbar)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.setHandleWidth(5)
    outer.addWidget(splitter, stretch=1)

    # ═══════════════════════════════════════════════════════════════════════════
    # LINKE SEITE – Szenarien + Lombard
    # ═══════════════════════════════════════════════════════════════════════════
    left = QWidget()
    left_lay = QVBoxLayout(left)
    left_lay.setContentsMargins(0, 0, 6, 0)
    left_lay.setSpacing(8)
    splitter.addWidget(left)

    tabs = QTabWidget()
    left_lay.addWidget(tabs, stretch=1)

    # ─── Tab 1: Historische Ereignisse ────────────────────────────────────────
    hist_tab = QWidget()
    hist_lay = QVBoxLayout(hist_tab)
    hist_lay.setSpacing(4)
    hist_lay.setContentsMargins(4, 6, 4, 4)
    tabs.addTab(hist_tab, TRS("tab_hist"))

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    hist_lay.addWidget(scroll, stretch=1)

    sc_widget = QWidget()
    sc_lay    = QVBoxLayout(sc_widget)
    sc_lay.setSpacing(3)
    sc_lay.setContentsMargins(2, 2, 2, 2)
    scroll.setWidget(sc_widget)

    checkboxes: list[tuple[QCheckBox, dict]] = []
    for sc in SCENARIOS:
        name  = TRS(f"sc_{sc['id']}")
        dd    = f"{sc['drawdown'] * 100:.0f} %"
        bear  = f"{sc['bear_months']} {TRS('months_short')}"
        rec   = f"{sc['recovery_months']} {TRS('months_short')}"
        label = f"{name}   {dd}  |  {TRS('lbl_bear_dur')}: {bear}  {TRS('lbl_rec_dur')}: {rec}"
        cb    = QCheckBox(label)
        cb.setToolTip(TRS(f"desc_{sc['id']}"))
        cb.setStyleSheet("font-size: 11px;")
        checkboxes.append((cb, sc))
        sc_lay.addWidget(cb)
    sc_lay.addStretch()

    # Kombinations-Optionen
    combine_frame = QFrame()
    combine_frame.setFrameShape(QFrame.Shape.StyledPanel)
    comb_lay = QVBoxLayout(combine_frame)
    comb_lay.setSpacing(4)
    comb_lay.setContentsMargins(8, 6, 8, 6)
    comb_lay.addWidget(QLabel(f"<b>{TRS('lbl_combine')}</b>"))
    rb_or  = QRadioButton(TRS("rb_or"))
    rb_and = QRadioButton(TRS("rb_and"))
    rb_or.setChecked(True)
    rg = QButtonGroup(dialog)
    rg.addButton(rb_or)
    rg.addButton(rb_and)
    comb_lay.addWidget(rb_or)
    comb_lay.addWidget(rb_and)
    hist_lay.addWidget(combine_frame)

    # ─── Tab 2: Eigenes Szenario ──────────────────────────────────────────────
    custom_tab = QWidget()
    custom_lay = QFormLayout(custom_tab)
    custom_lay.setSpacing(8)
    custom_lay.setContentsMargins(10, 10, 10, 10)
    tabs.addTab(custom_tab, TRS("tab_custom"))

    name1_edit = QLineEdit()
    name1_edit.setPlaceholderText(TRS("lbl_name"))
    custom_lay.addRow(TRS("lbl_name"), name1_edit)

    dd1_spin = QDoubleSpinBox()
    dd1_spin.setRange(-99.0, -1.0)
    dd1_spin.setValue(-30.0)
    dd1_spin.setSuffix(" %")
    dd1_spin.setSingleStep(1.0)
    custom_lay.addRow(TRS("lbl_dd"), dd1_spin)

    bear1_spin = QSpinBox()
    bear1_spin.setRange(1, 240)
    bear1_spin.setValue(12)
    bear1_spin.setSuffix(f" {TRS('months_short')}")
    custom_lay.addRow(TRS("lbl_bear"), bear1_spin)

    rec1_spin = QSpinBox()
    rec1_spin.setRange(1, 360)
    rec1_spin.setValue(36)
    rec1_spin.setSuffix(f" {TRS('months_short')}")
    custom_lay.addRow(TRS("lbl_rec"), rec1_spin)

    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    custom_lay.addRow(sep)

    chk_shock2 = QCheckBox(TRS("chk_shock2"))
    custom_lay.addRow(chk_shock2)

    link_widget = QWidget()
    link_lay    = QHBoxLayout(link_widget)
    link_lay.setContentsMargins(0, 0, 0, 0)
    rb_cust_or  = QRadioButton("OR")
    rb_cust_and = QRadioButton("AND")
    rb_cust_or.setChecked(True)
    rg2 = QButtonGroup(dialog)
    rg2.addButton(rb_cust_or)
    rg2.addButton(rb_cust_and)
    link_lay.addWidget(rb_cust_or)
    link_lay.addWidget(rb_cust_and)
    link_lay.addStretch()
    link_lbl = QLabel(TRS("lbl_link") + ":")
    custom_lay.addRow(link_lbl, link_widget)

    name2_edit = QLineEdit()
    name2_edit.setPlaceholderText(TRS("lbl_name"))
    custom_lay.addRow(TRS("lbl_name"), name2_edit)

    dd2_spin = QDoubleSpinBox()
    dd2_spin.setRange(-99.0, -1.0)
    dd2_spin.setValue(-20.0)
    dd2_spin.setSuffix(" %")
    dd2_spin.setSingleStep(1.0)
    custom_lay.addRow(TRS("lbl_dd"), dd2_spin)

    bear2_spin = QSpinBox()
    bear2_spin.setRange(1, 240)
    bear2_spin.setValue(6)
    bear2_spin.setSuffix(f" {TRS('months_short')}")
    custom_lay.addRow(TRS("lbl_bear"), bear2_spin)

    rec2_spin = QSpinBox()
    rec2_spin.setRange(1, 360)
    rec2_spin.setValue(24)
    rec2_spin.setSuffix(f" {TRS('months_short')}")
    custom_lay.addRow(TRS("lbl_rec"), rec2_spin)

    _shock2_widgets = [link_lbl, link_widget, name2_edit, dd2_spin, bear2_spin, rec2_spin]

    def _toggle_shock2(checked: bool) -> None:
        for w in _shock2_widgets:
            w.setVisible(checked)

    chk_shock2.toggled.connect(_toggle_shock2)
    _toggle_shock2(False)

    # ── Lombardkredit ─────────────────────────────────────────────────────────
    lombard_grp = QGroupBox(TRS("lbl_lombard_grp"))
    lombard_grp.setCheckable(True)
    lombard_grp.setChecked(False)
    lombard_form = QFormLayout(lombard_grp)
    lombard_form.setSpacing(6)
    lombard_form.setContentsMargins(8, 8, 8, 8)

    loan_spin = QDoubleSpinBox()
    loan_spin.setRange(0, 1e9)
    loan_spin.setValue(0)
    loan_spin.setGroupSeparatorShown(True)
    loan_spin.setSuffix(f"  {currency}")
    loan_spin.setSingleStep(10_000)
    lombard_form.addRow(TRS("lbl_amount"), loan_spin)

    rate_spin = QDoubleSpinBox()
    rate_spin.setRange(0, 30.0)
    rate_spin.setValue(3.5)
    rate_spin.setSuffix(" %")
    rate_spin.setSingleStep(0.25)
    lombard_form.addRow(TRS("lbl_rate"), rate_spin)

    ltv_spin = QDoubleSpinBox()
    ltv_spin.setRange(10.0, 95.0)
    ltv_spin.setValue(70.0)
    ltv_spin.setSuffix(" %")
    ltv_spin.setSingleStep(5.0)
    lombard_form.addRow(TRS("lbl_ltv"), ltv_spin)

    left_lay.addWidget(lombard_grp)

    # ═══════════════════════════════════════════════════════════════════════════
    # RECHTE SEITE – Ergebnisse + Chart
    # ═══════════════════════════════════════════════════════════════════════════
    right = QWidget()
    right_lay = QVBoxLayout(right)
    right_lay.setContentsMargins(6, 0, 0, 0)
    right_lay.setSpacing(8)
    splitter.addWidget(right)

    result_frame = QFrame()
    result_frame.setFrameShape(QFrame.Shape.StyledPanel)
    res_form = QFormLayout(result_frame)
    res_form.setSpacing(6)
    res_form.setContentsMargins(12, 10, 12, 10)
    right_lay.addWidget(result_frame)

    def _make_lbl(color: str = "", bold: bool = False) -> QLabel:
        lbl = QLabel("—")
        style = ""
        if color:
            style += f"color:{color};"
        if bold:
            style += "font-weight:bold; font-size:13px;"
        if style:
            lbl.setStyleSheet(style)
        return lbl

    lbl_pf_val    = _make_lbl(bold=True)
    lbl_stressed  = _make_lbl(color=_red, bold=True)
    lbl_loss      = _make_lbl(color=_red, bold=True)
    lbl_recovery  = _make_lbl()
    lbl_mc_at     = _make_lbl(color=_red)
    lbl_mc_hit    = _make_lbl()
    lbl_mc_buffer = _make_lbl()
    lbl_cost      = _make_lbl()

    res_form.addRow(f"<b>{TRS('lbl_pf_value')}:</b>",  lbl_pf_val)
    res_form.addRow(f"<b>{TRS('lbl_stressed')}:</b>",   lbl_stressed)
    res_form.addRow(f"<b>{TRS('lbl_loss')}:</b>",       lbl_loss)
    res_form.addRow(f"{TRS('lbl_recovery')}:",           lbl_recovery)
    res_form.addRow(f"{TRS('lbl_mc_at')}:",              lbl_mc_at)
    res_form.addRow(f"{TRS('lbl_mc_hit')}:",             lbl_mc_hit)
    res_form.addRow(f"{TRS('lbl_mc_buffer')}:",          lbl_mc_buffer)
    res_form.addRow(f"{TRS('lbl_annual_cost')}:",        lbl_cost)

    lbl_pf_val.setText(_fmt_val(portfolio_value, currency))

    fig    = Figure(figsize=(7, 4.5), dpi=96)
    canvas = FigureCanvasQTAgg(fig)
    right_lay.addWidget(canvas, stretch=1)

    # ── Footer (nur Disclaimer) ───────────────────────────────────────────────
    disc = QLabel(TRS("disclaimer"))
    disc.setWordWrap(True)
    disc.setStyleSheet(
        f"color:{_muted}; font-size:10px; font-style:italic; "
        f"padding:4px 0; border-top:1px solid {'#444' if _dm else '#ddd'};"
    )
    outer.addWidget(disc)

    splitter.setSizes([int(dlg_w * 0.36), int(dlg_w * 0.64)])

    # ── Berechnen ─────────────────────────────────────────────────────────────
    def _compute() -> None:
        lombard_on = lombard_grp.isChecked()

        if tabs.currentIndex() == 0:
            selected = [sc for cb, sc in checkboxes if cb.isChecked()]
            if not selected:
                QMessageBox.information(dialog, TRS("title"), TRS("err_no_scenario"))
                return
            mode = "AND" if rb_and.isChecked() else "OR"
        else:
            sc1 = {
                "id":              None,
                "name":            name1_edit.text() or "Szenario 1",
                "drawdown":        dd1_spin.value() / 100.0,
                "bear_months":     bear1_spin.value(),
                "recovery_months": rec1_spin.value(),
            }
            selected = [sc1]
            if chk_shock2.isChecked():
                sc2 = {
                    "id":              None,
                    "name":            name2_edit.text() or "Szenario 2",
                    "drawdown":        dd2_spin.value() / 100.0,
                    "bear_months":     bear2_spin.value(),
                    "recovery_months": rec2_spin.value(),
                }
                selected.append(sc2)
            mode = "AND" if rb_cust_and.isChecked() else "OR"

        res = _compute_scenario(
            scenarios  = selected,
            mode       = mode,
            portfolio  = portfolio_value,
            lombard_on = lombard_on,
            loan       = loan_spin.value() if lombard_on else 0.0,
            rate_pa    = rate_spin.value() if lombard_on else 0.0,
            ltv_limit  = ltv_spin.value()  if lombard_on else 0.0,
        )
        if not res:
            return

        lbl_pf_val.setText(_fmt_val(portfolio_value, currency))
        lbl_stressed.setText(
            f"{_fmt_val(res['stressed_value'], currency)}  ({res['loss_pct']:.1f} %)"
        )
        lbl_loss.setText(
            f"−{_fmt_val(res['loss'], currency)}  ({res['loss_pct']:.1f} %)"
        )
        lbl_recovery.setText(_fmt_months(res["recovery_months"]))

        if lombard_on and res["mc_value"] is not None:
            lbl_mc_at.setText(
                f"{_fmt_val(res['mc_value'], currency)}  ({res['mc_pct']:.1f} %)"
            )
            hit = res["mc_hit"]
            lbl_mc_hit.setText(TRS("yes") if hit else TRS("no"))
            lbl_mc_hit.setStyleSheet(
                f"color:{_red}; font-weight:bold;" if hit else f"color:{_green};"
            )
            lbl_mc_buffer.setText(_fmt_val(res["mc_buffer"], currency))
            lbl_cost.setText(_fmt_val(res["annual_cost"], currency) + " p.a.")
        else:
            for lbl in (lbl_mc_at, lbl_mc_hit, lbl_mc_buffer, lbl_cost):
                lbl.setText("—")
            lbl_mc_hit.setStyleSheet("")

        _draw_chart(fig, res, dark_mode=_dm)
        canvas.draw()

        # ── Export-Daten zusammenstellen ──────────────────────────────────────
        sc      = res["scenario"]
        sc_name = sc.get("name") or TRS(f"sc_{sc['id']}")
        headers = [
            TRS("title"),
            "Drawdown",
            TRS("lbl_loss"),
            TRS("lbl_recovery"),
            TRS("lbl_bear_dur"),
        ]
        row = [
            sc_name,
            f"{res['loss_pct']:.1f} %",
            _fmt_val(res["loss"], currency),
            _fmt_months(res["recovery_months"]),
            _fmt_months(res["bear_months"]),
        ]
        if lombard_on and res["mc_value"] is not None:
            headers += [
                TRS("lbl_mc_at"), TRS("lbl_mc_hit"),
                TRS("lbl_mc_buffer"), TRS("lbl_annual_cost"),
            ]
            row += [
                _fmt_val(res["mc_value"], currency),
                TRS("yes") if res["mc_hit"] else TRS("no"),
                _fmt_val(res["mc_buffer"], currency),
                _fmt_val(res["annual_cost"], currency) + " p.a.",
            ]
        _export_data[0] = {
            "title":   f"{TRS('title')} – {sc_name}",
            "headers": headers,
            "rows":    [row],
            "fig":     fig,
        }
        if export_btn is not None:
            export_btn.setEnabled(True)

    calc_btn.clicked.connect(_compute)
    dialog.exec()
