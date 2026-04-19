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

def save_portfolio(name: str, portfolio_data: dict, password: str,
                   price_cache: dict = None, sector_cache: dict = None) -> str:
    """Speichert portfolio_data als verschlüsselte .smpf-Datei. Gibt Pfad zurück."""
    if not CRYPTO_AVAILABLE:
        raise CryptoNotAvailableError("cryptography nicht installiert.")
    payload = {
        "name":         name,
        "created":      time.time(),
        "version":      1,
        "positions":    portfolio_data,
        "price_cache":  price_cache  or {},
        "sector_cache": sector_cache or {},
    }
    blob = encrypt_data(payload, password)
    path = portfolio_path(name)
    tmp  = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(blob)
    os.replace(tmp, path)
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
                   sector_cache=data.get("sector_cache", {}))
