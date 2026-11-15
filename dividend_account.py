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

from PyQt6.QtCore import Qt, QObject, QThread, QDate, QTimer, pyqtSignal
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
    if t == "bank":
        # Bankbuchung (Import): gross trägt das Vorzeichen; Dividenden mit Steuer
        if e.get("kind") == "dividend":
            return gross - float(e.get("tax", 0) or 0) if net else gross
        return gross
    if t == "dividend":
        return gross - float(e.get("tax", 0) or 0) if net else gross
    if t in ("withdrawal", "buy"):
        return -gross
    return gross   # deposit, sell


def balances(acc: dict, net: bool, entries=None) -> dict:
    """{cur: {"div": brutto, "tax": .., "trades": .., "transfers": .., "balance": ..}}
    "div" ist immer brutto; "balance" je nach Modus brutto oder netto.
    entries: Buchungen einer Ansicht (view_entries); Standard = alle gespeicherten."""
    out = {}
    for e in (acc.get("entries", []) if entries is None else entries):
        cur = e.get("currency", "USD")
        b = out.setdefault(cur, {"div": 0.0, "tax": 0.0, "trades": 0.0, "fx": 0.0,
                                 "costs": 0.0, "transfers": 0.0, "balance": 0.0})
        amt = entry_amount(e, net)
        t, kind = e.get("type"), e.get("kind")
        if t == "dividend" or (t == "bank" and kind == "dividend"):
            b["div"] += float(e.get("gross", 0) or 0)
            b["tax"] += float(e.get("tax", 0) or 0)
        elif t in ("buy", "sell"):
            b["trades"] += amt
        elif t == "bank" and kind == "fx":
            b["fx"] = b.get("fx", 0.0) + amt
        elif t == "bank" and kind in ("interest", "fee"):
            b["costs"] = b.get("costs", 0.0) + amt
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


# ── Ansicht „Alles“: Geldkonto mit Käufen/Verkäufen ───────────────────────────
#
# settings["trades"] = {"enabled": bool, "start": "YYYY-MM-DD", "asked": bool}
# Ein-/Auszahlungen:   "div_scope"  – gehört zur Ansicht „Nur Dividenden“
#                                     (fehlt = True: alle Buchungen von früher)
#                      "reinvested" – Auszahlung wurde in Aktien investiert →
#                                     in „Alles“ nicht abziehen (Kauf belastet schon)
# Anfangssaldo:        type "deposit", "opening": True, "div_scope": False
# Käufe/Verkäufe werden NICHT gespeichert, sondern bei jeder Anzeige aus dem
# Portfolio abgeleitet (trade_entries) – das Konto folgt so jeder Änderung.

VIEW_DIV, VIEW_ALL = "div", "all"


def trade_settings(acc: dict) -> dict:
    t = acc["settings"].get("trades")
    if not isinstance(t, dict):
        t = {"enabled": False, "start": "", "asked": False}
        acc["settings"]["trades"] = t
    return t


def entry_in_view(e: dict, view: str) -> bool:
    t = e.get("type")
    if t == "dividend":
        return True
    if t in ("buy", "sell", "bank"):
        return view == VIEW_ALL
    if view == VIEW_DIV:
        return bool(e.get("div_scope", True))
    return not e.get("reinvested")


def _crypto_cur(sym: str):
    s = sym.upper()
    for suf in _CRYPTO_SUFFIXES:
        if s.endswith(suf):
            return suf[1:]
    return None


def symbol_currency(sym, acc, known_cur=None):
    """(Währung normiert, Faktor) eines Symbols oder (None, 1.0)."""
    raw = (known_cur or {}).get(sym)
    if raw:
        return normalize_currency(raw)
    m = acc.get("symbols", {}).get(sym) or {}
    if m.get("currency"):
        return m["currency"], float(m.get("factor", 1.0) or 1.0)
    c = _crypto_cur(sym)
    if c:
        return c, 1.0
    return None, 1.0


def _f(v):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def trade_entries(positions_by_sym, acc, known_cur=None, all_dates=False):
    """Käufe/Verkäufe ab Startdatum als (virtuelle) Buchungen.

    positions_by_sym: offene Lots + verkaufte Lots (mit sell_date), wie
                      PortfolioDialog._positions_with_history()
    Rangfolge der Beträge: Betrag in Kontowährung (Bank-CSV) > Nettobetrag in
    Handelswährung > Kurs × Stück. Teile desselben Auftrags (FIFO über mehrere
    Lots, Restposten nach Teilverkauf) werden je Symbol/Tag/Währung zusammengefasst.
    all_dates=True: unabhängig von der Einstellung alle (für die Einrichtung).
    Gibt (entries, n_missing) zurück.
    """
    ts = trade_settings(acc)
    if not ts.get("enabled") and not all_dates:
        return [], 0
    start = "" if all_dates else str(ts.get("start") or "")[:10]
    groups = {}
    missing = 0

    def add(kind, sym, day, cur, amount, qty):
        key = (kind, sym, day, cur)
        g = groups.get(key)
        if g is None:
            g = groups[key] = {"id": f"trd:{kind}:{sym}:{day}:{cur}", "type": kind,
                               "date": day, "currency": cur, "gross": 0.0, "tax": 0.0,
                               "symbol": sym, "qty": 0.0, "note": "", "auto": True}
        g["gross"] += amount
        g["qty"] += qty

    for sym, lots in (positions_by_sym or {}).items():
        cur_n, factor = symbol_currency(sym, acc, known_cur)
        for p in lots or []:
            qty = _f(p.get("quantity"))
            if qty <= 0:
                continue
            bd = str(p.get("buy_date", ""))[:10]
            if bd and bd >= start and not p.get("staking"):
                if _f(p.get("acct_amount")) and p.get("acct_cur"):
                    add("buy", sym, bd, p["acct_cur"].upper(), _f(p["acct_amount"]), qty)
                elif _f(p.get("net_cost")) and p.get("net_cur"):
                    add("buy", sym, bd, p["net_cur"].upper(), _f(p["net_cost"]), qty)
                elif cur_n and _f(p.get("buy_price")) > 0:
                    add("buy", sym, bd, cur_n, _f(p["buy_price"]) * qty * factor, qty)
                elif _f(p.get("buy_price")) > 0:
                    missing += 1
            sd = str(p.get("sell_date", "") or "")[:10]
            if sd and sd >= start:
                if _f(p.get("sell_acct_amount")) and p.get("sell_acct_cur"):
                    add("sell", sym, sd, p["sell_acct_cur"].upper(), _f(p["sell_acct_amount"]), qty)
                elif _f(p.get("net_proceeds")) and p.get("sell_net_cur"):
                    add("sell", sym, sd, p["sell_net_cur"].upper(), _f(p["net_proceeds"]), qty)
                elif cur_n and _f(p.get("sell_price")) > 0:
                    add("sell", sym, sd, cur_n, _f(p["sell_price"]) * qty * factor, qty)
                else:
                    missing += 1
    out = []
    for g in groups.values():
        g["gross"] = round(g["gross"], 4)
        g["qty"] = round(g["qty"], 8)
        if g["qty"]:
            g["per_share"] = g["gross"] / g["qty"]
        out.append(g)
    return out, missing


def bank_info(acc: dict) -> dict:
    """settings["bank"] = {"source", "from", "to", "saldo": {cur: [iso, betrag]}}"""
    b = acc["settings"].get("bank")
    return b if isinstance(b, dict) else {}


def view_entries(acc, view, trades=None):
    """Alle Buchungen der Ansicht (gespeicherte + bei „Alles“ die Käufe/Verkäufe).

    „Alles“ mit importierten Bankbuchungen: Für den Zeitraum der Bank-CSV gelten
    die Dividenden laut Bank (exakt, inkl. Stornos) statt der Yahoo-Berechnung;
    Bankbuchungen vor dem Startdatum zählen nicht (Anfangssaldo deckt sie ab)."""
    es = [e for e in acc.get("entries", []) if entry_in_view(e, view)]
    if view == VIEW_ALL:
        bi = bank_info(acc)
        lo, hi = bi.get("from", ""), bi.get("to", "")
        start = str(trade_settings(acc).get("start") or "")[:10]
        if lo and hi:
            es = [e for e in es if not (e.get("type") == "dividend"
                                        and lo <= str(e.get("date", ""))[:10] <= hi)]
        es = [e for e in es if e.get("type") != "bank"
              or str(e.get("date", ""))[:10] >= start]
        if trades:
            es = es + list(trades)
    return es


def balance_at(acc, positions_by_sym, day_iso, known_cur=None):
    """Kontosaldo (netto) je Währung am Ende des Tages ``day_iso`` in der Ansicht
    „Alles“ – für die Vermögenssteuer (Steuerauszug).
    None, wenn die Ansicht „Alles“ (Käufe/Verkäufe ab Startdatum) nicht
    eingerichtet ist: Die Ansicht „Nur Dividenden“ ist kein echter Geldsaldo."""
    acc = ensure_account(acc)
    ts = trade_settings(acc)
    start = str(ts.get("start") or "")[:10]
    if not ts.get("enabled") or not start:
        return None
    if day_iso < start:
        return {}
    trades, _ = trade_entries(positions_by_sym, acc, known_cur)
    es = [e for e in view_entries(acc, VIEW_ALL, trades)
          if str(e.get("date", ""))[:10] <= day_iso]
    return {cur: b["balance"] for cur, b in balances(acc, True, es).items()
            if abs(b["balance"]) >= 0.005}


def sync_signature(positions_by_sym, base, skip=None) -> str:
    """Prüfsumme über alles, was den Dividenden-Abruf beeinflusst (Symbole,
    Lots mit Kauf-/Verkaufsdatum und Menge, Portfoliowährung). Gleiche
    Signatur am selben Tag → kein neuer Abruf nötig."""
    import hashlib
    import json
    data = []
    for sym in sorted(positions_by_sym or {}):
        if skip and skip(sym):
            continue
        lots = sorted((str(p.get("buy_date", ""))[:10], str(p.get("sell_date", "") or "")[:10],
                       round(_f(p.get("quantity")), 8))
                      for p in positions_by_sym[sym] or [] if isinstance(p, dict))
        data.append([sym, lots])
    raw = json.dumps([str(base or "").upper(), data], separators=(",", ":"))
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


BANK_KINDS = ("deposit", "withdrawal", "payment", "fx", "interest", "fee",
              "dividend", "other")


def import_bank_entries(acc: dict, rows, source: str, replace=False, period=None) -> int:
    """Übernimmt Kontobewegungen einer Bank-CSV ins Konto (nur Ansicht „Alles“).

    rows: [{"id", "date", "kind", "currency", "gross" (mit Vorzeichen), "tax",
            "symbol", "note"}], dazu optional saldo={cur: [iso, betrag]} über
    bank_set_saldo. Doppelte (gleiche id) werden übersprungen.
    replace=True: bisherige Bankbuchungen dieser Quelle zuerst entfernen.
    Ist das Konto noch nicht eingerichtet, werden Käufe/Verkäufe ab dem ersten
    Datum der CSV gebucht (Anfangssaldo 0 – die CSV beginnt mit Kontoeröffnung).
    period: (erstes, letztes Datum) der ganzen CSV – Standard: aus rows.
    Gibt die Zahl neuer Buchungen zurück."""
    acc = ensure_account(acc)
    if replace:
        acc["entries"] = [e for e in acc["entries"]
                          if not (e.get("type") == "bank" and e.get("bank") == source)]
    have = {e.get("id"): e for e in acc["entries"] if e.get("id")}
    n = 0
    dates = []
    for r in rows:
        dates.append(r["date"])
        if r["id"] in have:
            if r.get("symbol"):                 # Symbol-Zuordnung kann sich verbessert haben
                have[r["id"]]["symbol"] = r["symbol"]
            continue
        e = {"id": r["id"], "type": "bank", "kind": r.get("kind", "other"),
             "date": r["date"], "currency": r["currency"],
             "gross": round(float(r.get("gross", 0)), 4),
             "tax": round(float(r.get("tax", 0) or 0), 4),
             "symbol": r.get("symbol", ""), "note": r.get("note", ""),
             "bank": source, "div_scope": False, "edited": True}
        acc["entries"].append(e)
        have[r["id"]] = e
        n += 1
    if period and period[0] and period[1]:
        dates += [period[0], period[1]]
    if dates:
        bi = bank_info(acc) if not replace else {}
        lo, hi = min(dates), max(dates)
        bi.update({"source": source,
                   "from": min(lo, bi.get("from") or lo),
                   "to": max(hi, bi.get("to") or hi)})
        acc["settings"]["bank"] = bi
        ts = trade_settings(acc)
        if not ts.get("asked"):
            ts.update({"enabled": True, "start": bi["from"], "asked": True})
    return n


def bank_set_saldo(acc: dict, saldo: dict) -> None:
    """Letzter Saldo je Währung laut Bank {cur: [iso, betrag]} (neuere gewinnen)."""
    bi = bank_info(acc)
    cur_s = bi.get("saldo") if isinstance(bi.get("saldo"), dict) else {}
    for cur, (d, v) in saldo.items():
        if cur not in cur_s or d >= cur_s[cur][0]:
            cur_s[cur] = [d, v]
    bi["saldo"] = cur_s
    acc["settings"]["bank"] = bi


def bank_reconcile(acc: dict, entries) -> list:
    """Vergleicht den berechneten Netto-Saldo mit dem Saldo laut Bank.
    Gibt [(cur, datum, bank, berechnet, differenz)] zurück."""
    out = []
    for cur, (d, bank) in sorted((bank_info(acc).get("saldo") or {}).items()):
        calc = sum(entry_amount(e, True) for e in entries
                   if e.get("currency") == cur and str(e.get("date", ""))[:10] <= d)
        out.append((cur, d, float(bank), calc, calc - float(bank)))
    return out


# ══════════════════════════════════════════════════════════════════════════════
#  Hintergrund-Abruf
# ══════════════════════════════════════════════════════════════════════════════

_RUNNING_WORKERS = set()   # Referenzen halten, bis der Thread fertig ist

import logging as _logging
_log = _logging.getLogger("StockMonitor")   # gleiche Logdatei wie die App


class _SyncWorker(QThread):
    progress = pyqtSignal(str)
    done = pyqtSignal(dict)

    def __init__(self, positions_by_sym, symbol_meta, currencies, base, known_cur=None,
                 fx_only=False):
        super().__init__()
        self._fx_only = fx_only
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
        result = {"computed": {}, "meta": {}, "fx": {}, "errors": [], "error": "",
                  "fx_only": self._fx_only}
        try:
            import yfinance as yf
            today = date.today()
            syms = [] if self._fx_only else sorted(self._pos)
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


class _FitColumns(QObject):
    """Spaltenbreite = Inhalt (inkl. Überschrift) + gleichmässig verteilter Rest.
    Ersetzt „alle Spalten gleich breit“ (Stretch): Dort richtete sich jede
    Spalte nach der längsten Überschrift, auf Full HD mit 125 % Skalierung
    wurden so Überschriften wie „Ein-/Auszahlungen“ abgeschnitten."""

    def __init__(self, table):
        super().__init__(table)
        self._t = table
        self._busy = False
        self._pending = False
        table.viewport().installEventFilter(self)
        m = table.model()
        for sig in (m.dataChanged, m.rowsInserted, m.rowsRemoved, m.modelReset):
            sig.connect(self.schedule)

    def schedule(self, *_):
        """Nach Änderungen gesammelt einmal anpassen (nicht je Zelle)."""
        if self._pending:
            return
        self._pending = True

        def _run():
            self._pending = False
            try:
                self.fit()
            except RuntimeError:
                pass                     # Tabelle schon geschlossen
        QTimer.singleShot(0, _run)

    def eventFilter(self, obj, ev):
        from PyQt6.QtCore import QEvent
        if ev.type() == QEvent.Type.Resize:
            self.fit()
        return False

    def fit(self):
        t = self._t
        if self._busy:
            return
        self._busy = True
        try:
            cols = [c for c in range(t.columnCount()) if not t.isColumnHidden(c)]
            if not cols:
                return
            t.resizeColumnsToContents()
            need = {c: t.columnWidth(c) for c in cols}
            free = t.viewport().width() - sum(need.values())
            extra = max(0, free) // len(cols)
            for i, c in enumerate(cols):
                # Rest des Rundens an die letzte Spalte (keine Lücke rechts)
                add = extra + (max(0, free) - extra * len(cols) if i == len(cols) - 1 else 0)
                t.setColumnWidth(c, need[c] + add)
        finally:
            self._busy = False


def _make_table(headers):
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    t.setAlternatingRowColors(True)
    t.verticalHeader().setVisible(False)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    t.horizontalHeader().setStretchLastSection(False)
    t._fit_columns = _FitColumns(t)
    return t


def _fit_table(t):
    """Nach dem Füllen bzw. Ein-/Ausblenden von Spalten aufrufen."""
    f = getattr(t, "_fit_columns", None)
    if f is not None:
        f.fit()


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

    def __init__(self, currencies, preset_currency=None, parent=None, div_scope=True):
        super().__init__(parent)
        _fix_win_focus(self, parent)
        self._div_scope = div_scope
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
                "note": self.note.text().strip(), "edited": True,
                # erfasst in „Nur Dividenden“ → in beiden Ansichten; in „Alles“ → nur dort
                "div_scope": bool(self._div_scope)}


class SetupDialog(QDialog):
    """Einrichtung der Ansicht „Alles“: Käufe/Verkäufe ab Datum, Anfangssaldo
    je Währung, Einordnung früherer Auszahlungen (Bankkonto / reinvestiert)."""

    def __init__(self, acc, currencies, first_buy, parent=None):
        super().__init__(parent)
        _fix_win_focus(self, parent)
        self._acc = acc
        self.setWindowTitle(T("title_setup"))
        self.setMinimumWidth(560)
        ts = trade_settings(acc)
        muted = "#9aa5b1" if _is_dark() else "#6c7a89"
        lay = QVBoxLayout(self)
        intro = QLabel(T("lbl_setup_intro")); intro.setWordWrap(True)
        bg = "#0d2a3d" if _is_dark() else "#EBF5FB"
        intro.setStyleSheet(f"background:{bg}; border-radius:6px; padding:8px 12px;")
        lay.addWidget(intro)

        self.chk = QCheckBox(T("chk_trades"))
        self.chk.setChecked(bool(ts.get("enabled")) or not ts.get("asked"))
        f = self.chk.font(); f.setBold(True); self.chk.setFont(f)
        lay.addWidget(self.chk)

        self._body = QWidget()
        bl = QVBoxLayout(self._body); bl.setContentsMargins(18, 0, 0, 0)
        row = QHBoxLayout()
        row.addWidget(QLabel(T("lbl_start")))
        start = _parse_date(ts.get("start")) or date.today()
        self.start = QDateEdit(QDate(start.year, start.month, start.day))
        self.start.setCalendarPopup(True)
        try:
            _df = _cfg.get_date_format() if _cfg else "EU"
        except Exception:
            _df = "EU"
        self.start.setDisplayFormat({"ISO": "yyyy-MM-dd", "US": "MM/dd/yyyy"}.get(_df, "dd.MM.yyyy"))
        row.addWidget(self.start)
        b_first = QPushButton(T("btn_start_first"))
        b_first.clicked.connect(lambda: self.start.setDate(
            QDate(first_buy.year, first_buy.month, first_buy.day)))
        b_first.setEnabled(first_buy is not None)
        b_today = QPushButton(T("btn_start_today"))
        b_today.clicked.connect(lambda: self.start.setDate(QDate.currentDate()))
        row.addWidget(b_first); row.addWidget(b_today); row.addStretch()
        bl.addLayout(row)
        hint = QLabel(T("lbl_start_hint")); hint.setWordWrap(True)
        hint.setStyleSheet(f"color:{muted}; font-size:11px;")
        bl.addWidget(hint)

        bl.addWidget(QLabel(T("lbl_opening")))
        form = QFormLayout()
        opening = {e.get("currency"): float(e.get("gross", 0))
                   for e in acc["entries"] if e.get("opening")}
        self._open_spins = {}
        for cur in currencies:
            sp = QDoubleSpinBox(); sp.setRange(-1e12, 1e12); sp.setDecimals(2)
            sp.setGroupSeparatorShown(True)
            sp.setValue(opening.get(cur, 0.0))
            sp.setMinimumWidth(160)
            form.addRow(f"{cur}:", sp)
            self._open_spins[cur] = sp
        bl.addLayout(form)
        lay.addWidget(self._body)
        self.chk.toggled.connect(self._body.setEnabled)
        self._body.setEnabled(self.chk.isChecked())

        # Frühere Auszahlungen (aus der Zeit vor „Alles“)
        self._wd = [e for e in acc["entries"]
                    if e.get("type") == "withdrawal" and e.get("div_scope", True)]
        self._wd_combos = []
        if self._wd:
            sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
            lay.addWidget(sep)
            lbl = QLabel(T("lbl_withdrawals")); lbl.setWordWrap(True)
            lay.addWidget(lbl)
            wf = QFormLayout()
            for e in sorted(self._wd, key=lambda x: x.get("date", "")):
                cb = QComboBox()
                cb.addItem(T("wd_bank"), False)
                cb.addItem(T("wd_reinvested"), True)
                cb.setCurrentIndex(1 if e.get("reinvested") else 0)
                note = f"  ({e['note']})" if e.get("note") else ""
                wf.addRow(f"{_fmt_date(e.get('date'))}  {e.get('currency', '')} "
                          f"{_default_fmt(float(e.get('gross', 0)))}{note}", cb)
                self._wd_combos.append((e, cb))
            lay.addLayout(wf)
        lay.addLayout(_ok_cancel(self))

    def apply(self):
        acc = self._acc
        ts = trade_settings(acc)
        ts["asked"] = True
        ts["enabled"] = self.chk.isChecked()
        ts["start"] = self.start.date().toString("yyyy-MM-dd")
        # Anfangssaldo: je Währung eine Buchung am Startdatum (nur Ansicht „Alles“)
        acc["entries"] = [e for e in acc["entries"] if not e.get("opening")]
        if ts["enabled"]:
            for cur, sp in self._open_spins.items():
                v = round(sp.value(), 2)
                if abs(v) >= 0.005:
                    acc["entries"].append({
                        "id": f"open:{cur}", "type": "deposit" if v > 0 else "withdrawal",
                        "date": ts["start"], "currency": cur, "gross": abs(v), "tax": 0.0,
                        "note": T("type_opening"), "edited": True, "opening": True,
                        "div_scope": False})
        for e, cb in self._wd_combos:
            if cb.currentData():
                e["reinvested"] = True
            else:
                e.pop("reinvested", None)


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
        es = [e for e in self._owner.entries() if e.get("currency") == self._cur]
        # Bei gleichem Datum: Anfangssaldo zuerst, dann Gutschriften vor Belastungen
        order = {"deposit": 1, "dividend": 2, "sell": 3, "withdrawal": 4, "buy": 5}
        return sorted(es, key=lambda e: (e.get("date", ""), 0 if e.get("opening") else
                                         order.get(e.get("type"), 9), e.get("id", "")))

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
            is_trade = t in ("buy", "sell")
            is_bank = t == "bank"
            if is_bank and e.get("kind") == "dividend":
                is_div = True
            has_sym = is_div or is_trade
            gross = float(e.get("gross", 0))
            tax = float(e.get("tax", 0)) if is_div else 0.0
            signed_gross = -gross if t in ("withdrawal", "buy") else gross   # bank: mit Vorzeichen
            date_it = QTableWidgetItem(_fmt_date(e.get("date")))
            date_it.setData(Qt.ItemDataRole.UserRole, e.get("id"))
            type_txt = (T("type_opening") if e.get("opening")
                        else T(f"bank_{e.get('kind', 'other')}") if is_bank else T(f"type_{t}"))
            if is_div and e.get("edited") and not is_bank:
                type_txt += " ✏"
            type_it = QTableWidgetItem(type_txt)
            if is_bank:
                type_it.setToolTip(T("tip_bank"))
            elif is_div and e.get("edited"):
                type_it.setToolTip(T("tip_edited"))
            elif is_trade:
                type_it.setToolTip(T("tip_trade"))
            self.table.setItem(r, 0, date_it)
            self.table.setItem(r, 1, type_it)
            self.table.setItem(r, 2, QTableWidgetItem(e.get("symbol", "") if has_sym else ""))
            self.table.setItem(r, 3, _num_item(fmt(e.get("qty", 0), 4).rstrip("0").rstrip(".,")
                                               if has_sym and e.get("qty") else ""))
            self.table.setItem(r, 4, _num_item(fmt(e.get("per_share", 0), 4)
                                               if has_sym and e.get("per_share") else ""))
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
        if str(eid).startswith("trd:"):
            QMessageBox.information(self, T("msg_title_info"), T("msg_trade_edit"))
            return None
        return next((e for e in self._owner.account["entries"] if e.get("id") == eid), None)

    # ── Aktionen ──────────────────────────────────────────────────────────
    def _add(self):
        dlg = BookingDialog(self._owner.currencies(), self._cur, self,
                            div_scope=self._owner.view == VIEW_DIV)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._owner.account["entries"].append(dlg.entry())
            self._owner.changed()
            self.refresh()

    def _edit(self):
        e = self._selected()
        if e is None:
            return
        if e.get("type") != "dividend":
            QMessageBox.information(self, T("msg_title_info"), T("msg_no_edit")
                                    if e.get("type") != "bank" else T("tip_bank"))
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
                 price_cache=None, before_fetch=None, closed=None, view=VIEW_DIV):
        super().__init__(parent)
        self._closed = closed          # Verkaufshistorie (für „Realisierte Gewinne“)
        self.view = view if view in (VIEW_DIV, VIEW_ALL) else VIEW_DIV
        self._trades, self._trades_missing = [], 0
        self._gains = None
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
        self._fx_failed = set()        # Wechselkurse, die Yahoo nicht liefert (nicht dauernd neu versuchen)
        self._sig = sync_signature(self._portfolio, self._base, self._skip)

        self.setWindowTitle(T("title"))
        _center_on(self, parent, 0.6 if self.view == VIEW_ALL else 0.5, 0.6)
        self._build()
        if self.view == VIEW_ALL and not trade_settings(self.account).get("asked"):
            self.view = VIEW_DIV           # erst nach der Einrichtung umschalten
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self._set_view(VIEW_ALL))
        self._apply_view()
        self.refresh()
        self.finished.connect(self._stop_worker)

        if not self.account["settings"].get("configured"):
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, self._first_run)
        elif self._sync_cached():
            self.status.setText(T("status_cached", time=self._last_sync().get("time", "")))
            if any(c not in self._fx for c in self.currencies()):
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(0, lambda: self.start_sync(fx_only=True))
        else:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, self.start_sync)

    # ── Abruf-Cache ───────────────────────────────────────────────────────
    def _last_sync(self) -> dict:
        ls = self.account["settings"].get("last_sync")
        return ls if isinstance(ls, dict) else {}

    def _sync_cached(self) -> bool:
        """Heute schon mit denselben Positionen abgerufen? Dann reichen die
        gespeicherten Dividenden und Wechselkurse (🔄 lädt trotzdem neu)."""
        ls = self._last_sync()
        return ls.get("day") == date.today().isoformat() and ls.get("sig") == self._sig

    # ── Aufbau ────────────────────────────────────────────────────────────
    def _build(self):
        from PyQt6.QtWidgets import QButtonGroup, QTabWidget
        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 10, 14, 10)

        # Ansicht: „Nur Dividenden“ | „Alles“
        vrow = QHBoxLayout()
        self._view_btns = {}
        grp = QButtonGroup(self); grp.setExclusive(True)
        dark = _is_dark()
        sel_bg = "#2980b9"
        for v, key in ((VIEW_DIV, "view_div"), (VIEW_ALL, "view_all")):
            b = QPushButton(T(key)); b.setCheckable(True)
            b.setToolTip(T("tip_view"))
            b.setMinimumWidth(130)
            b.setStyleSheet(f"QPushButton:checked {{ background:{sel_bg}; color:white; "
                            f"font-weight:bold; }} QPushButton {{ padding:4px 12px; }}")
            grp.addButton(b)
            b.clicked.connect(lambda _=False, v=v: self._set_view(v))
            vrow.addWidget(b)
            self._view_btns[v] = b
        vrow.addSpacing(10)
        self.btn_setup = QPushButton(T("btn_setup")); _emoji_font(self.btn_setup)
        self.btn_setup.setToolTip(T("tip_setup"))
        self.btn_setup.clicked.connect(self._setup)
        vrow.addWidget(self.btn_setup)
        vrow.addStretch()
        outer.addLayout(vrow)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)      # kein Rahmen – „Nur Dividenden“ sieht aus wie bisher
        outer.addWidget(self.tabs, stretch=1)
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 8, 0, 0)
        self.tabs.addTab(page, T("tab_entries"))
        self.tabs.currentChanged.connect(self._on_tab)

        self.info = QLabel(T("info")); self.info.setWordWrap(True)
        bg = "#0d2a3d" if dark else "#EBF5FB"
        self.info.setStyleSheet(f"background:{bg}; border-radius:6px; padding:8px 14px; font-size:12px;")
        lay.addWidget(self.info)

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
            T("col_currency"), T("col_dividends"), T("col_tax"), T("col_trades"),
            T("col_fx"), T("col_costs"), T("col_transfers"), T("col_balance"),
            T("col_balance_base", cur=self._base)])
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

    # ── Ansicht ───────────────────────────────────────────────────────────
    def _apply_view(self):
        all_v = self.view == VIEW_ALL
        self._view_btns[self.view].setChecked(True)
        self.setWindowTitle(T("title_all") if all_v else T("title"))
        self.info.setText(T("info_all") if all_v else T("info"))
        self.btn_setup.setVisible(all_v)
        for c in (3, 4, 5):            # Käufe/Verkäufe, Devisen, Zinsen/Gebühren
            self.table.setColumnHidden(c, not all_v)
        _fit_table(self.table)
        if all_v and self._closed is not None and self.tabs.count() == 1:
            self.tabs.addTab(QWidget(), T("tab_gains"))     # Inhalt beim ersten Öffnen
        elif not all_v and self.tabs.count() > 1:
            self.tabs.setCurrentIndex(0)
        self.tabs.tabBar().setVisible(self.tabs.count() > 1 and all_v)
        if self.tabs.count() > 1:
            self.tabs.setTabVisible(1, all_v)

    def _set_view(self, view):
        if view == VIEW_ALL and not trade_settings(self.account).get("asked"):
            if not self._setup():
                self._view_btns[self.view].setChecked(True)
                return
        self.view = view
        self._apply_view()
        self.refresh()
        # Nur nachladen, wenn für eine Währung der Ansicht ein Wechselkurs fehlt
        # (Dividenden und Kurse sind seit dem Öffnen schon geladen)
        if any(c not in self._fx and c not in self._fx_failed for c in self.currencies()):
            self.start_sync(fx_only=True)

    def _on_tab(self, idx):
        if idx != 1 or self._gains is not None:
            return
        try:
            from realized_gains import RealizedGainsWidget
        except ImportError as exc:
            QMessageBox.warning(self, T("msg_title_error"), str(exc))
            return
        self._gains = RealizedGainsWidget(
            self._closed, base_currency=self._base, save_fn=self._save_fn,
            account=self.account, known_cur=self._known_cur, fmt_fn=self._fmt,
            export_factory=self._export_factory, before_fetch=self._before_fetch,
            parent=self, auto_fetch=False,
            busy_fn=lambda: self._worker is not None and self._worker.isRunning())
        page = QWidget(); pl = QVBoxLayout(page); pl.setContentsMargins(0, 8, 0, 0)
        pl.addWidget(self._gains)
        self.tabs.blockSignals(True)
        self.tabs.removeTab(1)
        self.tabs.insertTab(1, page, T("tab_gains"))
        self.tabs.setCurrentIndex(1)
        self.tabs.blockSignals(False)
        self._start_gains_fetch()

    def _start_gains_fetch(self):
        """Yahoo-Abrufe nie parallel (curl_cffi ist nicht thread-sicher):
        Gewinne erst laden, wenn die Dividenden-Aktualisierung fertig ist."""
        if self._gains is None:
            return
        if self._worker is not None and self._worker.isRunning():
            return                       # _on_done startet den Abruf danach
        self._gains.start_fetch()

    def _first_buy(self):
        days = [d for d in (_parse_date(p.get("buy_date", ""))
                            for lots in self._portfolio.values() for p in lots or []) if d]
        return min(days) if days else None

    def _setup(self):
        all_tr, _ = trade_entries(self._portfolio, self.account, self._known_cur,
                                  all_dates=True)
        curs = sorted({e.get("currency") for e in all_tr} | set(self.currencies())
                      | {self._base}, key=lambda c: (c != self._base, c))
        dlg = SetupDialog(self.account, curs, self._first_buy(), self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return False
        dlg.apply()
        self.changed()
        return True

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
    def entries(self):
        """Buchungen der aktuellen Ansicht (inkl. Käufe/Verkäufe bei „Alles“)."""
        return view_entries(self.account, self.view, self._trades)

    def currencies(self):
        return sorted({e.get("currency", "USD") for e in self.entries()}
                      | {e.get("currency", "USD") for e in self.account["entries"]})

    def refresh(self):
        fmt = self._fmt
        neg = "#e74c3c" if _is_dark() else "#c0392b"
        if self.view == VIEW_ALL:
            self._trades, self._trades_missing = trade_entries(
                self._portfolio, self.account, self._known_cur)
        else:
            self._trades, self._trades_missing = [], 0
        bals = balances(self.account, self.net_mode, self.entries())
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
            for c, k in ((3, "trades"), (4, "fx"), (5, "costs"), (6, "transfers")):
                v = b.get(k, 0.0)
                self.table.setItem(r, c, _num_item(fmt(v) if abs(v) >= 0.005 else "",
                                                   color=neg if v < 0 else None))
            self.table.setItem(r, 7, _num_item(fmt(b["balance"]), bold=True,
                                               color=neg if b["balance"] < 0 else None))
            rate = self._fx.get(cur)
            if rate:
                conv = b["balance"] * rate
                total += conv
                self.table.setItem(r, 8, _num_item(fmt(conv), color=neg if conv < 0 else None))
            else:
                if abs(b["balance"]) >= 0.005:
                    missing.append(cur)
                self.table.setItem(r, 8, _num_item("–"))
        self.empty_label.setVisible(not curs)
        mode = T("lbl_mode_net") if self.net_mode else T("lbl_mode_gross")
        self.total_label.setText(T("lbl_total", mode=mode, cur=self._base, amount=fmt(total)))
        note = T("lbl_fx_note") if any(c != self._base for c in curs) else ""
        if missing:
            note = (note + " " if note else "") + T("lbl_fx_missing", curs=", ".join(missing))
        if self.view == VIEW_ALL:
            ts = trade_settings(self.account)
            extra = (T("lbl_trades_since", date=_fmt_date(ts.get("start")))
                     if ts.get("enabled") else T("lbl_trades_off"))
            if self._trades_missing:
                extra += " " + T("lbl_trades_missing", n=self._trades_missing)
            note = (note + " " if note else "") + extra
            note += self._reconcile_text()
        self.fx_label.setText(note)
        if self._entries_dlg is not None:
            try:
                self._entries_dlg.refresh()
            except RuntimeError:
                self._entries_dlg = None

    def _reconcile_text(self):
        """Abgleich mit dem Saldo laut Bank-CSV (nur netto sinnvoll)."""
        bi = bank_info(self.account)
        if not bi.get("saldo") or not self.net_mode:
            return ""
        ts = trade_settings(self.account)
        if not ts.get("enabled") or str(ts.get("start", ""))[:10] > str(bi.get("from", "")):
            return ""              # Startdatum nach CSV-Beginn: Anfangssaldo von Hand
        rows = bank_reconcile(self.account, self.entries())
        bad = [r for r in rows if abs(r[4]) >= 0.01]
        src = bi.get("source", "Bank")
        if not bad:
            d = max((r[1] for r in rows), default="")
            return "\n" + T("lbl_reconcile_ok", source=src, date=_fmt_date(d))
        items = "; ".join(T("lbl_reconcile_item", cur=c, diff=self._fmt(diff),
                            bank=self._fmt(bank), date=_fmt_date(d))
                          for c, d, bank, _calc, diff in bad)
        return "\n⚠️ " + T("lbl_reconcile_diff", source=src, items=items)

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
        hidden = [c for c in range(self.table.columnCount()) if self.table.isColumnHidden(c)]
        headers = [h for c, h in enumerate(headers) if c not in hidden]
        rows = [tuple(v for c, v in enumerate(r) if c not in hidden) for r in rows]
        rows.append(tuple([""] * (len(headers) - 1) + [self.total_label.text()]))
        title = T("title_all").replace("💰 ", "") if self.view == VIEW_ALL else T("export_title")
        return {"title": title, "headers": headers, "rows": rows}

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
        dlg = BookingDialog(self.currencies(), preset, self,
                            div_scope=self.view == VIEW_DIV)
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
    def start_sync(self, fx_only=False):
        """Dividenden + Wechselkurse laden. fx_only=True: nur fehlende Wechselkurse
        (Ansichtswechsel, Abruf von heute im Cache)."""
        fx_only = fx_only is True        # clicked(bool) des Buttons → voller Abruf
        if self._worker is not None and self._worker.isRunning():
            return
        g = self._gains
        if g is not None and g._worker is not None and g._worker.isRunning():
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(500, lambda: self.start_sync(fx_only))  # warten, bis Gewinne geladen sind
            return
        if fx_only:
            positions = {}
            curs = {c for c in self.currencies() if c not in self._fx}
            if not curs:
                return
        else:
            self._fx_failed.clear()
            positions = {s: copy.deepcopy(p) for s, p in self._portfolio.items()
                         if p and not self._skip(s)}
            curs = set(self.currencies())
        if self._before_fetch:
            try:
                self._before_fetch()      # z. B. laufende Chart-Worker anhalten
            except Exception:
                pass
        w = _SyncWorker(positions, copy.deepcopy(self.account["symbols"]), curs, self._base,
                        known_cur=self._known_cur, fx_only=fx_only)
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
        if result.get("fx_only"):
            # Nur Wechselkurse nachgeladen: Dividenden bleiben, kein Speichern nötig
            got = result.get("fx") or {}
            self._fx_failed |= {c for c in self.currencies() if c not in self._fx and c not in got}
            if got:
                self._fx.update(got)
                self.account["fx"] = {"base": self._base,
                                      "rates": {k: v for k, v in self._fx.items()}}
            self.refresh()
            self._start_gains_fetch()
            return
        self.account["symbols"].update(result.get("meta", {}))
        n_new, n_upd = merge_dividends(self.account, result.get("computed", {}),
                                       [s for s in self._portfolio if not self._skip(s)])
        if result.get("fx"):
            self._fx.update(result["fx"])
            self.account["fx"] = {"base": self._base,
                                  "rates": {k: v for k, v in self._fx.items()}}
        self._fx_failed |= {c for c in self.currencies() if c not in self._fx}
        # Heute nicht nochmals automatisch laden (auch wenn einzelne Symbole fehlen –
        # sonst würde ein Symbol ohne Yahoo-Daten jedes Öffnen verlangsamen)
        from datetime import datetime as _dt
        self.account["settings"]["last_sync"] = {
            "day": date.today().isoformat(), "time": _dt.now().strftime("%H:%M"),
            "sig": self._sig}
        msg = T("status_done", new=n_new, upd=n_upd)
        if result.get("errors"):
            msg += "  │  " + T("status_errors", syms=", ".join(result["errors"]))
            if result.get("first_error"):
                msg += "  (" + result["first_error"][:160] + ")"
        self.status.setText(msg)
        self.changed()
        self._start_gains_fetch()

    def _stop_worker(self, *_):
        if self._gains is not None:
            try:
                self._gains.stop()
            except RuntimeError:
                pass
        self._show_overlay(False)
        w = self._worker
        if w is not None and w.isRunning():
            try:
                w.progress.disconnect(); w.done.disconnect()
            except Exception:
                pass
            w.requestInterruption()
        self._worker = None
