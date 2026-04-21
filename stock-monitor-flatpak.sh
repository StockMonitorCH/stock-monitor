#!/bin/bash
export QT_ENABLE_HIGHDPI_SCALING=1
export MPLBACKEND="QtAgg"
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu --in-process-gpu"
exec python3 /app/lib/stock-monitor/stock_monitor.py "$@"
