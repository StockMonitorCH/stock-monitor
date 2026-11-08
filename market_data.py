"""
market_data.py – Börsen-Stammdaten für Stock Monitor
=====================================================
Enthält Öffnungszeiten, Zeitzonen und Feiertage aller unterstützten Börsen.

Jährliche Pflege: Nur diese Datei muss aktualisiert werden — stock_monitor.py
bleibt unverändert.

Struktur EXCHANGES:
    Suffix → (Exchange-Name, Zeitzone, Open, Close, Pre-Open, After-Close)
    Pre-Open / After-Close = None wenn nicht vorhanden

Struktur HOLIDAYS:
    Exchange-Name → [date, date, ...]   (sortiert, nur Werktage Mo–Fr)

Die meisten Börsenfeiertage folgen festen Regeln (fixes Datum, Ostern,
"3. Montag im Januar", Ersatztage). Sie werden für HOLIDAY_YEARS berechnet,
statt sie von Hand abzutippen. Einmalige Schliessungen (Staatstrauer usw.)
stehen in _SPECIAL_CLOSED, Feiertage nach Mondkalender (Hongkong) in
_MANUAL_HOLIDAYS – diese können nur aus den offiziellen Kalendern ergänzt werden.

Börsen ohne Eintrag (China, Korea, Singapur, Indien, Tel Aviv): Feiertage
werden erst kurzfristig offiziell festgelegt → bewusst leer; Prüfungen in der
App beschränken sich dort auf das Wochenende.

Pflege: HOLIDAY_YEARS erweitern; _MANUAL_HOLIDAYS (HK) jährlich ergänzen.
"""

from datetime import date

EXCHANGES = {
    "":     ("NASDAQ / NYSE",            "America/New_York",      "09:30", "16:00", "04:00", "20:00"),
    "=F":   ("CME Futures",              "America/Chicago",       "08:30", "15:15", None,    None),
    ".SW":  ("SIX Swiss Exchange",       "Europe/Zurich",         "09:00", "17:30", None,    None),
    ".DE":  ("XETRA",                    "Europe/Berlin",         "09:00", "17:30", "08:00", "20:00"),
    ".F":   ("Frankfurt",                "Europe/Berlin",         "08:00", "20:00", None,    None),
    ".MU":  ("München",                  "Europe/Berlin",         "08:00", "20:00", None,    None),
    ".HM":  ("Hamburg",                  "Europe/Berlin",         "08:00", "20:00", None,    None),
    ".BE":  ("Berlin",                   "Europe/Berlin",         "08:00", "20:00", None,    None),
    ".SG":  ("Stuttgart",                "Europe/Berlin",         "08:00", "20:00", None,    None),
    ".L":   ("London Stock Exchange",    "Europe/London",         "08:00", "16:30", None,    None),
    ".PA":  ("Euronext Paris",           "Europe/Paris",          "09:00", "17:30", None,    None),
    ".AS":  ("Euronext Amsterdam",       "Europe/Amsterdam",      "09:00", "17:30", None,    None),
    ".BR":  ("Euronext Brussels",        "Europe/Brussels",       "09:00", "17:30", None,    None),
    ".LS":  ("Euronext Lisbon",          "Europe/Lisbon",         "08:00", "16:30", None,    None),
    ".MC":  ("Bolsa de Madrid",          "Europe/Madrid",         "09:00", "17:35", None,    None),
    ".MI":  ("Borsa Italiana",           "Europe/Rome",           "09:00", "17:30", None,    None),
    ".VI":  ("Wiener Börse",             "Europe/Vienna",         "09:00", "17:35", None,    None),
    ".ST":  ("Nasdaq Stockholm",         "Europe/Stockholm",      "09:00", "17:30", None,    None),
    ".OL":  ("Oslo Børs",               "Europe/Oslo",           "09:00", "16:25", None,    None),
    ".CO":  ("Nasdaq Copenhagen",        "Europe/Copenhagen",     "09:00", "17:00", None,    None),
    ".HE":  ("Nasdaq Helsinki",          "Europe/Helsinki",       "09:00", "17:30", None,    None),
    ".T":   ("Tokyo Stock Exchange",     "Asia/Tokyo",            "09:00", "15:30", None,    None),
    ".HK":  ("Hong Kong Stock Exchange", "Asia/Hong_Kong",        "09:30", "16:00", None,    None),
    ".SS":  ("Shanghai Stock Exchange",  "Asia/Shanghai",         "09:30", "15:00", None,    None),
    ".SZ":  ("Shenzhen Stock Exchange",  "Asia/Shanghai",         "09:30", "15:00", None,    None),
    ".KS":  ("Korea Stock Exchange",     "Asia/Seoul",            "09:00", "15:30", None,    None),
    ".SI":  ("Singapore Exchange",       "Asia/Singapore",        "09:00", "17:00", None,    None),
    ".BO":  ("BSE India",                "Asia/Kolkata",          "09:15", "15:30", None,    None),
    ".NS":  ("NSE India",                "Asia/Kolkata",          "09:15", "15:30", None,    None),
    ".AX":  ("ASX",                      "Australia/Sydney",      "10:00", "16:00", None,    None),
    ".NZ":  ("NZX",                      "Pacific/Auckland",      "10:00", "17:00", None,    None),
    ".TO":  ("Toronto Stock Exchange",   "America/Toronto",       "09:30", "16:00", None,    None),
    ".V":   ("TSX Venture",              "America/Toronto",       "09:30", "16:00", None,    None),
    ".MX":  ("Bolsa Mexicana",           "America/Mexico_City",   "08:30", "15:00", None,    None),
    ".SA":  ("B3 São Paulo",             "America/Sao_Paulo",     "10:00", "17:55", None,    None),
    ".JO":  ("Johannesburg Stock Exchange", "Africa/Johannesburg","09:00", "17:00", None,    None),
    ".TA":  ("Tel Aviv Stock Exchange",  "Asia/Jerusalem",        "09:59", "17:25", None,    None),
}

CRYPTO_SUFFIXES = ('-USD', '-EUR', '-CHF', '-BTC', '-USDT')
CRYPTO_EXCHANGE = ("Crypto (24/7)", "UTC", "00:00", "23:59", None, None)

from datetime import timedelta as _td

HOLIDAY_YEARS = range(2024, 2029)   # 2024 … 2028

# ── Hilfsfunktionen ──────────────────────────────────────────────────────────
def _easter(y: int) -> date:
    """Ostersonntag (gregorianisch, Meeus/Jones/Butcher)."""
    a = y % 19; b = y // 100; c = y % 100
    d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4; k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(y, month, day)


def _nth(y, m, wd, n):
    """n-ter Wochentag wd (0=Mo) im Monat; n=-1 = letzter."""
    if n > 0:
        d = date(y, m, 1)
        d += _td(days=(wd - d.weekday()) % 7)
        return d + _td(weeks=n - 1)
    d = date(y + (m == 12), m % 12 + 1, 1) - _td(days=1)
    return d - _td(days=(d.weekday() - wd) % 7)


def _sat_fri_sun_mon(d):
    """US-Regel: Samstag → Freitag davor, Sonntag → Montag danach."""
    if d.weekday() == 5:
        return d - _td(days=1)
    if d.weekday() == 6:
        return d + _td(days=1)
    return d


def _sun_mon(d):
    """Sonntag → Montag (Samstag entfällt)."""
    return d + _td(days=1) if d.weekday() == 6 else d


def _mondayise(d):
    """Samstag/Sonntag → folgender Montag."""
    return d + _td(days=(7 - d.weekday()) % 7) if d.weekday() >= 5 else d


def _pair_mondayise(d1):
    """Zwei aufeinanderfolgende Feiertage (25./26.12., 1./2.1. NZ) mit
    britischer Ersatzregel: fallen sie aufs Wochenende, rücken sie auf die
    nächsten freien Werktage."""
    out = []
    for d in (d1, d1 + _td(days=1)):
        while d.weekday() >= 5 or d in out:
            d += _td(days=1)
        out.append(d)
    return out


def _jp_equinox(y, spring=True):
    base = 20.8431 if spring else 23.2488
    day = int(base + 0.242194 * (y - 1980) - (y - 1980) // 4)
    return date(y, 3 if spring else 9, day)


# ── Regeln je Börse (Rückgabe: Feiertage eines Jahres, Wochenenden egal) ─────
def _nyse(y):
    e = _easter(y)
    hs = [_sat_fri_sun_mon(date(y, 1, 1)) if date(y, 1, 1).weekday() != 5 else None,
          _nth(y, 1, 0, 3), _nth(y, 2, 0, 3), e - _td(days=2), _nth(y, 5, 0, -1),
          _sat_fri_sun_mon(date(y, 6, 19)), _sat_fri_sun_mon(date(y, 7, 4)),
          _nth(y, 9, 0, 1), _nth(y, 11, 3, 4), _sat_fri_sun_mon(date(y, 12, 25))]
    return [d for d in hs if d]


def _six(y):
    e = _easter(y)
    return [date(y, 1, 1), date(y, 1, 2), e - _td(days=2), e + _td(days=1),
            date(y, 5, 1), e + _td(days=39), e + _td(days=50), date(y, 8, 1),
            date(y, 12, 24), date(y, 12, 25), date(y, 12, 26), date(y, 12, 31)]


def _xetra(y):
    e = _easter(y)
    return [date(y, 1, 1), e - _td(days=2), e + _td(days=1), date(y, 5, 1),
            date(y, 12, 24), date(y, 12, 25), date(y, 12, 26), date(y, 12, 31)]


def _lse(y):
    e = _easter(y)
    return [_mondayise(date(y, 1, 1)), e - _td(days=2), e + _td(days=1),
            _nth(y, 5, 0, 1), _nth(y, 5, 0, -1), _nth(y, 8, 0, -1),
            *_pair_mondayise(date(y, 12, 25))]


def _euronext(y):            # Paris, Amsterdam, Brüssel, Lissabon (keine Ersatztage)
    e = _easter(y)
    return [date(y, 1, 1), e - _td(days=2), e + _td(days=1), date(y, 5, 1),
            date(y, 12, 25), date(y, 12, 26)]


def _madrid(y):              # BME: TARGET-Kalender
    return _euronext(y)


def _milano(y):
    e = _easter(y)
    return [date(y, 1, 1), e - _td(days=2), e + _td(days=1), date(y, 5, 1),
            date(y, 8, 15), date(y, 12, 24), date(y, 12, 25), date(y, 12, 26),
            date(y, 12, 31)]


def _wien(y):
    e = _easter(y)
    return [date(y, 1, 1), e - _td(days=2), e + _td(days=1), date(y, 5, 1),
            e + _td(days=50), date(y, 12, 24), date(y, 12, 25), date(y, 12, 26),
            date(y, 12, 31)]


def _midsummer_eve(y):       # Freitag zwischen 19. und 25. Juni
    d = date(y, 6, 19)
    return d + _td(days=(4 - d.weekday()) % 7)


def _stockholm(y):
    e = _easter(y)
    return [date(y, 1, 1), date(y, 1, 6), e - _td(days=2), e + _td(days=1),
            date(y, 5, 1), e + _td(days=39), date(y, 6, 6), _midsummer_eve(y),
            date(y, 12, 24), date(y, 12, 25), date(y, 12, 26), date(y, 12, 31)]


def _oslo(y):
    e = _easter(y)
    return [date(y, 1, 1), e - _td(days=3), e - _td(days=2), e + _td(days=1),
            date(y, 5, 1), date(y, 5, 17), e + _td(days=39), e + _td(days=50),
            date(y, 12, 24), date(y, 12, 25), date(y, 12, 26), date(y, 12, 31)]


def _copenhagen(y):          # Store Bededag ab 2024 abgeschafft
    e = _easter(y)
    return [date(y, 1, 1), e - _td(days=3), e - _td(days=2), e + _td(days=1),
            e + _td(days=39), e + _td(days=40), e + _td(days=50), date(y, 6, 5),
            date(y, 12, 24), date(y, 12, 25), date(y, 12, 26), date(y, 12, 31)]


def _helsinki(y):
    e = _easter(y)
    return [date(y, 1, 1), date(y, 1, 6), e - _td(days=2), e + _td(days=1),
            date(y, 5, 1), e + _td(days=39), _midsummer_eve(y), date(y, 12, 6),
            date(y, 12, 24), date(y, 12, 25), date(y, 12, 26), date(y, 12, 31)]


def _toronto(y):
    e = _easter(y)
    victoria = date(y, 5, 24) - _td(days=date(y, 5, 24).weekday())   # Mo vor 25.5.
    return [_mondayise(date(y, 1, 1)), _nth(y, 2, 0, 3), e - _td(days=2), victoria,
            _mondayise(date(y, 7, 1)), _nth(y, 8, 0, 1), _nth(y, 9, 0, 1),
            _nth(y, 10, 0, 2), *_pair_mondayise(date(y, 12, 25))]


def _asx(y):                 # Anzac Day ohne Ersatztag
    e = _easter(y)
    return [_mondayise(date(y, 1, 1)), _mondayise(date(y, 1, 26)), e - _td(days=2),
            e + _td(days=1), date(y, 4, 25), _nth(y, 6, 0, 2),
            *_pair_mondayise(date(y, 12, 25))]


_MATARIKI = {2024: date(2024, 6, 28), 2025: date(2025, 6, 20), 2026: date(2026, 7, 10),
             2027: date(2027, 6, 25), 2028: date(2028, 7, 14)}   # gesetzlich festgelegt


def _nzx(y):
    e = _easter(y)
    hs = [*_pair_mondayise(date(y, 1, 1)), _mondayise(date(y, 2, 6)), e - _td(days=2),
          e + _td(days=1), _mondayise(date(y, 4, 25)), _nth(y, 6, 0, 1),
          _nth(y, 10, 0, 4), *_pair_mondayise(date(y, 12, 25))]
    if y in _MATARIKI:
        hs.append(_MATARIKI[y])
    return hs


def _jse(y):                 # Südafrika: Sonntag → Montag
    e = _easter(y)
    return [_sun_mon(date(y, m, d)) for m, d in
            ((1, 1), (3, 21), (4, 27), (5, 1), (6, 16), (8, 9), (9, 24),
             (12, 16), (12, 25), (12, 26))] + [e - _td(days=2), e + _td(days=1)]


def _bmv(y):                 # Bolsa Mexicana
    e = _easter(y)
    return [date(y, 1, 1), _nth(y, 2, 0, 1), _nth(y, 3, 0, 3), e - _td(days=3),
            e - _td(days=2), date(y, 5, 1), date(y, 9, 16), _nth(y, 11, 0, 3),
            date(y, 12, 12), date(y, 12, 25)]


def _b3(y):                  # B3 São Paulo
    e = _easter(y)
    return [date(y, 1, 1), e - _td(days=48), e - _td(days=47), e - _td(days=2),
            date(y, 4, 21), date(y, 5, 1), e + _td(days=60), date(y, 9, 7),
            date(y, 10, 12), date(y, 11, 2), date(y, 11, 15), date(y, 11, 20),
            date(y, 12, 24), date(y, 12, 25), date(y, 12, 31)]


def _tokyo(y):
    hs = {date(y, 1, 1), _nth(y, 1, 0, 2), date(y, 2, 11), date(y, 2, 23),
          _jp_equinox(y, True), date(y, 4, 29), date(y, 5, 3), date(y, 5, 4),
          date(y, 5, 5), _nth(y, 7, 0, 3), date(y, 8, 11), _nth(y, 9, 0, 3),
          _jp_equinox(y, False), _nth(y, 10, 0, 2), date(y, 11, 3), date(y, 11, 23)}
    # Ersatzfeiertag: Feiertag am Sonntag → nächster Nicht-Feiertag
    for d in sorted(hs):
        if d.weekday() == 6:
            n = d + _td(days=1)
            while n in hs:
                n += _td(days=1)
            hs.add(n)
    # "Bürgerfeiertag": Tag zwischen zwei Feiertagen
    for d in sorted(hs):
        n = d + _td(days=2)
        if n in hs and (d + _td(days=1)) not in hs and (d + _td(days=1)).weekday() != 6:
            hs.add(d + _td(days=1))
    # Börse zusätzlich geschlossen: 2./3. Januar, 31. Dezember
    hs |= {date(y, 1, 2), date(y, 1, 3), date(y, 12, 31)}
    return list(hs)


_RULES = {
    "NASDAQ / NYSE":           _nyse,
    "CME Futures":             _nyse,
    "SIX Swiss Exchange":      _six,
    "XETRA":                   _xetra,
    "London Stock Exchange":   _lse,
    "Euronext Paris":          _euronext,
    "Euronext Lisbon":         _euronext,
    "Bolsa de Madrid":         _madrid,
    "Borsa Italiana":          _milano,
    "Wiener Börse":            _wien,
    "Nasdaq Stockholm":        _stockholm,
    "Oslo Børs":               _oslo,
    "Nasdaq Copenhagen":       _copenhagen,
    "Nasdaq Helsinki":         _helsinki,
    "Toronto Stock Exchange":  _toronto,
    "ASX":                     _asx,
    "NZX":                     _nzx,
    "Johannesburg Stock Exchange": _jse,
    "Bolsa Mexicana":          _bmv,
    "B3 São Paulo":            _b3,
    "Tokyo Stock Exchange":    _tokyo,
}

# Einmalige Schliessungen (nicht aus Regeln ableitbar)
_SPECIAL_CLOSED = {
    "NASDAQ / NYSE": [date(2025, 1, 9)],   # Staatstrauer Jimmy Carter
}

# Feiertage nach Mondkalender – nur aus offiziellen Kalendern (HKEX) eintragen
_MANUAL_HOLIDAYS = {
    "Hong Kong Stock Exchange": [
        # 2026
        date(2026, 1, 1),   date(2026, 2, 17),  date(2026, 2, 18),
        date(2026, 2, 19),  date(2026, 4, 3),   date(2026, 4, 6),
        date(2026, 5, 1),   date(2026, 7, 1),   date(2026, 10, 1),
        date(2026, 12, 25), date(2026, 12, 26),
        # 2027
        date(2027, 1, 1),   date(2027, 2, 6),   date(2027, 2, 7),
        date(2027, 2, 8),   date(2027, 3, 26),  date(2027, 3, 29),   # Karfreitag/Ostermontag
        date(2027, 5, 1),   date(2027, 7, 1),   date(2027, 10, 1),
        date(2027, 12, 25), date(2027, 12, 27),
    ],
}


def _build_holidays():
    out = {}
    for name, rule in _RULES.items():
        days = set()
        for y in HOLIDAY_YEARS:
            days.update(rule(y))
        days.update(_SPECIAL_CLOSED.get(name, []))
        out[name] = sorted(d for d in days if d.weekday() < 5)
    for name, days in _MANUAL_HOLIDAYS.items():
        out[name] = sorted(d for d in days if d.weekday() < 5)
    return out


HOLIDAYS = _build_holidays()

# Geteilte Feiertage
for _exch in ("Frankfurt", "München", "Hamburg", "Berlin", "Stuttgart"):
    HOLIDAYS[_exch] = HOLIDAYS["XETRA"]
for _exch in ("Euronext Amsterdam", "Euronext Brussels"):
    HOLIDAYS[_exch] = HOLIDAYS["Euronext Paris"]
HOLIDAYS["TSX Venture"] = HOLIDAYS["Toronto Stock Exchange"]
