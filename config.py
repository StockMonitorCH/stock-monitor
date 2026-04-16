"""
config.py – App-Konfiguration für Stock Monitor
================================================
Speichert globale Einstellungen (Sprache, etc.) in ~/.stock_monitor_config.json
Unabhängig von Portfolio-Daten (.smpf).
"""

import os
import sys
import json

def _get_data_home() -> str:
    if sys.platform == "win32":
        try:
            base = (os.path.dirname(os.path.abspath(sys.executable))
                    if getattr(sys, 'frozen', False)
                    else os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(base, "_internal")
        except Exception:
            pass
    return os.path.expanduser("~")

CONFIG_PATH = os.path.join(_get_data_home(), ".stock_monitor_config.json")

_DEFAULTS = {
    "language":         "DE",    # "DE" | "EN"
    "number_format":    "CH",    # "CH" | "DE" | "US"
    "date_format":      "EU",    # "EU" | "ISO" | "US"
    # ── Globale Chart-Einstellungen ──────────────────────────────────────────
    "global_timeframe": "1mo",   # interner Wert z.B. "1mo", "1y", "2y"
    "global_ma20":      False,
    "global_ma50":      False,
    "global_ma200":     False,
    "global_trend":     False,
    "global_beta":      False,
    "global_alpha":     False,
    "global_target":    False,
    "auto_refresh":     "Keine", # "Keine" | "30 Sek" | "1 Min" | "5 Min"
    # ── Persistente Zeitraum-Auswahl der Dialoge ─────────────────────────────
    "indices_period":   "ytd",
    "perf_period":      "1y",
    "ai_balance_period":"cost",
    "dividend_period":  "1y",
    "sector_period":    "1y",
    "perf3d_period":          "1y",
    "perf3d_custom_start":    "",
    "perf3d_custom_end":      "",
    "compare_timeframe":      "",
    "compare_custom_start":   "",
    "compare_custom_end":     "",
    "mc_horizon":       5,       # Monte Carlo Zeithorizont in Jahren
    "mc_sims":          1000,    # Monte Carlo Simulationsanzahl
    "portfolio_currency": "USD", # Anzeigewährung: "USD" | "CHF" | "EUR" | "GBP"
}


def load_config() -> dict:
    """Lädt die Konfiguration. Gibt Defaults zurück wenn Datei fehlt."""
    if not os.path.exists(CONFIG_PATH):
        return _DEFAULTS.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Fehlende Keys mit Defaults auffüllen
        for k, v in _DEFAULTS.items():
            if k not in data:
                data[k] = v
        return data
    except Exception:
        return _DEFAULTS.copy()


def save_config(updates: dict) -> None:
    """Speichert einzelne Keys in die Konfigurationsdatei (merge, kein Überschreiben)."""
    cfg = load_config()
    cfg.update(updates)
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[config] Speichern fehlgeschlagen: {e}")


def get_language() -> str:
    return load_config().get("language", "DE")


def get_number_format() -> str:
    return load_config().get("number_format", "CH")


def get_date_format() -> str:
    """Gibt das Datumsformat zurück: 'EU' | 'ISO' | 'US'"""
    return load_config().get("date_format", "EU")


def get_global_timeframe() -> str:
    """Gibt den globalen Zeitraum als internen Wert zurück (z.B. '1mo', '2y')."""
    return load_config().get("global_timeframe", "1mo")


def get_global_chart_settings() -> dict:
    """Gibt alle globalen Chart-Einstellungen zurück."""
    cfg = load_config()
    return {
        "global_timeframe": cfg.get("global_timeframe", "1mo"),
        "global_ma20":      cfg.get("global_ma20",  False),
        "global_ma50":      cfg.get("global_ma50",  False),
        "global_ma200":     cfg.get("global_ma200", False),
        "global_trend":     cfg.get("global_trend", False),
        "global_beta":      cfg.get("global_beta",  False),
        "global_alpha":     cfg.get("global_alpha", False),
        "global_target":    cfg.get("global_target", False),
        "auto_refresh":     cfg.get("auto_refresh", "Keine"),
        # ── Persistente Zeitraum-Auswahl der Dialoge ─────────────────────
        "indices_period":    cfg.get("indices_period",    "ytd"),
        "perf_period":       cfg.get("perf_period",       "1y"),
        "ai_balance_period": cfg.get("ai_balance_period", "cost"),
        "dividend_period":   cfg.get("dividend_period",   "1y"),
        "sector_period":     cfg.get("sector_period",     "1y"),
        "perf3d_period":          cfg.get("perf3d_period",          "1y"),
        "perf3d_custom_start":    cfg.get("perf3d_custom_start",    ""),
        "perf3d_custom_end":      cfg.get("perf3d_custom_end",      ""),
        "compare_timeframe":      cfg.get("compare_timeframe",      ""),
        "compare_custom_start":   cfg.get("compare_custom_start",   ""),
        "compare_custom_end":     cfg.get("compare_custom_end",     ""),
        "mc_horizon":        cfg.get("mc_horizon",        5),
        "mc_sims":           cfg.get("mc_sims",           1000),
        "portfolio_currency": cfg.get("portfolio_currency", "USD"),
    }


def fmt_date(d, include_time: bool = False) -> str:
    """
    Formatiert ein Datum gemäss globaler Einstellung.
    d kann sein: datetime, date, pd.Timestamp, oder ISO-String 'YYYY-MM-DD'.
    include_time=True fügt HH:MM an (nur bei EU/ISO/US).
    """
    from datetime import datetime, date
    if d is None:
        return ""
    # String → datetime
    if isinstance(d, str):
        s = d.strip()
        if not s:
            return ""
        try:
            d = datetime.strptime(s[:10], "%Y-%m-%d")
        except ValueError:
            return s  # unbekanntes Format → unverändert zurück
    # pd.Timestamp → datetime
    try:
        import pandas as pd
        if isinstance(d, pd.Timestamp):
            d = d.to_pydatetime()
    except ImportError:
        pass
    # date → datetime
    if isinstance(d, date) and not isinstance(d, datetime):
        d = datetime(d.year, d.month, d.day)

    fmt_key = load_config().get("date_format", "EU")
    if fmt_key == "ISO":
        date_str = d.strftime("%Y-%m-%d")
        time_str = d.strftime(" %H:%M") if include_time else ""
    elif fmt_key == "US":
        date_str = d.strftime("%m/%d/%Y")
        time_str = d.strftime(" %H:%M") if include_time else ""
    else:  # EU (default)
        date_str = d.strftime("%d.%m.%Y")
        time_str = d.strftime(" %H:%M") if include_time else ""
    return date_str + time_str
