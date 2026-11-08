#!/usr/bin/env python3
"""
dividend_account.py – Dividendenkonto (Mehrwährungskonto) für Stock Monitor
============================================================================
Gutgeschriebene Dividenden werden – wie bei einem Mehrwährungskonto (z. B.
Swissquote) – dem Konto ihrer Währung gutgeschrieben. Zusätzlich können
manuelle Ein- und Auszahlungen erfasst werden. Der Gesamtsaldo wird in der
Portfolio-Währung angezeigt, wahlweise brutto oder netto (nach Quellensteuer).

Datenhaltung: ein dict, das mit dem Portfolio gespeichert wird
(Schlüssel "div_account" in der aktiven Portfolio-JSON und in der .smpf-Datei):

    {
      "version":  1,
      "settings": {"residence": "CH", "w8ben": True, "configured": True},
      "entries":  [ {id, type, date, currency, gross, tax, rate, symbol,
                     qty, per_share, note, edited}, ... ],
      "dismissed": [ids gelöschter automatischer Dividenden],
      "symbols":  {sym: {"currency": "USD", "factor": 1.0, "country": "US"}},
      "fx":       {"base": "CHF", "rates": {"USD": 0.88, ...}},
    }

Automatische Dividenden haben die id "div:<SYMBOL>:<EX-DATUM>" und werden beim
Aktualisieren nachgeführt (Bestand am Ex-Tag), ausser sie wurden manuell
geändert ("edited") oder gelöscht ("dismissed").
"""

from __future__ import annotations

import copy
import sys
import uuid
from datetime import date, datetime, timedelta

from PyQt6.QtCore import Qt, QThread, QDate, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontDatabase
from PyQt6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDateEdit, QDialog, QFrame,
    QDoubleSpinBox, QFormLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QApplication,
)

from dividend_account_translations import T

try:
    from tax_module import div_withholding_rate, DIV_ACCOUNT_RESIDENCES
except Exception:                                   # pragma: no cover
    DIV_ACCOUNT_RESIDENCES = ("CH", "DE", "AT", "UK", "US", "OTHER")

    def div_withholding_rate(source_country, residence, w8ben=True):
        return 0.0

try:
    import config as _cfg
except ImportError:                                 # pragma: no cover
    _cfg = None


# ══════════════════════════════════════════════════════════════════════════════
#  Datenmodell (ohne Qt – testbar)
# ══════════════════════════════════════════════════════════════════════════════

ACCOUNT_VERSION = 1

# Yahoo-Suffix → Sitzland (Fallback, wenn Yahoo kein Land liefert)
_SUFFIX_COUNTRY = {
    "SW": "CH", "VX": "CH",
    "DE": "DE", "F": "DE", "BE": "DE", "DU": "DE", "HM": "DE", "HA": "DE",
    "MU": "DE", "SG": "DE",
    "VI": "AT",
    "L": "UK", "IL": "UK",
    "PA": "FR", "AS": "NL", "MI": "IT", "MC": "ES", "BR": "BE", "IR": "IE",
    "CO": "DK", "ST": "SE", "OL": "NO", "HE": "FI",
    "TO": "CA", "V": "CA", "T": "JP", "HK": "HK", "SI": "SG",
}

# Yahoo-Ländernamen → Kürzel
_COUNTRY_NAMES = {
    "united states": "US", "switzerland": "CH", "germany": "DE", "austria": "AT",
    "united kingdom": "UK", "france": "FR", "netherlands": "NL", "italy": "IT",
    "spain": "ES", "belgium": "BE", "ireland": "IE", "denmark": "DK",
    "sweden": "SE", "norway": "NO", "finland": "FI", "canada": "CA",
    "japan": "JP", "hong kong": "HK", "singapore": "SG",
}

# Unterwährungen (Yahoo liefert Kurse/Dividenden teils in Pence/Cents)
_SUB_CURRENCIES = {"GBp": ("GBP", 0.01), "GBX": ("GBP", 0.01),
                   "ILA": ("ILS", 0.01), "ZAc": ("ZAR", 0.01), "ZAC": ("ZAR", 0.01)}

_CRYPTO_SUFFIXES = ("-USD", "-EUR", "-CHF", "-BTC")

COMMON_CURRENCIES = ["CHF", "USD", "EUR", "GBP", "CAD", "JPY", "SEK", "NOK",
                     "DKK", "AUD", "HKD", "SGD"]


def new_account() -> dict:
    return {
        "version":   ACCOUNT_VERSION,
        "settings":  {"residence": "CH", "w8ben": True, "configured": False},
        "entries":   [],
        "dismissed": [],
        "symbols":   {},
        "fx":        {"base": "", "rates": {}},
    }


def ensure_account(acc) -> dict:
    """Ergänzt fehlende Schlüssel (ältere/leere Daten) – arbeitet in-place."""
    if not isinstance(acc, dict):
        acc = {}
    base = new_account()
    for k, v in base.items():
        if k not in acc or not isinstance(acc[k], type(v)):
            acc[k] = v
    for k, v in base["settings"].items():
        acc["settings"].setdefault(k, v)
    return acc


def normalize_currency(cur):
    """'GBp' → ('GBP', 0.01); 'USD' → ('USD', 1.0)."""
    cur = (cur or "USD").strip()
    if cur in _SUB_CURRENCIES:
        return _SUB_CURRENCIES[cur]
    return cur.upper(), 1.0


def source_country(symbol: str, yahoo_country: str = "") -> str:
    c = _COUNTRY_NAMES.get((yahoo_country or "").strip().lower())
    if c:
        return c
    try:
        from tax_module import country_from_ticker
        return country_from_ticker(symbol)
    except Exception:
        if "." in symbol:
            return _SUFFIX_COUNTRY.get(symbol.rsplit(".", 1)[1].upper(), "")
        return "US"


def _parse_date(s):
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def qty_at_ex(positions, ex_day: date) -> float:
    """Bestand am Ex-Tag: gekauft VOR dem Ex-Tag, nicht vor dem Ex-Tag verkauft."""
    qty = 0.0
    for p in positions or []:
        buy_d = _parse_date(p.get("buy_date", "")) or date(1900, 1, 1)
        sell_d = _parse_date(p.get("sell_date", "")) or date(9999, 12, 31)
        if buy_d < ex_day <= sell_d:
            try:
                qty += float(p.get("quantity", 0) or 0)
            except (TypeError, ValueError):
                pass
    return qty


def earliest_buy(positions) -> date:
    days = [d for d in (_parse_date(p.get("buy_date", "")) for p in positions or []) if d]
    return min(days) if days else date.today() - timedelta(days=365)


def entry_amount(e: dict, net: bool) -> float:
    """Vorzeichenbehafteter Betrag einer Buchung in Kontowährung."""
    t = e.get("type")
    gross = float(e.get("gross", 0) or 0)
    if t == "dividend":
        return gross - float(e.get("tax", 0) or 0) if net else gross
    if t == "withdrawal":
        return -gross
    return gross   # deposit


def balances(acc: dict, net: bool) -> dict:
    """{cur: {"div": brutto, "tax": .., "transfers": .., "balance": ..}}
    "div" ist immer brutto; "balance" je nach Modus brutto oder netto."""
    out = {}
    for e in acc.get("entries", []):
        cur = e.get("currency", "USD")
        b = out.setdefault(cur, {"div": 0.0, "tax": 0.0, "transfers": 0.0, "balance": 0.0})
        amt = entry_amount(e, net)
        if e.get("type") == "dividend":
            b["div"] += float(e.get("gross", 0) or 0)
            b["tax"] += float(e.get("tax", 0) or 0)
        else:
            b["transfers"] += amt
        b["balance"] += amt
    return out


def merge_dividends(acc: dict, computed: dict, portfolio_syms) -> tuple:
    """Überträgt berechnete Dividenden ins Konto.

    computed: {sym: {"currency", "factor", "country",
                     "rows": [(ex_date_str, per_share_raw, qty), ...]}}
    portfolio_syms: Symbole, die aktuell im Portfolio sind.
    Gibt (neu, geändert) zurück.
    """
    settings = acc["settings"]
    residence = settings.get("residence", "CH")
    w8ben = bool(settings.get("w8ben", True))
    dismissed = set(acc.get("dismissed", []))
    by_id = {e["id"]: e for e in acc["entries"] if e.get("id")}
    n_new = n_upd = 0
    wanted_ids = set()

    for sym, info in computed.items():
        cur = info.get("currency") or "USD"
        factor = float(info.get("factor", 1.0) or 1.0)
        rate = div_withholding_rate(info.get("country", ""), residence, w8ben)
        for ex_str, per_share_raw, qty in info.get("rows", []):
            eid = f"div:{sym}:{ex_str}"
            if qty <= 0 or eid in dismissed:
                continue
            wanted_ids.add(eid)
            per_share = float(per_share_raw) * factor
            gross = round(per_share * qty, 4)
            tax = round(gross * rate, 4)
            e = by_id.get(eid)
            if e is None:
                e = {"id": eid, "type": "dividend", "date": ex_str, "currency": cur,
                     "gross": gross, "tax": tax, "rate": rate, "symbol": sym,
                     "qty": qty, "per_share": per_share, "note": "", "edited": False}
                acc["entries"].append(e)
                by_id[eid] = e
                n_new += 1
            elif not e.get("edited"):
                changed = (abs(e.get("gross", 0) - gross) > 1e-6
                           or abs(e.get("tax", 0) - tax) > 1e-6
                           or e.get("currency") != cur)
                e.update({"currency": cur, "gross": gross, "tax": tax, "rate": rate,
                          "qty": qty, "per_share": per_share})
                if changed:
                    n_upd += 1

    # Automatische Dividenden entfernen, die laut Portfolio nicht mehr zustehen
    # (z. B. Kaufdatum korrigiert). Symbole, die ganz aus dem Portfolio
    # verschwunden sind, bleiben erhalten – diese Dividenden wurden ausbezahlt.
    present = set(portfolio_syms)
    keep = []
    for e in acc["entries"]:
        if (e.get("type") == "dividend" and not e.get("edited")
                and e.get("symbol") in computed and e.get("symbol") in present
                and e.get("id") not in wanted_ids):
            n_upd += 1
            continue
        keep.append(e)
    acc["entries"] = keep
    return n_new, n_upd


def recalc_tax(acc: dict) -> None:
    """Quellensteuer nicht manuell geänderter Dividenden neu berechnen."""
    s = acc["settings"]
    for e in acc["entries"]:
        if e.get("type") != "dividend" or e.get("edited"):
            continue
        meta = acc["symbols"].get(e.get("symbol", ""), {})
        rate = div_withholding_rate(meta.get("country", ""), s.get("residence", "CH"),
                                    bool(s.get("w8ben", True)))
        e["rate"] = rate
        e["tax"] = round(float(e.get("gross", 0)) * rate, 4)


# ══════════════════════════════════════════════════════════════════════════════
#  Hintergrund-Abruf
# ══════════════════════════════════════════════════════════════════════════════

_RUNNING_WORKERS = set()   # Referenzen halten, bis der Thread fertig ist

import logging as _logging
_log = _logging.getLogger("StockMonitor")   # gleiche Logdatei wie die App


class _SyncWorker(QThread):
    progress = pyqtSignal(str)
    done = pyqtSignal(dict)

    def __init__(self, positions_by_sym, symbol_meta, currencies, base, known_cur=None):
        super().__init__()
        self._known_cur = known_cur or {}
        self._pos = positions_by_sym
        self._meta = symbol_meta
        self._currencies = set(currencies)
        self._base = base

    def run(self):
        # Gleicher Abrufweg wie die bewährten Dividenden-/Steuer-Funktionen:
        # ticker.history(actions=True) statt ticker.dividends, alle Yahoo-Abfragen
        # nacheinander in DIESEM Thread (curl_cffi ist nicht thread-sicher –
        # Problem v. a. unter Windows).
        result = {"computed": {}, "meta": {}, "fx": {}, "errors": [], "error": ""}
        try:
            import yfinance as yf
            today = date.today()
            syms = sorted(self._pos)
            for i, sym in enumerate(syms, 1):
                if self.isInterruptionRequested():
                    return
                self.progress.emit(T("status_loading", sym=sym, i=i, n=len(syms)))
                positions = self._pos[sym]
                try:
                    tk = yf.Ticker(sym)
                    meta = dict(self._meta.get(sym) or {})
                    if not meta.get("currency"):
                        raw_cur = self._known_cur.get(sym)
                        if not raw_cur:
                            try:
                                raw_cur = getattr(tk.fast_info, "currency", None)
                            except Exception:
                                raw_cur = None
                        meta["currency"], meta["factor"] = normalize_currency(raw_cur or "USD")
                    if not meta.get("country"):
                        try:
                            from tax_module import resolve_country
                            meta["country"] = resolve_country(sym, inline=True)
                        except Exception:
                            _log.warning("Dividendenkonto: Land für %s nicht ermittelt", sym,
                                         exc_info=True)
                            meta["country"] = source_country(sym)
                    result["meta"][sym] = meta

                    start = earliest_buy(positions)
                    hist = tk.history(start=(start - timedelta(days=5)).isoformat(),
                                      interval="1d", auto_adjust=True, actions=True)
                    rows = []
                    if hist is not None and not hist.empty and "Dividends" in hist.columns:
                        divs = hist["Dividends"][hist["Dividends"] > 0]
                        for ts, amount in divs.items():
                            ex_day = ts.date() if hasattr(ts, "date") else _parse_date(ts)
                            if ex_day is None or ex_day <= start or ex_day > today:
                                continue
                            q = qty_at_ex(positions, ex_day)
                            if q > 0 and float(amount) > 0:
                                rows.append((ex_day.isoformat(), float(amount), q))
                    elif hist is None or hist.empty:
                        raise RuntimeError("Yahoo lieferte keine Kursdaten")
                    result["computed"][sym] = {
                        "currency": meta["currency"], "factor": meta.get("factor", 1.0),
                        "country": meta["country"], "rows": rows,
                    }
                    self._currencies.add(meta["currency"])
                except Exception as e:
                    _log.warning("Dividendenkonto: %s fehlgeschlagen: %s", sym, e, exc_info=True)
                    result["errors"].append(sym)
                    if not result.get("first_error"):
                        result["first_error"] = f"{sym}: {e}"

            self.progress.emit(T("status_fx"))
            for cur in sorted(self._currencies):
                if self.isInterruptionRequested():
                    return
                if cur == self._base:
                    result["fx"][cur] = 1.0
                    continue
                pair = f"{cur}{self._base}=X"
                r = 0.0
                try:
                    r = float(yf.Ticker(pair).fast_info.last_price)
                except Exception:
                    try:
                        h = yf.Ticker(pair).history(period="5d", interval="1d")
                        r = float(h["Close"].dropna().iloc[-1])
                    except Exception:
                        _log.warning("Dividendenkonto: Wechselkurs %s fehlt", pair, exc_info=True)
                if r > 0:
                    result["fx"][cur] = r
            _log.info("Dividendenkonto: %d Symbole, %d Fehler, %d Währungen",
                      len(syms), len(result["errors"]), len(result["fx"]))
        except Exception as e:
            _log.error("Dividendenkonto: Abruf abgebrochen", exc_info=True)
            result["error"] = str(e)
        self.done.emit(result)


# ══════════════════════════════════════════════════════════════════════════════
#  UI-Helfer
# ══════════════════════════════════════════════════════════════════════════════

def _fix_win_focus(dialog: QDialog, parent: QWidget) -> None:
    """Windows: beim Schliessen das aufrufende Fenster wieder aktivieren,
    damit Windows den Fokus nicht an den Explorer übergibt."""
    if sys.platform == "win32" and parent is not None:
        def _restore():
            try:
                parent.raise_()
                parent.activateWindow()
            except RuntimeError:
                pass
        dialog.finished.connect(_restore)


def _emoji_font(widget, size=10):
    for name in ("Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji"):
        if name in QFontDatabase.families():
            widget.setFont(QFont(name, size))
            return


def _default_fmt(value, decimals=2):
    s = f"{abs(value):,.{decimals}f}".replace(",", "'")
    return f"-{s}" if value < 0 else s


def _fmt_date(s):
    d = _parse_date(s)
    if d is None:
        return str(s)
    try:
        return _cfg.fmt_date(d) if _cfg else d.strftime("%d.%m.%Y")
    except Exception:
        return d.strftime("%d.%m.%Y")


def _num_item(text, value=None, color=None, bold=False):
    it = QTableWidgetItem(text)
    it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    if value is not None:
        it.setData(Qt.ItemDataRole.UserRole, value)
    if color:
        it.setForeground(QColor(color))
    if bold:
        f = it.font(); f.setBold(True); it.setFont(f)
    return it


def _is_dark() -> bool:
    from PyQt6.QtGui import QPalette
    return QApplication.palette().color(QPalette.ColorRole.Window).lightness() < 128


def _center_on(dlg: QDialog, parent: QWidget, w_frac=0.5, h_frac=0.6):
    screen = ((parent.screen() if parent is not None else None)
              or QApplication.primaryScreen()).availableGeometry()
    w, h = int(screen.width() * w_frac), int(screen.height() * h_frac)
    dlg.resize(w, h)
    dlg.move(screen.x() + (screen.width() - w) // 2, screen.y() + (screen.height() - h) // 2)


def _make_table(headers):
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    t.setAlternatingRowColors(True)
    t.verticalHeader().setVisible(False)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    return t


# ══════════════════════════════════════════════════════════════════════════════
#  Kleine Dialoge
# ══════════════════════════════════════════════════════════════════════════════

class SettingsDialog(QDialog):
    """Steuerwohnsitz + W-8BEN."""

    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        _fix_win_focus(self, parent)
        self.setWindowTitle(T("title_settings"))
        self.setMinimumWidth(460)
        lay = QVBoxLayout(self)
        info = QLabel(T("lbl_settings")); info.setWordWrap(True)
        lay.addWidget(info)
        form = QFormLayout()
        self.res_combo = QComboBox()
        for code in DIV_ACCOUNT_RESIDENCES:
            self.res_combo.addItem(T(f"res_{code}"), code)
        idx = self.res_combo.findData(settings.get("residence", "CH"))
        self.res_combo.setCurrentIndex(max(0, idx))
        form.addRow(T("lbl_residence"), self.res_combo)
        lay.addLayout(form)
        self.w8 = QCheckBox(T("chk_w8ben"))
        self.w8.setChecked(bool(settings.get("w8ben", True)))
        lay.addWidget(self.w8)
        hint = QLabel(T("lbl_settings_hint")); hint.setWordWrap(True)
        hint.setStyleSheet("color:#888; font-size:11px;")
        lay.addWidget(hint)
        self.res_combo.currentIndexChanged.connect(
            lambda _: self.w8.setEnabled(self.res_combo.currentData() != "US"))
        self.w8.setEnabled(self.res_combo.currentData() != "US")
        lay.addLayout(_ok_cancel(self))

    def values(self):
        return {"residence": self.res_combo.currentData(), "w8ben": self.w8.isChecked(),
                "configured": True}


def _ok_cancel(dlg: QDialog):
    row = QHBoxLayout(); row.addStretch()
    ok = QPushButton(T("btn_ok")); ok.setDefault(True); ok.clicked.connect(dlg.accept)
    ca = QPushButton(T("btn_cancel")); ca.clicked.connect(dlg.reject)
    row.addWidget(ok); row.addWidget(ca)
    return row


class BookingDialog(QDialog):
    """Manuelle Ein-/Auszahlung erfassen."""

    def __init__(self, currencies, preset_currency=None, parent=None):
        super().__init__(parent)
        _fix_win_focus(self, parent)
        self.setWindowTitle(T("title_booking"))
        self.setMinimumWidth(420)
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.kind = QComboBox()
        self.kind.addItem(T("type_deposit"), "deposit")
        self.kind.addItem(T("type_withdrawal"), "withdrawal")
        form.addRow(T("lbl_kind"), self.kind)
        self.date = QDateEdit(QDate.currentDate()); self.date.setCalendarPopup(True)
        form.addRow(T("lbl_date"), self.date)
        self.cur = QComboBox(); self.cur.setEditable(True)
        for c in list(dict.fromkeys(list(currencies) + COMMON_CURRENCIES)):
            self.cur.addItem(c)
        if preset_currency:
            self.cur.setCurrentText(preset_currency)
        form.addRow(T("lbl_currency"), self.cur)
        self.amount = QDoubleSpinBox(); self.amount.setRange(0, 1e12); self.amount.setDecimals(2)
        form.addRow(T("lbl_amount"), self.amount)
        self.note = QLineEdit(); self.note.setPlaceholderText(T("ph_note"))
        form.addRow(T("lbl_note"), self.note)
        lay.addLayout(form)
        lay.addLayout(_ok_cancel(self))

    def accept(self):
        if self.amount.value() <= 0:
            QMessageBox.information(self, T("msg_title_info"), T("msg_amount"))
            return
        super().accept()

    def entry(self) -> dict:
        return {"id": "man:" + uuid.uuid4().hex[:12], "type": self.kind.currentData(),
                "date": self.date.date().toString("yyyy-MM-dd"),
                "currency": (self.cur.currentText().strip().upper() or "CHF")[:5],
                "gross": round(self.amount.value(), 2), "tax": 0.0,
                "note": self.note.text().strip(), "edited": True}


class EditDividendDialog(QDialog):
    """Brutto / Quellensteuer / Notiz einer Dividende korrigieren."""

    def __init__(self, entry: dict, parent=None):
        super().__init__(parent)
        _fix_win_focus(self, parent)
        self.setWindowTitle(T("title_edit_div"))
        self.setMinimumWidth(400)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(f"<b>{entry.get('symbol', '')}</b>  –  "
                             f"{_fmt_date(entry.get('date'))}  –  {entry.get('currency', '')}"))
        form = QFormLayout()
        self.gross = QDoubleSpinBox(); self.gross.setRange(0, 1e12); self.gross.setDecimals(2)
        self.gross.setValue(float(entry.get("gross", 0)))
        self.tax = QDoubleSpinBox(); self.tax.setRange(0, 1e12); self.tax.setDecimals(2)
        self.tax.setValue(float(entry.get("tax", 0)))
        self.note = QLineEdit(entry.get("note", ""))
        form.addRow(T("lbl_gross"), self.gross)
        form.addRow(T("lbl_tax"), self.tax)
        form.addRow(T("lbl_note"), self.note)
        lay.addLayout(form)
        lay.addLayout(_ok_cancel(self))

    def accept(self):
        if self.tax.value() > self.gross.value() + 1e-9:
            QMessageBox.information(self, T("msg_title_info"), T("msg_tax_too_high"))
            return
        super().accept()

    def apply(self, entry: dict):
        entry["gross"] = round(self.gross.value(), 2)
        entry["tax"] = round(self.tax.value(), 2)
        entry["note"] = self.note.text().strip()
        entry["edited"] = True


# ══════════════════════════════════════════════════════════════════════════════
#  Buchungen eines Währungskontos
# ══════════════════════════════════════════════════════════════════════════════

class EntriesDialog(QDialog):

    def __init__(self, owner: "DividendAccountDialog", currency: str):
        super().__init__(owner)
        _fix_win_focus(self, owner)
        self._owner = owner
        self._cur = currency
        self.setWindowTitle(T("title_entries", cur=currency))
        _center_on(self, owner, 0.6, 0.65)

        lay = QVBoxLayout(self)
        ctrl = QHBoxLayout()
        self.btn_add = QPushButton(T("btn_booking")); _emoji_font(self.btn_add)
        self.btn_edit = QPushButton(T("btn_edit")); _emoji_font(self.btn_edit)
        self.btn_del = QPushButton(T("btn_delete")); _emoji_font(self.btn_del)
        for b in (self.btn_add, self.btn_edit, self.btn_del):
            ctrl.addWidget(b)
        ctrl.addStretch()
        if owner._export_factory:
            ctrl.addWidget(owner._export_factory(self._export_data, T("export_title_cur", cur=currency)))
        close = QPushButton(T("btn_close")); close.clicked.connect(self.close)
        ctrl.addWidget(close)
        lay.addLayout(ctrl)

        self.table = _make_table([
            T("col_date"), T("col_type"), T("col_symbol"), T("col_qty"),
            T("col_per_share"), T("col_gross"), T("col_tax"), T("col_net"),
            T("col_balance"), T("col_note")])
        self.table.doubleClicked.connect(lambda _: self._edit())
        lay.addWidget(self.table, stretch=1)
        self.sum_label = QLabel()
        self.sum_label.setStyleSheet("font-weight:bold; padding:4px;")
        lay.addWidget(self.sum_label)

        self.btn_add.clicked.connect(self._add)
        self.btn_edit.clicked.connect(self._edit)
        self.btn_del.clicked.connect(self._delete)
        self.refresh()

    # ── Daten ─────────────────────────────────────────────────────────────
    def _entries(self):
        es = [e for e in self._owner.account["entries"] if e.get("currency") == self._cur]
        return sorted(es, key=lambda e: (e.get("date", ""), e.get("id", "")))

    def _rows(self):
        """Chronologisch mit laufendem Saldo, Anzeige neueste zuerst."""
        net = self._owner.net_mode
        bal = 0.0
        rows = []
        for e in self._entries():
            bal += entry_amount(e, net)
            rows.append((e, bal))
        rows.reverse()
        return rows

    def refresh(self):
        fmt = self._owner._fmt
        neg = "#e74c3c" if _is_dark() else "#c0392b"
        rows = self._rows()
        self.table.setRowCount(len(rows))
        for r, (e, bal) in enumerate(rows):
            t = e.get("type")
            is_div = t == "dividend"
            gross = float(e.get("gross", 0))
            tax = float(e.get("tax", 0)) if is_div else 0.0
            signed_gross = -gross if t == "withdrawal" else gross
            date_it = QTableWidgetItem(_fmt_date(e.get("date")))
            date_it.setData(Qt.ItemDataRole.UserRole, e.get("id"))
            type_txt = T(f"type_{t}")
            if is_div and e.get("edited"):
                type_txt += " ✏"
            type_it = QTableWidgetItem(type_txt)
            if is_div and e.get("edited"):
                type_it.setToolTip(T("tip_edited"))
            self.table.setItem(r, 0, date_it)
            self.table.setItem(r, 1, type_it)
            self.table.setItem(r, 2, QTableWidgetItem(e.get("symbol", "") if is_div else ""))
            self.table.setItem(r, 3, _num_item(fmt(e.get("qty", 0), 4).rstrip("0").rstrip(".,")
                                               if is_div and e.get("qty") else ""))
            self.table.setItem(r, 4, _num_item(fmt(e.get("per_share", 0), 4)
                                               if is_div and e.get("per_share") else ""))
            self.table.setItem(r, 5, _num_item(fmt(signed_gross), color=neg if signed_gross < 0 else None))
            self.table.setItem(r, 6, _num_item(fmt(-tax) if tax else ""))
            net_amt = signed_gross - tax
            self.table.setItem(r, 7, _num_item(fmt(net_amt), color=neg if net_amt < 0 else None))
            self.table.setItem(r, 8, _num_item(fmt(bal), bold=True, color=neg if bal < 0 else None))
            self.table.setItem(r, 9, QTableWidgetItem(e.get("note", "")))
        total = rows[0][1] if rows else 0.0
        mode = T("lbl_mode_net") if self._owner.net_mode else T("lbl_mode_gross")
        self.sum_label.setText(T("lbl_entries_sum", n=len(rows), mode=mode,
                                 cur=self._cur, amount=fmt(total)))

    def _export_data(self):
        headers = [self.table.horizontalHeaderItem(c).text() for c in range(self.table.columnCount())]
        rows = []
        for r in range(self.table.rowCount()):
            rows.append(tuple((self.table.item(r, c).text() if self.table.item(r, c) else "")
                              for c in range(self.table.columnCount())))
        return {"title": T("export_title_cur", cur=self._cur), "headers": headers, "rows": rows}

    def _selected(self):
        r = self.table.currentRow()
        if r < 0:
            QMessageBox.information(self, T("msg_title_info"), T("msg_select"))
            return None
        eid = self.table.item(r, 0).data(Qt.ItemDataRole.UserRole)
        return next((e for e in self._owner.account["entries"] if e.get("id") == eid), None)

    # ── Aktionen ──────────────────────────────────────────────────────────
    def _add(self):
        dlg = BookingDialog(self._owner.currencies(), self._cur, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._owner.account["entries"].append(dlg.entry())
            self._owner.changed()
            self.refresh()

    def _edit(self):
        e = self._selected()
        if e is None:
            return
        if e.get("type") != "dividend":
            QMessageBox.information(self, T("msg_title_info"), T("msg_no_edit"))
            return
        dlg = EditDividendDialog(e, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            dlg.apply(e)
            self._owner.changed()
            self.refresh()

    def _delete(self):
        e = self._selected()
        if e is None:
            return
        desc = f"{_fmt_date(e.get('date'))}  {T('type_' + e.get('type', 'deposit'))}  " \
               f"{e.get('symbol', '')}  {e.get('currency', '')} {self._owner._fmt(float(e.get('gross', 0)))}"
        msg = T("msg_delete", desc=desc)
        is_auto = str(e.get("id", "")).startswith("div:")
        if is_auto:
            msg += T("msg_delete_auto")
        if QMessageBox.question(self, T("title_delete"), msg,
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        acc = self._owner.account
        acc["entries"] = [x for x in acc["entries"] if x is not e]
        if is_auto and e["id"] not in acc["dismissed"]:
            acc["dismissed"].append(e["id"])
        self._owner.changed()
        self.refresh()


# ══════════════════════════════════════════════════════════════════════════════
#  Hauptfenster: Kontoübersicht
# ══════════════════════════════════════════════════════════════════════════════

class DividendAccountDialog(QDialog):
    """Mehrwährungs-Dividendenkonto.

    portfolio_data: {sym: [positions]}  (wird nur gelesen)
    account:        dict aus dem Portfolio (wird in-place geändert)
    save_fn:        wird nach jeder Änderung aufgerufen (Portfolio speichern)
    base_currency:  Portfolio-Währung für den Gesamtsaldo
    fmt_fn:         Zahlenformatierung der App (CH/DE/US)
    export_factory: fn(get_data_fn, title) -> QPushButton (Export PDF/XLSX/ODS)
    skip_fn:        fn(sym) -> True für Symbole ohne Dividenden (Krypto, Rohstoffe)
    """

    def __init__(self, portfolio_data, account, save_fn, parent=None,
                 base_currency="USD", fmt_fn=None, export_factory=None, skip_fn=None,
                 price_cache=None, before_fetch=None):
        super().__init__(parent)
        self._known_cur = {s: d.get("cur") for s, d in (price_cache or {}).items()
                           if isinstance(d, dict) and d.get("cur")}
        self._before_fetch = before_fetch
        _fix_win_focus(self, parent)
        self._portfolio = portfolio_data or {}
        self.account = ensure_account(account)
        self._save_fn = save_fn
        self._base = base_currency or "USD"
        self._fmt = fmt_fn or _default_fmt
        self._export_factory = export_factory
        self._skip = skip_fn or (lambda s: s.upper().endswith(_CRYPTO_SUFFIXES) or "=" in s)
        self._worker = None
        self._entries_dlg = None
        self.net_mode = True

        fx = self.account.get("fx", {})
        self._fx = dict(fx.get("rates", {})) if fx.get("base") == self._base else {}
        self._fx[self._base] = 1.0

        self.setWindowTitle(T("title"))
        _center_on(self, parent, 0.5, 0.55)
        self._build()
        self.refresh()
        self.finished.connect(self._stop_worker)

        if not self.account["settings"].get("configured"):
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, self._first_run)
        else:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, self.start_sync)

    # ── Aufbau ────────────────────────────────────────────────────────────
    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        info = QLabel(T("info")); info.setWordWrap(True)
        bg = "#0d2a3d" if _is_dark() else "#EBF5FB"
        info.setStyleSheet(f"background:{bg}; border-radius:6px; padding:8px 14px; font-size:12px;")
        lay.addWidget(info)

        ctrl = QHBoxLayout()
        self.btn_mode = QPushButton(T("btn_net"))
        self.btn_mode.setCheckable(True); self.btn_mode.setChecked(True)
        self.btn_mode.setToolTip(T("tip_net_gross"))
        self.btn_mode.setMinimumWidth(90)
        self.btn_mode.toggled.connect(self._toggle_mode)
        ctrl.addWidget(self.btn_mode)
        self.btn_refresh = QPushButton(T("btn_refresh")); _emoji_font(self.btn_refresh)
        self.btn_refresh.setToolTip(T("tip_refresh"))
        self.btn_refresh.clicked.connect(self.start_sync)
        ctrl.addWidget(self.btn_refresh)
        btn_book = QPushButton(T("btn_booking")); _emoji_font(btn_book)
        btn_book.clicked.connect(self._add_booking)
        ctrl.addWidget(btn_book)
        btn_set = QPushButton(T("btn_settings")); _emoji_font(btn_set)
        btn_set.clicked.connect(self._settings)
        ctrl.addWidget(btn_set)
        ctrl.addStretch()
        btn_open = QPushButton(T("btn_open")); _emoji_font(btn_open)
        btn_open.clicked.connect(self._open_selected)
        ctrl.addWidget(btn_open)
        if self._export_factory:
            ctrl.addWidget(self._export_factory(self._export_data, T("export_title")))
        btn_close = QPushButton(T("btn_close")); btn_close.clicked.connect(self.close)
        ctrl.addWidget(btn_close)
        lay.addLayout(ctrl)

        self.status = QLabel("")
        self.status.setStyleSheet("color:#888; font-size:11px;")
        lay.addWidget(self.status)

        self.table = _make_table([
            T("col_currency"), T("col_dividends"), T("col_tax"), T("col_transfers"),
            T("col_balance"), T("col_balance_base", cur=self._base)])
        self.table.doubleClicked.connect(lambda _: self._open_selected())
        lay.addWidget(self.table, stretch=1)

        self.empty_label = QLabel(T("lbl_empty")); self.empty_label.setWordWrap(True)
        self.empty_label.setStyleSheet("color:#888; padding:6px;")
        lay.addWidget(self.empty_label)

        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-size:15px; font-weight:bold; padding:6px 2px;")
        lay.addWidget(self.total_label)
        self.fx_label = QLabel(); self.fx_label.setWordWrap(True)
        self.fx_label.setStyleSheet("color:#888; font-size:11px;")
        lay.addWidget(self.fx_label)
        self._build_overlay()

    # ── Lade-Overlay (Dollarnote, wie im Dividendenfenster) ──────────────
    _NOTES = ("💵", "💴", "💶", "💷")

    def _build_overlay(self):
        ov = QFrame(self)
        ov.setStyleSheet("QFrame { background:rgba(240,248,255,235); "
                         "border:2px solid #3498db; border-radius:14px; }")
        v = QVBoxLayout(ov)
        v.setAlignment(Qt.AlignmentFlag.AlignCenter); v.setSpacing(6)
        self._ov_icon = QLabel(self._NOTES[0])
        fam = next((f for f in ("Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji")
                    if f in QFontDatabase.families()), "Arial")
        self._ov_icon.setFont(QFont(fam, 52))
        self._ov_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ov_icon.setStyleSheet("border:none; background:transparent;")
        v.addWidget(self._ov_icon)
        self._ov_title = QLabel(T("overlay_title"))
        self._ov_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self._ov_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ov_title.setStyleSheet("color:#2c3e50; border:none; background:transparent;")
        v.addWidget(self._ov_title)
        self._ov_sub = QLabel("")
        self._ov_sub.setFont(QFont("Arial", 9))
        self._ov_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ov_sub.setStyleSheet("color:#666; border:none; background:transparent;")
        v.addWidget(self._ov_sub)
        ov.hide()
        self._overlay = ov
        self._ov_idx = 0
        self._ov_timer = QTimer(self)
        self._ov_timer.setInterval(400)
        self._ov_timer.timeout.connect(self._rotate_note)

    def _rotate_note(self):
        self._ov_idx = (self._ov_idx + 1) % len(self._NOTES)
        self._ov_icon.setText(self._NOTES[self._ov_idx])

    def _place_overlay(self):
        w, h = 390, 220
        self._overlay.setGeometry((self.width() - w) // 2, (self.height() - h) // 2, w, h)

    def _show_overlay(self, show):
        try:
            if show:
                self._ov_sub.setText("")
                self._place_overlay()
                self._overlay.show(); self._overlay.raise_()
                self._ov_timer.start()
            else:
                self._ov_timer.stop()
                self._overlay.hide()
        except RuntimeError:
            pass

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        if getattr(self, "_overlay", None) is not None and self._overlay.isVisible():
            self._place_overlay()

    # ── Anzeige ───────────────────────────────────────────────────────────
    def currencies(self):
        return sorted({e.get("currency", "USD") for e in self.account["entries"]})

    def refresh(self):
        fmt = self._fmt
        neg = "#e74c3c" if _is_dark() else "#c0392b"
        bals = balances(self.account, self.net_mode)
        curs = sorted(bals, key=lambda c: (c != self._base, c))
        self.table.setRowCount(len(curs))
        total = 0.0
        missing = []
        for r, cur in enumerate(curs):
            b = bals[cur]
            cur_it = QTableWidgetItem(cur)
            f = cur_it.font(); f.setBold(True); cur_it.setFont(f)
            self.table.setItem(r, 0, cur_it)
            self.table.setItem(r, 1, _num_item(fmt(b["div"])))
            self.table.setItem(r, 2, _num_item(fmt(-b["tax"]) if b["tax"] and self.net_mode else ""))
            self.table.setItem(r, 3, _num_item(fmt(b["transfers"]) if b["transfers"] else "",
                                               color=neg if b["transfers"] < 0 else None))
            self.table.setItem(r, 4, _num_item(fmt(b["balance"]), bold=True,
                                               color=neg if b["balance"] < 0 else None))
            rate = self._fx.get(cur)
            if rate:
                conv = b["balance"] * rate
                total += conv
                self.table.setItem(r, 5, _num_item(fmt(conv), color=neg if conv < 0 else None))
            else:
                missing.append(cur)
                self.table.setItem(r, 5, _num_item("–"))
        self.empty_label.setVisible(not curs)
        mode = T("lbl_mode_net") if self.net_mode else T("lbl_mode_gross")
        self.total_label.setText(T("lbl_total", mode=mode, cur=self._base, amount=fmt(total)))
        note = T("lbl_fx_note") if any(c != self._base for c in curs) else ""
        if missing:
            note = (note + " " if note else "") + T("lbl_fx_missing", curs=", ".join(missing))
        self.fx_label.setText(note)
        if self._entries_dlg is not None:
            try:
                self._entries_dlg.refresh()
            except RuntimeError:
                self._entries_dlg = None

    def _toggle_mode(self, checked):
        self.net_mode = checked
        self.btn_mode.setText(T("btn_net") if checked else T("btn_gross"))
        self.refresh()

    def changed(self):
        """Nach jeder Änderung: speichern + Übersicht neu zeichnen."""
        try:
            if self._save_fn:
                self._save_fn()
        except Exception as e:
            QMessageBox.warning(self, T("msg_title_error"), str(e))
        self.refresh()

    def _export_data(self):
        headers = [self.table.horizontalHeaderItem(c).text() for c in range(self.table.columnCount())]
        rows = [tuple((self.table.item(r, c).text() if self.table.item(r, c) else "")
                      for c in range(self.table.columnCount()))
                for r in range(self.table.rowCount())]
        rows.append(("", "", "", "", "", self.total_label.text()))
        return {"title": T("export_title"), "headers": headers, "rows": rows}

    # ── Aktionen ──────────────────────────────────────────────────────────
    def _open_selected(self):
        r = self.table.currentRow()
        if r < 0:
            if self.table.rowCount() == 0:
                return
            r = 0
        cur = self.table.item(r, 0).text()
        dlg = EntriesDialog(self, cur)
        self._entries_dlg = dlg
        dlg.exec()
        self._entries_dlg = None
        self.refresh()

    def _add_booking(self):
        r = self.table.currentRow()
        preset = self.table.item(r, 0).text() if r >= 0 else self._base
        dlg = BookingDialog(self.currencies(), preset, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.account["entries"].append(dlg.entry())
            self.changed()

    def _settings(self):
        dlg = SettingsDialog(self.account["settings"], self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.account["settings"].update(dlg.values())
            recalc_tax(self.account)
            self.changed()
            return True
        return False

    def _first_run(self):
        self._settings()
        if not self.account["settings"].get("configured"):
            # Abgebrochen: mit Standardwerten weiterarbeiten, beim nächsten Mal erneut fragen
            pass
        self.start_sync()

    # ── Synchronisation ───────────────────────────────────────────────────
    def start_sync(self):
        if self._worker is not None and self._worker.isRunning():
            return
        positions = {s: copy.deepcopy(p) for s, p in self._portfolio.items()
                     if p and not self._skip(s)}
        curs = set(self.currencies())
        if self._before_fetch:
            try:
                self._before_fetch()      # z. B. laufende Chart-Worker anhalten
            except Exception:
                pass
        w = _SyncWorker(positions, copy.deepcopy(self.account["symbols"]), curs, self._base,
                        known_cur=self._known_cur)
        w.progress.connect(self._on_progress)
        w.done.connect(self._on_done)
        _RUNNING_WORKERS.add(w)
        w.finished.connect(lambda w=w: _RUNNING_WORKERS.discard(w))
        self._worker = w
        self.btn_refresh.setEnabled(False)
        self._show_overlay(True)
        w.start()

    def _on_progress(self, msg):
        try:
            self.status.setText(msg)
            self._ov_sub.setText(msg)
        except RuntimeError:
            pass

    def _on_done(self, result):
        self._show_overlay(False)
        try:
            self.btn_refresh.setEnabled(True)
        except RuntimeError:
            return
        self._worker = None
        if result.get("error"):
            self.status.setText(T("status_failed", e=result["error"]))
            return
        self.account["symbols"].update(result.get("meta", {}))
        n_new, n_upd = merge_dividends(self.account, result.get("computed", {}),
                                       [s for s in self._portfolio if not self._skip(s)])
        if result.get("fx"):
            self._fx.update(result["fx"])
            self.account["fx"] = {"base": self._base,
                                  "rates": {k: v for k, v in self._fx.items()}}
        msg = T("status_done", new=n_new, upd=n_upd)
        if result.get("errors"):
            msg += "  │  " + T("status_errors", syms=", ".join(result["errors"]))
            if result.get("first_error"):
                msg += "  (" + result["first_error"][:160] + ")"
        self.status.setText(msg)
        self.changed()

    def _stop_worker(self, *_):
        self._show_overlay(False)
        w = self._worker
        if w is not None and w.isRunning():
            try:
                w.progress.disconnect(); w.done.disconnect()
            except Exception:
                pass
            w.requestInterruption()
        self._worker = None
