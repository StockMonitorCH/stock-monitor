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
    Exchange-Name → [date, date, ...]
    Nur Werktage (Wochenenden werden separat geprüft).

Nächste Pflege: Dezember 2027 für 2028.
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

# Easter 2026: April 5  |  Easter 2027: April 25
HOLIDAYS = {

    "NASDAQ / NYSE": [
        # 2026
        date(2026, 1, 1),   # New Year's Day
        date(2026, 1, 19),  # MLK Day
        date(2026, 2, 16),  # Presidents' Day
        date(2026, 4, 3),   # Good Friday
        date(2026, 5, 25),  # Memorial Day
        date(2026, 6, 19),  # Juneteenth
        date(2026, 7, 3),   # Independence Day (observed, Jul 4 = Saturday)
        date(2026, 9, 7),   # Labor Day
        date(2026, 11, 26), # Thanksgiving
        date(2026, 12, 25), # Christmas
        # 2027
        date(2027, 1, 1),   # New Year's Day
        date(2027, 1, 18),  # MLK Day
        date(2027, 2, 15),  # Presidents' Day
        date(2027, 4, 23),  # Good Friday
        date(2027, 5, 31),  # Memorial Day
        date(2027, 6, 18),  # Juneteenth (observed, Jun 19 = Saturday)
        date(2027, 7, 5),   # Independence Day (observed, Jul 4 = Sunday)
        date(2027, 9, 6),   # Labor Day
        date(2027, 11, 25), # Thanksgiving
        date(2027, 12, 24), # Christmas (observed, Dec 25 = Saturday)
    ],

    "SIX Swiss Exchange": [
        # 2026
        date(2026, 1, 1),   # Neujahr
        date(2026, 4, 3),   # Karfreitag
        date(2026, 4, 6),   # Ostermontag
        date(2026, 5, 1),   # Tag der Arbeit
        date(2026, 5, 14),  # Auffahrt
        date(2026, 5, 25),  # Pfingstmontag
        date(2026, 8, 3),   # Bundesfeiertag (Aug 1 = Saturday → observed Mon)
        date(2026, 12, 24), # Heiligabend
        date(2026, 12, 25), # Weihnachten
        date(2026, 12, 26), # Stephanstag
        date(2026, 12, 31), # Silvester
        # 2027
        date(2027, 1, 1),   # Neujahr
        date(2027, 4, 23),  # Karfreitag
        date(2027, 4, 26),  # Ostermontag
        date(2027, 6, 3),   # Auffahrt
        date(2027, 6, 14),  # Pfingstmontag
        date(2027, 8, 2),   # Bundesfeiertag (Aug 1 = Sunday → observed Mon)
        date(2027, 12, 24), # Heiligabend
        date(2027, 12, 31), # Silvester
    ],

    "XETRA": [
        # 2026
        date(2026, 1, 1),   # Neujahr
        date(2026, 4, 3),   # Karfreitag
        date(2026, 4, 6),   # Ostermontag
        date(2026, 5, 1),   # Tag der Arbeit
        date(2026, 12, 24), # Heiligabend
        date(2026, 12, 25), # 1. Weihnachtstag
        date(2026, 12, 26), # 2. Weihnachtstag
        date(2026, 12, 31), # Silvester
        # 2027
        date(2027, 1, 1),   # Neujahr
        date(2027, 4, 23),  # Karfreitag
        date(2027, 4, 26),  # Ostermontag
        date(2027, 12, 24), # Heiligabend
        date(2027, 12, 31), # Silvester
    ],

    "London Stock Exchange": [
        # 2026
        date(2026, 1, 1),   # New Year's Day
        date(2026, 4, 3),   # Good Friday
        date(2026, 4, 6),   # Easter Monday
        date(2026, 5, 4),   # Early May Bank Holiday
        date(2026, 5, 25),  # Spring Bank Holiday
        date(2026, 8, 31),  # Summer Bank Holiday
        date(2026, 12, 25), # Christmas Day
        date(2026, 12, 28), # Boxing Day (observed)
        # 2027
        date(2027, 1, 1),   # New Year's Day
        date(2027, 4, 23),  # Good Friday
        date(2027, 4, 26),  # Easter Monday
        date(2027, 5, 3),   # Early May Bank Holiday
        date(2027, 5, 31),  # Spring Bank Holiday
        date(2027, 8, 30),  # Summer Bank Holiday
        date(2027, 12, 27), # Christmas (observed, Dec 25 = Saturday)
        date(2027, 12, 28), # Boxing Day (observed, Dec 26 = Sunday)
    ],

    "Euronext Paris": [
        # 2026
        date(2026, 1, 1),   # New Year's Day
        date(2026, 4, 3),   # Good Friday
        date(2026, 4, 6),   # Easter Monday
        date(2026, 5, 1),   # Labour Day
        date(2026, 12, 25), # Christmas
        date(2026, 12, 26), # Boxing Day
        # 2027
        date(2027, 1, 1),
        date(2027, 4, 23),  # Good Friday
        date(2027, 4, 26),  # Easter Monday
        date(2027, 5, 1),   # Labour Day
        date(2027, 12, 26), # Boxing Day
    ],

    "Tokyo Stock Exchange": [
        # 2026
        date(2026, 1, 1),   date(2026, 1, 2),   date(2026, 1, 12),
        date(2026, 2, 11),  date(2026, 2, 23),  date(2026, 3, 20),
        date(2026, 4, 29),  date(2026, 5, 3),   date(2026, 5, 4),
        date(2026, 5, 5),   date(2026, 7, 20),  date(2026, 8, 11),
        date(2026, 9, 21),  date(2026, 9, 23),  date(2026, 10, 12),
        date(2026, 11, 3),  date(2026, 11, 23), date(2026, 12, 31),
        # 2027
        date(2027, 1, 1),   date(2027, 1, 2),   date(2027, 1, 11),
        date(2027, 2, 11),  date(2027, 2, 23),  date(2027, 3, 22),
        date(2027, 4, 29),  date(2027, 5, 3),   date(2027, 5, 4),
        date(2027, 5, 5),   date(2027, 7, 19),  date(2027, 8, 11),
        date(2027, 9, 20),  date(2027, 9, 23),  date(2027, 10, 11),
        date(2027, 11, 3),  date(2027, 11, 23), date(2027, 12, 31),
    ],

    "Hong Kong Stock Exchange": [
        # 2026
        date(2026, 1, 1),   date(2026, 2, 17),  date(2026, 2, 18),
        date(2026, 2, 19),  date(2026, 4, 3),   date(2026, 4, 6),
        date(2026, 5, 1),   date(2026, 7, 1),   date(2026, 10, 1),
        date(2026, 12, 25), date(2026, 12, 26),
        # 2027
        date(2027, 1, 1),   date(2027, 2, 6),   date(2027, 2, 7),
        date(2027, 2, 8),   date(2027, 4, 23),  date(2027, 4, 26),
        date(2027, 5, 1),   date(2027, 7, 1),   date(2027, 10, 1),
        date(2027, 12, 25), date(2027, 12, 27),
    ],

    "ASX": [
        # 2026
        date(2026, 1, 1),   date(2026, 1, 26),  date(2026, 4, 3),
        date(2026, 4, 6),   date(2026, 4, 25),  date(2026, 6, 8),
        date(2026, 12, 25), date(2026, 12, 26),
        # 2027
        date(2027, 1, 1),   date(2027, 1, 26),  date(2027, 4, 23),
        date(2027, 4, 26),  date(2027, 4, 25),  date(2027, 6, 14),
        date(2027, 12, 27), date(2027, 12, 28),
    ],

    "Toronto Stock Exchange": [
        # 2026
        date(2026, 1, 1),   date(2026, 2, 16),  date(2026, 4, 3),
        date(2026, 5, 18),  date(2026, 7, 1),   date(2026, 9, 7),
        date(2026, 10, 12), date(2026, 12, 25), date(2026, 12, 26),
        # 2027
        date(2027, 1, 1),   date(2027, 2, 15),  date(2027, 4, 23),
        date(2027, 5, 24),  date(2027, 7, 1),   date(2027, 9, 6),
        date(2027, 10, 11), date(2027, 12, 27), date(2027, 12, 28),
    ],

}

# Geteilte Feiertage
for _exch in ("Frankfurt", "München", "Hamburg", "Berlin", "Stuttgart"):
    HOLIDAYS[_exch] = HOLIDAYS["XETRA"]
for _exch in ("Euronext Amsterdam", "Euronext Brussels"):
    HOLIDAYS[_exch] = HOLIDAYS["Euronext Paris"]
HOLIDAYS["TSX Venture"] = HOLIDAYS["Toronto Stock Exchange"]
