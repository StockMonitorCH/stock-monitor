#!/bin/bash
# ── Stock Monitor RPM Build-Skript ─────────────────────────────────────────────
# Baut ein x86_64 RPM das auf Fedora 40+ und openSUSE Tumbleweed läuft.
# Benötigt: rpm-build  (sudo dnf install rpm-build)
# Aufruf:   bash build_rpm.sh

set -e
cd "$(dirname "$0")"

VERSION="5.0.3"
PKG="stock-monitor-${VERSION}"
RPMBUILD="$HOME/rpmbuild"

echo "=== Stock Monitor ${VERSION} – RPM Build ==="

# ── Voraussetzungen prüfen ─────────────────────────────────────────────────────
if ! command -v rpmbuild &>/dev/null; then
    echo "FEHLER: rpmbuild nicht gefunden."
    echo "       sudo dnf install rpm-build   # Fedora"
    echo "       sudo zypper install rpm-build # openSUSE"
    exit 1
fi

# ── rpmbuild-Verzeichnisstruktur anlegen ──────────────────────────────────────
mkdir -p "$RPMBUILD"/{SOURCES,SPECS,BUILD,RPMS,SRPMS}

# ── Quell-Tarball zusammenstellen ─────────────────────────────────────────────
echo "→ Erstelle Quell-Tarball..."
TMPDIR=$(mktemp -d)
SRCDIR="$TMPDIR/$PKG"
mkdir -p "$SRCDIR/app"
mkdir -p "$SRCDIR/wheels"

# App-Dateien
for f in stock_monitor.py portfolio_db.py config.py market_data.py \
          tax_module.py tax_translations.py translations.py help_texts.py \
          world_map.py dividend_lists.json Demo.smpf LICENSE; do
    if [ -f "$f" ]; then
        cp "$f" "$SRCDIR/app/$f"
    else
        echo "WARNUNG: $f nicht gefunden, wird übersprungen"
    fi
done

# Launcher, Desktop, Metainfo, Icon, Lizenz
cp stock-monitor.sh                       "$SRCDIR/"
cp ch.stockmonitor.StockMonitor.desktop   "$SRCDIR/"
cp stock-monitor.metainfo.xml             "$SRCDIR/"
cp LICENSE                                "$SRCDIR/"

# Icon aus fp/sources/
if [ -f "fp/sources/stock-monitor-256.png" ]; then
    cp "fp/sources/stock-monitor-256.png" "$SRCDIR/"
elif [ -f "fp/sources/ch.stockmonitor.StockMonitor.png" ]; then
    cp "fp/sources/ch.stockmonitor.StockMonitor.png" "$SRCDIR/stock-monitor-256.png"
else
    echo "WARNUNG: Icon nicht gefunden"
fi

# Alle verwendbaren Wheels: pure-Python, abi3 und cp313/cp314 (kompilierte Pakete)
echo "→ Kopiere Wheels..."
WHEEL_COUNT=0
for whl in fp/sources/*.whl; do
    [ -f "$whl" ] || continue
    cp "$whl" "$SRCDIR/wheels/"
    WHEEL_COUNT=$((WHEEL_COUNT + 1))
done

# odfpy Quell-Tarball
if [ -f "fp/sources/odfpy-1.4.1.tar.gz" ]; then
    cp "fp/sources/odfpy-1.4.1.tar.gz" "$SRCDIR/wheels/"
    WHEEL_COUNT=$((WHEEL_COUNT + 1))
fi

echo "   $WHEEL_COUNT Pakete eingebettet"

# Tarball packen
tar -czf "$RPMBUILD/SOURCES/${PKG}.tar.gz" -C "$TMPDIR" "$PKG"
rm -rf "$TMPDIR"
echo "   Tarball: $RPMBUILD/SOURCES/${PKG}.tar.gz"

# ── Spec kopieren ─────────────────────────────────────────────────────────────
cp stock-monitor.spec "$RPMBUILD/SPECS/"

# ── Alte Builds aufräumen (damit kein falsches RPM erwischt wird) ─────────────
rm -f "$RPMBUILD/RPMS/x86_64/stock-monitor-${VERSION}"*.rpm
rm -f "$RPMBUILD/SRPMS/stock-monitor-${VERSION}"*.rpm

# ── RPM bauen ─────────────────────────────────────────────────────────────────
echo "→ Baue RPM (das kann 1-2 Minuten dauern)..."
rpmbuild -ba "$RPMBUILD/SPECS/stock-monitor.spec" \
    --define "_topdir $RPMBUILD" \
    2>&1 | grep -v "^Processing\|^Executing\|^Checking\|^warning: bogus" || true

# ── Ergebnis ins Projektverzeichnis kopieren ──────────────────────────────────
RPM_FILE=$(find "$RPMBUILD/RPMS" -name "stock-monitor-${VERSION}*.rpm" -newer "$RPMBUILD/SPECS/stock-monitor.spec" | head -1)
SRPM_FILE=$(find "$RPMBUILD/SRPMS" -name "stock-monitor-${VERSION}*.rpm" -newer "$RPMBUILD/SPECS/stock-monitor.spec" | head -1)

if [ -n "$RPM_FILE" ]; then
    # Ausgabedatei ohne Release-Zähler (-1) benennen
    CLEAN_NAME="stock-monitor-${VERSION}.x86_64.rpm"
    cp "$RPM_FILE" "./$CLEAN_NAME"
    [ -n "$SRPM_FILE" ] && cp "$SRPM_FILE" .
    echo ""
    echo "=== Fertig! ==="
    echo "RPM:  $CLEAN_NAME"
    [ -n "$SRPM_FILE" ] && echo "SRPM: $(basename "$SRPM_FILE")"
    echo ""
    echo "Installation:"
    echo "  Doppelklick auf $CLEAN_NAME  →  Discover öffnet sich"
    echo "  sudo dnf install $CLEAN_NAME          (Fedora)"
    echo "  sudo zypper install $CLEAN_NAME       (openSUSE)"
    echo ""
    echo "Einzige Abhängigkeit die vom System kommt: python3-pyqt6"
else
    echo "FEHLER: RPM wurde nicht erstellt. Ausgabe von rpmbuild oben prüfen."
    exit 1
fi
