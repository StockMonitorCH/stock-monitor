"""
portfolio_db.py – Verschlüsselte Portfolio-Dateien für Stock Monitor
=====================================================================
Jedes Portfolio wird als eigene .smpf-Datei gespeichert (Stock Monitor Portfolio File).
Jede Datei hat ihr eigenes Passwort → portabel, exportierbar, auf anderem PC einlesbar.

Format:    MAGIC | SALT (32B) | NONCE (12B) | AES-256-GCM(JSON-Daten)
JSON:      {"name": str, "created": float, "positions": {sym: [...]},
            "price_cache": {...}, "sector_cache": {...}}

Abhängigkeiten (einmalig installieren):
  pip install cryptography --break-system-packages
"""

import os
import sys
import json
import time
import shutil

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

def _get_portfolio_dir() -> str:
    if os.path.exists("/.flatpak-info"):
        xdg = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        return os.path.join(xdg, "stock-monitor", "portfolios")
    return os.path.join(_get_data_home(), ".stock_monitor_portfolios")

try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# ── Konstanten ────────────────────────────────────────────────────────────────
PORTFOLIO_DIR  = _get_portfolio_dir()
PBKDF2_ITER    = 600_000       # OWASP-Empfehlung 2024
SALT_LEN       = 32            # 256 Bit Salt
NONCE_LEN      = 12            # 96 Bit GCM-Nonce
KEY_LEN        = 32            # 256 Bit AES-Key
MAGIC          = b"SMPF\x01"  # Stock Monitor Portfolio File v1
FILE_EXT       = ".smpf"
PRICE_TTL      = 300           # 5 Minuten
SECTOR_TTL     = 7 * 86400     # 7 Tage
DB_PATH        = os.path.join(_get_data_home(), ".stock_monitor_db.enc")  # Legacy


class WrongPasswordError(Exception):
    pass

class CryptoNotAvailableError(Exception):
    pass


# ── Krypto ────────────────────────────────────────────────────────────────────

def _derive_key(password: str, salt: bytes) -> bytes:
    if not CRYPTO_AVAILABLE:
        raise CryptoNotAvailableError(
            "Die 'cryptography'-Bibliothek fehlt.\n"
            "Installieren mit:  pip install cryptography --break-system-packages"
        )
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LEN,
        salt=salt,
        iterations=PBKDF2_ITER,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_data(data: dict, password: str) -> bytes:
    salt  = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key   = _derive_key(password, salt)
    plain = json.dumps(data, ensure_ascii=False).encode("utf-8")
    ct    = AESGCM(key).encrypt(nonce, plain, None)
    return MAGIC + salt + nonce + ct


def decrypt_data(blob: bytes, password: str) -> dict:
    if not blob.startswith(MAGIC):
        raise WrongPasswordError("Ungültiges Dateiformat (kein .smpf).")
    offset = len(MAGIC)
    salt   = blob[offset: offset + SALT_LEN];  offset += SALT_LEN
    nonce  = blob[offset: offset + NONCE_LEN]; offset += NONCE_LEN
    ct     = blob[offset:]
    key    = _derive_key(password, salt)
    try:
        plain = AESGCM(key).decrypt(nonce, ct, None)
        return json.loads(plain.decode("utf-8"))
    except Exception:
        raise WrongPasswordError("Falsches Passwort oder beschädigte Datei.")


# ── Datei-Hilfsfunktionen ─────────────────────────────────────────────────────

def _safe_name(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in " _-").strip()


def portfolio_path(name: str) -> str:
    os.makedirs(PORTFOLIO_DIR, exist_ok=True)
    return os.path.join(PORTFOLIO_DIR, _safe_name(name) + FILE_EXT)


def portfolio_exists(name: str) -> bool:
    return os.path.exists(portfolio_path(name))


# ── Haupt-API ─────────────────────────────────────────────────────────────────

def _payload(name, portfolio_data, price_cache=None, sector_cache=None,
             notes=None, div_account=None, closed=None, settings=None) -> dict:
    return {
        "name":         name,
        "created":      time.time(),
        "version":      1,
        "positions":    portfolio_data,
        "price_cache":  price_cache  or {},
        "sector_cache": sector_cache or {},
        "notes":        notes        or [],
        "div_account":  div_account  or {},
        "closed":       closed       or {},
        "settings":     settings     or {},
    }


def _write_atomic(path: str, blob: bytes) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(blob)
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass
    os.replace(tmp, path)


def save_portfolio(name: str, portfolio_data: dict, password: str,
                   price_cache: dict = None, sector_cache: dict = None,
                   notes: list = None, div_account: dict = None,
                   closed: dict = None, settings: dict = None) -> str:
    """Speichert portfolio_data als verschlüsselte .smpf-Datei. Gibt Pfad zurück.
    closed: Verkaufshistorie {sym: [{buy_date, buy_price, quantity, sell_date}]}
    (intern für Dividendenkonto/Steuern, nicht in der Hauptansicht).
    settings: portfoliobezogene Einstellungen (Limits, AI-Balance-Ziele …)."""
    if not CRYPTO_AVAILABLE:
        raise CryptoNotAvailableError("cryptography nicht installiert.")
    payload = {
        "name":         name,
        "created":      time.time(),
        "version":      1,
        "positions":    portfolio_data,
        "price_cache":  price_cache  or {},
        "sector_cache": sector_cache or {},
        "notes":        notes        or [],
        "div_account":  div_account  or {},
        "closed":       closed       or {},
        "settings":     settings     or {},
    }
    blob = encrypt_data(payload, password)
    path = portfolio_path(name)
    _write_atomic(path, blob)
    return path


def load_portfolio(name: str, password: str) -> dict:
    """Lädt und entschlüsselt .smpf. Keys: positions, price_cache, sector_cache, name."""
    path = portfolio_path(name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Portfolio nicht gefunden: {path}")
    with open(path, "rb") as f:
        blob = f.read()
    return decrypt_data(blob, password)


def load_from_file(filepath: str, password: str) -> dict:
    """Lädt .smpf von beliebigem Pfad (Import von anderem PC)."""
    with open(filepath, "rb") as f:
        blob = f.read()
    return decrypt_data(blob, password)


def list_portfolios() -> list:
    """Gibt Liste aller lokalen .smpf-Portfolios zurück."""
    os.makedirs(PORTFOLIO_DIR, exist_ok=True)
    result = []
    for fname in sorted(os.listdir(PORTFOLIO_DIR)):
        if fname.endswith(FILE_EXT):
            path = os.path.join(PORTFOLIO_DIR, fname)
            stat = os.stat(path)
            result.append({
                "name":    fname[:-len(FILE_EXT)],
                "path":    path,
                "size_kb": max(1, stat.st_size // 1024),
                "mtime":   stat.st_mtime,
            })
    return result


def delete_portfolio(name: str) -> None:
    path = portfolio_path(name)
    if os.path.exists(path):
        os.remove(path)


def export_portfolio(name: str, dest_path: str, password: str) -> None:
    """Exportiert .smpf an Zielort (Passwort wird vorher verifiziert)."""
    load_portfolio(name, password)   # Verifizierung
    shutil.copy2(portfolio_path(name), dest_path)


def import_portfolio_file(filepath: str, password: str, new_name: str = None) -> str:
    """Importiert .smpf von beliebigem Pfad in lokalen Ordner. Gibt Namen zurück."""
    data = load_from_file(filepath, password)
    name = new_name or data.get("name") or os.path.basename(filepath)[:-len(FILE_EXT)]
    dest = portfolio_path(name)
    shutil.copy2(filepath, dest)
    return name


def change_password(name: str, old_password: str, new_password: str) -> None:
    """Ändert das Passwort einer .smpf-Datei."""
    data = load_portfolio(name, old_password)
    save_portfolio(name, data["positions"], new_password,
                   price_cache=data.get("price_cache", {}),
                   sector_cache=data.get("sector_cache", {}),
                   notes=data.get("notes", []),
                   div_account=data.get("div_account", {}),
                   closed=data.get("closed", {}),
                   settings=data.get("settings", {}))


# ── Sitzung: automatisches Speichern ohne erneute Passworteingabe ───────────
# Die Schlüsselableitung (PBKDF2, 600'000 Runden) dauert bewusst lange. Für das
# automatische Speichern nach jeder Änderung wird der Schlüssel einmal pro
# Sitzung abgeleitet und nur im Arbeitsspeicher gehalten (nicht das Passwort).
# Jede Speicherung nutzt einen neuen Nonce (AES-GCM), das Salt bleibt gleich.

def open_session(name: str, password: str) -> dict:
    """Prüft das Passwort einer bestehenden .smpf und gibt eine Sitzung zurück.
    {"name", "salt", "key"} – WrongPasswordError bei falschem Passwort."""
    path = portfolio_path(name)
    with open(path, "rb") as f:
        blob = f.read()
    if not blob.startswith(MAGIC):
        raise WrongPasswordError("Ungültiges Dateiformat (kein .smpf).")
    o = len(MAGIC)
    salt, nonce = blob[o:o + SALT_LEN], blob[o + SALT_LEN:o + SALT_LEN + NONCE_LEN]
    key = _derive_key(password, salt)
    try:
        AESGCM(key).decrypt(nonce, blob[o + SALT_LEN + NONCE_LEN:], None)
    except Exception:
        raise WrongPasswordError("Falsches Passwort oder beschädigte Datei.")
    return {"name": name, "salt": salt, "key": key}


def new_session(name: str, password: str) -> dict:
    """Sitzung für ein neues Passwort (Speichern unter)."""
    salt = os.urandom(SALT_LEN)
    return {"name": name, "salt": salt, "key": _derive_key(password, salt)}


def save_with_session(session: dict, portfolio_data: dict, **kw) -> str:
    """Speichert mit dem Sitzungsschlüssel (schnell, kein PBKDF2)."""
    if not CRYPTO_AVAILABLE:
        raise CryptoNotAvailableError("cryptography nicht installiert.")
    payload = _payload(session["name"], portfolio_data, **kw)
    nonce = os.urandom(NONCE_LEN)
    plain = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ct = AESGCM(session["key"]).encrypt(nonce, plain, None)
    path = portfolio_path(session["name"])
    _write_atomic(path, MAGIC + session["salt"] + nonce + ct)
    return path


# ── Sicherungen (verschlüsselt wie das Original) ────────────────────────────
# Dateiname: <Portfolio>_<JJJJ-MM-TT_HHMMSS>_<grund>.smpf  in .backups/<Portfolio>/
# Aufbewahrung: die letzten 10, dazu je die neueste pro Tag (30 Tage) und pro
# Monat (12 Monate). Eine Sicherung ist nur wenige KB gross.
BACKUP_KEEP = 10
BACKUP_DAYS = 30
BACKUP_MONTHS = 12
BACKUP_REASONS = ("session", "import", "hourly", "overwrite", "restore")


def _backup_dir(name: str) -> str:
    return os.path.join(PORTFOLIO_DIR, ".backups", _safe_name(name))


def backup_portfolio(name: str, reason: str = "hourly"):
    """Kopiert die aktuelle .smpf in den Sicherungsordner und räumt alte auf.
    Gibt den Pfad der Sicherung zurück oder None (keine Datei vorhanden)."""
    src = portfolio_path(name)
    if not os.path.exists(src):
        return None
    d = _backup_dir(name)
    os.makedirs(d, exist_ok=True)
    reason = reason if reason in BACKUP_REASONS else "hourly"
    stamp = time.strftime("%Y-%m-%d_%H%M%S")
    base = f"{_safe_name(name)}_{stamp}_{reason}"
    dest = os.path.join(d, base + FILE_EXT)
    n = 1
    while os.path.exists(dest):
        n += 1
        dest = os.path.join(d, f"{base}-{n}{FILE_EXT}")
    shutil.copy2(src, dest)
    prune_backups(name)
    return dest


def prune_backups(name: str, now: float = None) -> None:
    """Aufbewahrungsregel anwenden (siehe oben)."""
    now = now or time.time()
    bl = list_backups(name)                      # neueste zuerst
    keep = {b["path"] for b in bl[:BACKUP_KEEP]}
    days, months = set(), set()
    for b in bl:
        t = time.localtime(b["mtime"])
        day, month = time.strftime("%Y-%m-%d", t), time.strftime("%Y-%m", t)
        age = now - b["mtime"]
        if age <= BACKUP_DAYS * 86400 and day not in days:
            days.add(day); keep.add(b["path"])
        if age <= BACKUP_MONTHS * 31 * 86400 and month not in months:
            months.add(month); keep.add(b["path"])
    for b in bl:
        if b["path"] not in keep:
            try:
                os.remove(b["path"])
            except OSError:
                pass


def list_backups(name: str) -> list:
    """Sicherungen eines Portfolios, neueste zuerst:
    [{"path", "file", "mtime", "size_kb", "reason"}]."""
    d = _backup_dir(name)
    if not os.path.isdir(d):
        return []
    out = []
    for f in os.listdir(d):
        if f.endswith(FILE_EXT):
            p = os.path.join(d, f)
            st = os.stat(p)
            # <Portfolio>_<Datum>_<grund>[-n] → grund (ältere Sicherungen ohne Grund: "")
            reason = f[:-len(FILE_EXT)].rsplit("_", 1)[-1].split("-")[0]
            out.append({"path": p, "file": f, "mtime": st.st_mtime,
                        "size_kb": max(1, st.st_size // 1024),
                        "reason": reason if reason in BACKUP_REASONS else ""})
    out.sort(key=lambda b: b["mtime"], reverse=True)
    return out


def portfolios_with_backups() -> list:
    """Namen aller Portfolios, für die es Sicherungen gibt."""
    root = os.path.join(PORTFOLIO_DIR, ".backups")
    if not os.path.isdir(root):
        return []
    return sorted(d for d in os.listdir(root)
                  if os.path.isdir(os.path.join(root, d)) and list_backups(d))


def summarize_backups(paths, password: str = None, session: dict = None) -> dict:
    """{pfad: {"n_sym", "n_pos"}} – ein Schlüssel je Salt (schnell, auch für viele
    Sicherungen). Mit session wird deren Schlüssel genutzt, wo das Salt passt.
    Nicht lesbare Dateien (anderes Passwort) fehlen im Ergebnis."""
    keys = {}
    if session:
        keys[session["salt"]] = session["key"]
    out = {}
    for p in paths:
        try:
            with open(p, "rb") as f:
                blob = f.read()
            if not blob.startswith(MAGIC):
                continue
            o = len(MAGIC)
            salt = blob[o:o + SALT_LEN]
            nonce = blob[o + SALT_LEN:o + SALT_LEN + NONCE_LEN]
            if salt not in keys:
                if password is None:
                    continue
                keys[salt] = _derive_key(password, salt)
            plain = AESGCM(keys[salt]).decrypt(nonce, blob[o + SALT_LEN + NONCE_LEN:], None)
            pos = (json.loads(plain.decode("utf-8")).get("positions") or {})
            out[p] = {"n_sym": len(pos), "n_pos": sum(len(v or []) for v in pos.values())}
        except Exception:
            continue
    return out


def restore_backup(name: str, backup_path: str) -> None:
    """Stellt eine Sicherung wieder her; der aktuelle Stand wird vorher
    seinerseits gesichert (Wiederherstellen ist damit umkehrbar)."""
    backup_portfolio(name, "restore")
    shutil.copy2(backup_path, portfolio_path(name))


def summarize_file(path: str, password: str) -> dict:
    """Kurzinfo zu einer (Sicherungs-)Datei: Anzahl Symbole/Positionen."""
    data = load_from_file(path, password)
    pos = data.get("positions") or {}
    return {"n_sym": len(pos), "n_pos": sum(len(v or []) for v in pos.values())}
