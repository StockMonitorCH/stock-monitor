#!/bin/bash
# Install script for Stock Monitor Flatpak build
PREFIX="${1:-/app}"

install -Dm755 stock_monitor.py       "$PREFIX/lib/stock-monitor/stock_monitor.py"
install -Dm644 tax_module.py          "$PREFIX/lib/stock-monitor/tax_module.py"
install -Dm644 translations.py        "$PREFIX/lib/stock-monitor/translations.py"
install -Dm644 tax_translations.py    "$PREFIX/lib/stock-monitor/tax_translations.py"
install -Dm644 help_texts.py          "$PREFIX/lib/stock-monitor/help_texts.py"
install -Dm644 world_map.py           "$PREFIX/lib/stock-monitor/world_map.py"
install -Dm644 config.py              "$PREFIX/lib/stock-monitor/config.py"
install -Dm644 market_data.py         "$PREFIX/lib/stock-monitor/market_data.py"
install -Dm644 portfolio_db.py        "$PREFIX/lib/stock-monitor/portfolio_db.py"
install -Dm644 dividend_lists.json    "$PREFIX/lib/stock-monitor/dividend_lists.json"
install -Dm755 stock-monitor-flatpak.sh "$PREFIX/bin/stock-monitor"
install -Dm644 ch.stockmonitor.StockMonitor.desktop \
    "$PREFIX/share/applications/ch.stockmonitor.StockMonitor.desktop"
install -Dm644 stock-monitor.metainfo.xml \
    "$PREFIX/share/metainfo/ch.stockmonitor.StockMonitor.metainfo.xml"
install -Dm644 Chart.png \
    "$PREFIX/share/icons/hicolor/256x256/apps/ch.stockmonitor.StockMonitor.png"
