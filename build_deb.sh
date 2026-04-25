#!/bin/bash
# ── Stock Monitor DEB Build-Skript ─────────────────────────────────────────────
# Baut ein amd64 .deb das auf Ubuntu 22.04+, Debian 12+, Linux Mint 21+ läuft.
# Benötigt: dpkg-deb  (sudo dnf install dpkg  # Fedora)
#                     (auf Ubuntu/Debian bereits vorhanden)
# Aufruf:   bash build_deb.sh

set -e
cd "$(dirname "$0")"

VERSION="5.0.7"
PKG="stock-monitor"
PKGDIR="$(mktemp -d)/stock-monitor_${VERSION}_amd64"

echo "=== Stock Monitor ${VERSION} – DEB Build ==="

# ── Voraussetzungen prüfen ─────────────────────────────────────────────────────
if ! command -v dpkg-deb &>/dev/null; then
    echo "FEHLER: dpkg-deb nicht gefunden."
    echo "       sudo dnf install dpkg   # Fedora"
    echo "       (auf Ubuntu/Debian bereits vorhanden)"
    exit 1
fi

# ── Verzeichnisstruktur anlegen ────────────────────────────────────────────────
echo "→ Erstelle Paketstruktur..."
mkdir -p "$PKGDIR/DEBIAN"
mkdir -p "$PKGDIR/opt/stock-monitor/app"
mkdir -p "$PKGDIR/opt/stock-monitor/wheels"
mkdir -p "$PKGDIR/usr/bin"
mkdir -p "$PKGDIR/usr/share/applications"
mkdir -p "$PKGDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$PKGDIR/usr/share/metainfo"
mkdir -p "$PKGDIR/usr/share/doc/$PKG"

# ── App-Dateien ────────────────────────────────────────────────────────────────
for f in stock_monitor.py portfolio_db.py config.py market_data.py \
          tax_module.py tax_translations.py translations.py help_texts.py \
          world_map.py dividend_lists.json Demo.smpf; do
    [ -f "$f" ] && cp "$f" "$PKGDIR/opt/stock-monitor/app/$f" \
                || echo "WARNUNG: $f nicht gefunden"
done

# ── Wheels ─────────────────────────────────────────────────────────────────────
echo "→ Kopiere Wheels..."
WHEEL_COUNT=0
for whl in fp/sources/*.whl fp/sources/*.tar.gz; do
    [ -f "$whl" ] || continue
    cp "$whl" "$PKGDIR/opt/stock-monitor/wheels/"
    WHEEL_COUNT=$((WHEEL_COUNT + 1))
done
echo "   $WHEEL_COUNT Pakete eingebettet"

# ── Launcher ───────────────────────────────────────────────────────────────────
cp stock-monitor.sh "$PKGDIR/usr/bin/stock-monitor"
chmod 0755 "$PKGDIR/usr/bin/stock-monitor"

# ── Desktop + Metainfo + Icon ──────────────────────────────────────────────────
cp stock-monitor.desktop \
   "$PKGDIR/usr/share/applications/stock-monitor.desktop"
cp stock-monitor.metainfo.xml \
   "$PKGDIR/usr/share/metainfo/ch.stockmonitor.StockMonitor.metainfo.xml"
if [ -f "fp/sources/stock-monitor-256.png" ]; then
    cp "fp/sources/stock-monitor-256.png" \
       "$PKGDIR/usr/share/icons/hicolor/256x256/apps/stock-monitor.png"
fi

# ── Lizenz / Copyright ─────────────────────────────────────────────────────────
cat > "$PKGDIR/usr/share/doc/$PKG/copyright" << 'EOF'
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: stock-monitor
Upstream-Contact: noreply@stockmonitor.ch
Source: https://github.com/StockMonitorCH/Stock-Monitor

Files: *
Copyright: 2026 StockMonitorCH
License: MIT
EOF

# ── DEBIAN/control ─────────────────────────────────────────────────────────────
cat > "$PKGDIR/DEBIAN/control" << EOF
Package: stock-monitor
Version: ${VERSION}
Architecture: amd64
Maintainer: StockMonitorCH <noreply@stockmonitor.ch>
Homepage: https://www.stock-monitor.ch
Depends: python3
Description: Aktien-Portfolio Monitor und Verwaltung
 Stock Monitor ist eine kostenlose, quelloffene Desktop-Anwendung zur
 Verwaltung und Analyse von Aktien-Portfolios. Aktien, ETFs, Krypto-
 währungen und Rohstoffe aller wichtigen Weltbörsen – ohne Cloud,
 ohne Abo, alle Daten bleiben lokal.
 .
 Features: Echtzeit-Kurse, Portfolio-Analyse, Steuerberechnung,
 Dividenden-Tracking, Charts, PDF/Excel-Export und mehr.
EOF

# ── DEBIAN/postinst ────────────────────────────────────────────────────────────
cat > "$PKGDIR/DEBIAN/postinst" << 'POSTINST'
#!/bin/bash
# Läuft still im Hintergrund – kein Terminal-Output für den User
exec 2>/dev/null

LIBDIR=/opt/stock-monitor/lib
WHEELDIR=/opt/stock-monitor/wheels
mkdir -p "$LIBDIR"

# Python 3.10+ finden (neueste zuerst)
PYTHON=""
for py in python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$py" &>/dev/null; then
        ok=$("$py" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null)
        if [ "$ok" = "True" ]; then PYTHON="$py"; break; fi
    fi
done

# Falls kein Python 3.10+ vorhanden: still versuchen nachzuinstallieren
if [ -z "$PYTHON" ]; then
    # Universe aktivieren + Paketliste aktualisieren (nötig auf Ubuntu 20.04)
    export DEBIAN_FRONTEND=noninteractive
    add-apt-repository -y universe >/dev/null 2>&1 || true
    apt-get update -qq >/dev/null 2>&1 || true
    # Einzeln installieren: wenn distutils fehlt bricht python3.10 sonst auch ab
    apt-get install -y python3.10          >/dev/null 2>&1 || true
    apt-get install -y python3.10-distutils >/dev/null 2>&1 || true
    apt-get install -y python3.12          >/dev/null 2>&1 || true
    # Fallback für Ubuntu 18.04: deadsnakes PPA
    if ! command -v python3.10 &>/dev/null && ! command -v python3.12 &>/dev/null; then
        apt-get install -y software-properties-common >/dev/null 2>&1 || true
        add-apt-repository -y ppa:deadsnakes/ppa      >/dev/null 2>&1 || true
        apt-get update -qq                            >/dev/null 2>&1 || true
        apt-get install -y python3.10                 >/dev/null 2>&1 || true
        apt-get install -y python3.10-distutils       >/dev/null 2>&1 || true
    fi
    for py in python3.13 python3.12 python3.11 python3.10; do
        if command -v "$py" &>/dev/null; then
            ok=$("$py" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null)
            if [ "$ok" = "True" ]; then PYTHON="$py"; break; fi
        fi
    done
fi

# Kein Python 3.10+ gefunden → Launcher übernimmt beim ersten Start
[ -z "$PYTHON" ] && exit 0

echo "$PYTHON" > /opt/stock-monitor/python_bin

# pip sicherstellen (Ubuntu 22.04: kein ensurepip, braucht python3-pip)
"$PYTHON" -m ensurepip --upgrade >/dev/null 2>&1 || \
    apt-get install -y python3-pip >/dev/null 2>&1 || true

# PyQt6: universe aktivieren (python3-pyqt6 existiert erst ab Ubuntu 23.04 in apt)
if ! "$PYTHON" -c "import PyQt6" >/dev/null 2>&1; then
    DEBIAN_FRONTEND=noninteractive add-apt-repository -y universe >/dev/null 2>&1 || true
    DEBIAN_FRONTEND=noninteractive apt-get update -qq              >/dev/null 2>&1 || true
    DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pyqt6 >/dev/null 2>&1 || true
fi

# --break-system-packages erst ab pip 22.3 verfügbar
PIP_VER=$("$PYTHON" -m pip --version 2>/dev/null | awk '{print $2}')
PIP_MAJOR=$(echo "$PIP_VER" | cut -d. -f1)
PIP_MINOR=$(echo "$PIP_VER" | cut -d. -f2)
if [ "${PIP_MAJOR:-0}" -gt 22 ] || { [ "${PIP_MAJOR:-0}" -eq 22 ] && [ "${PIP_MINOR:-0}" -ge 3 ]; }; then
    BSP="--break-system-packages"
else
    BSP=""
fi

PIP="$PYTHON -m pip install --quiet --target $LIBDIR --no-index --find-links $WHEELDIR --no-deps $BSP"

$PIP \
    beautifulsoup4 certifi cryptography "curl-cffi" cycler defusedxml \
    et-xmlfile frozendict idna "markdown-it-py" mdurl multitasking \
    openpyxl packaging peewee platformdirs protobuf pycparser pygments \
    pyparsing pyqtgraph "python-dateutil" pytz reportlab requests rich \
    six soupsieve "typing-extensions" tzdata urllib3 yfinance >/dev/null 2>&1 || true

PYVER=$("$PYTHON" -c "import sys; print('cp%d%d' % sys.version_info[:2])" 2>/dev/null)
NUMPY_WHL=$(ls "$WHEELDIR"/numpy-*-${PYVER}-*.whl 2>/dev/null | head -1)
if [ -n "$NUMPY_WHL" ]; then
    "$PYTHON" -m pip install --quiet --target "$LIBDIR" --no-deps $BSP "$NUMPY_WHL" >/dev/null 2>&1 || true
else
    $PIP numpy >/dev/null 2>&1 || true
fi
for pkg in pandas matplotlib Pillow websockets \
           contourpy fonttools kiwisolver "charset-normalizer" cffi; do
    $PIP "$pkg" >/dev/null 2>&1 || true
done

$PYTHON -m pip install --quiet --target "$LIBDIR" --no-deps $BSP \
    "$WHEELDIR/odfpy-1.4.1.tar.gz" >/dev/null 2>&1 || true

gtk-update-icon-cache -f -t /usr/share/icons/hicolor >/dev/null 2>&1 || true
update-desktop-database /usr/share/applications >/dev/null 2>&1 || true
POSTINST
chmod 0755 "$PKGDIR/DEBIAN/postinst"

# ── DEBIAN/prerm ───────────────────────────────────────────────────────────────
cat > "$PKGDIR/DEBIAN/prerm" << 'PRERM'
#!/bin/bash
if [ "$1" = "remove" ] || [ "$1" = "upgrade" ]; then
    rm -rf /opt/stock-monitor/lib
fi
PRERM
chmod 0755 "$PKGDIR/DEBIAN/prerm"

# ── DEBIAN/postrm ──────────────────────────────────────────────────────────────
cat > "$PKGDIR/DEBIAN/postrm" << 'POSTRM'
#!/bin/bash
if [ "$1" = "purge" ]; then
    rm -rf /opt/stock-monitor
fi
POSTRM
chmod 0755 "$PKGDIR/DEBIAN/postrm"

# ── DEB bauen ──────────────────────────────────────────────────────────────────
echo "→ Baue DEB..."
dpkg-deb --build --root-owner-group "$PKGDIR" 2>&1 | grep -v "^$" || true

DEBFILE="$(dirname "$PKGDIR")/stock-monitor_${VERSION}_amd64.deb"
OUTFILE="stock-monitor_${VERSION}_amd64.deb"

if [ -f "$DEBFILE" ]; then
    cp "$DEBFILE" "./$OUTFILE"
    rm -rf "$(dirname "$PKGDIR")"
    echo ""
    echo "=== Fertig! ==="
    echo "DEB:  $OUTFILE ($(du -sh "./$OUTFILE" | cut -f1))"
    echo ""
    echo "Installation:"
    echo "  Doppelklick auf $OUTFILE  →  Software-Center öffnet sich"
    echo "  sudo apt install ./$OUTFILE          (Ubuntu/Debian/Mint)"
else
    echo "FEHLER: DEB wurde nicht erstellt."
    rm -rf "$(dirname "$PKGDIR")"
    exit 1
fi
