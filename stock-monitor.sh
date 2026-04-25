#!/bin/bash
# Stock Monitor Launcher
USER_LIB="${XDG_DATA_HOME:-$HOME/.local/share}/stock-monitor/lib"
mkdir -p "$USER_LIB"
export SM_LOG_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/stock-monitor"
mkdir -p "$SM_LOG_DIR"

# ── Hilfsfunktion: grafische Meldungen ───────────────────────────────────────
show_dialog() {
    local type="$1" title="$2" msg="$3"
    if command -v zenity &>/dev/null; then
        zenity --"$type" --title="$title" --text="$msg" --no-wrap 2>/dev/null
    elif command -v kdialog &>/dev/null; then
        kdialog --title "$title" --"$type" "$msg" 2>/dev/null
    else
        echo "$msg" >&2
    fi
}

# ── Hilfsfunktion: Befehl als root via pkexec mit Fortschrittsbalken ─────────
run_as_root() {
    local label="$1" scriptfile="$2"
    chmod +x "$scriptfile"
    if command -v zenity &>/dev/null; then
        # Zenity im Hintergrund starten – NICHT pipen (pkexec braucht freie stdout)
        zenity --progress --title="Stock Monitor" \
               --text="$label" \
               --pulsate --no-cancel 2>/dev/null &
        ZENITY_PID=$!
        pkexec bash "$scriptfile"
        PKEXEC_RC=$?
        kill "$ZENITY_PID" 2>/dev/null
        wait "$ZENITY_PID" 2>/dev/null
        return $PKEXEC_RC
    else
        pkexec bash "$scriptfile"
    fi
}

# ── Python 3.10+ finden ───────────────────────────────────────────────────────
find_python() {
    local py ok
    for py in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$py" &>/dev/null; then
            ok=$("$py" -c "import sys; print(sys.version_info>=(3,10))" 2>/dev/null)
            if [ "$ok" = "True" ]; then echo "$py"; return 0; fi
        fi
    done
    return 1
}

PYTHON=""
[ -f /opt/stock-monitor/python_bin ] && PYTHON=$(cat /opt/stock-monitor/python_bin)
command -v "$PYTHON" &>/dev/null || PYTHON=""
[ -z "$PYTHON" ] && PYTHON=$(find_python)

# ── Python 3.10 installieren falls nötig ─────────────────────────────────────
if [ -z "$PYTHON" ]; then
    show_dialog question "Stock Monitor – Einmalige Einrichtung" \
"Stock Monitor benötigt Python 3.10, das auf Ihrem System noch fehlt.

Soll es jetzt automatisch installiert werden?
(Erfordert einmalig Ihr Passwort)"
    [ $? -ne 0 ] && exit 1

    # Installations-Skript in Datei schreiben (kein Quoting-Problem)
    SETUP=$(mktemp /tmp/sm-setup-XXXXXX.sh)
    cat > "$SETUP" << 'SCRIPT'
#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
# Universe aktivieren und Paketliste aktualisieren
add-apt-repository -y universe >/dev/null 2>&1 || true
apt-get update -qq             >/dev/null 2>&1 || true
# Einzeln installieren (wenn distutils fehlt bricht python3.10 sonst auch ab)
apt-get install -y python3.10           >/dev/null 2>&1 || true
apt-get install -y python3.10-distutils >/dev/null 2>&1 || true
# Falls immer noch nicht vorhanden: deadsnakes PPA (Ubuntu 18.04)
if ! command -v python3.10 >/dev/null 2>&1; then
    apt-get install -y software-properties-common >/dev/null 2>&1 || true
    add-apt-repository -y ppa:deadsnakes/ppa      >/dev/null 2>&1 || true
    apt-get update -qq                            >/dev/null 2>&1 || true
    apt-get install -y python3.10           >/dev/null 2>&1 || true
    apt-get install -y python3.10-distutils >/dev/null 2>&1 || true
fi
# pip sicherstellen
python3.10 -m ensurepip --upgrade >/dev/null 2>&1 || true
SCRIPT
    run_as_root "Python 3.10 wird installiert…" "$SETUP"
    rm -f "$SETUP"

    PYTHON=$(find_python)
    if [ -z "$PYTHON" ]; then
        show_dialog error "Stock Monitor – Einrichtung fehlgeschlagen" \
"Python 3.10 konnte nicht installiert werden.

Bitte prüfen Sie Ihre Internetverbindung
oder kontaktieren Sie: https://www.stock-monitor.ch"
        exit 1
    fi
fi

# ── PyQt6 installieren falls nötig ───────────────────────────────────────────
if ! "$PYTHON" -c "import PyQt6" 2>/dev/null; then
    show_dialog question "Stock Monitor – Einmalige Einrichtung" \
"Stock Monitor wird jetzt einmalig eingerichtet.

Es werden ca. 50 MB heruntergeladen.
Das dauert je nach Internetverbindung 1–2 Minuten.

Jetzt einrichten?"
    [ $? -ne 0 ] && exit 1

    # Python-Pfad in Skript einbetten (keine Variable-Expansion-Probleme)
    PYQT_SETUP=$(mktemp /tmp/sm-pyqt-XXXXXX.sh)
    PYBIN="$PYTHON"
    SM_INSTALL_LOG="/tmp/stock-monitor-install.log"
    cat > "$PYQT_SETUP" << SCRIPT
#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
LOG="$SM_INSTALL_LOG"
echo "=== Stock Monitor PyQt6 Setup \$(date) ===" > "\$LOG"
echo "Python: $PYBIN" >> "\$LOG"

# Universe-Repo aktivieren
echo "--- add-apt-repository universe ---" >> "\$LOG"
add-apt-repository -y universe >> "\$LOG" 2>&1 || true
apt-get update -qq             >> "\$LOG" 2>&1 || true

# python3-pyqt6 per apt versuchen (Ubuntu 23.04+; auf 22.04 nicht vorhanden)
echo "--- apt install python3-pyqt6 ---" >> "\$LOG"
apt-get install -y python3-pyqt6 >> "\$LOG" 2>&1 || true

if ! $PYBIN -c "import PyQt6" >/dev/null 2>&1; then
    echo "--- apt PyQt6 fehlgeschlagen, versuche pip ---" >> "\$LOG"
    # pip sicherstellen (Ubuntu 22.04 hat kein ensurepip, braucht python3-pip)
    apt-get install -y python3-pip >> "\$LOG" 2>&1 || true
    # pip-Flags je nach Version: --break-system-packages erst ab pip 22.3
    PIP_VER=\$($PYBIN -m pip --version 2>/dev/null | awk '{print \$2}')
    MAJOR=\$(echo "\$PIP_VER" | cut -d. -f1)
    MINOR=\$(echo "\$PIP_VER" | cut -d. -f2)
    echo "--- pip version: \$PIP_VER ---" >> "\$LOG"
    if [ "\${MAJOR:-0}" -gt 22 ] || { [ "\${MAJOR:-0}" -eq 22 ] && [ "\${MINOR:-0}" -ge 3 ]; }; then
        $PYBIN -m pip install PyQt6 --break-system-packages >> "\$LOG" 2>&1 || true
    else
        $PYBIN -m pip install PyQt6 >> "\$LOG" 2>&1 || true
    fi
    echo "--- pip fertig, import-test ---" >> "\$LOG"
    $PYBIN -c "import PyQt6; print('PyQt6 OK')" >> "\$LOG" 2>&1 || true
fi
SCRIPT
    run_as_root "PyQt6 wird installiert (ca. 100 MB)…" "$PYQT_SETUP"
    rm -f "$PYQT_SETUP"

    if ! "$PYTHON" -c "import PyQt6" 2>/dev/null; then
        LOG_HINT=""
        [ -f "$SM_INSTALL_LOG" ] && LOG_HINT="

Fehlerprotokoll: $SM_INSTALL_LOG"
        show_dialog error "Stock Monitor – Einrichtung fehlgeschlagen" \
"Die Einrichtung konnte nicht abgeschlossen werden.

Bitte prüfen Sie Ihre Internetverbindung
oder kontaktieren Sie: https://www.stock-monitor.ch${LOG_HINT}"
        exit 1
    fi
fi

# ── Pip-Pakete einrichten falls noch nicht geschehen ─────────────────────────
if [ -z "$(ls -A /opt/stock-monitor/lib 2>/dev/null)" ]; then
    PYBIN="$PYTHON"
    WHEEL_SETUP=$(mktemp /tmp/sm-wheels-XXXXXX.sh)
    cat > "$WHEEL_SETUP" << SCRIPT
#!/bin/bash
LIBDIR=/opt/stock-monitor/lib
WHEELDIR=/opt/stock-monitor/wheels
mkdir -p "\$LIBDIR"
echo "$PYBIN" > /opt/stock-monitor/python_bin
# --break-system-packages erst ab pip 22.3 verfügbar
PIP_VER=\$($PYBIN -m pip --version 2>/dev/null | awk '{print \$2}')
MAJOR=\$(echo "\$PIP_VER" | cut -d. -f1)
MINOR=\$(echo "\$PIP_VER" | cut -d. -f2)
if [ "\${MAJOR:-0}" -gt 22 ] || { [ "\${MAJOR:-0}" -eq 22 ] && [ "\${MINOR:-0}" -ge 3 ]; }; then
    BSP="--break-system-packages"
else
    BSP=""
fi
PIP="$PYBIN -m pip install --quiet --target \$LIBDIR --no-index --find-links \$WHEELDIR --no-deps \$BSP"
\$PIP beautifulsoup4 certifi cryptography curl-cffi cycler defusedxml \
    et-xmlfile frozendict idna markdown-it-py mdurl multitasking \
    openpyxl packaging peewee platformdirs protobuf pycparser pygments \
    pyparsing pyqtgraph python-dateutil pytz reportlab requests rich \
    six soupsieve typing-extensions tzdata urllib3 yfinance >/dev/null 2>&1 || true
PYVER=\$($PYBIN -c "import sys; print('cp%d%d' % sys.version_info[:2])" 2>/dev/null)
NUMPY_WHL=\$(ls "\$WHEELDIR"/numpy-*-\${PYVER}-*.whl 2>/dev/null | head -1)
if [ -n "\$NUMPY_WHL" ]; then
    $PYBIN -m pip install --quiet --target \$LIBDIR --no-deps \$BSP "\$NUMPY_WHL" >/dev/null 2>&1 || true
else
    \$PIP numpy >/dev/null 2>&1 || true
fi
for pkg in pandas matplotlib Pillow websockets contourpy fonttools kiwisolver charset-normalizer cffi; do
    \$PIP \$pkg >/dev/null 2>&1 || true
done
$PYBIN -m pip install --quiet --target \$LIBDIR --no-deps \$BSP \
    \$WHEELDIR/odfpy-1.4.1.tar.gz >/dev/null 2>&1 || true
SCRIPT
    run_as_root "Bibliotheken werden eingerichtet…" "$WHEEL_SETUP"
    rm -f "$WHEEL_SETUP"
fi

echo "$PYTHON" > /opt/stock-monitor/python_bin 2>/dev/null || true

# ── Qt-Umgebung ───────────────────────────────────────────────────────────────
export PYTHONPATH="$USER_LIB:/opt/stock-monitor/lib:${PYTHONPATH}"
if [ -n "$WAYLAND_DISPLAY" ] && [ -z "$FORCE_X11" ]; then
    export QT_QPA_PLATFORM="wayland;xcb"
else
    export QT_QPA_PLATFORM="xcb"
fi
export QT_ENABLE_HIGHDPI_SCALING=1
export MPLBACKEND="QtAgg"
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu --in-process-gpu"

# ── App starten – Fehler in Log schreiben und anzeigen ───────────────────────
APP_LOG="${SM_LOG_DIR}/stock_monitor.log"
"$PYTHON" /opt/stock-monitor/app/stock_monitor.py "$@" 2>>"$APP_LOG"
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    LAST_LINES=$(tail -20 "$APP_LOG" 2>/dev/null)
    show_dialog error "Stock Monitor – Startfehler" \
"Stock Monitor konnte nicht gestartet werden (Code $EXIT_CODE).

Fehlerprotokoll: $APP_LOG

Letzte Meldung:
$LAST_LINES"
fi
exit $EXIT_CODE
