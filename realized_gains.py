#!/usr/bin/env python3
"""
realized_gains.py – Realisierte Gewinne für Stock Monitor
==========================================================
Wertet die Verkaufshistorie (``_closed_positions`` im Portfolio) aus:
je verkauftem Lot Kauf-/Verkaufskurs, Stück, Haltedauer und Gewinn in
Handelswährung und in der Portfoliowährung, dazu Jahressummen und der
Gesamtertrag (Kursgewinne + Dividenden aus dem Dividendenkonto).

Datenquelle je Verkaufs-Lot (Felder siehe ``PortfolioDialog._record_sale``):
  buy_date, buy_price, quantity, sell_date, [sell_price], [hist_fx_to_chf],
  [fees, net_cost, net_cur, acct_amount, acct_cur]            ← Kauf (Bank-CSV)
  [sell_fees, net_proceeds, sell_net_cur, sell_acct_amount, sell_acct_cur]
                                                              ← Verkauf (Bank-CSV)

Rangfolge der Berechnung (genaueste Quelle zuerst):
  Handelswährung: Nettobeträge der Bank > Kurs × Stück (± bekannte Gebühren)
  Portfoliowährung: Betrag in Kontowährung (Bank) > hist_fx_to_chf (nur CHF)
                    > Yahoo-Wechselkurs am Kauf- bzw. Verkaufstag
Fehlt der Verkaufskurs (ältere Verkäufe), wird der Yahoo-Schlusskurs am
Verkaufstag verwendet und mit „≈“ markiert; er wird NICHT gespeichert, bis der
Nutzer ihn per Doppelklick bestätigt/korrigiert.

Die Berechnung (``compute_rows``, ``summarize``) ist ohne Qt testbar.
"""

from __future__ import annotations

import bisect
import logging as _logging
import sys
from datetime import date, datetime, timedelta

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontDatabase
from PyQt6.QtWidgets import (
    QAbstractItemView, QApplication, QComboBox, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFrame, QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from realized_gains_translations import T

try:
    import config as _cfg
except ImportError:                                 # pragma: no cover
    _cfg = None

_log = _logging.getLogger("StockMonitor")
_RUNNING_WORKERS = set()

# Unterwährungen (Yahoo notiert London in Pence)
_SUB_CURRENCIES = {"GBp": ("GBP", 0.01), "GBX": ("GBP", 0.01),
                   "ZAc": ("ZAR", 0.01), "ILA": ("ILS", 0.01)}

# Sitzungs-Cache: Wechselkurse (cur, base) → sortierte [(iso, rate)], Kurse (sym, iso) → price
_FX_CACHE: dict = {}
_PRICE_CACHE: dict = {}
_CUR_CACHE: dict = {}       # sym → Yahoo-Währung (Sitzung)


def normalize_currency(cur):
    """'GBp' → ('GBP', 0.01); 'USD' → ('USD', 1.0)."""
    cur = (cur or "USD").strip()
    if cur in _SUB_CURRENCIES:
        return _SUB_CURRENCIES[cur]
    return cur.upper(), 1.0


def _parse_date(s):
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _num(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return 0.0
    return v if v == v else 0.0   # NaN → 0


# ══════════════════════════════════════════════════════════════════════════════
#  Berechnung (ohne Qt)
# ══════════════════════════════════════════════════════════════════════════════

def fx_lookup(series, day_iso):
    """Kurs am Tag oder am letzten Handelstag davor (sonst der erste danach)."""
    if not series:
        return None
    keys = [d for d, _ in series]
    i = bisect.bisect_right(keys, day_iso)
    if i > 0:
        return series[i - 1][1]
    return series[0][1]


def iter_sales(closed):
    """(sym, rec) für alle Verkaufs-Lots mit Verkaufsdatum."""
    for sym, lots in (closed or {}).items():
        for rec in lots or []:
            if isinstance(rec, dict) and rec.get("sell_date") and _num(rec.get("quantity")) > 0:
                yield sym, rec


def compute_rows(closed, base, sym_cur, fx_series, est_prices=None):
    """Berechnet eine Zeile je Verkaufs-Lot.

    sym_cur:    {sym: Yahoo-Währung roh, z. B. 'GBp'}
    fx_series:  {(cur, base): [(iso, rate), …]}  (cur → base)
    est_prices: {(sym, sell_iso): Schlusskurs}   (Ersatz für fehlenden sell_price)
    """
    est_prices = est_prices or {}
    base = (base or "USD").upper()
    rows = []

    def rate(cur, day):
        if not cur or cur == base:
            return 1.0
        return fx_lookup(fx_series.get((cur, base)), day)

    for sym, rec in iter_sales(closed):
        qty = _num(rec.get("quantity"))
        buy_d, sell_d = str(rec.get("buy_date", ""))[:10], str(rec.get("sell_date"))[:10]
        raw_cur = sym_cur.get(sym)
        cur, f = normalize_currency(raw_cur) if raw_cur else (None, 1.0)
        buy_price = _num(rec.get("buy_price"))
        sell_price = _num(rec.get("sell_price"))
        est = False
        if not sell_price and (sym, sell_d) in est_prices:
            sell_price = _num(est_prices[(sym, sell_d)])
            est = sell_price > 0

        net_cur = (rec.get("net_cur") or "").upper()
        sell_net_cur = (rec.get("sell_net_cur") or "").upper()
        # Ohne bekannte Yahoo-Währung: Währung aus der Bank-CSV übernehmen
        if cur is None and (net_cur or sell_net_cur):
            cur = net_cur or sell_net_cur

        # ── Handelswährung ────────────────────────────────────────────────
        cost_cur = None
        if cur:
            if _num(rec.get("net_cost")) and net_cur == cur:
                cost_cur = _num(rec["net_cost"])
            else:
                cost_cur = buy_price * qty * f
                if _num(rec.get("fees")) and net_cur == cur:
                    cost_cur += _num(rec["fees"])
        proceeds_cur = None
        if cur:
            if _num(rec.get("net_proceeds")) and sell_net_cur == cur:
                proceeds_cur = _num(rec["net_proceeds"])
            elif sell_price:
                proceeds_cur = sell_price * qty * f
                if _num(rec.get("sell_fees")) and sell_net_cur == cur:
                    proceeds_cur -= _num(rec["sell_fees"])
        bank = bool(_num(rec.get("net_cost")) and _num(rec.get("net_proceeds")))

        # ── Portfoliowährung ──────────────────────────────────────────────
        cost_base = None
        acct_cur = (rec.get("acct_cur") or "").upper()
        if _num(rec.get("acct_amount")) and acct_cur:
            r = rate(acct_cur, buy_d)
            cost_base = _num(rec["acct_amount"]) * r if r else None
        elif cost_cur is not None:
            hfx = _num(rec.get("hist_fx_to_chf"))
            if base == "CHF" and hfx > 0:
                cost_base = cost_cur * hfx / f          # hist_fx gilt je Roh-Einheit
            else:
                r = rate(cur, buy_d)
                cost_base = cost_cur * r if r else None
        proceeds_base = None
        s_acct_cur = (rec.get("sell_acct_cur") or "").upper()
        if _num(rec.get("sell_acct_amount")) and s_acct_cur:
            r = rate(s_acct_cur, sell_d)
            proceeds_base = _num(rec["sell_acct_amount"]) * r if r else None
        elif proceeds_cur is not None:
            r = rate(cur, sell_d)
            proceeds_base = proceeds_cur * r if r else None

        gain_cur = (proceeds_cur - cost_cur
                    if proceeds_cur is not None and cost_cur is not None else None)
        gain_base = (proceeds_base - cost_base
                     if proceeds_base is not None and cost_base is not None else None)
        pct = (gain_base / cost_base * 100 if gain_base is not None and cost_base
               else (gain_cur / cost_cur * 100 if gain_cur is not None and cost_cur else None))
        bd, sd = _parse_date(buy_d), _parse_date(sell_d)
        rows.append({
            "sym": sym, "rec": rec, "buy_date": buy_d, "sell_date": sell_d,
            "year": sell_d[:4], "qty": qty, "cur": cur, "raw_cur": raw_cur or cur,
            "buy_price": buy_price, "sell_price": sell_price or None, "est": est,
            "days": (sd - bd).days if bd and sd else None,
            "cost_cur": cost_cur, "proceeds_cur": proceeds_cur, "gain_cur": gain_cur,
            "cost_base": cost_base, "proceeds_base": proceeds_base, "gain_base": gain_base,
            "pct": pct, "bank": bank, "staking": bool(rec.get("staking")),
        })
    rows.sort(key=lambda r: (r["sell_date"], r["sym"]), reverse=True)
    return rows


def summarize(rows, year=None):
    """Summen in Portfoliowährung (nur Zeilen mit vollständigem Ergebnis)."""
    sel = [r for r in rows if year is None or r["year"] == year]
    ok = [r for r in sel if r["gain_base"] is not None]
    gains = sum(r["gain_base"] for r in ok if r["gain_base"] > 0)
    losses = sum(r["gain_base"] for r in ok if r["gain_base"] < 0)
    return {"total": gains + losses, "gains": gains, "losses": losses,
            "n": len(sel), "missing": len(sel) - len(ok)}


def _account_entries(account):
    """Buchungen wie in der Konto-Ansicht „Alles“ (Bankdividenden haben im
    CSV-Zeitraum Vorrang vor der Yahoo-Berechnung)."""
    try:
        import dividend_account as _da
        return _da.view_entries(_da.ensure_account(account), _da.VIEW_ALL)
    except Exception:
        return list((account or {}).get("entries", []))


def _sum_entries(account, base, fx_series, year, pick):
    sel = [e for e in _account_entries(account) if pick(e)]
    if not sel:
        return None
    base = (base or "USD").upper()
    total = 0.0
    for e in sel:
        d = str(e.get("date", ""))[:10]
        if year is not None and d[:4] != year:
            continue
        cur = (e.get("currency") or base).upper()
        amt = _num(e.get("gross")) - _num(e.get("tax"))
        r = 1.0 if cur == base else fx_lookup(fx_series.get((cur, base)), d)
        if r:
            total += amt * r
    return total


def dividend_amounts(account, base, fx_series, year=None):
    """[(brutto, Quellensteuer)] der Dividenden in Portfoliowährung (für die
    Steuerschätzung „nach Steuern“)."""
    base = (base or "USD").upper()
    out = []
    for e in _account_entries(account):
        if not (e.get("type") == "dividend"
                or (e.get("type") == "bank" and e.get("kind") == "dividend")):
            continue
        d = str(e.get("date", ""))[:10]
        if year is not None and d[:4] != year:
            continue
        cur = (e.get("currency") or base).upper()
        r = 1.0 if cur == base else fx_lookup(fx_series.get((cur, base)), d)
        if r:
            out.append((_num(e.get("gross")) * r, _num(e.get("tax")) * r))
    return out


def after_tax(rows, account, base, fx_series, year=None):
    """Geschätzte Steuern (Summe über die Jahre bei year=None) oder None.
    Gibt (residence, ergebnis|None) zurück."""
    residence = str(((account or {}).get("settings") or {}).get("residence") or "CH").upper()
    try:
        import tax_module as _tm
    except Exception:
        return residence, None
    years = sorted({r["year"] for r in rows}) if year is None else [year]
    if year is None:
        years = sorted(set(years) | {str(e.get("date", ""))[:4]
                                     for e in _account_entries(account)
                                     if e.get("type") in ("dividend", "bank")})
    base = (base or "USD").upper()

    acc_fx = (account or {}).get("fx") or {}

    def fx_to_base(cur):
        r = fx_lookup(fx_series.get((cur, base)), date.today().isoformat())
        if not r and str(acc_fx.get("base", "")).upper() == base:
            r = (acc_fx.get("rates") or {}).get(cur)    # aktuelle Kurse des Dividendenkontos
        return r
    total = None
    for y in [y for y in years if y]:
        res = _tm.after_tax_estimate(
            residence, _tm.compact_gain_rows([r for r in rows if r["year"] == y]),
            dividend_amounts(account, base, fx_series, y), base, fx_to_base)
        if res is None:
            return residence, None
        if total is None:
            total = dict(res)
        else:
            for k in ("tax", "gain_tax", "div_tax"):
                total[k] += res[k]
            total["allow_ignored"] = total["allow_ignored"] or res["allow_ignored"]
    return residence, total


def dividends_net(account, base, fx_series, year=None):
    """Netto-Dividenden in Portfoliowährung (None: noch keine Dividenden)."""
    return _sum_entries(account, base, fx_series, year,
                        lambda e: e.get("type") == "dividend"
                        or (e.get("type") == "bank" and e.get("kind") == "dividend"))


def costs_net(account, base, fx_series, year=None):
    """Zinsen (v. a. Lombardkredit) und Gebühren laut Bank, negativ = Kosten.
    None, wenn keine Bankbuchungen importiert wurden."""
    return _sum_entries(account, base, fx_series, year,
                        lambda e: e.get("type") == "bank"
                        and e.get("kind") in ("interest", "fee"))


def needed_fx(closed, base, sym_cur, account=None):
    """Welche Währungen (→ base) werden für welchen Zeitraum gebraucht?
    {cur: (min_iso, max_iso)}"""
    base = (base or "USD").upper()
    need = {}

    def add(cur, d):
        cur = (cur or "").upper()
        if not cur or cur == base or not d:
            return
        lo, hi = need.get(cur, (d, d))
        need[cur] = (min(lo, d), max(hi, d))

    for sym, rec in iter_sales(closed):
        raw = sym_cur.get(sym)
        cur = normalize_currency(raw)[0] if raw else (rec.get("net_cur") or "")
        bd, sd = str(rec.get("buy_date", ""))[:10], str(rec["sell_date"])[:10]
        add(rec.get("acct_cur") or cur, bd)
        add(rec.get("sell_acct_cur") or cur, sd)
        if not (rec.get("acct_cur") and rec.get("sell_acct_cur")):
            add(cur, bd); add(cur, sd)
    for e in (account or {}).get("entries", []):
        if e.get("type") == "dividend" or (e.get("type") == "bank"
                                           and e.get("kind") in ("dividend", "interest", "fee")):
            add(e.get("currency"), str(e.get("date", ""))[:10])
    return need


# ══════════════════════════════════════════════════════════════════════════════
#  Yahoo-Abruf (eigener Thread, alles nacheinander – curl_cffi ist nicht thread-sicher)
# ══════════════════════════════════════════════════════════════════════════════

class _FetchWorker(QThread):
    progress = pyqtSignal(str)
    done = pyqtSignal(dict)

    def __init__(self, cur_syms, price_jobs, fx_jobs, base):
        super().__init__()
        self._cur_syms = cur_syms          # [sym] ohne bekannte Währung
        self._price_jobs = price_jobs      # {sym: [sell_iso, …]}
        self._fx_jobs = fx_jobs            # {cur: (min_iso, max_iso)}
        self._base = base

    def run(self):
        res = fetch_data(self._cur_syms, self._price_jobs, self._fx_jobs, self._base,
                         progress=self.progress.emit,
                         interrupted=self.isInterruptionRequested)
        if res is not None:
            self.done.emit(res)


def fetch_data(cur_syms, price_jobs, fx_jobs, base, progress=None, interrupted=None):
    """Lädt Handelswährungen, Ersatz-Schlusskurse und Wechselkurse nacheinander.
    Gibt {"cur", "prices", "fx", "errors", "error"} zurück (None bei Abbruch).
    Wird vom _FetchWorker und vom Steuerauszug (tax_module) verwendet."""
    progress = progress or (lambda _msg: None)
    interrupted = interrupted or (lambda: False)
    res = {"cur": {}, "prices": {}, "fx": {}, "errors": [], "error": ""}
    try:
        import yfinance as yf
        for sym in cur_syms:
            if interrupted():
                return None
            progress(T("status_cur", sym=sym))
            try:
                c = getattr(yf.Ticker(sym).fast_info, "currency", None)
                if c:
                    res["cur"][sym] = c
            except Exception:
                res["errors"].append(sym)
        n = len(price_jobs)
        for i, (sym, days) in enumerate(sorted(price_jobs.items()), 1):
            if interrupted():
                return None
            progress(T("status_loading", sym=sym, i=i, n=n))
            try:
                lo = (_parse_date(min(days)) - timedelta(days=10)).isoformat()
                hi = (_parse_date(max(days)) + timedelta(days=2)).isoformat()
                # auto_adjust=False: echter Schlusskurs (nicht dividendenbereinigt)
                h = yf.Ticker(sym).history(start=lo, end=hi, interval="1d",
                                           auto_adjust=False)
                if h is None or h.empty:
                    raise RuntimeError("keine Kursdaten")
                series = [(ts.date().isoformat(), float(c))
                          for ts, c in h["Close"].dropna().items()]
                for d in days:
                    p = fx_lookup(series, d)
                    if p:
                        res["prices"][(sym, d)] = p
            except Exception as e:
                _log.warning("Realisierte Gewinne: Kurs %s fehlt: %s", sym, e)
                res["errors"].append(sym)
        for cur, (lo, hi) in sorted(fx_jobs.items()):
            if interrupted():
                return None
            progress(T("status_fx", cur=cur, base=base))
            pair = f"{cur}{base}=X"
            try:
                start = (_parse_date(lo) - timedelta(days=10)).isoformat()
                end = (_parse_date(hi) + timedelta(days=2)).isoformat()
                h = yf.Ticker(pair).history(start=start, end=end, interval="1d")
                if h is None or h.empty:
                    raise RuntimeError("keine Daten")
                res["fx"][(cur, base)] = sorted(
                    (ts.date().isoformat(), float(c))
                    for ts, c in h["Close"].dropna().items() if float(c) > 0)
            except Exception as e:
                _log.warning("Realisierte Gewinne: Wechselkurs %s fehlt: %s", pair, e)
                res["errors"].append(pair)
    except Exception as e:
        _log.error("Realisierte Gewinne: Abruf abgebrochen", exc_info=True)
        res["error"] = str(e)
    return res


def sym_currencies(known_cur=None, account=None):
    """{sym: Yahoo-Rohwährung} aus Kurs-Cache und Dividendenkonto."""
    out = dict(_CUR_CACHE)
    out.update({s: c for s, c in (known_cur or {}).items() if c})
    for s, m in ((account or {}).get("symbols") or {}).items():
        # Dividendenkonto kennt normierte Währung + Faktor → Rohwährung rekonstruieren
        if s not in out and isinstance(m, dict) and m.get("currency"):
            out[s] = ("GBp" if m.get("currency") == "GBP"
                      and m.get("factor") == 0.01 else m["currency"])
    return out


def rows_for_period(closed, base, known_cur=None, account=None, lo=None, hi=None,
                    progress=None):
    """Realisierte Gewinne der Verkäufe im Zeitraum [lo, hi] (ISO-Daten) in
    Währung ``base`` – lädt fehlende Daten SYNCHRON (für den Steuerauszug;
    Aufruf ohne parallele Yahoo-Threads). Nutzt und füllt die Sitzungs-Caches.
    Gibt (rows, errors) zurück."""
    base = (base or "USD").upper()
    sel = {}
    for sym, rec in iter_sales(closed):
        d = str(rec["sell_date"])[:10]
        if (lo is None or d >= lo) and (hi is None or d <= hi):
            sel.setdefault(sym, []).append(rec)
    if not sel:
        return [], []
    sym_cur = sym_currencies(known_cur, account)
    errors = []

    def _run(cur_syms, price_jobs, fx_jobs):
        if not (cur_syms or price_jobs or fx_jobs):
            return
        res = fetch_data(cur_syms, price_jobs, fx_jobs, base, progress=progress) or {}
        sym_cur.update(res.get("cur", {}))
        _CUR_CACHE.update(res.get("cur", {}))
        _PRICE_CACHE.update(res.get("prices", {}))
        _FX_CACHE.update(res.get("fx", {}))
        errors.extend(res.get("errors", []))

    cur_syms = sorted(s for s in sel if s not in sym_cur)
    price_jobs = {}
    for s, recs in sel.items():
        for rec in recs:
            d = str(rec["sell_date"])[:10]
            if not _num(rec.get("sell_price")) and not _num(rec.get("net_proceeds")) \
                    and (s, d) not in _PRICE_CACHE:
                price_jobs.setdefault(s, set()).add(d)
    _run(cur_syms, {s: sorted(v) for s, v in price_jobs.items()}, {})

    def _fx_jobs():
        jobs = {}
        for cur, (a, b) in needed_fx(sel, base, sym_cur).items():
            ser = _FX_CACHE.get((cur, base))
            if (not ser or ser[0][0] > a
                    or ser[-1][0] < min(b, date.today().isoformat())) \
                    and f"{cur}{base}=X" not in errors:
                jobs[cur] = (a, b)
        return jobs
    _run([], {}, _fx_jobs())
    return compute_rows(sel, base, sym_cur, _FX_CACHE, _PRICE_CACHE), errors


# ══════════════════════════════════════════════════════════════════════════════
#  UI
# ══════════════════════════════════════════════════════════════════════════════

def _is_dark() -> bool:
    from PyQt6.QtGui import QPalette
    return QApplication.palette().color(QPalette.ColorRole.Window).lightness() < 128


def _colors():
    if _is_dark():
        return {"pos": "#2ecc71", "neg": "#ff6b6b", "muted": "#9aa5b1",
                "info_bg": "#0d2a3d", "sum_bg": "#1e2535", "sum_border": "#2a3a50",
                "warn": "#f0b429"}
    return {"pos": "#1e8449", "neg": "#c0392b", "muted": "#6c7a89",
            "info_bg": "#EBF5FB", "sum_bg": "#f8f9fa", "sum_border": "#dee2e6",
            "warn": "#b9770e"}


def _emoji_font(widget, size=10):
    for name in ("Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji"):
        if name in QFontDatabase.families():
            widget.setFont(QFont(name, size))
            return


def _default_fmt(value, decimals=2):
    s = f"{abs(value):,.{decimals}f}".replace(",", "'")
    return f"-{s}" if value < 0 else s


def _fmt_date(iso):
    d = _parse_date(iso)
    if d is None:
        return str(iso)
    try:
        return _cfg.fmt_date(d) if _cfg else d.strftime("%d.%m.%Y")
    except Exception:
        return d.strftime("%d.%m.%Y")


class _Item(QTableWidgetItem):
    """Tabellenzelle, die nach UserRole (Zahl/Datum) statt nach Text sortiert."""

    def __lt__(self, other):
        a = self.data(Qt.ItemDataRole.UserRole)
        b = other.data(Qt.ItemDataRole.UserRole)
        if a is None or b is None:
            return (a is None) and (b is not None)
        try:
            return a < b
        except TypeError:
            return str(a) < str(b)


def _item(text, sort=None, right=True, color=None, bold=False, italic=False, tip=None):
    it = _Item(text)
    it.setData(Qt.ItemDataRole.UserRole, sort if sort is not None else text)
    if right:
        it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    if color:
        it.setForeground(QColor(color))
    if bold or italic:
        f = it.font(); f.setBold(bold); f.setItalic(italic); it.setFont(f)
    if tip:
        it.setToolTip(tip)
    return it


class _PriceEditDialog(QDialog):
    def __init__(self, row, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("edit_title"))
        self.setMinimumWidth(380)
        lay = QVBoxLayout(self)
        qty = f"{row['qty']:g}"
        lbl = QLabel(T("edit_label", sym=row["sym"], date=_fmt_date(row["sell_date"]),
                       qty=qty, cur=row["raw_cur"] or "?"))
        lbl.setWordWrap(True)
        lay.addWidget(lbl)
        self.spin = QDoubleSpinBox()
        self.spin.setDecimals(4)
        self.spin.setRange(0.0, 1e9)
        self.spin.setValue(row["sell_price"] or 0.0)
        self.spin.selectAll()
        lay.addWidget(self.spin)
        muted = _colors()["muted"]
        if row["raw_cur"] == "GBp":
            h = QLabel(T("edit_hint_pence")); h.setStyleSheet(f"color:{muted};")
            h.setWordWrap(True); lay.addWidget(h)
        if _num(row["rec"].get("net_proceeds")):
            h = QLabel(T("edit_hint_bank")); h.setStyleSheet(f"color:{muted};")
            h.setWordWrap(True); lay.addWidget(h)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                              | QDialogButtonBox.StandardButton.Cancel)
        bb.button(QDialogButtonBox.StandardButton.Ok).setText(T("btn_ok"))
        bb.button(QDialogButtonBox.StandardButton.Cancel).setText(T("btn_cancel"))
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
        lay.addWidget(bb)

    def value(self):
        return self.spin.value()


class RealizedGainsWidget(QWidget):
    """Ansicht „Realisierte Gewinne“ – eigenständig oder im Konto-Fenster eingebettet.

    closed:         Verkaufshistorie {sym: [lots]} (wird bei Kurskorrektur geändert!)
    base_currency:  Portfoliowährung
    save_fn:        speichert das Portfolio (nach Kurskorrektur)
    account:        Dividendenkonto-dict (für Gesamtertrag), optional
    known_cur:      {sym: Yahoo-Währung} aus dem Kurs-Cache, optional
    fmt_fn, export_factory, before_fetch: wie beim Dividendenkonto
    """

    def __init__(self, closed, base_currency="USD", save_fn=None, account=None,
                 known_cur=None, fmt_fn=None, export_factory=None, before_fetch=None,
                 parent=None, auto_fetch=True, busy_fn=None):
        super().__init__(parent)
        self._busy_fn = busy_fn      # True, solange ein anderer Yahoo-Abruf läuft
        self._closed = closed if isinstance(closed, dict) else {}
        self._base = (base_currency or "USD").upper()
        self._save_fn = save_fn
        self._account = account if isinstance(account, dict) else {}
        self._sym_cur = sym_currencies(known_cur, self._account)
        self._fmt = fmt_fn or _default_fmt
        self._export_factory = export_factory
        self._before_fetch = before_fetch
        self._worker = None
        self._rows = []
        self._build()
        self.refresh()
        if auto_fetch:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, self.start_fetch)

    # ── Aufbau ────────────────────────────────────────────────────────────
    def _build(self):
        c = _colors()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        info = QLabel(T("info", base=self._base)); info.setWordWrap(True)
        info.setStyleSheet(f"background:{c['info_bg']}; border-radius:6px; "
                           "padding:8px 14px; font-size:12px;")
        lay.addWidget(info)

        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel(T("lbl_year")))
        self.cmb_year = QComboBox()
        self.cmb_year.setMinimumWidth(120)
        self.cmb_year.currentIndexChanged.connect(lambda _: self._fill())
        ctrl.addWidget(self.cmb_year)
        self.btn_refresh = QPushButton(T("btn_refresh")); _emoji_font(self.btn_refresh)
        self.btn_refresh.setToolTip(T("tip_refresh"))
        self.btn_refresh.clicked.connect(lambda: self.start_fetch(force=True))
        ctrl.addWidget(self.btn_refresh)
        ctrl.addStretch()
        if self._export_factory:
            ctrl.addWidget(self._export_factory(self._export_data, T("export_title")))
        self._ctrl = ctrl
        lay.addLayout(ctrl)

        self.status = QLabel("")
        self.status.setStyleSheet(f"color:{c['muted']}; font-size:11px;")
        lay.addWidget(self.status)

        headers = [T("col_symbol"), T("col_sell_date"), T("col_buy_date"), T("col_qty"),
                   T("col_buy_price"), T("col_sell_price"), T("col_holding"),
                   T("col_gain_cur"), T("col_gain_base", base=self._base), T("col_pct"),
                   T("col_source")]
        t = QTableWidget(0, len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        t.setAlternatingRowColors(True)
        t.verticalHeader().setVisible(False)
        hh = t.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSortIndicator(1, Qt.SortOrder.DescendingOrder)   # neueste Verkäufe oben
        t.setSortingEnabled(True)
        t.doubleClicked.connect(self._edit_selected)
        self.table = t
        lay.addWidget(t, stretch=1)

        self.empty_label = QLabel(T("lbl_empty")); self.empty_label.setWordWrap(True)
        self.empty_label.setStyleSheet(f"color:{c['muted']}; padding:6px;")
        lay.addWidget(self.empty_label)

        box = QFrame()
        box.setStyleSheet(f"QFrame {{ background:{c['sum_bg']}; border:1px solid "
                          f"{c['sum_border']}; border-radius:6px; }} "
                          "QLabel { border:none; background:transparent; }")
        bl = QVBoxLayout(box); bl.setContentsMargins(12, 8, 12, 8); bl.setSpacing(3)
        self.lbl_gains = QLabel(); self.lbl_divs = QLabel(); self.lbl_total = QLabel()
        self.lbl_costs = QLabel()
        self.lbl_total.setStyleSheet("font-size:14px;")
        self.lbl_after_tax = QLabel(); self.lbl_after_tax.setWordWrap(True)
        self.lbl_years = QLabel(); self.lbl_years.setWordWrap(True)
        self.lbl_years.setStyleSheet(f"color:{c['muted']}; font-size:11px;")
        self.lbl_missing = QLabel(); self.lbl_missing.setWordWrap(True)
        self.lbl_missing.setStyleSheet(f"color:{c['warn']}; font-size:11px;")
        for w in (self.lbl_gains, self.lbl_divs, self.lbl_costs, self.lbl_total,
                  self.lbl_after_tax, self.lbl_years, self.lbl_missing):
            w.setTextFormat(Qt.TextFormat.RichText)
            bl.addWidget(w)
        self.sum_box = box
        lay.addWidget(box)

    def add_control(self, widget):
        """Weitere Buttons (z. B. Schliessen) rechts in die Steuerleiste."""
        self._ctrl.addWidget(widget)

    # ── Daten ─────────────────────────────────────────────────────────────
    def refresh(self, est_prices=None):
        self._rows = compute_rows(self._closed, self._base, self._sym_cur,
                                  _FX_CACHE, est_prices if est_prices is not None
                                  else _PRICE_CACHE)
        years = sorted({r["year"] for r in self._rows}, reverse=True)
        cur_sel = self.cmb_year.currentData()
        self.cmb_year.blockSignals(True)
        self.cmb_year.clear()
        self.cmb_year.addItem(T("all_years"), None)
        for y in years:
            self.cmb_year.addItem(y, y)
        i = self.cmb_year.findData(cur_sel)
        self.cmb_year.setCurrentIndex(i if i >= 0 else 0)
        self.cmb_year.blockSignals(False)
        self._fill()

    def _fill(self):
        c = _colors()
        fmt = self._fmt
        year = self.cmb_year.currentData()
        rows = [r for r in self._rows if year is None or r["year"] == year]
        t = self.table
        t.setSortingEnabled(False)
        t.setRowCount(len(rows))

        def col_for(v):
            return None if v is None or abs(v) < 0.005 else (c["pos"] if v > 0 else c["neg"])

        for i, r in enumerate(rows):
            sym_it = _item(r["sym"], right=False, bold=True,
                           tip=T("tip_staking") if r["staking"] else None)
            sym_it.setData(Qt.ItemDataRole.UserRole + 1, r)   # Zeile für Doppelklick
            t.setItem(i, 0, sym_it)
            t.setItem(i, 1, _item(_fmt_date(r["sell_date"]), r["sell_date"]))
            t.setItem(i, 2, _item(_fmt_date(r["buy_date"]), r["buy_date"]))
            t.setItem(i, 3, _item(f"{r['qty']:g}", r["qty"]))
            unit = f" {r['raw_cur']}" if r["raw_cur"] else ""
            t.setItem(i, 4, _item(fmt(r["buy_price"]) + unit, r["buy_price"]))
            if r["sell_price"]:
                txt = ("≈ " if r["est"] else "") + fmt(r["sell_price"]) + unit
                t.setItem(i, 5, _item(txt, r["sell_price"], italic=r["est"],
                                      tip=T("tip_est_price") if r["est"] else None))
            else:
                t.setItem(i, 5, _item("–", -1, tip=T("tip_est_price")))
            d = r["days"]
            if d is None:
                hold = "–"
            elif d < 365:
                hold = T("holding_days", n=d)
            else:
                hold = T("holding_years", n=f"{d / 365.25:.1f}")
            t.setItem(i, 6, _item(hold, d if d is not None else -1))
            g = r["gain_cur"]
            t.setItem(i, 7, _item((fmt(g) + f" {r['cur']}") if g is not None else "–",
                                  g if g is not None else -1e18, color=col_for(g)))
            gb = r["gain_base"]
            t.setItem(i, 8, _item(fmt(gb) if gb is not None else "–",
                                  gb if gb is not None else -1e18, color=col_for(gb),
                                  bold=gb is not None))
            p = r["pct"]
            t.setItem(i, 9, _item(f"{p:+.1f} %" if p is not None else "–",
                                  p if p is not None else -1e18, color=col_for(p)))
            src = T("src_bank") if r["bank"] else T("src_price")
            t.setItem(i, 10, _item(src, right=False,
                                   tip=T("tip_src_bank") if r["bank"] else T("tip_src_price")))
        t.setSortingEnabled(True)
        self.empty_label.setVisible(not self._rows)
        self.sum_box.setVisible(bool(self._rows))
        self._fill_summary(year)

    def _fill_summary(self, year):
        c = _colors()
        fmt = self._fmt
        period = T("period_all") if year is None else T("period_year", year=year)
        s = summarize(self._rows, year)

        def signed(v):
            col = c["pos"] if v > 0.005 else (c["neg"] if v < -0.005 else None)
            txt = ("+" if v > 0.005 else "") + fmt(v)
            return f"<span style='color:{col}'>{txt}</span>" if col else txt

        self.lbl_gains.setText(T("lbl_sum_gains", period=period, amount=signed(s["total"]),
                                 base=self._base, gains=fmt(s["gains"]),
                                 losses=fmt(s["losses"]), n=s["n"], muted=c["muted"]))
        divs = dividends_net(self._account, self._base, _FX_CACHE, year)
        if divs is None:
            self.lbl_divs.setText(f"<span style='color:{c['muted']}'>"
                                  f"{T('lbl_sum_divs_none')}</span>")
            total = s["total"]
        else:
            self.lbl_divs.setText(T("lbl_sum_divs", period=period, amount=signed(divs),
                                    base=self._base))
            total = s["total"] + divs
        costs = costs_net(self._account, self._base, _FX_CACHE, year)
        if costs is None:
            self.lbl_costs.setVisible(False)
        else:
            self.lbl_costs.setVisible(True)
            self.lbl_costs.setText(T("lbl_sum_costs", period=period, amount=signed(costs),
                                     base=self._base))
            total += costs
        self.lbl_total.setText(T("lbl_sum_total", period=period, amount=signed(total),
                                 base=self._base))
        self._fill_after_tax(year, period, total, signed)
        if year is None:
            years = sorted({r["year"] for r in self._rows})
            items = " · ".join(f"{y}: {signed(summarize(self._rows, y)['total'])}"
                               for y in years)
            self.lbl_years.setText(T("lbl_by_year", items=items) if len(years) > 1 else "")
        else:
            self.lbl_years.setText("")
        self.lbl_years.setVisible(bool(self.lbl_years.text()))
        self.lbl_missing.setText(T("lbl_missing", n=s["missing"]) if s["missing"] else "")
        self.lbl_missing.setVisible(bool(s["missing"]))

    def _fill_after_tax(self, year, period, total, signed):
        """Zeile „Gesamtertrag nach Steuern (geschätzt)“ je Steuerwohnsitz."""
        c = _colors()
        fmt = self._fmt
        try:
            residence, res = after_tax(self._rows, self._account, self._base, _FX_CACHE, year)
        except Exception:
            _log.warning("Realisierte Gewinne: Steuerschätzung fehlgeschlagen", exc_info=True)
            self.lbl_after_tax.setVisible(False)
            return
        muted = c["muted"]
        if res is None:
            key = "lbl_after_tax_ch" if residence == "CH" else "lbl_after_tax_none"
            self.lbl_after_tax.setText(f"<span style='color:{muted}; font-size:11px'>"
                                       f"{T(key, res=residence)}</span>")
        else:
            parts = [T("after_tax_gains", amount=fmt(res["gain_tax"]))]
            if res["kind"] in ("DE", "AT"):
                parts.append(T("after_tax_divs", amount=fmt(res["div_tax"])))
            note = T("after_tax_note_" + res["kind"])
            if res["allow_ignored"]:
                note += " " + T("after_tax_allow_ignored")
            self.lbl_after_tax.setText(
                T("lbl_after_tax", period=period, amount=signed(total - res["tax"]),
                  base=self._base, res=residence)
                + f"<br><span style='color:{muted}; font-size:11px'>"
                + T("after_tax_detail", tax=fmt(-res["tax"]), parts=", ".join(parts))
                + " " + note + "</span>")
        self.lbl_after_tax.setVisible(True)

    # ── Abruf ─────────────────────────────────────────────────────────────
    def start_fetch(self, force=False):
        if self._worker is not None and self._worker.isRunning():
            return
        if self._busy_fn is not None and self._busy_fn():
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(500, lambda: self.start_fetch(force))
            return
        sales = list(iter_sales(self._closed))
        if not sales:
            return
        cur_syms = sorted({s for s, _ in sales if s not in self._sym_cur})
        price_jobs = {}
        for s, rec in sales:
            d = str(rec["sell_date"])[:10]
            if not _num(rec.get("sell_price")) and not _num(rec.get("net_proceeds")) \
                    and (force or (s, d) not in _PRICE_CACHE):
                price_jobs.setdefault(s, set()).add(d)
        price_jobs = {s: sorted(v) for s, v in price_jobs.items()}
        need = needed_fx(self._closed, self._base, self._sym_cur, self._account)
        fx_jobs = {}
        for cur, (lo, hi) in need.items():
            ser = _FX_CACHE.get((cur, self._base))
            if force or not ser or ser[0][0] > lo or ser[-1][0] < min(hi, date.today().isoformat()):
                fx_jobs[cur] = (lo, hi)
        if not (cur_syms or price_jobs or fx_jobs):
            return
        if self._before_fetch:
            try:
                self._before_fetch()
            except Exception:
                pass
        w = _FetchWorker(cur_syms, price_jobs, fx_jobs, self._base)
        w.progress.connect(self._on_progress)
        w.done.connect(self._on_done)
        _RUNNING_WORKERS.add(w)
        w.finished.connect(lambda w=w: _RUNNING_WORKERS.discard(w))
        self._worker = w
        self.btn_refresh.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
        w.start()

    def _on_progress(self, msg):
        try:
            self.status.setText(msg)
        except RuntimeError:
            pass

    def _on_done(self, res):
        QApplication.restoreOverrideCursor()
        try:
            self.btn_refresh.setEnabled(True)
        except RuntimeError:
            return
        self._worker = None
        if res.get("error"):
            self.status.setText(T("status_failed", e=res["error"]))
            return
        self._sym_cur.update(res.get("cur", {}))
        _CUR_CACHE.update(res.get("cur", {}))
        _PRICE_CACHE.update(res.get("prices", {}))
        _FX_CACHE.update(res.get("fx", {}))
        # Neue Währungen bekannt → evtl. weitere Wechselkurse nötig
        missing_fx = [c for c in needed_fx(self._closed, self._base, self._sym_cur,
                                           self._account)
                      if (c, self._base) not in _FX_CACHE and f"{c}{self._base}=X"
                      not in res.get("errors", [])]
        msg = T("status_done")
        if res.get("errors"):
            msg += "  │  " + T("status_errors", items=", ".join(sorted(set(res["errors"]))))
        self.status.setText(msg)
        self.refresh()
        if res.get("cur") and missing_fx:
            self.start_fetch()

    def stop(self):
        w = self._worker
        if w is not None and w.isRunning():
            try:
                w.progress.disconnect(); w.done.disconnect()
            except Exception:
                pass
            w.requestInterruption()
            QApplication.restoreOverrideCursor()
        self._worker = None

    # ── Aktionen ──────────────────────────────────────────────────────────
    def _edit_selected(self, *_):
        r = self.table.currentRow()
        if r < 0:
            return
        it = self.table.item(r, 0)
        row = it.data(Qt.ItemDataRole.UserRole + 1) if it else None
        if not row:
            return
        dlg = _PriceEditDialog(row, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        v = dlg.value()
        rec = row["rec"]
        if v > 0:
            rec["sell_price"] = round(v, 6)
        else:
            rec.pop("sell_price", None)
        if self._save_fn:
            try:
                self._save_fn()
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, T("msg_title_error"), str(e))
        self.refresh()

    def _export_data(self):
        t = self.table
        headers = [t.horizontalHeaderItem(c).text() for c in range(t.columnCount())]
        rows = [tuple((t.item(r, c).text() if t.item(r, c) else "")
                      for c in range(t.columnCount()))
                for r in range(t.rowCount())]
        import re
        strip = lambda s: re.sub(r"<[^>]+>", "", s or "")
        for lbl in (self.lbl_gains, self.lbl_divs, self.lbl_costs, self.lbl_total,
                    self.lbl_after_tax, self.lbl_years):
            if lbl.text():
                rows.append(tuple([""] * (len(headers) - 1) + [strip(lbl.text())]))
        year = self.cmb_year.currentData()
        title = T("export_title") + (f" {year}" if year else "")
        return {"title": title, "headers": headers, "rows": rows}


class RealizedGainsDialog(QDialog):
    """Eigenständiges Fenster um RealizedGainsWidget (bis das Konto-Fenster steht)."""

    def __init__(self, closed, parent=None, **kw):
        super().__init__(parent)
        self.setWindowTitle(T("title"))
        if sys.platform == "win32" and parent is not None:
            self.finished.connect(lambda *_: (parent.raise_(), parent.activateWindow()))
        scr = ((parent.screen() if parent is not None else None)
               or QApplication.primaryScreen()).availableGeometry()
        w, h = int(scr.width() * 0.62), int(scr.height() * 0.65)
        self.resize(w, h)
        self.move(scr.x() + (scr.width() - w) // 2, scr.y() + (scr.height() - h) // 2)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        self.widget = RealizedGainsWidget(closed, parent=self, **kw)
        btn = QPushButton(T("btn_close")); btn.clicked.connect(self.close)
        self.widget.add_control(btn)
        lay.addWidget(self.widget)
        self.finished.connect(lambda *_: self.widget.stop())
