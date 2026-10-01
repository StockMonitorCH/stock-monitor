"""
mc_scenarios.py – Szenario-Portfolio & Monte Carlo Vergleich
Ausgelagert aus stock_monitor.py für bessere Wartbarkeit.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from typing import Optional

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QPalette
from PyQt6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDialog, QDoubleSpinBox,
    QFileDialog, QFrame, QHBoxLayout, QHeaderView, QInputDialog, QLabel,
    QLineEdit, QListWidget, QMessageBox, QPushButton, QSizePolicy,
    QStackedWidget, QTableWidget, QTableWidgetItem, QTabWidget,
    QVBoxLayout, QWidget, QApplication,
)

try:
    from translations import TR
except ImportError:
    def TR(key, **kw):
        return kw and key.format(**kw) or key

try:
    import config as _cfg
except ImportError:
    class _cfg:                               # type: ignore
        @staticmethod
        def get_date_format(): return 'EU'

# ── Pfad-Hilfsfunktionen ──────────────────────────────────────────────────────

def _data_home() -> str:
    if sys.platform == 'win32':
        if getattr(sys, 'frozen', False):
            return os.path.join(os.path.dirname(sys.executable), '_internal')
        return os.path.dirname(os.path.abspath(__file__))
    if os.path.exists('/.flatpak-info'):
        return os.environ.get('XDG_DATA_HOME', os.path.expanduser('~'))
    return os.path.expanduser('~')


def _scenarios_dir() -> str:
    d = os.path.join(_data_home(), '.stock_monitor_configs', 'scenarios')
    os.makedirs(d, exist_ok=True)
    return d


# ── Kleine Helfer ─────────────────────────────────────────────────────────────

def _fix_win_focus(dialog: QDialog, parent: QWidget) -> None:
    """Windows: Parent-Fenster nach Dialog-Schluss reaktivieren."""
    if sys.platform == 'win32':
        dialog.finished.connect(
            lambda: (parent.raise_(), parent.activateWindow()))


def _emoji_font(size: int = 10) -> Optional[QFont]:
    for name in ['Segoe UI Emoji', 'Noto Color Emoji', 'Apple Color Emoji']:
        if name in QFontDatabase.families():
            return QFont(name, size)
    return None


def _fmt(value: float, decimals: int = 2) -> str:
    try:
        import stock_monitor as _sm
        nfmt = getattr(_sm, '_NUMBER_FORMAT', 'CH')
    except Exception:
        nfmt = 'CH'
    formatted = f"{abs(value):,.{decimals}f}"
    if nfmt == 'CH':
        formatted = formatted.replace(',', "'")
    elif nfmt == 'DE':
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"-{formatted}" if value < 0 else formatted


def _is_dark() -> bool:
    return QApplication.palette().color(
        QPalette.ColorRole.Window).lightness() < 128


# ── Symbol-Typ Klassifizierung ────────────────────────────────────────────────

_CRYPTO_SFX  = ('-USD', '-EUR', '-CHF', '-BTC', '-ETH', '-USDT', '-USDC')
_COMMOD_SYMS = {'XAU', 'XAG', 'XPT', 'XPD', 'XCU', 'XBR', 'XPALLAD', 'XPLAT'}
_COMMOD_SFX  = ('=F',)   # Futures: GC=F, CL=F, …


def _sym_type(sym: str) -> str:
    """Gibt 'crypto', 'commodity', 'forex' oder 'stock' zurück."""
    s = sym.upper()
    if any(s.endswith(x) for x in _CRYPTO_SFX):
        return 'crypto'
    # Rohstoff-Spotpreise: XAU=X, XAG=X, …
    if s.endswith('=X') and s[:-2] in _COMMOD_SYMS:
        return 'commodity'
    # Rohstoff-Futures: GC=F, CL=F, …
    if s.endswith('=F'):
        return 'commodity'
    if s in _COMMOD_SYMS:
        return 'commodity'
    # Forex-Paare: EURUSD=X, GBPCHF=X, … → ausschliessen
    if '=' in s:
        return 'forex'
    return 'stock'


# ── ScenarioStore: Speichern / Laden ─────────────────────────────────────────

class ScenarioStore:
    """Persistiert Szenario-Portfolios als JSON-Dateien."""

    @staticmethod
    def _path(name: str) -> str:
        safe = "".join(c for c in name if c.isalnum() or c in ' _-').strip()
        if not safe:
            safe = "szenario"
        return os.path.join(_scenarios_dir(), f"{safe}.json")

    @staticmethod
    def save(name: str, positions: dict[str, float],
             real_pf_value: float) -> None:
        data = {
            'version': 1,
            'name': name,
            'saved_at': datetime.now().isoformat(timespec='seconds'),
            'real_pf_value': real_pf_value,
            'positions': positions,
        }
        with open(ScenarioStore._path(name), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load(name: str) -> Optional[dict]:
        p = ScenarioStore._path(name)
        if not os.path.exists(p):
            return None
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def list_names() -> list[str]:
        d = _scenarios_dir()
        names = []
        for fn in sorted(os.listdir(d)):
            if fn.endswith('.json'):
                try:
                    with open(os.path.join(d, fn), encoding='utf-8') as f:
                        obj = json.load(f)
                    names.append(obj.get('name', fn[:-5]))
                except Exception:
                    names.append(fn[:-5])
        return names

    @staticmethod
    def delete(name: str) -> None:
        p = ScenarioStore._path(name)
        if os.path.exists(p):
            os.remove(p)


# ── ScenarioMCWorker ──────────────────────────────────────────────────────────

class ScenarioMCWorker(QThread):
    """
    Führt Monte Carlo GBM für ein oder zwei Portfolios durch.
    values_usd      : dict[sym → USD-Wert] für das Szenario
    real_values_usd : dict[sym → USD-Wert] für das echte Portfolio (optional)
    """
    done = pyqtSignal(object)

    def __init__(self, values_usd: dict[str, float], years: int, n_sims: int,
                 inc_crypto: bool, inc_commod: bool,
                 real_values_usd: Optional[dict[str, float]] = None,
                 parent=None):
        super().__init__(parent)
        self._vals       = dict(values_usd)
        self._real_vals  = dict(real_values_usd) if real_values_usd else None
        self._years      = years
        self._n          = n_sims
        self._inc_crypto = inc_crypto
        self._inc_commod = inc_commod

    def run(self):
        try:
            import yfinance as yf
            import numpy as np
            import pandas as pd

            CRYPTO_SFX  = ('-USD', '-EUR', '-CHF', '-BTC')
            COMMOD_SYMS = {'XAU', 'XAG', 'XPT', 'XPD', 'XCU'}

            def _keep(s):
                if _sym_type(s) == 'forex': return False
                if not self._inc_crypto and _sym_type(s) == 'crypto': return False
                if not self._inc_commod and _sym_type(s) == 'commodity': return False
                return True

            scen_syms = [s for s in self._vals if _keep(s)]
            real_syms = ([s for s in self._real_vals if _keep(s)]
                         if self._real_vals else [])
            all_syms = list(dict.fromkeys(scen_syms + real_syms))

            if not scen_syms:
                self.done.emit({'error': TR('msg_mc_no_syms_after_filter')}); return

            today = pd.Timestamp.today().normalize()
            start = today - pd.Timedelta(days=730)
            try:
                raw = yf.download(all_syms, start=start.strftime('%Y-%m-%d'),
                                  auto_adjust=True, progress=False)
            except Exception:
                self.done.emit({'error': TR('msg_mc_no_prices')}); return

            if raw.empty:
                self.done.emit({'error': TR('msg_mc_no_prices')}); return

            if isinstance(raw.columns, pd.MultiIndex):
                close = raw['Close']
            else:
                close = raw[['Close']].rename(columns={'Close': all_syms[0]})

            close.index = pd.to_datetime(close.index).normalize().tz_localize(None)
            close = close.ffill().dropna(how='all')

            if len(close) < 60:
                self.done.emit({'error': TR('msg_mc_too_short')}); return

            def _simulate(sym_list, val_dict):
                total = sum(val_dict.get(s, 0) for s in sym_list
                            if s in close.columns)
                if total <= 0:
                    return None
                pf_ret = pd.Series(0.0, index=close.index[1:])
                for s in sym_list:
                    if s not in close.columns: continue
                    w = val_dict.get(s, 0) / total
                    if w <= 0: continue
                    r = close[s].pct_change().dropna()
                    r = r.reindex(pf_ret.index).fillna(0.0)
                    pf_ret += r * w

                pf_ret = pf_ret.replace(
                    [float('inf'), float('-inf')], float('nan')).dropna()
                if len(pf_ret) < 30:
                    return None

                mu  = float(pf_ret.mean())
                sig = float(pf_ret.std())
                steps = self._years * 252
                dt    = 1.0 / 252.0
                drift = (mu - 0.5 * sig ** 2) * dt
                diff  = sig * np.sqrt(dt)
                Z     = np.random.normal(0, 1, (self._n, steps))
                paths = total * np.exp(np.cumsum(drift + diff * Z, axis=1))
                dates = pd.date_range(today, periods=steps, freq='B')
                return {
                    'dates': dates,
                    'p10':  np.percentile(paths, 10,  axis=0),
                    'p25':  np.percentile(paths, 25,  axis=0),
                    'p50':  np.percentile(paths, 50,  axis=0),
                    'p75':  np.percentile(paths, 75,  axis=0),
                    'p90':  np.percentile(paths, 90,  axis=0),
                    'portfolio_value': total,
                    'years': self._years, 'n_sims': self._n,
                }

            scen_res = _simulate(scen_syms, self._vals)
            if scen_res is None:
                self.done.emit({'error': TR('msg_mc_no_data')}); return

            real_res = None
            if self._real_vals and real_syms:
                real_res = _simulate(real_syms, self._real_vals)

            self.done.emit({'scenario': scen_res, 'real': real_res})

        except Exception as ex:
            self.done.emit({'error': str(ex)})


# ── Ticker-Such-Worker ────────────────────────────────────────────────────────

class _SymSearchWorker(QThread):
    """Prüft ob ein Ticker existiert; falls nicht, liefert yfinance-Suchvorschläge."""
    # (symbol, found_name, suggestions: list[(sym, name)])
    result = pyqtSignal(str, str, list)

    def __init__(self, sym: str, parent=None):
        super().__init__(parent)
        self._sym = sym

    def run(self):
        try:
            import yfinance as yf
            ticker = yf.Ticker(self._sym)
            hist = ticker.history(period='5d')
            if not hist.empty:
                fi = ticker.fast_info
                name = (getattr(fi, 'long_name', None) or
                        getattr(fi, 'shortName', None) or
                        self._sym)
                self.result.emit(self._sym, str(name), [])
                return
            # Nicht gefunden → Suchvorschläge
            suggestions = []
            try:
                search = yf.Search(self._sym, max_results=6)
                for q in (search.quotes or []):
                    s = q.get('symbol', '')
                    n = q.get('shortname') or q.get('longname') or ''
                    if s:
                        suggestions.append((s, n))
            except Exception:
                pass
            self.result.emit(self._sym, '', suggestions)
        except Exception:
            self.result.emit(self._sym, '', [])


# ── Namen-Lade-Worker ────────────────────────────────────────────────────────

class _NameLoader(QThread):
    """Lädt Firmennamen parallel via yfinance.Ticker.info im Hintergrund."""
    name_ready = pyqtSignal(str, str)   # (symbol, name)

    def __init__(self, symbols: list[str], parent=None):
        super().__init__(parent)
        self._symbols = list(symbols)

    def run(self):
        import yfinance as yf
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def _fetch_one(sym: str):
            try:
                info = yf.Ticker(sym).info
                name = info.get('longName') or info.get('shortName') or ''
                return sym, name
            except Exception:
                return sym, ''

        workers = min(8, max(1, len(self._symbols)))
        with ThreadPoolExecutor(max_workers=workers) as exe:
            futs = {exe.submit(_fetch_one, s): s for s in self._symbols}
            for fut in as_completed(futs):
                try:
                    sym, name = fut.result()
                    if name:
                        self.name_ready.emit(sym, name)
                except Exception:
                    pass


# ── Standalone-Export ─────────────────────────────────────────────────────────

def _export_pdf(path: str, data: dict) -> None:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, Image as RLImage)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    import io

    headers = data.get('headers', [])
    rows    = data.get('rows', [])
    fig     = data.get('fig')
    title   = data.get('title', 'Export')

    ps  = landscape(A4) if len(headers) > 6 else A4
    doc = SimpleDocTemplate(path, pagesize=ps,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    story  = [Paragraph(title, styles['Title']), Spacer(1, 0.3*cm)]

    if fig is not None:
        try:
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            from PIL import Image as _PILImg
            _pil = _PILImg.open(buf); _pw, _ph = _pil.size; buf.seek(0)
            max_w = ps[0] - 3*cm; max_h = ps[1] - 8*cm
            aspect = _ph / _pw if _pw > 0 else 0.6
            img_w = max_w; img_h = img_w * aspect
            if img_h > max_h:
                img_h = max_h; img_w = img_h / aspect
            story += [RLImage(buf, width=img_w, height=img_h), Spacer(1, 0.4*cm)]
        except Exception:
            pass

    if headers and rows:
        story.append(Paragraph(TR('lbl_data'), styles['Heading2']))
        story.append(Spacer(1, 0.2*cm))
        page_w = ps[0] - 3*cm
        def _cw(h):
            hl = h.lower()
            if any(k in hl for k in ('name', 'firma', 'company')): return 3.0
            if any(k in hl for k in ('symbol', 'sym')): return 1.5
            return 1.0
        ws  = [_cw(h) for h in headers]; col_w = [page_w * w/sum(ws) for w in ws]
        cs  = ParagraphStyle('c', parent=styles['Normal'], fontSize=7, leading=9)
        hs  = ParagraphStyle('h', parent=styles['Normal'], fontSize=7, leading=9,
                              textColor=colors.white, fontName='Helvetica-Bold')
        def _cell(t, st):
            return Paragraph(str(t or '').replace('\n', '<br/>'), st)
        n   = len(headers)
        td  = [[_cell(h, hs) for h in headers]] + [
              [_cell((list(r)+['']*n)[i], cs) for i in range(n)] for r in rows if r]
        t   = Table(td, colWidths=col_w, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND',     (0,0), (-1,0),  colors.HexColor('#2c3e50')),
            ('TEXTCOLOR',      (0,0), (-1,0),  colors.white),
            ('FONTSIZE',       (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1),
             [colors.HexColor('#f8f9fa'), colors.white]),
            ('GRID',           (0,0), (-1,-1), 0.4, colors.HexColor('#dee2e6')),
            ('TOPPADDING',     (0,0), (-1,-1), 3),
            ('BOTTOMPADDING',  (0,0), (-1,-1), 3),
        ]))
        story.append(t)

    story += [Spacer(1, 0.5*cm), Paragraph(
        TR('export_footer_long',
           dt=datetime.now().strftime('%d.%m.%Y %H:%M')),
        ParagraphStyle('f', parent=styles['Normal'], fontSize=7,
                       textColor=colors.grey))]
    doc.build(story)


def _export_xlsx(path: str, data: dict) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter

    headers = data.get('headers', []); rows = data.get('rows', [])
    wb = Workbook(); ws = wb.active
    ws.title = data.get('title', 'Szenarien')[:31]

    hdr_fill = PatternFill('solid', fgColor='2C3E50')
    hdr_font = Font(color='FFFFFF', bold=True, size=10)
    for ci, h in enumerate(headers, 1):
        cell = ws.cell(1, ci, h)
        cell.fill = hdr_fill; cell.font = hdr_font
        cell.alignment = Alignment(horizontal='center')

    alt_fill = PatternFill('solid', fgColor='F8F9FA')
    for ri, row in enumerate(rows, 2):
        for ci, val in enumerate(list(row)[:len(headers)], 1):
            cell = ws.cell(ri, ci, val)
            if ri % 2 == 0: cell.fill = alt_fill

    for ci, h in enumerate(headers, 1):
        mx = max((len(str(h)),) + tuple(
            len(str((list(r)+[''])[ci-1])) for r in rows if r), default=8)
        ws.column_dimensions[get_column_letter(ci)].width = min(mx + 4, 45)

    wb.save(path)


def _export_ods(path: str, data: dict) -> None:
    try:
        import odf.opendocument as _odd
        import odf.table as _odt
        import odf.style as _ods_style
        import odf.text as _odt_text
    except ImportError:
        _export_xlsx(path.replace('.ods', '.xlsx'), data)
        return

    headers = data.get('headers', []); rows = data.get('rows', [])
    doc = _odd.OpenDocumentSpreadsheet()
    sheet = _odt.Table(name=data.get('title', 'Szenarien')[:30])
    doc.spreadsheet.addElement(sheet)

    for row_data in ([headers] + list(rows)):
        tr = _odt.TableRow()
        for val in (list(row_data)[:len(headers)] if row_data is not headers
                    else row_data):
            tc = _odt.TableCell()
            tc.addElement(_odt_text.P(text=str(val or '')))
            tr.addElement(tc)
        sheet.addElement(tr)
    doc.save(path)


def _run_export_dialog(parent: QWidget, get_data_fn,
                       default_title: str = 'Szenarien') -> None:
    try:
        data = get_data_fn()
    except Exception as e:
        QMessageBox.warning(parent, TR('msg_title_error'),
                            TR('msg_data_load_failed', e=e))
        return
    if not data:
        QMessageBox.information(parent, TR('msg_title_info'),
                                TR('scen_msg_no_export_data'))
        return

    fmt_dlg = QDialog(parent)
    fmt_dlg.setWindowTitle(TR('title_export2'))
    fmt_dlg.setFixedWidth(340)
    _fix_win_focus(fmt_dlg, parent)

    lay = QVBoxLayout(fmt_dlg)
    lay.setSpacing(10); lay.setContentsMargins(18, 14, 18, 14)
    lay.addWidget(QLabel(f"<b>{TR('lbl_export_colon')} {data.get('title','')}</b>"))
    lay.addWidget(QLabel(TR('lbl_format_choose')))

    from PyQt6.QtWidgets import QButtonGroup, QRadioButton
    grp = QButtonGroup(fmt_dlg)
    rb_pdf  = QRadioButton('📄  PDF');        rb_pdf.setChecked(True)
    rb_xlsx = QRadioButton('📊  Excel (.xlsx)')
    rb_ods  = QRadioButton('📋  OpenDocument (.ods)')
    for rb in (rb_pdf, rb_xlsx, rb_ods):
        grp.addButton(rb); lay.addWidget(rb)

    btn_row = QHBoxLayout()
    ok_btn = QPushButton(TR('btn_save_dots'))
    ok_btn.setStyleSheet('font-weight:bold;')
    ca_btn = QPushButton(TR('btn_cancel'))
    btn_row.addWidget(ok_btn); btn_row.addWidget(ca_btn)
    lay.addLayout(btn_row)
    ca_btn.clicked.connect(fmt_dlg.reject)

    def _do_save():
        if rb_pdf.isChecked():    ext, flt = '.pdf',  'PDF (*.pdf)'
        elif rb_xlsx.isChecked(): ext, flt = '.xlsx', 'Excel (*.xlsx)'
        else:                     ext, flt = '.ods',  'ODS (*.ods)'
        safe = ''.join(c for c in data.get('title', default_title)
                       if c.isalnum() or c in ' _-').strip()
        path, _ = QFileDialog.getSaveFileName(
            fmt_dlg, TR('btn_save_dots'),
            os.path.expanduser(f'~/{safe}{ext}'), flt)
        if not path: return
        fmt_dlg.accept()
        try:
            if ext == '.pdf':   _export_pdf(path, data)
            elif ext == '.xlsx': _export_xlsx(path, data)
            else:                _export_ods(path, data)
            QMessageBox.information(parent, TR('msg_title_exported'),
                                    TR('msg_saved_ok', path=path))
        except Exception as e:
            QMessageBox.warning(parent, TR('msg_title_error'),
                                TR('msg_export_failed', e=e))

    ok_btn.clicked.connect(_do_save)
    fmt_dlg.exec()


# ── ScenarioEditorDialog ──────────────────────────────────────────────────────

class ScenarioEditorDialog(QDialog):
    """
    Haupt-Dialog für Szenario-Portfolio-Erstellung und MC-Simulation.
    portfolio_data : dict[sym, list[positions]]  – echtes Portfolio
    price_cache    : dict[sym, {value_usd, ...}] – aktueller Cache
    currency       : Anzeigewährung ('USD', 'CHF', ...)
    fx_rate        : Umrechnungskurs USD → currency
    """

    def __init__(self, portfolio_data: dict, price_cache: dict,
                 parent: QWidget,
                 currency: str = 'USD', fx_rate: float = 1.0):
        super().__init__(parent)
        self._pf_data    = portfolio_data
        self._cache      = price_cache
        self._cur        = currency
        self._fx         = fx_rate
        self._cur_sym    = {'USD': '$', 'CHF': 'CHF ', 'EUR': '€',
                            'GBP': '£'}.get(currency, '$')
        self._dm         = _is_dark()
        self._ef         = _emoji_font(10)

        # Echtes Portfolio: {sym: value_usd} aus Cache
        # Forex-Paare ausschliessen, Rohstoffe (=X Spot, =F Futures) einschliessen
        self._real_values: dict[str, float] = {}
        for sym, positions in portfolio_data.items():
            if _sym_type(sym) == 'forex':
                continue
            ce = price_cache.get(sym, {})
            v = float(ce.get('value_usd', 0) or 0) if isinstance(ce, dict) else 0.0
            if v > 0:
                self._real_values[sym] = v
        self._real_total = sum(self._real_values.values())

        # Szenario-Positionen (bearbeitbar)
        self._positions: dict[str, float] = dict(self._real_values)
        self._backup:    Optional[dict[str, float]] = None   # für Undo
        self._is_dirty   = False
        self._locked     = True   # ±10%-Sperre aktiv

        # Name für das aktuelle Szenario
        self._name       = TR('scen_default_name')

        # Name-Cache: bleibt über _refresh_table hinaus erhalten
        self._name_cache: dict[str, str] = {}

        # MC-Ergebnis-Referenz für Export
        self._mc_fig          = [None]
        self._mc_export_data  = [{}]
        self._worker_ref      = [None]

        self.setWindowTitle(TR('scen_title'))
        screen = (parent.screen() if hasattr(parent, 'screen') else
                  None) or QApplication.primaryScreen()
        geo = screen.availableGeometry()
        w = int(geo.width()  * 0.84)
        h = int(geo.height() * 0.88)
        self.resize(w, h)
        self.move(geo.x() + (geo.width()  - w) // 2,
                  geo.y() + (geo.height() - h) // 2)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        _fix_win_focus(self, parent)

        self._build_ui()
        self._refresh_table()

    # ── UI-Aufbau ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setSpacing(6)
        outer.setContentsMargins(12, 10, 12, 8)

        # Titelzeile mit Name + Speichern/Laden/Schließen
        top = QHBoxLayout(); top.setSpacing(8)
        top.addWidget(QLabel(f"<b style='font-size:13px'>{TR('scen_title')}</b>"))
        top.addSpacing(16)
        top.addWidget(QLabel(f"<b>{TR('scen_lbl_name')}</b>"))
        self._name_edit = QLineEdit(self._name)
        self._name_edit.setMinimumWidth(200)
        self._name_edit.setMaximumWidth(300)
        self._name_edit.textChanged.connect(
            lambda t: setattr(self, '_name', t.strip() or TR('scen_default_name')))
        top.addWidget(self._name_edit)

        save_btn = QPushButton(TR('scen_btn_save'))
        save_btn.setMinimumHeight(28); save_btn.setMaximumWidth(110)
        if self._ef: save_btn.setFont(self._ef)
        save_btn.setStyleSheet(
            'QPushButton{background:#2ecc71;color:white;font-weight:bold;'
            'border-radius:4px;padding:2px 10px;}'
            'QPushButton:hover{background:#27ae60;}')
        save_btn.clicked.connect(self._save_scenario)
        top.addWidget(save_btn)

        load_btn = QPushButton(TR('scen_btn_load'))
        load_btn.setMinimumHeight(28); load_btn.setMaximumWidth(110)
        if self._ef: load_btn.setFont(self._ef)
        load_btn.clicked.connect(self._load_scenario)
        top.addWidget(load_btn)

        self._undo_btn = QPushButton(TR('scen_btn_undo_clear'))
        self._undo_btn.setMinimumHeight(28)
        self._undo_btn.setSizePolicy(QSizePolicy.Policy.Preferred,
                                     QSizePolicy.Policy.Fixed)
        if self._ef: self._undo_btn.setFont(self._ef)
        self._undo_btn.setStyleSheet(
            'QPushButton{background:#e67e22;color:white;font-weight:bold;'
            'border-radius:4px;padding:2px 10px;}'
            'QPushButton:hover{background:#d35400;}')
        self._undo_btn.setVisible(False)
        self._undo_btn.clicked.connect(self._undo_clear)
        top.addWidget(self._undo_btn)

        top.addStretch()

        help_btn = QPushButton(TR('btn_help'))
        help_btn.setMaximumWidth(90)
        if self._ef: help_btn.setFont(self._ef)
        def _show_scen_help():
            app = self.parent()
            while app and not hasattr(app, 'show_help'):
                app = app.parent() if hasattr(app, 'parent') else None
            if app:
                app.show_help(anchor='mc-szenarien', parent_widget=self)
        help_btn.clicked.connect(_show_scen_help)
        top.addWidget(help_btn)

        close_btn = QPushButton(TR('btn_close'))
        close_btn.setMaximumWidth(110)
        close_btn.clicked.connect(self.close)
        top.addWidget(close_btn)
        outer.addLayout(top)

        # Tabs
        self._tabs = QTabWidget()
        outer.addWidget(self._tabs, stretch=1)

        pos_widget = QWidget()
        self._build_positions_tab(pos_widget)
        self._tabs.addTab(pos_widget, TR('scen_tab_positions'))

        mc_widget = QWidget()
        self._build_mc_tab(mc_widget)
        self._tabs.addTab(mc_widget, TR('scen_tab_mc'))

    # ── Tab 1: Positionen ─────────────────────────────────────────────────────

    def _build_positions_tab(self, container: QWidget) -> None:
        lay = QVBoxLayout(container)
        lay.setSpacing(6); lay.setContentsMargins(8, 8, 8, 8)

        # Info
        info_bg = '#0d2a3d' if self._dm else '#EBF5FB'
        info = QLabel(TR('scen_lbl_info'))
        info.setWordWrap(True)
        info.setStyleSheet(
            f'background:{info_bg};border-radius:6px;padding:8px 14px;font-size:12px;')
        lay.addWidget(info)

        # Tabelle
        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels([
            TR('scen_col_symbol'), TR('scen_col_name'),
            f"{TR('scen_col_value')} ({self._cur})",
            TR('scen_col_pct'), '',
        ])
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(0, 90)
        self._table.setColumnWidth(2, 145)
        self._table.setColumnWidth(3, 80)
        self._table.setColumnWidth(4, 44)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        lay.addWidget(self._table, stretch=1)

        # Gesamtwert-Anzeige
        self._total_lbl = QLabel('')
        self._total_lbl.setStyleSheet(
            'font-size:12px; font-weight:bold; padding:4px 8px;'
            'border-radius:5px;')
        lay.addWidget(self._total_lbl)

        # Button-Zeile
        btn_row = QHBoxLayout(); btn_row.setSpacing(8)

        add_btn = QPushButton(TR('scen_btn_add_pos'))
        add_btn.setMinimumHeight(30)
        if self._ef: add_btn.setFont(self._ef)
        add_btn.setStyleSheet(
            'QPushButton{background:#3498db;color:white;font-weight:bold;'
            'border-radius:4px;padding:2px 12px;}'
            'QPushButton:hover{background:#2980b9;}')
        add_btn.clicked.connect(self._add_position)
        btn_row.addWidget(add_btn)

        clear_btn = QPushButton(TR('scen_btn_clear_all'))
        clear_btn.setMinimumHeight(30)
        if self._ef: clear_btn.setFont(self._ef)
        clear_btn.setStyleSheet(
            'QPushButton{background:#e74c3c;color:white;font-weight:bold;'
            'border-radius:4px;padding:2px 12px;}'
            'QPushButton:hover{background:#c0392b;}')
        clear_btn.clicked.connect(self._clear_all)
        btn_row.addWidget(clear_btn)

        new_btn = QPushButton(TR('scen_btn_new'))
        new_btn.setMinimumHeight(30)
        if self._ef: new_btn.setFont(self._ef)
        new_btn.clicked.connect(self._new_portfolio)
        btn_row.addWidget(new_btn)

        btn_row.addStretch()

        self._lock_btn = QPushButton(TR('scen_btn_unlock'))
        self._lock_btn.setMinimumHeight(30); self._lock_btn.setMaximumWidth(210)
        if self._ef: self._lock_btn.setFont(self._ef)
        self._lock_btn.setCheckable(True)
        self._lock_btn.clicked.connect(self._toggle_lock)
        btn_row.addWidget(self._lock_btn)
        self._refresh_lock_btn()

        lay.addLayout(btn_row)

    # ── Tab 2: Monte Carlo ────────────────────────────────────────────────────

    def _build_mc_tab(self, container: QWidget) -> None:
        import matplotlib
        matplotlib.use('QtAgg')
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        from matplotlib.figure import Figure

        lay = QVBoxLayout(container)
        lay.setSpacing(6); lay.setContentsMargins(8, 8, 8, 8)

        # Info
        info_bg = '#0d2a3d' if self._dm else '#EBF5FB'
        info = QLabel(TR('lbl_mc_info'))
        info.setWordWrap(True)
        info.setStyleSheet(
            f'background:{info_bg};border-radius:6px;padding:8px 14px;font-size:12px;')
        lay.addWidget(info)

        # Steuerung
        ctrl = QHBoxLayout(); ctrl.setSpacing(8)

        ctrl.addWidget(QLabel(f"<b>{TR('lbl_mc_horizon')}</b>"))
        self._horizon_combo = QComboBox()
        HORIZONS = [(TR('mc_horizon_1y'), 1), (TR('mc_horizon_3y'), 3),
                    (TR('mc_horizon_5y'), 5), (TR('mc_horizon_10y'), 10),
                    (TR('mc_horizon_15y'), 15), (TR('mc_horizon_20y'), 20),
                    (TR('mc_horizon_25y'), 25), (TR('mc_horizon_30y'), 30)]
        self._HORIZONS = HORIZONS
        for lbl, _ in HORIZONS: self._horizon_combo.addItem(lbl)
        self._horizon_combo.setCurrentIndex(2)
        self._horizon_combo.setMinimumWidth(110); self._horizon_combo.setMinimumHeight(28)
        ctrl.addWidget(self._horizon_combo)

        ctrl.addWidget(QLabel(f"<b>{TR('lbl_mc_simulations')}</b>"))
        self._sims_combo = QComboBox()
        SIMS = [(f"500 ({TR('mc_sims_suffix_fast')})",   500),
                (f"1'000 ({TR('mc_sims_suffix_default')})", 1000),
                (f"5'000 ({TR('mc_sims_suffix_precise')})", 5000),
                (f"10'000 ({TR('mc_sims_suffix_max')})",    10000)]
        self._SIMS = SIMS
        for lbl, _ in SIMS: self._sims_combo.addItem(lbl)
        self._sims_combo.setCurrentIndex(1)
        self._sims_combo.setMinimumWidth(140); self._sims_combo.setMinimumHeight(28)
        ctrl.addWidget(self._sims_combo)

        self._run_btn = QPushButton(TR('btn_mc_run'))
        self._run_btn.setMinimumHeight(28)
        self._run_btn.setStyleSheet('font-weight:bold;padding:2px 14px;')
        self._run_btn.clicked.connect(self._run_mc)
        ctrl.addWidget(self._run_btn)

        self._crypto_cb = QCheckBox(TR('chk_mc_crypto'))
        self._commod_cb = QCheckBox(TR('chk_mc_commodities'))
        ctrl.addWidget(self._crypto_cb)
        ctrl.addWidget(self._commod_cb)

        self._compare_cb = QCheckBox(TR('scen_chk_compare'))
        self._compare_cb.setChecked(True)
        ctrl.addWidget(self._compare_cb)

        ctrl.addStretch()

        export_btn = QPushButton(TR('btn_export'))
        export_btn.setMinimumHeight(28)
        export_btn.setStyleSheet('padding:2px 12px;')
        if self._ef: export_btn.setFont(self._ef)
        export_btn.clicked.connect(
            lambda: _run_export_dialog(self, lambda: self._mc_export_data[0],
                                       TR('scen_title')))
        ctrl.addWidget(export_btn)
        lay.addLayout(ctrl)

        # Status
        self._mc_status = QLabel('')
        self._mc_status.setStyleSheet('color:#666;font-size:11px;')
        lay.addWidget(self._mc_status)

        # Chart + Lade-Overlay
        self._fig = Figure(figsize=(14, 8))
        self._fig.patch.set_facecolor('#ffffff')
        self._canvas = FigureCanvasQTAgg(self._fig)
        self._mc_fig[0] = self._fig

        self._mc_stack = QStackedWidget()
        self._mc_stack.addWidget(self._canvas)

        self._mc_loading = QLabel()
        self._mc_loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mc_loading.setStyleSheet(
            'background:#ffffff;color:#2471A3;font-size:22px;font-weight:bold;')
        if self._ef: self._mc_loading.setFont(self._ef)
        self._mc_stack.addWidget(self._mc_loading)
        self._mc_stack.setCurrentIndex(0)
        lay.addWidget(self._mc_stack, stretch=1)

        # Animations-Timer
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(400)
        self._anim_dots = [0]
        self._anim_icons = ['💵', '📈', '🎲', '⚙️', '🔢']
        self._anim_idx   = [0]
        def _tick():
            self._anim_dots[0] = (self._anim_dots[0] + 1) % 4
            self._anim_idx[0]  = (self._anim_idx[0]  + 1) % len(self._anim_icons)
            n = self._SIMS[self._sims_combo.currentIndex()][1]
            h = self._HORIZONS[self._horizon_combo.currentIndex()][1]
            try:
                self._mc_loading.setText(
                    f"{self._anim_icons[self._anim_idx[0]]}  "
                    f"{TR('status_mc_running', n=n, h=h)}"
                    f"{'.' * self._anim_dots[0]}")
            except RuntimeError:
                self._anim_timer.stop()
        self._anim_timer.timeout.connect(_tick)

        # Ergebnistabelle
        self._result_table = QTableWidget(0, 3)
        self._result_table.setHorizontalHeaderLabels([
            TR('mc_table_header'), TR('mc_table_value'), TR('mc_table_change')])
        self._result_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self._result_table.setMaximumHeight(160)
        self._result_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self._result_table.setAlternatingRowColors(True)
        self._result_table.setVisible(False)
        lay.addWidget(self._result_table)

        disc = QLabel(TR('lbl_mc_disclaimer'))
        disc.setWordWrap(True)
        disc.setStyleSheet(
            'background:#FEF9E7;border-radius:5px;padding:6px 12px;'
            'font-size:11px;color:#7D6608;')
        lay.addWidget(disc)

    # ── Tabelle aktualisieren ─────────────────────────────────────────────────

    def _refresh_table(self) -> None:
        self._table.setRowCount(0)
        # _row_sym_map: Zeilen-Index → Symbol (None für Gruppen-Header)
        self._row_sym_map: list[Optional[str]] = []

        total_usd = sum(self._positions.values())
        stocks      = {s: v for s, v in self._positions.items()
                       if _sym_type(s) == 'stock'}
        cryptos     = {s: v for s, v in self._positions.items()
                       if _sym_type(s) == 'crypto'}
        commodities = {s: v for s, v in self._positions.items()
                       if _sym_type(s) == 'commodity'}

        grp_hdr_bg = QColor('#34495e') if self._dm else QColor('#2c3e50')
        grp_hdr_fg = QColor('#ecf0f1')

        groups = [
            (TR('scen_group_stocks'),      stocks),
            (TR('scen_group_crypto'),      cryptos),
            (TR('scen_group_commodities'), commodities),
        ]

        for grp_label, grp_dict in groups:
            if not grp_dict:
                continue

            # ── Gruppen-Header ──────────────────────────────────────────
            hdr_row = self._table.rowCount()
            self._table.insertRow(hdr_row)
            self._table.setRowHeight(hdr_row, 26)
            self._row_sym_map.append(None)

            hdr_item = QTableWidgetItem(grp_label)
            hdr_item.setBackground(grp_hdr_bg)
            hdr_item.setForeground(grp_hdr_fg)
            hdr_item.setFont(QFont('Arial', 9, QFont.Weight.Bold))
            hdr_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self._table.setItem(hdr_row, 0, hdr_item)
            self._table.setSpan(hdr_row, 0, 1, 5)

            # ── Symbole dieser Gruppe ───────────────────────────────────
            for sym in sorted(grp_dict, key=lambda s: -grp_dict[s]):
                val_usd  = grp_dict[sym]
                val_disp = val_usd * self._fx
                pct      = val_usd / total_usd * 100 if total_usd > 0 else 0

                data_row = self._table.rowCount()
                self._table.insertRow(data_row)
                self._table.setRowHeight(data_row, 36)
                self._row_sym_map.append(sym)

                # Symbol
                sym_item = QTableWidgetItem(sym)
                sym_item.setFont(QFont('Arial', 10, QFont.Weight.Bold))
                sym_item.setFlags(sym_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self._table.setItem(data_row, 0, sym_item)

                # Name (aus Cache – lazy, Tooltip wird in _fetch_names_lazy gesetzt)
                name_item = QTableWidgetItem('')
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self._table.setItem(data_row, 1, name_item)

                # Wert – editierbares SpinBox
                spin = QDoubleSpinBox()
                spin.setRange(0.01, 999_999_999.0)
                spin.setDecimals(0)
                spin.setSingleStep(100)
                spin.setValue(round(val_disp))
                spin.setMinimumHeight(30)
                spin.editingFinished.connect(
                    lambda s=sym, sp=spin: self._on_value_changed(s, sp.value()))
                self._table.setCellWidget(data_row, 2, spin)

                # Anteil
                pct_item = QTableWidgetItem(f"{pct:.1f}%")
                pct_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                pct_item.setFlags(pct_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self._table.setItem(data_row, 3, pct_item)

                # Löschen-Button
                del_btn = QPushButton('✕')
                del_btn.setFixedSize(32, 28)
                if self._ef: del_btn.setFont(self._ef)
                del_btn.setStyleSheet(
                    'QPushButton{color:#e74c3c;font-weight:bold;border:none;}'
                    'QPushButton:hover{background:#fdecea;border-radius:4px;}')
                del_btn.clicked.connect(
                    lambda _, s=sym: self._delete_position(s))
                self._table.setCellWidget(data_row, 4, del_btn)

        self._refresh_total_bar()
        self._fetch_names_lazy()

    def _fetch_names_lazy(self) -> None:
        """
        1. Sofort: bekannte Namen aus _name_cache in Tabelle schreiben.
        2. Fehlende: _NameLoader (parallel, Hintergrund) starten.
        """
        missing = []
        for row in range(self._table.rowCount()):
            sym_item = self._table.item(row, 0)
            if not sym_item or not sym_item.text():
                continue
            sym = sym_item.text()
            name = self._name_cache.get(sym, '')
            if name:
                self._set_name_in_row(row, sym, name)
            else:
                missing.append(sym)

        if missing:
            loader = _NameLoader(missing, self)
            loader.name_ready.connect(
                self._on_name_ready, Qt.ConnectionType.QueuedConnection)
            loader.finished.connect(loader.deleteLater)
            loader.start()

    def _set_name_in_row(self, row: int, sym: str, name: str) -> None:
        """Schreibt Namen in die Tabellenzelle, Tooltip auf Symbol-Zelle."""
        self._name_cache[sym] = name
        name_item = self._table.item(row, 1)
        if name_item:
            name_item.setText(name)
        sym_item = self._table.item(row, 0)
        if sym_item:
            sym_item.setToolTip(name)

    def _on_name_ready(self, sym: str, name: str) -> None:
        """Callback wenn _NameLoader einen Namen geliefert hat."""
        self._name_cache[sym] = name
        # Zeile in der Tabelle suchen und aktualisieren
        for row, mapped_sym in enumerate(getattr(self, '_row_sym_map', [])):
            if mapped_sym == sym:
                self._set_name_in_row(row, sym, name)
                break

    def _refresh_total_bar(self) -> None:
        total_usd = sum(self._positions.values())
        total_disp = total_usd * self._fx
        ref_disp   = self._real_total * self._fx
        if ref_disp > 0:
            diff_pct = (total_usd - self._real_total) / self._real_total * 100
        else:
            diff_pct = 0.0

        sign = '+' if diff_pct >= 0 else ''
        txt = (f"{TR('scen_total_label')}: "
               f"{self._cur_sym}{_fmt(total_disp, 0)}  /  "
               f"{self._cur_sym}{_fmt(ref_disp, 0)} "
               f"({sign}{diff_pct:.1f}%)")

        if not self._locked:
            bg = '#1a3a1a' if self._dm else '#e8f5e9'
            col = '#27ae60'
        elif abs(diff_pct) <= 10:
            bg = '#1a3a1a' if self._dm else '#eafaf1'
            col = '#27ae60'
        elif abs(diff_pct) <= 15:
            bg = '#3a2a00' if self._dm else '#fef9e7'
            col = '#d35400'
        else:
            bg = '#3a1a1a' if self._dm else '#fdecea'
            col = '#c0392b'

        self._total_lbl.setText(txt)
        self._total_lbl.setStyleSheet(
            f'font-size:12px;font-weight:bold;padding:6px 10px;'
            f'border-radius:6px;background:{bg};color:{col};')

    def _refresh_lock_btn(self) -> None:
        if self._locked:
            self._lock_btn.setText(TR('scen_btn_unlock'))
            self._lock_btn.setStyleSheet(
                'QPushButton{background:#7f8c8d;color:white;border-radius:4px;'
                'padding:2px 10px;}QPushButton:hover{background:#636e72;}')
        else:
            self._lock_btn.setText(TR('scen_btn_lock'))
            self._lock_btn.setStyleSheet(
                'QPushButton{background:#e74c3c;color:white;border-radius:4px;'
                'padding:2px 10px;}QPushButton:hover{background:#c0392b;}')

    # ── Aktionen ──────────────────────────────────────────────────────────────

    def _on_value_changed(self, sym: str, disp_val: float) -> None:
        new_usd = disp_val / self._fx if self._fx > 0 else disp_val
        if self._locked and self._real_total > 0:
            new_total = (sum(self._positions.values()) - self._positions.get(sym, 0)
                         + new_usd)
            diff_pct = abs(new_total - self._real_total) / self._real_total * 100
            if diff_pct > 10:
                max_usd = self._real_total * 1.10 - (
                    sum(self._positions.values()) - self._positions.get(sym, 0))
                min_usd = max(0.01,
                              self._real_total * 0.90 - (
                                  sum(self._positions.values())
                                  - self._positions.get(sym, 0)))
                new_usd = max(min_usd, min(max_usd, new_usd))
        self._positions[sym] = new_usd
        self._is_dirty = True
        self._refresh_total_bar()
        self._update_pct_column()

    def _update_pct_column(self) -> None:
        total = sum(self._positions.values())
        for row, sym in enumerate(getattr(self, '_row_sym_map', [])):
            if sym is None:
                continue
            pct_item = self._table.item(row, 3)
            if pct_item:
                pct = self._positions.get(sym, 0) / total * 100 if total > 0 else 0
                pct_item.setText(f"{pct:.1f}%")

    def _add_position(self) -> None:
        """Symbol eingeben, Ticker wird beim OK-Klick automatisch geprüft."""
        add_dlg = QDialog(self)
        add_dlg.setWindowTitle(TR('scen_add_title'))
        add_dlg.setMinimumWidth(380)
        add_dlg.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        _fix_win_focus(add_dlg, self)

        lay = QVBoxLayout(add_dlg)
        lay.setSpacing(10); lay.setContentsMargins(16, 14, 16, 12)

        lay.addWidget(QLabel(f"<b>{TR('scen_lbl_symbol')}</b>"))
        sym_edit = QLineEdit()
        sym_edit.setPlaceholderText('z.B. NVDA, MSFT, BTC-USD, GC=F')
        sym_edit.setMinimumHeight(30)
        lay.addWidget(sym_edit)

        # Status-Label (unsichtbar bis OK geklickt)
        status_lbl = QLabel('')
        status_lbl.setWordWrap(True)
        status_lbl.setStyleSheet('font-size:11px;min-height:18px;')
        lay.addWidget(status_lbl)

        # Vorschläge-Bereich (zunächst versteckt)
        sugg_widget = QWidget()
        sugg_lay = QVBoxLayout(sugg_widget)
        sugg_lay.setSpacing(4); sugg_lay.setContentsMargins(0, 4, 0, 0)
        sugg_widget.setVisible(False)
        lay.addWidget(sugg_widget)

        lay.addWidget(QLabel(f"<b>{TR('scen_lbl_value')} ({self._cur})</b>"))
        val_spin = QDoubleSpinBox()
        val_spin.setRange(1, 999_999_999); val_spin.setDecimals(0)
        val_spin.setValue(1000); val_spin.setSingleStep(500)
        val_spin.setMinimumHeight(30)
        lay.addWidget(val_spin)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton(TR('btn_ok'))
        ok_btn.setStyleSheet('font-weight:bold;')
        ca_btn = QPushButton(TR('btn_cancel'))
        btn_row.addWidget(ok_btn); btn_row.addWidget(ca_btn)
        lay.addLayout(btn_row)
        ca_btn.clicked.connect(add_dlg.reject)

        _worker_ref = [None]

        def _clear_suggestions():
            while sugg_lay.count():
                item = sugg_lay.takeAt(0)
                if item.widget(): item.widget().deleteLater()
            sugg_widget.setVisible(False)
            add_dlg.adjustSize()

        def _on_sym_typed():
            _clear_suggestions()
            status_lbl.setText('')

        sym_edit.textChanged.connect(_on_sym_typed)

        def _use_suggestion(s: str, n: str):
            """Vorschlag anklicken → Symbol übernehmen und sofort einfügen."""
            _clear_suggestions()
            val_disp = val_spin.value()
            val_usd  = val_disp / self._fx if self._fx > 0 else val_disp
            if s in self._positions:
                self._positions[s] += val_usd
            else:
                self._positions[s] = val_usd
            self._is_dirty = True
            # Name in Cache merken für Tooltip
            if n and s not in self._cache:
                self._cache[s] = {'longName': n}
            add_dlg.accept()
            self._refresh_table()

        def _on_result(checked_sym: str, name: str, suggestions: list):
            ok_btn.setEnabled(True)
            ca_btn.setEnabled(True)
            if name:
                # Gefunden → sofort einfügen
                val_disp = val_spin.value()
                val_usd  = val_disp / self._fx if self._fx > 0 else val_disp
                if checked_sym in self._positions:
                    self._positions[checked_sym] += val_usd
                else:
                    self._positions[checked_sym] = val_usd
                self._is_dirty = True
                if name and checked_sym not in self._cache:
                    self._cache[checked_sym] = {'longName': name}
                add_dlg.accept()
                self._refresh_table()
            else:
                # Nicht gefunden → Fehlermeldung + Vorschläge
                status_lbl.setStyleSheet('color:#e74c3c;font-size:11px;')
                status_lbl.setText(TR('scen_msg_sym_not_found'))
                _clear_suggestions()
                if suggestions:
                    _dm_s = _is_dark()
                    sugg_hdr = QLabel(TR('scen_lbl_suggestions'))
                    sugg_hdr.setStyleSheet(f'font-size:11px;color:{"#aaa" if _dm_s else "#555"};font-style:italic;')
                    sugg_lay.addWidget(sugg_hdr)
                    for s_sym, s_name in suggestions[:5]:
                        lbl = f"  {s_sym}  –  {s_name}" if s_name else f"  {s_sym}"
                        sb = QPushButton(lbl)
                        if _dm_s:
                            sb.setStyleSheet(
                                'QPushButton{text-align:left;padding:3px 8px;border:1px solid #555;'
                                'border-radius:4px;background:#2a2a2a;color:#e0e0e0;font-size:11px;}'
                                'QPushButton:hover{background:#1a4a6a;border-color:#2980b9;color:#fff;}')
                        else:
                            sb.setStyleSheet(
                                'QPushButton{text-align:left;padding:3px 8px;border:1px solid #bbb;'
                                'border-radius:4px;background:#f8f9fa;font-size:11px;}'
                                'QPushButton:hover{background:#d5e8f5;border-color:#2980b9;}')
                        sb.clicked.connect(
                            lambda _, ss=s_sym, sn=s_name: _use_suggestion(ss, sn))
                        sugg_lay.addWidget(sb)
                    sugg_widget.setVisible(True)
                    add_dlg.adjustSize()
            w = _worker_ref[0]
            if w:
                w.finished.connect(w.deleteLater)
                _worker_ref[0] = None

        def _do_check():
            sym = sym_edit.text().strip().upper()
            if not sym:
                status_lbl.setStyleSheet('color:#e74c3c;font-size:11px;')
                status_lbl.setText(TR('scen_msg_enter_symbol'))
                return
            ok_btn.setEnabled(False)
            ca_btn.setEnabled(False)
            _clear_suggestions()
            status_lbl.setStyleSheet('color:#2471A3;font-size:11px;')
            status_lbl.setText(TR('scen_msg_checking'))
            w = _SymSearchWorker(sym, add_dlg)
            _worker_ref[0] = w
            w.result.connect(_on_result, Qt.ConnectionType.QueuedConnection)
            w.start()

        ok_btn.clicked.connect(_do_check)
        sym_edit.returnPressed.connect(_do_check)
        add_dlg.exec()

    def _delete_position(self, sym: str) -> None:
        if sym in self._positions:
            del self._positions[sym]
            self._is_dirty = True
            self._refresh_table()

    def _clear_all(self) -> None:
        if not self._positions:
            return
        mb = QMessageBox(self)
        mb.setWindowTitle(TR('scen_btn_clear_all'))
        mb.setText(TR('scen_msg_confirm_clear'))
        yes = mb.addButton(TR('scen_btn_clear_all'), QMessageBox.ButtonRole.AcceptRole)
        mb.addButton(TR('btn_cancel'), QMessageBox.ButtonRole.RejectRole)
        _fix_win_focus(mb, self)
        mb.exec()
        if mb.clickedButton() != yes:
            return
        self._backup = dict(self._positions)
        self._positions.clear()
        self._is_dirty = True
        self._undo_btn.setVisible(True)
        self._refresh_table()

    def _undo_clear(self) -> None:
        if self._backup is not None:
            self._positions = dict(self._backup)
            self._backup = None
            self._undo_btn.setVisible(False)
            self._is_dirty = True
            self._refresh_table()

    def _new_portfolio(self) -> None:
        mb = QMessageBox(self)
        mb.setWindowTitle(TR('scen_btn_new'))
        mb.setText(TR('scen_msg_confirm_new'))
        yes = mb.addButton(TR('scen_btn_new'), QMessageBox.ButtonRole.AcceptRole)
        mb.addButton(TR('btn_cancel'), QMessageBox.ButtonRole.RejectRole)
        _fix_win_focus(mb, self)
        mb.exec()
        if mb.clickedButton() != yes:
            return
        self._backup    = dict(self._positions)
        self._positions = {}
        self._is_dirty  = True
        self._undo_btn.setVisible(True)
        self._name_edit.setText(TR('scen_new_portfolio_name'))
        self._refresh_table()

    def _toggle_lock(self) -> None:
        self._locked = not self._locked
        if not self._locked:
            QMessageBox.information(
                self, TR('scen_btn_unlock'), TR('scen_msg_unlock_info'))
        self._refresh_lock_btn()
        self._refresh_total_bar()

    # ── Speichern / Laden ─────────────────────────────────────────────────────

    def _save_scenario(self) -> None:
        name = self._name.strip() or TR('scen_default_name')
        if not self._positions:
            QMessageBox.warning(self, TR('scen_btn_save'),
                                TR('scen_msg_no_positions'))
            return
        ScenarioStore.save(name, self._positions, self._real_total)
        self._is_dirty = False
        self._undo_btn.setVisible(False)
        self._backup = None
        QMessageBox.information(
            self, TR('scen_btn_save'), TR('scen_msg_saved', name=name))

    def _load_scenario(self) -> None:
        names = ScenarioStore.list_names()
        if not names:
            QMessageBox.information(self, TR('scen_btn_load'),
                                    TR('scen_msg_no_scenarios'))
            return

        load_dlg = QDialog(self)
        load_dlg.setWindowTitle(TR('scen_btn_load'))
        load_dlg.setMinimumWidth(360)
        _fix_win_focus(load_dlg, self)

        lay = QVBoxLayout(load_dlg)
        lay.setSpacing(8); lay.setContentsMargins(16, 14, 16, 12)
        lay.addWidget(QLabel(f"<b>{TR('scen_load_select')}</b>"))

        lst = QListWidget()
        for n in names: lst.addItem(n)
        if names: lst.setCurrentRow(0)
        lst.setMinimumHeight(200)
        lay.addWidget(lst)

        btn_row = QHBoxLayout()
        ok_btn  = QPushButton(TR('scen_btn_load'))
        ok_btn.setStyleSheet('font-weight:bold;')
        del_btn = QPushButton(TR('btn_delete'))
        ca_btn  = QPushButton(TR('btn_cancel'))
        btn_row.addWidget(ok_btn); btn_row.addWidget(del_btn)
        btn_row.addStretch(); btn_row.addWidget(ca_btn)
        lay.addLayout(btn_row)
        ca_btn.clicked.connect(load_dlg.reject)

        def _do_load():
            item = lst.currentItem()
            if not item: return
            name = item.text()
            data = ScenarioStore.load(name)
            if not data:
                QMessageBox.warning(load_dlg, TR('scen_btn_load'),
                                    TR('scen_msg_load_error'))
                return
            self._positions = {k: float(v)
                               for k, v in data.get('positions', {}).items()}
            self._name = name
            self._name_edit.setText(name)
            self._is_dirty = False
            self._backup   = None
            self._undo_btn.setVisible(False)
            load_dlg.accept()
            self._refresh_table()
            QMessageBox.information(
                self, TR('scen_btn_load'), TR('scen_msg_loaded', name=name))

        def _do_delete():
            item = lst.currentItem()
            if not item: return
            name = item.text()
            mb = QMessageBox(load_dlg)
            mb.setText(TR('scen_msg_confirm_delete', name=name))
            yes = mb.addButton(TR('btn_delete'), QMessageBox.ButtonRole.AcceptRole)
            mb.addButton(TR('btn_cancel'), QMessageBox.ButtonRole.RejectRole)
            mb.exec()
            if mb.clickedButton() == yes:
                ScenarioStore.delete(name)
                lst.takeItem(lst.currentRow())
                if lst.count() == 0:
                    load_dlg.reject()

        ok_btn.clicked.connect(_do_load)
        del_btn.clicked.connect(_do_delete)
        lst.itemDoubleClicked.connect(lambda _: _do_load())
        load_dlg.exec()

    # ── Monte Carlo ───────────────────────────────────────────────────────────

    def _run_mc(self) -> None:
        if not self._positions:
            QMessageBox.warning(self, TR('scen_tab_mc'),
                                TR('scen_msg_no_positions'))
            return

        self._tabs.setCurrentIndex(1)

        years      = self._HORIZONS[self._horizon_combo.currentIndex()][1]
        n_sims     = self._SIMS[self._sims_combo.currentIndex()][1]
        inc_crypto = self._crypto_cb.isChecked()
        inc_commod = self._commod_cb.isChecked()
        compare    = self._compare_cb.isChecked() and bool(self._real_values)

        self._run_btn.setEnabled(False)
        self._result_table.setVisible(False)
        self._fig.clear(); self._canvas.draw()
        self._mc_stack.setCurrentIndex(1)
        self._anim_timer.start()

        try:
            self._mc_status.setText(TR('status_mc_running', n=n_sims, h=years))
        except RuntimeError:
            pass

        real_vals = self._real_values if compare else None
        w = ScenarioMCWorker(
            self._positions, years, n_sims,
            inc_crypto, inc_commod, real_vals, parent=self)
        self._worker_ref[0] = w
        w.finished.connect(lambda _t=w: (_t.wait(), _t.deleteLater()))
        w.done.connect(self._on_mc_done, Qt.ConnectionType.QueuedConnection)
        w.start()

    def _on_mc_done(self, result: dict) -> None:
        import matplotlib.ticker as mticker
        import matplotlib.dates as mdates

        self._anim_timer.stop()
        self._mc_stack.setCurrentIndex(0)
        self._run_btn.setEnabled(True)

        if 'error' in result:
            try: self._mc_status.setText(f"❌  {result['error']}")
            except RuntimeError: pass
            return

        scen = result.get('scenario', {})
        real = result.get('real')
        years  = scen['years']
        n_sims = scen['n_sims']
        fx     = self._fx
        sym    = self._cur_sym
        cur    = self._cur

        def _yfmt(v, _):
            if v >= 1_000_000:
                return f"{sym}{_fmt(v/1_000_000, 2)}M"
            return f"{sym}{_fmt(v, 0)}"

        df = _cfg.get_date_format() if hasattr(_cfg, 'get_date_format') else 'EU'
        def _xfmt(x, _):
            try:
                dt = mdates.num2date(x)
                if df == 'EU':  return dt.strftime('%m.%Y')
                if df == 'ISO': return dt.strftime('%Y-%m')
                return dt.strftime('%m/%Y')
            except Exception: return ''

        def _draw_mc(ax, res, title_str):
            d = res['dates']
            p10 = res['p10']*fx; p25=res['p25']*fx; p50=res['p50']*fx
            p75 = res['p75']*fx; p90=res['p90']*fx
            v0  = res['portfolio_value']*fx

            ax.fill_between(d, p10, p90, alpha=0.13, color='#2980b9',
                            label=f"{TR('mc_legend_p10')} / {TR('mc_legend_p90')}")
            ax.fill_between(d, p25, p75, alpha=0.22, color='#2980b9',
                            label=f"{TR('mc_legend_p25')} / {TR('mc_legend_p75')}")
            ax.plot(d, p10, color='#e74c3c', linewidth=0.9, linestyle='--',
                    label=TR('mc_legend_p10'))
            ax.plot(d, p25, color='#e67e22', linewidth=0.8, linestyle=':')
            ax.plot(d, p50, color='#2980b9', linewidth=2.0,
                    label=TR('mc_legend_median'), zorder=5)
            ax.plot(d, p75, color='#27ae60', linewidth=0.8, linestyle=':')
            ax.plot(d, p90, color='#1a8a3c', linewidth=0.9, linestyle='--',
                    label=TR('mc_legend_p90'))
            ax.axhline(v0, color='#888', linewidth=0.9, linestyle='-.',
                       label=f"{TR('mc_legend_today')} ({sym}{_fmt(v0, 0)})")
            ax.set_ylabel(f"{TR('mc_axis_label')} ({cur})", fontsize=9, color='#555')
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(_yfmt))
            ax.xaxis.set_major_formatter(mticker.FuncFormatter(_xfmt))
            ax.tick_params(labelsize=8)
            ax.grid(axis='y', color='#f0f0f0', linewidth=0.8)
            ax.grid(axis='x', color='#f5f5f5', linewidth=0.5)
            ax.set_axisbelow(True)
            for sp in ['top', 'right']:  ax.spines[sp].set_visible(False)
            ax.spines['left'].set_color('#dee2e6')
            ax.spines['bottom'].set_color('#dee2e6')
            ax.legend(loc='upper left', fontsize=8, framealpha=0.95,
                      edgecolor='#dee2e6', ncol=2)
            ax.set_title(title_str, fontsize=11, fontweight='bold',
                         pad=8, color='#2c3e50')
            return p10, p25, p50, p75, p90, v0

        self._fig.clear()
        self._fig.patch.set_facecolor('#ffffff')

        scen_title = (f"{TR('scen_mc_title_scenario', name=self._name)} – "
                      f"{TR('mc_title_chart', n=n_sims, h=years)}")

        if real is not None:
            ax1, ax2 = self._fig.subplots(2, 1, sharex=False)
            ax1.set_facecolor('#ffffff'); ax2.set_facecolor('#ffffff')
            _draw_mc(ax1, real, f"{TR('scen_mc_title_real')} – {TR('mc_title_chart', n=n_sims, h=years)}")
            _draw_mc(ax2, scen, scen_title)
            self._fig.tight_layout(pad=1.8, h_pad=2.5)
        else:
            ax = self._fig.add_subplot(111)
            ax.set_facecolor('#ffffff')
            _draw_mc(ax, scen, scen_title)
            self._fig.tight_layout(pad=1.5)

        self._canvas.draw()

        # Ergebnistabelle (Szenario)
        p10_, p25_, p50_, p75_, p90_, v0_ = (
            scen['p10'][-1]*fx, scen['p25'][-1]*fx, scen['p50'][-1]*fx,
            scen['p75'][-1]*fx, scen['p90'][-1]*fx, scen['portfolio_value']*fx)

        ROWS = [
            (TR('mc_row_today'),  v0_,  v0_),
            (TR('mc_row_p10'),    p10_, v0_),
            (TR('mc_row_p25'),    p25_, v0_),
            (TR('mc_row_median'), p50_, v0_),
            (TR('mc_row_p75'),    p75_, v0_),
            (TR('mc_row_p90'),    p90_, v0_),
        ]
        if real is not None:
            rv0 = real['portfolio_value']*fx
            ROWS += [
                (f"── {TR('scen_mc_title_real')} ──", rv0, rv0),
                (TR('mc_row_p10'),    real['p10'][-1]*fx,  rv0),
                (TR('mc_row_median'), real['p50'][-1]*fx,  rv0),
                (TR('mc_row_p90'),    real['p90'][-1]*fx,  rv0),
            ]

        RC = (['#f8f9fa','#fdecea','#fef5ec','#eaf6fb','#eafaf1','#d5f5e3']
              + ['#e8e8e8','#fdecea','#eaf6fb','#d5f5e3'])
        self._result_table.setRowCount(len(ROWS))
        for i, (lbl, val, base) in enumerate(ROWS):
            pct     = (val - base)/base*100 if base > 0 and i not in (0, 6) else 0
            pct_str = f"{_fmt(pct, 1)}%" if i not in (0, 6) else '—'
            pct_col = '#27ae60' if pct >= 0 else '#e74c3c'
            bg = QColor(RC[i] if i < len(RC) else '#f8f9fa')
            for ci, text in enumerate((lbl, f"{sym}{_fmt(val, 0)}", pct_str)):
                item = QTableWidgetItem(text)
                item.setBackground(bg)
                if ci == 2 and i not in (0, 6): item.setForeground(QColor(pct_col))
                if ci > 0: item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self._result_table.setItem(i, ci, item)
        self._result_table.resizeRowsToContents()
        self._result_table.setVisible(True)

        # Export-Daten
        export_rows = [(TR('mc_row_today'), f"{sym}{_fmt(v0_, 0)}", '—')]
        for lbl, val, base in ROWS[1:]:
            pct = (val-base)/base*100 if base > 0 and base != val else 0
            export_rows.append((lbl, f"{sym}{_fmt(val, 0)}", f"{_fmt(pct,1)}%"))
        self._mc_export_data[0] = {
            'title':   scen_title,
            'headers': [TR('mc_table_header'), TR('mc_table_value'), TR('mc_table_change')],
            'rows':    export_rows,
            'fig':     self._fig,
        }

        try:
            self._mc_status.setText(TR('status_mc_done',
                n=n_sims, h=years,
                med=f"{sym}{_fmt(p50_, 0)}",
                p10=f"{sym}{_fmt(p10_, 0)}",
                p90=f"{sym}{_fmt(p90_, 0)}"))
        except RuntimeError:
            pass
