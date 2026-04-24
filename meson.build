project('stock-monitor',
  version: '5.0.3',
  meson_version: '>= 0.59.0',
)

py_sources = [
  'stock_monitor.py',
  'tax_module.py',
  'translations.py',
  'tax_translations.py',
  'help_texts.py',
  'world_map.py',
  'config.py',
  'market_data.py',
  'portfolio_db.py',
]

install_data(py_sources,
  install_dir: get_option('prefix') / 'lib' / 'stock-monitor',
)

install_data('dividend_lists.json',
  install_dir: get_option('prefix') / 'lib' / 'stock-monitor',
)

install_data('stock-monitor-256.png',
  install_dir: get_option('prefix') / 'share' / 'icons' / 'hicolor' / '256x256' / 'apps',
  rename: 'ch.stock-monitor.StockMonitor.png',
)

install_data('ch.stock-monitor.StockMonitor.desktop',
  install_dir: get_option('prefix') / 'share' / 'applications',
)

install_data('ch.stock-monitor.StockMonitor.metainfo.xml',
  install_dir: get_option('prefix') / 'share' / 'metainfo',
)

install_data('stock-monitor-flatpak.sh',
  install_dir: get_option('prefix') / 'bin',
  rename: 'stock-monitor',
  install_mode: 'rwxr-xr-x',
)
