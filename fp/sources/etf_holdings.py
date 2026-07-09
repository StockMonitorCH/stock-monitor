"""
etf_holdings.py – ETF/Fonds-Holdings für Stock Monitor
=======================================================
Holt Top-Positionen und Sektorgewichtung von ETFs und Fonds.
Primärquelle: yfinance funds_data (deckt die meisten US-ETFs ab).
"""

from __future__ import annotations


# ── Sektor-Übersetzung (Englisch → Deutsch) ──────────────────────────────────
_SECTOR_DE: dict[str, str] = {
    "technology":             "Technologie",
    "financial_services":     "Finanzen",
    "healthcare":             "Gesundheit",
    "consumer_cyclical":      "Konsum (zyklisch)",
    "industrials":            "Industrie",
    "communication_services": "Kommunikation",
    "consumer_defensive":     "Konsum (defensiv)",
    "energy":                 "Energie",
    "real_estate":            "Immobilien",
    "basic_materials":        "Rohstoffe",
    "utilities":              "Versorgung",
}

_SECTOR_EN: dict[str, str] = {
    "technology":             "Technology",
    "financial_services":     "Financial Services",
    "healthcare":             "Healthcare",
    "consumer_cyclical":      "Consumer Cyclical",
    "industrials":            "Industrials",
    "communication_services": "Communication",
    "consumer_defensive":     "Consumer Defensive",
    "energy":                 "Energy",
    "real_estate":            "Real Estate",
    "basic_materials":        "Basic Materials",
    "utilities":              "Utilities",
}


def _fmt_assets(val: float | None, currency: str = "USD") -> str:
    """Formatiert Fondsvolumen in lesbarer Form (Mrd./Bio.)."""
    if val is None:
        return "—"
    sym = {"USD": "$", "EUR": "€", "CHF": "CHF ", "GBP": "£"}.get(currency, currency + " ")
    if val >= 1_000_000_000_000:
        return f"{sym}{val / 1_000_000_000_000:.2f} Bio."
    if val >= 1_000_000_000:
        return f"{sym}{val / 1_000_000_000:.2f} Mrd."
    if val >= 1_000_000:
        return f"{sym}{val / 1_000_000:.2f} Mio."
    return f"{sym}{val:,.0f}"


def fetch_holdings(symbol: str) -> tuple[list[dict], dict]:
    """
    Holt ETF/Fonds-Holdings via yfinance.

    Returns
    -------
    holdings : list[dict]
        [{'rank': 1, 'symbol': 'AAPL', 'name': 'Apple Inc.', 'weight': 7.23}, ...]
    meta : dict
        Fond-Metadaten: quote_type, fund_name, total_assets, expense_ratio,
        ytd_return, category, sector_weights, source, error
    """
    meta: dict = {
        "quote_type":     "",
        "fund_name":      symbol,
        "total_assets":   None,
        "currency":       "USD",
        "expense_ratio":  None,
        "ytd_return":     None,
        "category":       None,
        "sector_weights": {},
        "source":         "",
        "error":          "",
    }

    try:
        import yfinance as yf

        ticker   = yf.Ticker(symbol)
        info     = ticker.info
        qtype    = (info.get("quoteType") or "").upper()

        meta["quote_type"]    = qtype
        meta["fund_name"]     = info.get("longName") or info.get("shortName") or symbol
        meta["total_assets"]  = info.get("totalAssets")
        meta["currency"]      = info.get("currency", "USD")
        meta["expense_ratio"] = info.get("annualReportExpenseRatio") or info.get("expenseRatio")
        meta["ytd_return"]    = info.get("ytdReturn")
        meta["category"]      = info.get("category")

        if qtype not in ("ETF", "MUTUALFUND"):
            meta["error"] = "not_fund"
            return [], meta

        # ── Holdings via funds_data ───────────────────────────────────────────
        holdings: list[dict] = []
        try:
            fd  = ticker.funds_data
            df  = fd.top_holdings
            if df is not None and not df.empty:
                # Spaltennamen normalisieren (verschiedene yfinance-Versionen)
                col_map = {c.lower().replace(" ", "_"): c for c in df.columns}
                col_name = col_map.get("name") or col_map.get("holdingname") or col_map.get("holding_name")
                col_pct  = (col_map.get("holding_percent") or col_map.get("holdingpercent")
                            or col_map.get("weight") or col_map.get("percent"))
                for rank, (idx, row) in enumerate(df.iterrows(), 1):
                    sym  = str(idx)
                    name = str(row[col_name]) if col_name and col_name in row else sym
                    pct  = float(row[col_pct]) if col_pct and col_pct in row else 0.0
                    holdings.append({
                        "rank":   rank,
                        "symbol": sym,
                        "name":   name,
                        "weight": pct * 100,
                    })

            # Sektor-Gewichtung
            try:
                sw = fd.sector_weightings
                if sw:
                    meta["sector_weights"] = {k: v * 100 for k, v in sw.items() if v}
            except Exception:
                pass

        except Exception as exc:
            meta["error"] = str(exc)

        if holdings:
            meta["source"] = "Yahoo Finance"
            return holdings, meta

        meta["error"] = "no_holdings"
        return [], meta

    except Exception as exc:
        meta["error"] = str(exc)
        return [], meta


# ══════════════════════════════════════════════════════════════════════════════
#  ETFHoldingsDialog
# ══════════════════════════════════════════════════════════════════════════════

def show_etf_holdings_dialog(symbol: str, parent=None) -> None:
    """Öffnet den Holdings-Dialog für den gegebenen ETF/Fonds-Ticker."""
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
        QScrollArea, QWidget, QProgressBar, QApplication, QSizePolicy,
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QFont, QPalette, QColor

    try:
        from translations import TR
    except ImportError:
        def TR(key, **kw):  # type: ignore[misc]
            return kw.get("default", key)

    # ── Bildschirmgrösse & Dark-Mode ─────────────────────────────────────────
    screen  = QApplication.primaryScreen().availableGeometry()
    is_fhd  = screen.width() <= 1920
    dm      = QApplication.palette().color(QPalette.ColorRole.Window).lightness() < 128

    dlg_w = int(screen.width()  * (0.72 if is_fhd else 0.60))
    dlg_h = int(screen.height() * (0.82 if is_fhd else 0.75))
    dlg_w = max(720, min(dlg_w, 1300))
    dlg_h = max(560, min(dlg_h, 1000))

    # ── Farben ───────────────────────────────────────────────────────────────
    C = {
        "bg":         "#1e1e2e" if dm else "#f8f9fa",
        "card":       "#2a2a3e" if dm else "#ffffff",
        "border":     "#3a3a5c" if dm else "#dee2e6",
        "text":       "#cdd6f4" if dm else "#212529",
        "text_dim":   "#a6adc8" if dm else "#6c757d",
        "accent":     "#89b4fa" if dm else "#0d6efd",
        "header_bg":  "#313244" if dm else "#e9ecef",
        "row_alt":    "#252535" if dm else "#f8f9fa",
        "bar_fill":   "#89b4fa" if dm else "#0d6efd",
        "bar_bg":     "#3a3a5c" if dm else "#dee2e6",
        "tag_etf_bg": "#1e3a5f" if dm else "#cfe2ff",
        "tag_etf_fg": "#89b4fa" if dm else "#084298",
        "tag_mf_bg":  "#1e3f2e" if dm else "#d1e7dd",
        "tag_mf_fg":  "#a6e3a1" if dm else "#0a3622",
    }

    # ── Lade-Dialog ──────────────────────────────────────────────────────────
    dlg = QDialog(parent)
    dlg.setWindowTitle(f"📋  {TR('title_etf_holdings', symbol=symbol)}")
    dlg.resize(dlg_w, dlg_h)
    dlg.move(
        screen.x() + (screen.width()  - dlg_w) // 2,
        screen.y() + (screen.height() - dlg_h) // 2,
    )
    if dm:
        dlg.setStyleSheet(f"QDialog {{ background: {C['bg']}; color: {C['text']}; }}")

    outer = QVBoxLayout(dlg)
    outer.setContentsMargins(16, 14, 16, 14)
    outer.setSpacing(10)

    # ── Ladehinweis ──────────────────────────────────────────────────────────
    loading_lbl = QLabel(f"⏳  {TR('lbl_etf_loading', symbol=symbol)}")
    loading_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    loading_lbl.setStyleSheet(f"font-size: 14px; color: {C['text_dim']}; padding: 40px;")
    outer.addWidget(loading_lbl)

    dlg.show()
    QApplication.processEvents()

    # ── Daten laden ──────────────────────────────────────────────────────────
    holdings, meta = fetch_holdings(symbol)

    # Ladehinweis entfernen
    loading_lbl.hide()
    outer.removeWidget(loading_lbl)
    loading_lbl.deleteLater()

    # ── Fehlerfall: kein ETF ─────────────────────────────────────────────────
    if meta.get("error") == "not_fund":
        err_lbl = QLabel(TR("lbl_not_etf", symbol=symbol, qtype=meta.get("quote_type", "?")))
        err_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        err_lbl.setWordWrap(True)
        err_lbl.setStyleSheet(
            f"font-size: 13px; color: {'#f38ba8' if dm else '#842029'}; "
            f"background: {'#3e1a1e' if dm else '#f8d7da'}; "
            "border-radius: 6px; padding: 20px;"
        )
        outer.addWidget(err_lbl)
        _add_close_btn(outer, dlg, C, dm, TR)
        dlg.exec()
        return

    # ── Header-Karte ─────────────────────────────────────────────────────────
    hdr_frame = QFrame()
    hdr_frame.setStyleSheet(
        f"QFrame {{ background: {C['card']}; border: 1px solid {C['border']}; "
        "border-radius: 8px; }}"
    )
    hdr_lay = QVBoxLayout(hdr_frame)
    hdr_lay.setContentsMargins(16, 12, 16, 12)
    hdr_lay.setSpacing(6)

    # Titelzeile
    title_row = QHBoxLayout()
    title_lbl = QLabel(f"<b>{meta['fund_name']}</b>")
    title_lbl.setStyleSheet(f"font-size: {15 if is_fhd else 17}px; color: {C['text']};")
    title_row.addWidget(title_lbl, stretch=1)

    # ETF/Fonds-Badge
    qtype = meta.get("quote_type", "")
    if qtype == "ETF":
        tag_txt, tag_bg, tag_fg = "ETF", C["tag_etf_bg"], C["tag_etf_fg"]
    else:
        tag_txt, tag_bg, tag_fg = TR("lbl_fund_badge"), C["tag_mf_bg"], C["tag_mf_fg"]
    badge = QLabel(f"  {tag_txt}  ")
    badge.setStyleSheet(
        f"background: {tag_bg}; color: {tag_fg}; font-size: 11px; font-weight: bold; "
        "border-radius: 4px; padding: 2px 6px;"
    )
    badge.setFixedHeight(22)
    title_row.addWidget(badge)
    hdr_lay.addLayout(title_row)

    # Metadaten-Zeile
    meta_parts: list[str] = []
    if meta.get("total_assets"):
        meta_parts.append(f"💰 {TR('lbl_etf_aum')}: {_fmt_assets(meta['total_assets'], meta['currency'])}")
    if meta.get("expense_ratio") is not None:
        meta_parts.append(f"⚙️  TER: {meta['expense_ratio'] * 100:.2f}%")
    if meta.get("ytd_return") is not None:
        ytd = meta["ytd_return"] * 100
        color = "#a6e3a1" if dm else "#198754" if ytd >= 0 else "#f38ba8" if dm else "#dc3545"
        sign  = "+" if ytd >= 0 else ""
        meta_parts.append(f'<span style="color:{color}">📈 YTD: {sign}{ytd:.1f}%</span>')
    if meta.get("category"):
        meta_parts.append(f"📂 {meta['category']}")

    if meta_parts:
        meta_lbl = QLabel("   │   ".join(meta_parts))
        meta_lbl.setStyleSheet(f"font-size: {10 if is_fhd else 11}px; color: {C['text_dim']};")
        meta_lbl.setWordWrap(True)
        hdr_lay.addWidget(meta_lbl)

    outer.addWidget(hdr_frame)

    # ── Keine Holdings ────────────────────────────────────────────────────────
    if not holdings:
        no_data = QLabel(TR("lbl_etf_no_holdings"))
        no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_data.setWordWrap(True)
        no_data.setStyleSheet(
            f"font-size: 13px; color: {'#f9e2af' if dm else '#664d03'}; "
            f"background: {'#3e2e0a' if dm else '#fff3cd'}; "
            "border-radius: 6px; padding: 20px;"
        )
        outer.addWidget(no_data)
        _add_close_btn(outer, dlg, C, dm, TR)
        dlg.exec()
        return

    # ── Haupt-Scrollbereich ──────────────────────────────────────────────────
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet(
        f"QScrollArea {{ border: none; background: {C['bg']}; }}"
        f"QScrollBar:vertical {{ background: {C['header_bg']}; width: 10px; border-radius: 5px; }}"
        f"QScrollBar::handle:vertical {{ background: {C['border']}; border-radius: 5px; }}"
    )
    scroll_widget = QWidget()
    scroll_widget.setStyleSheet(f"background: {C['bg']};")
    scroll_lay = QVBoxLayout(scroll_widget)
    scroll_lay.setContentsMargins(0, 0, 4, 0)
    scroll_lay.setSpacing(10)

    # ── Holdings-Tabelle ─────────────────────────────────────────────────────
    pos_sec = _make_section_label(TR("lbl_etf_positions", n=len(holdings)), C, dm, is_fhd)
    scroll_lay.addWidget(pos_sec)

    max_weight = max((h["weight"] for h in holdings), default=1.0)

    table = QTableWidget(len(holdings), 4)
    table.setHorizontalHeaderLabels([
        TR("lbl_etf_col_rank"),
        TR("lbl_etf_col_symbol"),
        TR("lbl_etf_col_name"),
        TR("lbl_etf_col_weight"),
    ])
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setAlternatingRowColors(True)
    table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
    table.setColumnWidth(0, 50)
    table.setColumnWidth(1, 80)
    table.setColumnWidth(3, 200 if not is_fhd else 170)

    fs_tbl = 11 if is_fhd else 12
    table.setStyleSheet(
        f"QTableWidget {{"
        f"  background: {C['card']}; color: {C['text']}; "
        f"  gridline-color: {C['border']}; font-size: {fs_tbl}px; border: none;"
        f"}}"
        f"QTableWidget::item:alternate {{ background: {C['row_alt']}; }}"
        f"QTableWidget::item:selected  {{ background: {C['accent']}; color: white; }}"
        f"QHeaderView::section {{"
        f"  background: {C['header_bg']}; color: {C['text']}; "
        f"  font-weight: bold; font-size: {fs_tbl}px; padding: 5px; "
        f"  border: none; border-bottom: 1px solid {C['border']};"
        f"}}"
    )

    row_h = 28 if is_fhd else 32
    table.verticalHeader().setDefaultSectionSize(row_h)

    for h in holdings:
        r = h["rank"] - 1
        # Rang
        ri = QTableWidgetItem(str(h["rank"]))
        ri.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(r, 0, ri)
        # Symbol
        si = QTableWidgetItem(h["symbol"])
        si.setFont(QFont("Monospace", fs_tbl))
        si.setForeground(QColor(C["accent"]))
        table.setItem(r, 1, si)
        # Name
        ni = QTableWidgetItem(h["name"])
        table.setItem(r, 2, ni)
        # Gewicht + Mini-Balken (als HTML in QLabel innerhalb Cell-Widget)
        w_cell = QWidget()
        w_cell.setStyleSheet(f"background: transparent;")
        w_lay  = QHBoxLayout(w_cell)
        w_lay.setContentsMargins(6, 3, 8, 3)
        w_lay.setSpacing(6)

        w_lbl = QLabel(f"{h['weight']:.2f}%")
        w_lbl.setFixedWidth(48)
        w_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        w_lbl.setStyleSheet(f"font-size: {fs_tbl}px; color: {C['text']}; font-weight: bold;")
        w_lay.addWidget(w_lbl)

        bar = QProgressBar()
        bar.setRange(0, 1000)
        bar.setValue(int(h["weight"] / max_weight * 1000))
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        bar.setStyleSheet(
            f"QProgressBar {{ background: {C['bar_bg']}; border-radius: 4px; border: none; }}"
            f"QProgressBar::chunk {{ background: {C['bar_fill']}; border-radius: 4px; }}"
        )
        w_lay.addWidget(bar, stretch=1)
        table.setCellWidget(r, 3, w_cell)

    scroll_lay.addWidget(table)

    # ── Sektor-Gewichtung ────────────────────────────────────────────────────
    sector_weights = meta.get("sector_weights", {})
    if sector_weights:
        scroll_lay.addSpacing(4)
        sec_sec = _make_section_label(TR("lbl_etf_sectors"), C, dm, is_fhd)
        scroll_lay.addWidget(sec_sec)

        try:
            from translations import _CURRENT_LANG
            lang = _CURRENT_LANG
        except ImportError:
            lang = "DE"

        sector_map = _SECTOR_DE if lang == "DE" else _SECTOR_EN
        sorted_sectors = sorted(sector_weights.items(), key=lambda x: x[1], reverse=True)
        max_sw = sorted_sectors[0][1] if sorted_sectors else 1.0

        sec_frame = QFrame()
        sec_frame.setStyleSheet(
            f"QFrame {{ background: {C['card']}; border: 1px solid {C['border']}; "
            "border-radius: 6px; }}"
        )
        sec_inner = QVBoxLayout(sec_frame)
        sec_inner.setContentsMargins(14, 10, 14, 10)
        sec_inner.setSpacing(5)

        for skey, spct in sorted_sectors:
            if spct < 0.1:
                continue
            sname = sector_map.get(skey, skey.replace("_", " ").title())
            row_w = QWidget()
            row_w.setStyleSheet("background: transparent;")
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(0, 0, 0, 0)
            row_l.setSpacing(8)

            name_l = QLabel(sname)
            name_l.setFixedWidth(170 if not is_fhd else 150)
            name_l.setStyleSheet(f"font-size: {fs_tbl}px; color: {C['text']};")
            row_l.addWidget(name_l)

            sbar = QProgressBar()
            sbar.setRange(0, 1000)
            sbar.setValue(int(spct / max_sw * 1000))
            sbar.setTextVisible(False)
            sbar.setFixedHeight(10)
            sbar.setStyleSheet(
                f"QProgressBar {{ background: {C['bar_bg']}; border-radius: 5px; border: none; }}"
                f"QProgressBar::chunk {{ background: {C['bar_fill']}; border-radius: 5px; }}"
            )
            row_l.addWidget(sbar, stretch=1)

            pct_l = QLabel(f"{spct:.1f}%")
            pct_l.setFixedWidth(44)
            pct_l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            pct_l.setStyleSheet(f"font-size: {fs_tbl}px; color: {C['text_dim']};")
            row_l.addWidget(pct_l)

            sec_inner.addWidget(row_w)

        scroll_lay.addWidget(sec_frame)

    scroll_lay.addStretch()
    scroll.setWidget(scroll_widget)
    outer.addWidget(scroll, stretch=1)

    # ── Quellen-Hinweis + Schliessen-Button ───────────────────────────────────
    foot_row = QHBoxLayout()
    if meta.get("source"):
        src_lbl = QLabel(TR("lbl_etf_source", source=meta["source"]))
        src_lbl.setStyleSheet(f"font-size: 10px; color: {C['text_dim']};")
        foot_row.addWidget(src_lbl)
    foot_row.addStretch()
    close_btn = QPushButton(TR("btn_close"))
    close_btn.setFixedWidth(120)
    close_btn.setStyleSheet(
        f"QPushButton {{ background: {C['accent']}; color: white; font-weight: bold; "
        f"border-radius: 5px; padding: 6px 16px; font-size: {fs_tbl}px; }}"
        "QPushButton:hover { opacity: 0.85; }"
    )
    close_btn.clicked.connect(dlg.accept)
    foot_row.addWidget(close_btn)
    outer.addLayout(foot_row)

    dlg.exec()


# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

def _make_section_label(text: str, C: dict, dm: bool, is_fhd: bool):
    from PyQt6.QtWidgets import QLabel
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size: {12 if is_fhd else 13}px; font-weight: bold; "
        f"color: {C['text']}; padding: 2px 0;"
    )
    return lbl


def _add_close_btn(layout, dlg, C: dict, dm: bool, TR):
    from PyQt6.QtWidgets import QHBoxLayout, QPushButton
    row = QHBoxLayout()
    row.addStretch()
    btn = QPushButton(TR("btn_close"))
    btn.setFixedWidth(120)
    btn.setStyleSheet(
        f"QPushButton {{ background: {C['accent']}; color: white; font-weight: bold; "
        "border-radius: 5px; padding: 6px 16px; }}"
    )
    btn.clicked.connect(dlg.accept)
    row.addWidget(btn)
    layout.addLayout(row)
