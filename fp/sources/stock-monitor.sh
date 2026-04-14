#!/bin/bash
export PYTHONPATH="/app/lib/stock-monitor:${PYTHONPATH}"

# Log-Verzeichnis im Flatpak-eigenen Datenordner
export SM_LOG_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/stock-monitor"
mkdir -p "$SM_LOG_DIR"

if [ -n "$WAYLAND_DISPLAY" ] && [ -z "$FORCE_X11" ]; then
    export QT_QPA_PLATFORM="wayland;xcb"
else
    export QT_QPA_PLATFORM="xcb"
fi

export QTWEBENGINE_DISABLE_SANDBOX=1
# --disable-gpu + --in-process-gpu: verhindert Chromium GPU-Prozess-Spawn in Flatpak-Sandbox
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu --in-process-gpu"
export MPLBACKEND="QtAgg"

exec python3 /app/lib/stock-monitor/stock_monitor.py "$@"
