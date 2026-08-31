"""
stock_rating.py – Aktien-Bewertungsdialog für Stock Monitor
============================================================
Enthält StarRatingWidget und StockRatingDialog.
Wird aus stock_monitor.py importiert, um die Hauptdatei schlank zu halten.
"""

import math
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt, QThread, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF

from translations import TR


class StarRatingWidget(QWidget):
    """Zeichnet 1–5 Sterne mit halben-Stern-Unterstützung via QPainter."""

    def __init__(self, score: float, max_stars: int = 5, star_size: int = 26, parent=None):
        super().__init__(parent)
        self.score = max(0.0, min(float(max_stars), round(score * 2) / 2))
        self.max_stars = max_stars
        self.star_size = star_size
        gap = 5
        self.setFixedSize(max_stars * (star_size + gap) - gap + 4, star_size + 4)

    def _star_points(self, cx, cy, outer_r, inner_r, n=5):
        pts = []
        for i in range(n * 2):
            r = outer_r if i % 2 == 0 else inner_r
            angle = math.pi * i / n - math.pi / 2
            pts.append(QPointF(cx + r * math.cos(angle), cy + r * math.sin(angle)))
        return QPolygonF(pts)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        full   = int(self.score)
        half   = 1 if (self.score - full) >= 0.5 else 0
        gap    = 5
        sz     = self.star_size
        gold   = QColor("#FFD700")
        gray   = QColor("#CCCCCC")
        border = QColor("#DAA520")

        for i in range(self.max_stars):
            x  = 2 + i * (sz + gap)
            cx = x + sz / 2
            cy = 2 + sz / 2
            r  = sz / 2 - 1
            poly = self._star_points(cx, cy, r, r * 0.4)
            if i < full:
                painter.setPen(QPen(border, 1))
                painter.setBrush(QBrush(gold))
                painter.drawPolygon(poly)
            elif i == full and half:
                painter.setPen(QPen(gray, 1))
                painter.setBrush(QBrush(Qt.GlobalColor.transparent))
                painter.drawPolygon(poly)
                painter.save()
                painter.setClipRect(QRectF(x, 0, sz / 2, sz + 4))
                painter.setPen(QPen(border, 1))
                painter.setBrush(QBrush(gold))
                painter.drawPolygon(poly)
                painter.restore()
            else:
                painter.setPen(QPen(gray, 1))
                painter.setBrush(QBrush(Qt.GlobalColor.transparent))
                painter.drawPolygon(poly)
        painter.end()


class StockRatingDialog(QDialog):
    """Bewertet eine Aktie in 6 Kategorien + Gesamtrating mit Sternen."""

    _WEIGHTS = {
        'technical':   0.22,
        'risk':        0.20,
        'performance': 0.18,
        'longterm':    0.18,
        'trading':     0.12,
        'analyst':     0.10,
    }
    _CAT_KEYS = {
        'performance': "rating_cat_performance",
        'risk':        "rating_cat_risk",
        'technical':   "rating_cat_technical",
        'trading':     "rating_cat_trading",
        'longterm':    "rating_cat_longterm",
        'analyst':     "rating_cat_analyst",
    }

    def __init__(self, chart_widget, parent=None):
        super().__init__(parent)
        self.cw      = chart_widget
        self.symbol  = chart_widget.symbol
        self._scores = {}
        self._basis  = {}
        self.setWindowTitle(TR("title_stock_rating", symbol=self.symbol))
        self.setMinimumWidth(480)
        self._build_ui()
        self._fetch_data()

    @staticmethod
    def _apply_emoji_font(btn):
        from PyQt6.QtGui import QFontDatabase, QFont as _QFont
        current_size = btn.font().pointSize()
        ef = next((
            _QFont(f, current_size if current_size > 0 else 10)
            for f in ['Segoe UI Emoji', 'Noto Color Emoji', 'Apple Color Emoji']
            if f in QFontDatabase.families()
        ), None)
        if ef:
            btn.setFont(ef)

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setSpacing(10)

        hdr = QLabel(f"<b style='font-size:15px'>{self.symbol}</b> – {TR('rating_cat_overall')}")
        hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._main_layout.addWidget(hdr)

        self._loading_lbl = QLabel(TR("rating_loading"))
        self._loading_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self._loading_lbl.font()
        font.setItalic(True)
        self._loading_lbl.setFont(font)
        self._main_layout.addWidget(self._loading_lbl)

        self._result_frame = QFrame()
        self._result_frame.setVisible(False)
        self._result_layout = QVBoxLayout(self._result_frame)
        self._result_layout.setSpacing(6)
        self._main_layout.addWidget(self._result_frame)

        btn_row = QHBoxLayout()
        info_btn = QPushButton(TR("btn_rating_info"))
        info_btn.clicked.connect(self._show_info)
        info_btn.setMaximumWidth(140)
        self._apply_emoji_font(info_btn)
        close_btn = QPushButton(TR("btn_close"))
        close_btn.clicked.connect(self.accept)
        close_btn.setMaximumWidth(100)
        disc = QLabel(f"<small><i>{TR('rating_disclaimer')}</i></small>")
        disc.setWordWrap(True)
        btn_row.addWidget(info_btn)
        btn_row.addStretch()
        btn_row.addWidget(disc)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        self._main_layout.addLayout(btn_row)

    def _show_results(self):
        self._loading_lbl.setVisible(False)
        self._result_frame.setVisible(True)
        rl = self._result_layout

        def _sep():
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setStyleSheet("color:#ddd")
            return line

        overall  = self._calc_overall()
        ov_row   = QHBoxLayout()
        ov_lbl   = QLabel(f"<b style='font-size:14px'>{TR('rating_cat_overall')}</b>")
        ov_lbl.setMinimumWidth(170)
        ov_stars = StarRatingWidget(overall, star_size=32)
        ov_row.addWidget(ov_lbl)
        ov_row.addWidget(ov_stars)
        ov_row.addStretch()
        rl.addLayout(ov_row)

        rl.addWidget(_sep())

        order = ['performance', 'risk', 'technical', 'trading', 'longterm', 'analyst']
        for cat in order:
            if cat not in self._scores:
                continue
            score  = self._scores[cat]
            label  = TR(self._CAT_KEYS[cat])
            row    = QHBoxLayout()
            name_l = QLabel(f"<b>{label}</b>")
            name_l.setMinimumWidth(170)
            stars  = StarRatingWidget(score)
            row.addWidget(name_l)
            row.addWidget(stars)
            row.addStretch()
            rl.addLayout(row)

        self.adjustSize()

    # ── Score-Berechnung ──────────────────────────────────────────────────────
    def _score_1y_perf(self, pct):
        return (5.0 if pct >= 60 else 4.5 if pct >= 40 else 4.0 if pct >= 25 else
                3.5 if pct >= 15 else 3.0 if pct >= 5  else 2.5 if pct >= 0  else
                2.0 if pct >= -10 else 1.5 if pct >= -20 else 1.0 if pct >= -35 else 0.5)

    def _score_5y_perf(self, pct):
        return (5.0 if pct >= 150 else 4.5 if pct >= 100 else 4.0 if pct >= 60 else
                3.5 if pct >= 30  else 3.0 if pct >= 10  else 2.5 if pct >= 0  else
                2.0 if pct >= -15 else 1.5 if pct >= -30 else 1.0 if pct >= -50 else 0.5)

    def _score_beta(self, beta):
        return (5.0 if beta < 0.3 else 4.5 if beta < 0.6 else 4.0 if beta < 0.8 else
                3.5 if beta < 1.0 else 3.0 if beta < 1.3 else 2.5 if beta < 1.6 else
                2.0 if beta < 2.0 else 1.5 if beta < 2.5 else 1.0)

    def _score_sortino(self, s):
        return (5.0 if s >= 3.0 else 4.5 if s >= 2.0 else 4.0 if s >= 1.5 else
                3.5 if s >= 1.0 else 3.0 if s >= 0.5 else 2.5 if s >= 0.0 else
                2.0 if s >= -0.5 else 1.5 if s >= -1.0 else 1.0)

    def _score_volatility(self, vol_pct):
        return (5.0 if vol_pct < 10 else 4.5 if vol_pct < 15 else 4.0 if vol_pct < 20 else
                3.5 if vol_pct < 30 else 3.0 if vol_pct < 40 else 2.5 if vol_pct < 55 else
                2.0 if vol_pct < 70 else 1.0)

    def _score_ma_position(self, price, ma20, ma50, ma200):
        def _valid(v):
            return v is not None and not np.isnan(v)
        pts = 0.0
        max_pts = 0.0
        if _valid(ma20):
            pts += 1.0 if price > ma20 else 0.0
            max_pts += 1.0
        if _valid(ma50):
            pts += 1.5 if price > ma50 else 0.0
            max_pts += 1.5
        if _valid(ma200):
            pts += 2.0 if price > ma200 else 0.0
            max_pts += 2.0
        if _valid(ma50) and _valid(ma200):
            pts += 0.5 if ma50 > ma200 else 0.0
            max_pts += 0.5
        if max_pts == 0:
            return None
        return 1.0 + (pts / max_pts) * 4.0

    def _score_rsi_technical(self, rsi):
        return (5.0 if 50 <= rsi <= 65 else
                4.0 if (45 <= rsi < 50) or (65 < rsi <= 70) else
                3.5 if (40 <= rsi < 45) or (70 < rsi <= 75) else
                3.0 if (35 <= rsi < 40) or (75 < rsi <= 80) else
                2.5 if (25 <= rsi < 35) or (80 < rsi <= 85) else
                2.0 if (15 <= rsi < 25) or (85 < rsi <= 90) else 1.0)

    def _score_rsi_trading(self, rsi):
        return (5.0 if 30 <= rsi <= 45 else
                4.5 if 45 < rsi <= 55 else
                4.0 if (25 <= rsi < 30) or (55 < rsi <= 65) else
                3.5 if 20 <= rsi < 25 else
                3.0 if 65 < rsi <= 72 else
                2.0 if 72 < rsi <= 80 else 1.5)

    def _score_ma_trend_trading(self, ma20, ma50, ma200, price):
        def _valid(v):
            return v is not None and not np.isnan(v)
        if not _valid(ma20) or not _valid(ma50):
            return None
        if ma20 > ma50:
            return 5.0 if (_valid(ma200) and ma50 > ma200) else 4.0
        if abs(ma20 - ma50) / ma50 < 0.01:
            return 3.5
        return 3.0 if (_valid(ma200) and price > ma200) else 2.0

    def _score_alpha(self, alpha):
        return (5.0 if alpha >= 0.25 else 4.5 if alpha >= 0.15 else 4.0 if alpha >= 0.08 else
                3.5 if alpha >= 0.03 else 3.0 if alpha >= 0.0  else 2.5 if alpha >= -0.05 else
                2.0 if alpha >= -0.10 else 1.5 if alpha >= -0.20 else 1.0)

    def _score_beta_longterm(self, beta):
        return (5.0 if beta < 0.5 else 4.5 if beta < 0.7 else 4.0 if beta < 0.9 else
                3.5 if beta < 1.1 else 3.0 if beta < 1.4 else 2.5 if beta < 1.8 else
                2.0 if beta < 2.5 else 1.0)

    def _score_analyst_upside(self, upside_pct):
        return (5.0 if upside_pct >= 40 else 4.5 if upside_pct >= 25 else
                4.0 if upside_pct >= 15 else 3.5 if upside_pct >= 5  else
                3.0 if upside_pct >= 0  else 2.5 if upside_pct >= -10 else
                2.0 if upside_pct >= -20 else 1.0)

    def _score_ma200_position(self, price, ma200):
        if ma200 is None or np.isnan(ma200):
            return None
        diff = (price - ma200) / ma200 * 100
        return (5.0 if diff >= 5 else 4.0 if diff >= 0 else
                3.0 if diff >= -5 else 2.0 if diff >= -15 else 1.0)

    def _score_analyst_consensus(self, recommendation, num_analysts, upside_pct):
        rec_map = {
            'strong_buy': 5.0, 'strongbuy': 5.0,
            'buy': 4.0,
            'hold': 3.0,
            'sell': 2.0,
            'strong_sell': 1.0, 'strongsell': 1.0,
        }
        base = rec_map.get(str(recommendation).lower().replace('_', ''), None)
        if base is None or not num_analysts:
            return None
        bonus = (0.5  if upside_pct is not None and upside_pct >= 30  else
                 0.25 if upside_pct is not None and upside_pct >= 15  else
                -0.25 if upside_pct is not None and upside_pct < 0   else
                -0.5  if upside_pct is not None and upside_pct < -15 else 0.0)
        return max(1.0, min(5.0, base + bonus))

    def _calc_overall(self):
        weights = self._WEIGHTS
        total_w = sum(weights[k] for k in self._scores if k in weights)
        if total_w == 0:
            return 0.0
        return sum(self._scores[k] * weights[k] / total_w
                   for k in self._scores if k in weights)

    # ── Datenabruf ────────────────────────────────────────────────────────────
    def _fetch_data(self):
        sym = self.symbol

        class _RatingWorker(QThread):
            from PyQt6.QtCore import pyqtSignal
            done = pyqtSignal(object, object)

            def run(self_t):
                try:
                    import yfinance as yf
                    t   = yf.Ticker(sym)
                    d1y = t.history(period='1y', interval='1d')
                    d5y = t.history(period='5y', interval='1d')
                    self_t.done.emit(
                        d1y if not d1y.empty else None,
                        d5y if not d5y.empty else None,
                    )
                except Exception:
                    self_t.done.emit(None, None)

        self._worker = _RatingWorker()
        self._worker.done.connect(self._on_data)
        self._worker.start()

    def _on_data(self, data_1y, data_5y):
        try:
            self._compute_scores(data_1y, data_5y)
        except Exception as e:
            print(f"[Rating] Fehler bei Score-Berechnung: {e}")
        self._show_results()

    def _compute_scores(self, data_1y, data_5y):
        cw   = self.cw
        beta = getattr(cw, '_last_beta_value', None)
        tp   = getattr(cw, '_last_target_price', None)

        def _prices(data):
            if data is None or data.empty:
                return None
            return data['Close'].resample('1D').last().dropna()

        def _perf(prices):
            if prices is None or len(prices) < 2:
                return None
            return (float(prices.iloc[-1]) - float(prices.iloc[0])) / float(prices.iloc[0]) * 100

        def _vol(prices):
            if prices is None or len(prices) < 10:
                return None
            return float(prices.pct_change().dropna().std()) * (252 ** 0.5) * 100

        def _last_ma(prices, period):
            if prices is None or len(prices) < period:
                return None
            return float(prices.rolling(period).mean().dropna().iloc[-1])

        def _last_rsi(prices):
            if prices is None or len(prices) < 15:
                return None
            arr    = prices.values.astype(float)
            deltas = np.diff(arr)
            gains  = np.where(deltas > 0, deltas, 0.0)
            losses = np.where(deltas < 0, -deltas, 0.0)
            ag = float(np.mean(gains[:14]))
            al = float(np.mean(losses[:14]))
            for i in range(14, len(deltas)):
                ag = (ag * 13 + gains[i]) / 14
                al = (al * 13 + losses[i]) / 14
            return 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)

        def _sortino(prices):
            if prices is None or len(prices) < 20:
                return None
            r    = prices.pct_change().dropna()
            exc  = r - 0.05 / 252
            down = exc[exc < 0]
            if len(down) < 3 or down.std() == 0:
                return None
            return float((exc.mean() / down.std()) * (252 ** 0.5))

        prices_1y = _prices(data_1y)
        prices_5y = _prices(data_5y)
        price     = float(prices_1y.iloc[-1]) if prices_1y is not None else None

        # ── Performance ──────────────────────────────────────────────────
        p1, p5 = _perf(prices_1y), _perf(prices_5y)
        sub_p  = []
        if p1 is not None:
            sub_p.append((self._score_1y_perf(p1), 0.7, f"1J: {p1:+.1f}%"))
        if p5 is not None:
            sub_p.append((self._score_5y_perf(p5), 0.3, f"5J: {p5:+.1f}%"))
        if sub_p:
            tw = sum(w for _, w, _ in sub_p)
            self._scores['performance'] = sum(s * w / tw for s, w, _ in sub_p)
            self._basis['performance']  = " · ".join(t for _, _, t in sub_p)

        # ── Risiko ───────────────────────────────────────────────────────
        vol  = _vol(prices_1y)
        sort = _sortino(prices_1y)
        risk_subs, risk_basis = {}, []
        if beta is not None:
            risk_subs['beta']    = self._score_beta(abs(beta))
            risk_basis.append(f"Beta {beta:.2f}")
        if sort is not None:
            risk_subs['sortino'] = self._score_sortino(sort)
            risk_basis.append(f"Sortino {sort:.2f}")
        if vol is not None:
            risk_subs['vol']     = self._score_volatility(vol)
            risk_basis.append(f"Vol {vol:.0f}%")
        if risk_subs:
            self._scores['risk'] = sum(risk_subs.values()) / len(risk_subs)
            self._basis['risk']  = " · ".join(risk_basis)

        # ── Technisch ────────────────────────────────────────────────────
        ma20 = ma50 = ma200 = rsi = None
        if prices_1y is not None and price is not None:
            ma20  = _last_ma(prices_1y, 20)
            ma50  = _last_ma(prices_1y, 50)
            ma200 = _last_ma(prices_1y, 200)
            rsi   = _last_rsi(prices_1y)
            ma_s  = self._score_ma_position(price, ma20, ma50, ma200)
            rsi_s = self._score_rsi_technical(rsi) if rsi is not None else None
            tech_subs, tech_basis = [], []
            if ma_s is not None:
                tech_subs.append((ma_s, 0.6))
                above = sum([
                    bool(ma20  is not None and price > ma20),
                    bool(ma50  is not None and price > ma50),
                    bool(ma200 is not None and price > ma200),
                ])
                tech_basis.append(f"MA {above}/3 ober")
            if rsi_s is not None:
                tech_subs.append((rsi_s, 0.4))
                tech_basis.append(f"RSI {rsi:.0f}")
            if tech_subs:
                tw = sum(w for _, w in tech_subs)
                self._scores['technical'] = sum(s * w / tw for s, w in tech_subs)
                self._basis['technical']  = " · ".join(tech_basis)

        # ── Zum Traden ───────────────────────────────────────────────────
        if prices_1y is not None and price is not None:
            rsi_t = rsi if rsi is not None else _last_rsi(prices_1y)
            trade_subs, trade_basis = [], []
            if rsi_t is not None:
                trade_subs.append((self._score_rsi_trading(rsi_t), 0.55))
                trade_basis.append(f"RSI {rsi_t:.0f}")
            mat = self._score_ma_trend_trading(ma20, ma50, ma200, price)
            if mat is not None:
                trade_subs.append((mat, 0.45))
                arrow = "↑" if (ma20 is not None and ma50 is not None and ma20 > ma50) else "↓"
                trade_basis.append(f"MA20/50 {arrow}")
            if trade_subs:
                tw = sum(w for _, w in trade_subs)
                self._scores['trading'] = sum(s * w / tw for s, w in trade_subs)
                self._basis['trading']  = " · ".join(trade_basis)

        # ── Langfrist-Eignung ─────────────────────────────────────────────
        alpha_v = cw.calculate_alpha(data_1y) if data_1y is not None else None
        lt_subs, lt_basis = {}, []
        if alpha_v is not None:
            lt_subs['alpha']   = self._score_alpha(alpha_v)
            lt_basis.append(f"Alpha {alpha_v:+.2f}")
        if beta is not None:
            lt_subs['beta']    = self._score_beta_longterm(abs(beta))
            lt_basis.append(f"Beta {beta:.2f}")
        if sort is not None:
            lt_subs['sortino'] = self._score_sortino(sort)
            lt_basis.append(f"Sortino {sort:.2f}")
        if p5 is not None:
            lt_subs['perf5y']  = self._score_5y_perf(p5)
            lt_basis.append(f"5J {p5:+.1f}%")
        if tp and price:
            upside = (tp - price) / price * 100
            lt_subs['upside']  = self._score_analyst_upside(upside)
            lt_basis.append(f"Upside {upside:+.1f}%")
        if prices_1y is not None and price is not None:
            ma200_lt = ma200 if ma200 is not None else _last_ma(prices_1y, 200)
            if ma200_lt is not None:
                lt_subs['ma200'] = self._score_ma200_position(price, ma200_lt)
                lt_basis.append(f"MA200 {'↑' if price > ma200_lt else '↓'}")
        if lt_subs:
            self._scores['longterm'] = sum(lt_subs.values()) / len(lt_subs)
            self._basis['longterm']  = " · ".join(lt_basis)

        # ── Analystenempfehlung ───────────────────────────────────────────
        try:
            import yfinance as yf
            info       = yf.Ticker(self.symbol).info
            n_analysts = info.get('numberOfAnalystOpinions', 0) or 0
            rec        = info.get('recommendationKey', 'none')
            cur_price  = info.get('currentPrice') or info.get('regularMarketPrice')
            target     = info.get('targetMeanPrice') or tp
            upside_a   = ((target - cur_price) / cur_price * 100
                          if target and cur_price else None)
            a_s = self._score_analyst_consensus(rec, n_analysts, upside_a)
            if a_s is not None:
                self._scores['analyst'] = a_s
                rec_label = {
                    'strong_buy': TR('rating_strong_buy'),
                    'buy':        TR('rating_buy'),
                    'hold':       TR('rating_hold'),
                    'sell':       TR('rating_sell'),
                    'strong_sell': TR('rating_strong_sell'),
                }.get(str(rec).lower(), rec)
                self._basis['analyst'] = (
                    f"{rec_label} · {n_analysts} Analysten"
                    + (f" · Upside {upside_a:+.1f}%" if upside_a is not None else "")
                )
        except Exception:
            pass

    # ── Info-Dialog ───────────────────────────────────────────────────────────
    def _show_info(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(TR("title_rating_info"))
        dlg.setMinimumWidth(500)
        layout = QVBoxLayout(dlg)
        text = QLabel(TR("rating_info_text"))
        text.setWordWrap(True)
        text.setTextFormat(Qt.TextFormat.PlainText)
        # Kein Emoji-Font hier: der macht bei Fließtext mit Zahlen (z.B. "70 %")
        # die Zeichenabstände kaputt. Das ⭐-Symbol wird trotzdem über Qt's
        # automatischen Font-Fallback korrekt dargestellt.
        font = text.font()
        font.setPointSize(10)
        text.setFont(font)
        scroll = QScrollArea()
        scroll.setWidget(text)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(420)
        layout.addWidget(scroll)
        close = QPushButton(TR("btn_close"))
        close.clicked.connect(dlg.accept)
        close.setMaximumWidth(100)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close)
        layout.addLayout(btn_row)
        dlg.exec()
