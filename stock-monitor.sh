#!/bin/bash
# Stock Monitor Launcher
# User-Lib hat Vorrang – dort landen manuell aktualisierte Pakete (z.B. yfinance)
USER_LIB="${XDG_DATA_HOME:-$HOME/.local/share}/stock-monitor/lib"
mkdir -p "$USER_LIB"
export PYTHONPATH="$USER_LIB:/opt/stock-monitor/lib:${PYTHONPATH}"

export SM_LOG_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/stock-monitor"
mkdir -p "$SM_LOG_DIR"

# PyQt6 prüfen – einzige Abhängigkeit die nicht eingebettet ist
if ! python3 -c "import PyQt6" 2>/dev/null; then
    MSG="Stock Monitor benötigt python3-pyqt6, das auf diesem System fehlt.

Bitte installieren:
  Fedora:   sudo dnf install python3-pyqt6
  openSUSE: sudo zypper install python3-PyQt6"

    # Grafische Fehlermeldung (KDE / GNOME / Fallback Terminal)
    if command -v kdialog &>/dev/null; then
        kdialog --title "Stock Monitor – Abhängigkeit fehlt" --error "$MSG"
    elif command -v zenity &>/dev/null; then
        zenity --error --title="Stock Monitor – Abhängigkeit fehlt" --text="$MSG"
    elif command -v xmessage &>/dev/null; then
        xmessage -center "$MSG"
    else
        echo "$MSG" >&2
    fi
    exit 1
fi

if [ -n "$WAYLAND_DISPLAY" ] && [ -z "$FORCE_X11" ]; then
    export QT_QPA_PLATFORM="wayland;xcb"
else
    export QT_QPA_PLATFORM="xcb"
fi

# HiDPI-Scaling: Qt soll logische (skalierte) Pixel melden, nicht physische.
# Verhindert falsches 4K-Layout auf Full-HD-Notebooks mit Skalierungseinstellungen.
export QT_ENABLE_HIGHDPI_SCALING=1

export MPLBACKEND="QtAgg"
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu --in-process-gpu"

exec python3 /opt/stock-monitor/app/stock_monitor.py "$@"
