# Kein Debug-Paket (pure Python, keine C-Quellen)
%global debug_package %{nil}
# Kein Distro-Tag → RPM läuft auf Fedora, openSUSE usw. ohne Anpassung
%global dist %{nil}

Name:           stock-monitor
Version:        5.0.7
Release:        1
Summary:        Aktien-Portfolio Monitor und Verwaltung
License:        MIT
URL:            https://github.com/StockMonitorCH/Stock-Monitor
Source0:        stock-monitor-%{version}.tar.gz
BuildArch:      x86_64

# ── Python-Interpreter ─────────────────────────────────────────────────────────
Requires:       python3

# PyQt6 wird im %post via pip installiert falls kein System-Paket vorhanden

BuildRequires:  python3

%description
Stock Monitor ist eine kostenlose, quelloffene Desktop-Anwendung zur Verwaltung
und Analyse von Aktien-Portfolios. Aktien, ETFs, Kryptowährungen und Rohstoffe
aller wichtigen Weltbörsen – ohne Cloud, ohne Abo, alle Daten lokal.

Features: Echtzeit-Kurse, Portfolio-Analyse, Steuerberechnung, Dividenden-
Tracking, interaktive Charts, PDF/Excel-Export, Wechselkursrechner und mehr.


%prep
%setup -q


%build
# Pure Python – kein Kompilieren nötig


%install
install -d %{buildroot}/opt/stock-monitor/app
install -d %{buildroot}/opt/stock-monitor/wheels
install -d %{buildroot}/usr/bin
install -d %{buildroot}/usr/share/applications
install -d %{buildroot}/usr/share/icons/hicolor/256x256/apps
install -d %{buildroot}/usr/share/metainfo
install -d %{buildroot}/usr/share/licenses/%{name}

# ── App-Dateien ────────────────────────────────────────────────────────────────
for f in stock_monitor.py portfolio_db.py config.py market_data.py \
          tax_module.py tax_translations.py translations.py help_texts.py \
          world_map.py dividend_lists.json Demo.smpf; do
    install -m 0644 app/$f %{buildroot}/opt/stock-monitor/app/$f
done

# ── Gebündelte Wheels ──────────────────────────────────────────────────────────
for f in wheels/*; do
    install -m 0644 "$f" %{buildroot}/opt/stock-monitor/wheels/
done

# ── Launcher ───────────────────────────────────────────────────────────────────
install -m 0755 stock-monitor.sh %{buildroot}/usr/bin/stock-monitor

# ── Desktop-Integration ────────────────────────────────────────────────────────
install -m 0644 stock-monitor.desktop \
    %{buildroot}/usr/share/applications/stock-monitor.desktop
install -m 0644 stock-monitor-256.png \
    %{buildroot}/usr/share/icons/hicolor/256x256/apps/stock-monitor.png

# ── AppStream Metainfo (für Discover / GNOME Software) ────────────────────────
install -m 0644 stock-monitor.metainfo.xml \
    %{buildroot}/usr/share/metainfo/stock-monitor.metainfo.xml

# ── Lizenz ─────────────────────────────────────────────────────────────────────
install -m 0644 LICENSE %{buildroot}/usr/share/licenses/%{name}/LICENSE


%post
# Läuft still im Hintergrund – kein Terminal-Output für den User
exec 2>/dev/null

LIBDIR=/opt/stock-monitor/lib
WHEELDIR=/opt/stock-monitor/wheels
# Bei Upgrade/Neuinstallation immer frisch starten (kein alter defekter Stand)
rm -rf "$LIBDIR"
mkdir -p "$LIBDIR"

PYTHON=""
for py in python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$py" &>/dev/null; then
        ok=$("$py" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null)
        if [ "$ok" = "True" ]; then PYTHON="$py"; break; fi
    fi
done

if [ -z "$PYTHON" ]; then
    if command -v dnf &>/dev/null; then
        dnf install -y python3.12 >/dev/null 2>&1 || true
    elif command -v zypper &>/dev/null; then
        zypper install -y python312 >/dev/null 2>&1 || zypper install -y python310 >/dev/null 2>&1 || true
    fi
    for py in python3.13 python3.12 python3.11 python3.10; do
        if command -v "$py" &>/dev/null; then
            ok=$("$py" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null)
            if [ "$ok" = "True" ]; then PYTHON="$py"; break; fi
        fi
    done
fi

# Kein Python 3.10+ → Launcher übernimmt beim ersten Start
[ -z "$PYTHON" ] && exit 0

echo "$PYTHON" > /opt/stock-monitor/python_bin

# PyQt6: System-Paket (Fedora/openSUSE) oder pip als Fallback
if ! "$PYTHON" -c "import PyQt6" >/dev/null 2>&1; then
    if command -v dnf &>/dev/null; then
        dnf install -y python3-pyqt6 >/dev/null 2>&1 || true
    elif command -v zypper &>/dev/null; then
        zypper install -y python3-PyQt6 >/dev/null 2>&1 || true
    fi
fi
if ! "$PYTHON" -c "import PyQt6" >/dev/null 2>&1; then
    "$PYTHON" -m pip install --quiet PyQt6 >/dev/null 2>&1 || true
fi

PIP="$PYTHON -m pip install --quiet --target $LIBDIR --no-index --find-links $WHEELDIR --no-deps"

$PIP \
    beautifulsoup4 certifi cryptography "curl-cffi" cycler defusedxml \
    et-xmlfile frozendict idna "markdown-it-py" mdurl multitasking \
    openpyxl packaging peewee platformdirs protobuf pycparser pygments \
    pyparsing pyqtgraph "python-dateutil" pytz reportlab requests rich \
    six soupsieve "typing-extensions" tzdata urllib3 yfinance >/dev/null 2>&1 || true

PYVER=$("$PYTHON" -c "import sys; print('cp%d%d' % sys.version_info[:2])" 2>/dev/null)
NUMPY_WHL=$(ls "$WHEELDIR"/numpy-*-${PYVER}-*.whl 2>/dev/null | head -1)
if [ -n "$NUMPY_WHL" ]; then
    "$PYTHON" -m pip install --quiet --target "$LIBDIR" --no-deps "$NUMPY_WHL" >/dev/null 2>&1 || true
else
    $PIP numpy >/dev/null 2>&1 || true
fi

for pkg in pandas matplotlib Pillow websockets \
           contourpy fonttools kiwisolver charset-normalizer cffi; do
    $PIP "$pkg" >/dev/null 2>&1 || true
done

$PYTHON -m pip install --quiet --target "$LIBDIR" --no-deps \
    "$WHEELDIR/odfpy-1.4.1.tar.gz" >/dev/null 2>&1 || true

gtk-update-icon-cache -f -t /usr/share/icons/hicolor >/dev/null 2>&1 || true
update-desktop-database /usr/share/applications >/dev/null 2>&1 || true


%preun
# Beim vollständigen Entfernen die pip-installierten Pakete löschen
if [ $1 -eq 0 ]; then
    rm -rf /opt/stock-monitor/lib
fi


%postun
# Beim vollständigen Entfernen das komplette Verzeichnis aufräumen
if [ $1 -eq 0 ]; then
    rm -rf /opt/stock-monitor
fi
gtk-update-icon-cache -f -t /usr/share/icons/hicolor >/dev/null 2>&1 || true
update-desktop-database /usr/share/applications >/dev/null 2>&1 || true


%files
%license /usr/share/licenses/%{name}/LICENSE
/opt/stock-monitor/app/
/opt/stock-monitor/wheels/
/usr/bin/stock-monitor
/usr/share/applications/stock-monitor.desktop
/usr/share/icons/hicolor/256x256/apps/stock-monitor.png
/usr/share/metainfo/stock-monitor.metainfo.xml


%changelog
* Fri Apr 25 2026 StockMonitorCH <noreply@stockmonitor.ch> - 5.0.7-1
- Fix: Flatpak – Einstellungen persistent (XDG_DATA_HOME), WebEngine-Absturz
- Fix: NumPy – passendes Wheel direkt installieren (kein Versions-Konflikt)
- Fix: Weltkarte und Finment im Flatpak (Berechtigungen, Thread-Sicherheit)
* Thu Apr 23 2026 StockMonitorCH <noreply@stockmonitor.ch> - 5.0.3-1
- Fix: Sharpe-Ratio negativer Wert zeigte fehlendes Minus im Erklärungstext
- Fix: Übersetzungsfehler in DE behoben
- Feature: Währungsrechner merkt sich die zuletzt gewählten Währungen
* Wed Apr 22 2026 StockMonitorCH <noreply@stockmonitor.ch> - 5.0.2-1
- Fix: NumPy 2.2.6 (Python 3.12 kompatibel), lib bei Upgrade bereinigt
* Tue Apr 21 2026 StockMonitorCH <noreply@stockmonitor.ch> - 5.0.1-1
- Version 5.0.1: Demo-Portfolio ohne Passwort, UnboundLocalError os-Fix
* Fri Apr 17 2026 StockMonitorCH <noreply@stockmonitor.ch> - 5.0.0-1
- Erstveröffentlichung
