# Stock Monitor – Flatpak Build-Anleitung
============================================

## Voraussetzungen (einmalig installieren)

```bash
# Fedora KDE (dein System)
sudo dnf install flatpak flatpak-builder python3-pip

# Flathub + KDE-Runtime hinzufügen
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install flathub org.kde.Platform//6.8 org.kde.Sdk//6.8

# flatpak-pip-generator (einmalig)
pip install flatpak-pip-generator --break-system-packages
```

---

## Verzeichnisstruktur

```
flatpak/
├── ch.stock-monitor.StockMonitor.yml   ← Flatpak-Manifest
├── requirements.txt                     ← Python-Pakete
├── sources/
│   ├── stock_monitor.py                ← App (alle .py Dateien)
│   ├── tax_module.py
│   ├── translations.py
│   ├── tax_translations.py
│   ├── help_texts.py
│   ├── world_map.py
│   ├── config.py
│   ├── market_data.py
│   ├── portfolio_db.py
│   ├── dividend_lists.json
│   ├── stock-monitor.sh                ← Starter-Skript
│   ├── stock-monitor-256.png           ← App-Icon (256×256 PNG) ← FEHLT NOCH
│   ├── ch.stock-monitor.StockMonitor.desktop
│   └── ch.stock-monitor.StockMonitor.metainfo.xml
└── BUILD.md                             ← diese Datei
```

---

## Schritt 1: Python-Abhängigkeiten generieren

Der `flatpak-pip-generator` erstellt eine JSON-Datei mit allen Wheel-URLs
und SHA256-Hashes – vollständig offline reproduzierbar:

```bash
cd flatpak/

flatpak-pip-generator \
  --runtime org.kde.Sdk//6.8 \
  --output generated-sources \
  --requirements-file requirements.txt
```

Das erzeugt `generated-sources.json` im aktuellen Verzeichnis.

> **Hinweis:** Dauert ~1–2 Minuten, lädt Metadaten von PyPI.

---

## Schritt 2: App-Quelldateien kopieren

```bash
# Alle Python-Dateien ins sources/-Verzeichnis
cp /pfad/zu/deiner/app/*.py sources/
cp /pfad/zu/deiner/app/dividend_lists.json sources/

# Icon: Ersetze mit deinem echten Icon (256×256 PNG)
cp /pfad/zu/icon.png sources/stock-monitor-256.png
```

---

## Schritt 3: Bauen (lokal, ohne Installation)

```bash
flatpak-builder \
  --force-clean \
  --repo=repo \
  build-dir \
  ch.stock-monitor.StockMonitor.yml
```

Erster Build: **15–30 Minuten** (lädt alle Wheels, kompiliert).
Folge-Builds: **2–5 Minuten** (gecacht).

---

## Schritt 4: Lokal testen

```bash
# Direkt ausführen (ohne Installation)
flatpak-builder --run build-dir ch.stock-monitor.StockMonitor.yml stock-monitor

# Oder als lokales Flatpak installieren
flatpak build-export repo build-dir
flatpak install --user repo ch.stock-monitor.StockMonitor
flatpak run ch.stock-monitor.StockMonitor
```

---

## Schritt 5: .flatpak-Bundle erstellen (für Weitergabe)

```bash
flatpak build-bundle repo stock-monitor.flatpak ch.stock-monitor.StockMonitor

# Installieren auf einem anderen Rechner:
flatpak install stock-monitor.flatpak
```

Die `.flatpak`-Datei enthält **alles** — kein Internet nötig beim Empfänger.

---

## Häufige Probleme

### WebEngine / Sandbox-Fehler
```
# Wenn die Weltkarte nicht lädt:
export QTWEBENGINE_DISABLE_SANDBOX=1
flatpak run ch.stock-monitor.StockMonitor
```
Das ist im Starter-Skript bereits gesetzt.

### Emoji fehlen auf KDE
KDE-Runtime enthält Noto Emoji — sollte automatisch funktionieren.
Falls nicht: `sudo dnf install google-noto-emoji-fonts` auf dem Host.

### yfinance-Netzwerkfehler im Flatpak
Prüfe ob `--share=network` im Manifest gesetzt ist (ist es).
Falls Firewall blockiert: Flatpak läuft im eigenen Namespace, aber
Netzwerk ist shared — normaler Browser-Proxy-Einstellungen gelten.

### Portfolios nicht gefunden
Portfolios liegen in `~/.stock_monitor_portfolios/` — durch `--filesystem=home`
hat das Flatpak vollen Zugriff. Bestehende Portfolios vom Nicht-Flatpak-System
sind sofort sichtbar.

---

## Für Flathub-Einreichung (später, nach GitHub)

1. GitHub-Repo erstellen: `github.com/timm/stock-monitor`
2. Separates Manifest-Repo: `github.com/flathub/ch.stock-monitor.StockMonitor`
3. Screenshots in `sources/screenshots/` ablegen + metainfo.xml aktualisieren
4. Pull Request auf `github.com/flathub/flathub` öffnen

Flathub-Doku: https://docs.flathub.org/docs/for-app-authors/submission

---

## PyQt6-WebEngine: Besonderheit

PyQt6-WebEngine ist gross (~300 MB). Wenn das Flatpak zu gross wird:
- Option A: WebEngine als **optional** markieren (App funktioniert ohne Weltkarte)
- Option B: Leaflet-Karte direkt in `QTextBrowser` mit `setOpenLinks(False)` rendern
- Option C: KDE-Runtime nutzt QtWebEngine systemweit → kein extra Download

Aktuell ist Option C durch `org.kde.Platform` bereits gegeben —
die KDE-Runtime 6.8 enthält QtWebEngine bereits!
PyQt6-WebEngine-Bindings müssen trotzdem separat installiert werden.
