"""
screener.py – Aktien-Screener für Stock Monitor
Filtert Aktien nach 1-Jahres-Performance und optionalem Max-KGV (P/E).
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import sys
from typing import Optional

import yfinance as yf
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFont, QFontDatabase
from PyQt6.QtWidgets import (
    QAbstractItemView, QButtonGroup, QComboBox, QDialog,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox,
    QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QProgressBar, QWidget,
)

try:
    from translations import TR
except ImportError:
    def TR(key, **kwargs):
        return kwargs and key.format(**kwargs) or key


# ── Prefs-Datei (gleiche Pfadlogik wie stock_monitor.py) ─────────────────────
def _prefs_path() -> str:
    if sys.platform == 'win32':
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(os.path.abspath(sys.executable))
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, '_internal', '.stock_monitor_screener_prefs.json')
    if os.path.exists('/.flatpak-info'):
        base = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~'))
    else:
        base = os.path.expanduser('~')
    return os.path.join(base, '.stock_monitor_screener_prefs.json')

_PREFS_FILE = _prefs_path()

# ── Modul-Level Cache (überlebt Dialog-Schliessen innerhalb einer App-Session) ─
_cache: dict = {
    'index_idx': 0,
    'perf_idx':  0,
    'kgv_text':  '',
    'logic':     None,
    'results':   [],
    'searched':  False,
    'chart': {
        'timeframe': None,
        'ma20': False, 'ma50': False, 'ma200': False,
        'trend': False, 'beta': False, 'alpha': False,
        'sharpe': False, 'sortino': False,
        'rsi': False, 'w52': False, 'bb': False, 'dd': False, 'target': False,
    },
}

_CHART_ATTRS = [
    ('ma20_checkbox',    'ma20'),
    ('ma50_checkbox',    'ma50'),
    ('ma200_checkbox',   'ma200'),
    ('trend_checkbox',   'trend'),
    ('beta_checkbox',    'beta'),
    ('alpha_checkbox',   'alpha'),
    ('sharpe_checkbox',  'sharpe'),
    ('sortino_checkbox', 'sortino'),
    ('rsi_checkbox',     'rsi'),
    ('w52_checkbox',     'w52'),
    ('bb_checkbox',      'bb'),
    ('dd_checkbox',      'dd'),
    ('target_checkbox',  'target'),
]

def _load_chart_prefs_from_disk() -> None:
    try:
        with open(_PREFS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        p = _cache['chart']
        for k in p:
            if k in data:
                p[k] = data[k]
    except Exception:
        pass

def _save_chart_prefs_to_disk() -> None:
    try:
        with open(_PREFS_FILE, 'w', encoding='utf-8') as f:
            json.dump(_cache['chart'], f)
    except Exception:
        pass

_load_chart_prefs_from_disk()

def apply_chart_prefs(widget) -> None:
    p = _cache['chart']
    for attr, key in _CHART_ATTRS:
        cb = getattr(widget, attr, None)
        if cb is not None:
            cb.blockSignals(True)
            cb.setChecked(p[key])
            cb.blockSignals(False)
    if p['timeframe']:
        widget.timeframe_combo.setCurrentText(p['timeframe'])

def save_chart_prefs(widget) -> None:
    p = _cache['chart']
    p['timeframe'] = widget.timeframe_combo.currentText()
    for attr, key in _CHART_ATTRS:
        cb = getattr(widget, attr, None)
        if cb is not None:
            p[key] = cb.isChecked()
    _save_chart_prefs_to_disk()

# ─────────────────────────────────────────────────────────────────────────────
# Index-Symbollisten
# ─────────────────────────────────────────────────────────────────────────────

_SP500 = [
    'MMM','AOS','ABT','ABBV','ACN','ADBE','AMD','AES','AFL','A',
    'APD','ABNB','AKAM','ALB','ARE','ALGN','ALLE','LNT','ALL','GOOGL',
    'GOOG','MO','AMZN','AMCR','AEE','AEP','AXP','AIG','AMT','AWK',
    'AMP','AME','AMGN','APH','ADI','ANSS','AON','APA','AAPL','AMAT',
    'APTV','ACGL','ADM','ANET','AJG','AIZ','T','ATO','ADSK','ADP',
    'AZO','AVB','AVY','AXON','BKR','BALL','BAC','BAX','BDX','WRB',
    'BBY','BIIB','BLK','BX','BK','BA','BKNG','BWA','BSX','BMY',
    'AVGO','BR','BRO','BLDR','BG','CDNS','CZR','CPT','CPB','COF',
    'CAH','KMX','CCL','CARR','CAT','CBOE','CBRE','CDW','CE','COR',
    'CNC','CDAY','CF','CRL','SCHW','CHTR','CVX','CMG','CB','CHD',
    'CI','CINF','CTAS','CSCO','C','CFG','CLX','CME','CMS','KO',
    'CTSH','CL','CMCSA','CAG','COP','ED','STZ','CEG','COO','CPRT',
    'GLW','CPAY','COST','CTRA','CRWD','CCI','CSX','CMI','CVS','DHR',
    'DRI','DVA','DE','DELL','DAL','DVN','DXCM','FANG','DLR','DFS',
    'DG','DLTR','D','DPZ','DOV','DTE','DUK','DD','EMN','ETN',
    'EBAY','ECL','EIX','EW','EA','ELV','EMR','ENPH','ETR','EOG',
    'EPAM','EQT','EFX','EQIX','EQR','ESS','EL','ETSY','EG','EXAS',
    'EXPE','EXPD','EXR','XOM','FFIV','FDS','FICO','FAST','FRT','FDX',
    'FIS','FITB','FSLR','FE','FI','F','FTNT','FTV','FOXA','FOX',
    'BEN','FCX','GRMN','IT','GE','GEHC','GEV','GEN','GNRC','GD',
    'GIS','GM','GPC','GILD','GS','HAL','HIG','HAS','HCA','DOC',
    'HSIC','HSY','HES','HPE','HLT','HOLX','HD','HON','HRL','HST',
    'HWM','HPQ','HUBB','HUM','HBAN','HII','IBM','IEX','IDXX','ITW',
    'INCY','IR','ICE','IP','IPG','ISRG','IVZ','INVH','IQV','IRM',
    'JBHT','JBL','JKHY','J','JNJ','JCI','JPM','JNPR','K','KVUE',
    'KDP','KEY','KEYS','KMB','KIM','KMI','KLAC','KHC','KR','LHX',
    'LH','LRCX','LW','LVS','LDOS','LEN','LLY','LIN','LYV','LKQ',
    'LMT','L','LOW','LULU','LYB','MTB','MRO','MPC','MKTX','MAR',
    'MMC','MLM','MAS','MA','MTCH','MKC','MCD','MCK','MDT','MRK',
    'META','MET','MTD','MGM','MCHP','MU','MSFT','MAA','MRNA','MHK',
    'MOH','TAP','MDLZ','MPWR','MNST','MCO','MS','MOS','MSI','MSCI',
    'NDAQ','NTAP','NFLX','NEM','NWSA','NWS','NEE','NKE','NI','NDSN',
    'NSC','NTRS','NOC','NCLH','NRG','NUE','NVDA','NVR','NXPI','ORLY',
    'OXY','ODFL','OMC','ON','OKE','ORCL','OTIS','PCAR','PKG','PLTR',
    'PANW','PH','PAYX','PAYC','PYPL','PNR','PEP','PFE','PCG','PM',
    'PSX','PNW','PNC','POOL','PPG','PPL','PFG','PG','PGR','PLD',
    'PRU','PEG','PTC','PSA','PHM','PWR','QCOM','DGX','RL','RJF',
    'RTX','O','REG','REGN','RF','RSG','RMD','RVTY','ROK','ROL',
    'ROP','ROST','RCL','SPGI','CRM','SBAC','SLB','STX','SRE','NOW',
    'SHW','SPG','SWKS','SJM','SW','SNA','SOLV','SO','LUV','SWK',
    'SBUX','STT','STLD','STE','SYK','SYF','SNPS','SYY','TMUS','TROW',
    'TTWO','TPR','TRGP','TGT','TEL','TDY','TFX','TER','TSLA','TXN',
    'TXT','TMO','TJX','TSCO','TT','TDG','TRV','TRMB','TFC','TYL',
    'TSN','USB','UBER','UDR','UHS','UNP','UAL','UPS','URI','UNH',
    'VLO','VTR','VLTO','VRSN','VRSK','VZ','VRTX','V','VST','VNO',
    'VTRS','VICI','VMC','WAB','WBA','WMT','DIS','WBD','WM','WAT',
    'WEC','WFC','WELL','WST','WDC','WY','WHR','WMB','WTW','GWW',
    'WYNN','XEL','XYL','YUM','ZBRA','ZBH','ZTS','APO','SMCI','DAY',
    'CTLT','TECH','CNX','CMA','VNT','VIAV',
]

_NASDAQ100 = [
    'MSFT','AAPL','NVDA','AMZN','META','TSLA','GOOGL','GOOG','AVGO','COST',
    'NFLX','AMD','CSCO','ADBE','QCOM','INTU','PEP','TMUS','TXN','AMAT',
    'HON','ISRG','AMGN','BKNG','VRTX','REGN','SBUX','ADI','MU','KLAC',
    'MDLZ','LRCX','PANW','GILD','SNPS','CDNS','CTAS','ASML','MRVL','INTC',
    'MELI','PYPL','ORLY','MNST','FTNT','NXPI','CHTR','WDAY','ABNB','DXCM',
    'ADSK','MCHP','PAYX','AEP','FAST','VRSK','CSX','EXC','ODFL','KDP',
    'IDXX','CPRT','ROP','ROST','EA','BIIB','CEG','KHC','GEHC','ON',
    'FANG','CTSH','DLTR','BKR','ANSS','NDAQ','DDOG','ZS','TTWO','XEL',
    'ILMN','MRNA','WBD','ALGN','ARM','DASH','TEAM','TTD','SMCI','CSGP',
    'SIRI','CCEP','CDW','PCAR','CRWD','SBAC','GFS','LULU','RIVN','PLTR',
]

_NASDAQ_EXTRA = [
    # Cloud / SaaS
    'NET','SNOW','MDB','OKTA','DOCN','BILL','GTLB','PD','ZI','APPN',
    'SMAR','PCOR','FROG','S','BASE','VERX',
    # AI / Quantum
    'IONQ','QUBT','RGTI','QBTS','SOUN','AI','PATH','QLYS','BBAI',
    # EV / Clean Energy
    'LCID','NIO','LI','XPEV','BLNK','CHPT','EVGO','BE','PLUG','ARRY','NOVA','RUN',
    # Space / Defense Tech
    'RKLB','ASTS','LUNR','ACHR','JOBY','IRDM','KTOS','AVAV','AXON',
    # Crypto / Fintech
    'COIN','MSTR','MARA','RIOT','HOOD','SOFI','AFRM','UPST','LMND',
    # Biotech
    'NVAX','BNTX','BEAM','EDIT','CRSP','NTLA','SRPT','HALO',
    # Gaming / Social / Consumer
    'RBLX','SPOT','RDDT','SNAP','PINS','DUOL','DKNG','CVNA',
    # Semiconductors (mid-cap)
    'WOLF','SITM','AEIS','ONTO','AZTA','CRUS','AMBA','POWI','RMBS',
]

_DAX = [
    'ADS.DE','AIR.DE','ALV.DE','BAS.DE','BAYN.DE','BMW.DE','BNR.DE','CON.DE',
    'DTG.DE','DTE.DE','DHER.DE','DB1.DE','DBK.DE','DHL.DE','DPW.DE','ENR.DE',
    'EOAN.DE','FME.DE','FRE.DE','HFG.DE','HEI.DE','HEN3.DE','IFX.DE','LEG.DE',
    'MBG.DE','MRK.DE','MTX.DE','MUV2.DE','P911.DE','PAH3.DE','PUMA.DE',
    'QIA.DE','RHM.DE','RWE.DE','SAP.DE','SIE.DE','SHL.DE','SY1.DE','VOW3.DE','ZAL.DE',
]

_SMI = [
    'ABBN.SW','ALC.SW','CFR.SW','GEBN.SW','GIVN.SW','HOLN.SW','KNIN.SW',
    'LONN.SW','NESN.SW','NOVN.SW','PGHN.SW','ROG.SW','RIEN.SW','SGSN.SW',
    'SLHN.SW','SREN.SW','SOON.SW','UHR.SW','UBSG.SW','ZURN.SW',
]

_CAC40 = [
    'AC.PA','AI.PA','AIR.PA','ALO.PA','AXA.PA','BNP.PA','EN.PA',
    'CAP.PA','CA.PA','ACA.PA','DSY.PA','ENGI.PA','EL.PA','RMS.PA',
    'KER.PA','LR.PA','OR.PA','MC.PA','ML.PA','ORA.PA','RI.PA','PUB.PA',
    'RNO.PA','SAF.PA','SGO.PA','SAN.PA','SU.PA','GLE.PA','STM.PA',
    'HO.PA','TTE.PA','URW.PA','VIE.PA','DG.PA','VIV.PA','WLN.PA',
    'MT.AS','BN.PA','SW.PA','STLA.PA',
]

_FTSE100 = [
    'AAL.L','ABF.L','ADM.L','AHT.L','ANTO.L','AZN.L','AUTO.L','AV.L',
    'BA.L','BARC.L','BATS.L','BDEV.L','BKG.L','BP.L','BRBY.L','BT-A.L',
    'BWY.L','CCH.L','CNA.L','CPG.L','CRDA.L','DARK.L','DCC.L','DGE.L',
    'DPLM.L','EMG.L','EXPN.L','EZJ.L','FERG.L','FLTR.L','FRES.L',
    'GLEN.L','GSK.L','HIK.L','HLN.L','HLMA.L','HSBA.L','HWDN.L',
    'IAG.L','IHG.L','III.L','IMB.L','IMI.L',
    'JD.L','KGF.L','LAND.L','LGEN.L','LLOY.L','LSEG.L',
    'MKS.L','MNDI.L','MNG.L','MRO.L','NG.L','NWG.L','NXT.L','OCDO.L',
    'PHNX.L','PRU.L','PSH.L','PSN.L','PSON.L','REL.L','RIO.L','RKT.L',
    'RMV.L','RR.L','RS1.L','SBRY.L','SDR.L','SGE.L','SGRO.L',
    'SHEL.L','SMIN.L','SMT.L','SN.L','SSE.L','STAN.L','STJ.L',
    'SVT.L','TSCO.L','TW.L','ULVR.L','UU.L','VTY.L','VOD.L',
    'WEIR.L','WPP.L','WTB.L',
]

_NIKKEI225 = [
    '6758.T','9984.T','7203.T','6861.T','4063.T','8306.T','9432.T',
    '6367.T','7267.T','8035.T','4502.T','9433.T','6594.T','4568.T',
    '8316.T','7741.T','4519.T','8411.T','4523.T','6702.T',
    '7751.T','8766.T','7733.T','6645.T','8058.T','9022.T','8031.T',
    '7011.T','6501.T','6503.T','9020.T','4901.T','7201.T','2914.T',
    '8001.T','9101.T','6857.T','5401.T','8002.T','7269.T','4661.T',
    '6902.T','8053.T','3382.T','9202.T','6954.T','7752.T','4507.T',
    '4503.T','8630.T','1925.T','2802.T','9613.T','6724.T','5711.T',
    '4188.T','8601.T','3407.T','7270.T','5201.T','4452.T','6471.T',
    '2503.T','9735.T','8309.T','5108.T','4042.T','6701.T','7912.T',
    '8591.T','9502.T','5333.T','7832.T','4151.T','8750.T','6473.T',
    '9766.T','7731.T','2501.T','4004.T','5714.T','8725.T','9983.T',
    '4578.T','6981.T','6526.T','6098.T','6326.T','6841.T',
]

_TSX = [
    'ENB.TO','RY.TO','TD.TO','BNS.TO','BMO.TO','CM.TO','MFC.TO','SLF.TO',
    'SU.TO','CNQ.TO','TRP.TO','PPL.TO','IMO.TO','CVE.TO','AEM.TO','WPM.TO',
    'K.TO','ABX.TO','FNV.TO','OVV.TO','ERF.TO','CPG.TO',
    'CNR.TO','CP.TO','WCN.TO','ATD.TO','L.TO','MRU.TO','GIL.TO',
    'QSR.TO','DOL.TO','TIH.TO','WFG.TO','IFC.TO','IAG.TO',
    'SHOP.TO','CSU.TO','OTEX.TO','BAM.TO','PWF.TO','GWO.TO','FFH.TO','POW.TO',
    'TRI.TO','RCI-B.TO','BCE.TO','T.TO','SJ.TO','MG.TO','AC.TO',
    'CAR-UN.TO','REI-UN.TO','AP-UN.TO','NTR.TO','AGI.TO','KL.TO',
    'PEY.TO','TVE.TO','BTE.TO','MEG.TO','ARX.TO','BEI-UN.TO','HR-UN.TO',
]

_ASX200 = [
    'BHP.AX','CBA.AX','CSL.AX','ANZ.AX','WBC.AX','NAB.AX','WES.AX','MQG.AX',
    'TLS.AX','RIO.AX','WOW.AX','FMG.AX','STO.AX','WDS.AX','AMC.AX',
    'TCL.AX','COL.AX','REA.AX','ALL.AX','GMG.AX','APA.AX','ASX.AX','SHL.AX',
    'QBE.AX','IAG.AX','MPL.AX','AZJ.AX','ORA.AX','SCG.AX','DXS.AX',
    'GPT.AX','SGP.AX','MGR.AX','AGL.AX','ORG.AX','S32.AX','ILU.AX','LYC.AX',
    'MIN.AX','PLS.AX','NHC.AX','WHC.AX','SEK.AX','CAR.AX','IEL.AX',
    'ALU.AX','TNE.AX','PME.AX','XRO.AX','WTC.AX','CPU.AX','EBO.AX',
    'RHC.AX','EVN.AX','SFR.AX','BSL.AX','JHX.AX','LLC.AX','SUL.AX',
    'VEA.AX','ALD.AX','TWE.AX','SGM.AX','IPL.AX','CHC.AX','VCX.AX',
    'BWP.AX','CWY.AX','CLW.AX','HLS.AX','NEC.AX','NXT.AX',
    'HVN.AX','JBH.AX','MTS.AX','ARB.AX','BLD.AX','NST.AX','EVN.AX',
]

_STI = [
    'D05.SI','U11.SI','O39.SI','Z74.SI','C6L.SI','S68.SI',
    'C09.SI','BN4.SI','S63.SI','U96.SI','BS6.SI','V03.SI',
    'S59.SI','J36.SI','C07.SI','H78.SI','G13.SI','F34.SI',
    'A17U.SI','C38U.SI','M44U.SI','ME8U.SI','N2IU.SI',
    'T82U.SI','K71U.SI','BUOU.SI','9CI.SI','Y92.SI',
    'E5H.SI','RW0U.SI',
]

_NIFTY50 = [
    'RELIANCE.NS','TCS.NS','HDFCBANK.NS','INFY.NS','ICICIBANK.NS',
    'HINDUNILVR.NS','ITC.NS','SBIN.NS','BHARTIARTL.NS','KOTAKBANK.NS',
    'LT.NS','AXISBANK.NS','ASIANPAINT.NS','BAJFINANCE.NS','MARUTI.NS',
    'WIPRO.NS','HCLTECH.NS','SUNPHARMA.NS','TITAN.NS','ULTRACEMCO.NS',
    'POWERGRID.NS','NTPC.NS','ADANIPORTS.NS','BAJAJFINSV.NS','TECHM.NS',
    'NESTLEIND.NS','ONGC.NS','COALINDIA.NS','DRREDDY.NS','CIPLA.NS',
    'BRITANNIA.NS','DIVISLAB.NS','EICHERMOT.NS','GRASIM.NS','HEROMOTOCO.NS',
    'HINDALCO.NS','INDUSINDBK.NS','JSWSTEEL.NS','M&M.NS','TATAMOTORS.NS',
    'TATASTEEL.NS','TATACONSUM.NS','APOLLOHOSP.NS','BPCL.NS','SBILIFE.NS',
    'HDFCLIFE.NS','BAJAJ-AUTO.NS','BEL.NS','TRENT.NS','ETERNAL.NS',
]

_HANGSENG = [
    '0700.HK','9988.HK','0939.HK','1299.HK','3690.HK',
    '1398.HK','2318.HK','0941.HK','0005.HK','0388.HK',
    '1810.HK','0011.HK','0016.HK','0002.HK','0003.HK',
    '0006.HK','0012.HK','0017.HK','0027.HK','0066.HK',
    '0175.HK','0267.HK','0288.HK','0291.HK','0386.HK',
    '0669.HK','0688.HK','0762.HK','0823.HK','0857.HK',
    '0883.HK','0960.HK','1038.HK','1044.HK','1093.HK',
    '1109.HK','1113.HK','1177.HK','1211.HK','1288.HK',
    '1876.HK','1928.HK','2020.HK','2269.HK','2313.HK',
    '2382.HK','2388.HK','2628.HK','3328.HK','3988.HK',
    '6618.HK','6690.HK','6862.HK','9618.HK','9633.HK',
    '9888.HK','9999.HK','1347.HK','0101.HK','1024.HK',
]

_EWZ = [
    'VALE3.SA','PETR4.SA','ITUB4.SA','PETR3.SA','BBDC4.SA',
    'ABEV3.SA','B3SA3.SA','BBAS3.SA','WEGE3.SA','RENT3.SA',
    'SUZB3.SA','RDOR3.SA','LREN3.SA','JBSS3.SA','UGPA3.SA',
    'ELET3.SA','ELET6.SA','CMIG4.SA','BBSE3.SA','PRIO3.SA',
    'SBSP3.SA','VIVT3.SA','CCRO3.SA','GGBR4.SA','BPAC11.SA',
    'EQTL3.SA','TOTS3.SA','RAIL3.SA','BRFS3.SA','CSAN3.SA',
    'CSNA3.SA','MULT3.SA','ALUP11.SA','ENBR3.SA','HYPE3.SA',
    'RADL3.SA','FLRY3.SA','ENEV3.SA','CPLE6.SA','IGTI11.SA',
    'BEEF3.SA','MRVE3.SA','CMIN3.SA','HAPV3.SA','EMBR3.SA',
    'MGLU3.SA','TAEE11.SA','NTCO3.SA','PETZ3.SA','YDUQ3.SA',
]

_SCANDINAVIA = [
    # Schweden – OMXS30
    'ABB.ST','ALFA.ST','ASSA-B.ST','ATCO-A.ST','ATCO-B.ST','AZN.ST',
    'BOL.ST','ERIC-B.ST','EVO.ST','ESSITY-B.ST','GETI-B.ST','HEXA-B.ST',
    'HM-B.ST','INVE-B.ST','NDA-SE.ST','NIBE-B.ST','SAND.ST','SCA-B.ST',
    'SEB-A.ST','SECU-B.ST','SKA-B.ST','SKF-B.ST','SHB-A.ST','SWED-A.ST',
    'TEL2-B.ST','TELIA.ST','VOLV-B.ST','SINCH.ST',
    # Dänemark – OMXC25
    'NOVO-B.CO','MAERSK-B.CO','DSV.CO','ORSTED.CO','CARL-B.CO',
    'COLO-B.CO','DEMANT.CO','GMAB.CO','VWS.CO','PNDORA.CO',
    'TRYG.CO','AMBU-B.CO','GN.CO','ROCK-B.CO','NSIS-B.CO',
    'BAVA.CO','FLS.CO','DFDS.CO','ISS.CO','RBREW.CO',
    # Norwegen – OBX
    'EQNR.OL','DNB.OL','MOWI.OL','TEL.OL','NHY.OL','AKRBP.OL',
    'ORK.OL','YAR.OL','SALM.OL','AKER.OL','SUBC.OL','NEL.OL',
    'GOGL.OL','STB.OL','SCATC.OL','BAKKA.OL','TOMRA.OL',
    'SRBANK.OL','ATEA.OL','AFG.OL',
    # Finnland – OMXH25
    'NOKIA.HE','FORTUM.HE','NESTE.HE','SAMPO.HE','UPM.HE',
    'METSO.HE','ELISA.HE','TIETO.HE','OUTOKUMPU.HE','HUHTAMAKI.HE',
    'KONECRANES.HE','KEMIRA.HE','KOJAMO.HE','KNEBV.HE','NDA-FI.HE',
    'WRTBV.HE','ORNBV.HE','KESKOB.HE',
]

_OSTEUROPA = [
    # Polen – WIG20
    'PKN.WA','PKO.WA','PEO.WA','PZU.WA','KGH.WA','LPP.WA',
    'CDR.WA','DNP.WA','MBK.WA','OPL.WA','PGE.WA','SANPL.WA',
    'TPE.WA','ALR.WA','CCC.WA','JSW.WA','MIL.WA','XTB.WA',
    'ALE.WA','KETY.WA',
    # Österreich – ATX
    'EBS.VI','OMV.VI','VOE.VI','VIG.VI','RBI.VI','AMS.VI',
    'WIE.VI','FLUG.VI','POST.VI','EVN.VI','BAWAG.VI','SBO.VI',
    'UQA.VI','S1.VI','ANDR.VI','TKA.VI','DO.VI','ATS.VI',
]

_RUSSELL2000 = [
    # Technology
    'AAOI','ACMR','ADEA','AGYS','ALKT','ALRM','AMSC','ANGI','APPF','ARLO',
    'AVNW','BAND','BLKB','CALX','COHU','EGHT','ENFN','ENVX','EVTC','EXLS',
    'FIVN','FSLY','JAMF','LPSN','MARA','MITK','NCNO','NEOG','NTGR','PERI',
    'PLAB','PRFT','RPAY','RSKD','SYNC','TACT','TTGT','UPLD','VIAV','VIRT',
    'XPER','SCSC','BIGC','DUOS','EVCM','FOUR','GRIN','HCAT','IIIV','INFU',
    'IOTS','KIDS','LPSN','MLNK','MNTV','NABL','NCNO','NTCT','PDFS','PRTS',
    # Healthcare / Biotech
    'ACRS','ADMA','ADUS','AFMD','AGEN','AGIO','ALEC','AMPH','ARWR','AXNX',
    'BCRX','BFLY','CALT','CNMD','CORT','CPSI','DVAX','FATE','FOLD','HIMS',
    'HALO','IMNM','IRMD','KYMR','LGND','LUMO','MDXG','NKTR','NTLA','NVAX',
    'PDCO','PRAX','RCKT','SAVA','SWAV','TMDX','TXMD','VKTX','VRCA',
    'AKRO','ARDX','BTAI','CRSP','DAWN','DVAX','EDIT','GLYC','HOOK','HRMY',
    'IMVT','ITCI','KDNY','LMNX','MNKD','MRUS','NRIX','ONCR','PTGX','SAGE',
    # Financials / Banking
    'AROW','AMNB','BHLB','BFIN','CASH','CNOB','ESSA','FRME','HTBK','KRNY',
    'LKFN','MBWM','NBTB','OCFC','OFG','PFBC','PRK','RNST','SASR','TBK',
    'TRMK','WASH','BCAL','BSVN','BWFG','CFFN','FFBH','FLIC','HONE','SMBC',
    # Consumer / Retail
    'BOOT','HIBB','BJRI','PLAY','CAKE','WING','JACK','ELY','RCII','SNBR',
    'LESL','ASO','SWIM','CATO','BIG','LOVE','XPOF','EVRI','MODV','CBRL',
    'RUTH','GOLF','PRTY','CVGW','DORM','HELE','HGV','JJSF','LANC','MATW',
    'NACCO','PETS','PLCE','POWL','PRGS','RCII','RGP','SCVL','TPVG',
    # Energy
    'AMPY','ARCH','BTU','CIVI','GPOR','MTDR','MNRL','NOG','SBOW',
    'CEIX','BATL','FLNG','HPK','IMPP','MXC','REX','SGU','SJT','VAALCO',
    # Industrials
    'AAON','ALGT','AVAV','DNOW','ECVT','GMS','HURN','KTOS','LMAT',
    'MYRG','PRIM','SALT','SHYF','SKYW','SPXC','TGI','TITN','TPIC','TREX',
    'WLDN','ARCB','ATRI','BWXT','CVEO','DY','EXPO','GEO','HAYN','HXL',
    # Real Estate
    'AIRC','ALEX','BRT','BNL','EPR','FCPT','GMRE','GTY','IIPR','ILPT',
    'INN','KRG','NXRT','PSTL','SAFE','SBRA','STAG','SVC','UHT','UNIT',
]

_RUSSELL2000_LARGE = list(dict.fromkeys(_RUSSELL2000 + [
    # Technology (additional)
    'ACLS','AEIS','AMKR','AOSL','AZTA','CRUS','DAVA','DIOD','EGAN','EMKR',
    'FORM','GDYN','HOLI','IDCC','ITRN','LSCC','LUNA','MGNI','MKSI','MTSI',
    'POWI','RMBS','SLAB','SMTC','SSYS','STAA','TTEC','TTMI','UCTT','VERI',
    'VICR','VSEC','YEXT','EVBG','EPAY','CLFD','FCFS','EZPW','PCYG','TELA',
    'LYTS','DMRC','AXTI','AVID','INVA','FORR','GSIT','SWIR','ATNI','NXGN',
    'NEON','NNOX','WRAP','CMPR','JCOM','AMSWA','AVPT','CEVA','CLPS','CNXN',
    'DGII','IOSP','RYAM','SILC','SIGA','MTRN','CBPX','LAAC','TPCS','BLTH',
    # Healthcare / Biotech (additional)
    'ACAD','ACST','ADPT','AKBA','AKTX','ALDX','ALIM','ALPN','AMRX','ANAB',
    'APLS','ARAV','ARCUS','ARMP','ARQT','ARVN','ASND','ASPN','ATNX','ATRC',
    'AVNS','AVXL','AXGN','AXSM','AZYO','BDTX','BHVN','BOLT','BPMC','CARA',
    'CBAY','CDMO','CDTX','CGTX','CHRS','CLDX','CMRX','CNCE','COGT','CPRX',
    'CRNX','CUTR','ETNB','FBIO','FLGT','FULC','GERN','GRTS','HGEN','HRTX',
    'INMD','INSM','IONS','ISEE','JNCE','KPTI','KRYS','KTRA','KYTX','LGMD',
    'MGNX','MRKR','NUVB','OCGN','OMER','AVEO','AXDX','KROS','NRXP',
    'PRPH','RLAY','VNDA','XNCR','YMAB','ZGNX','ZYXI',
    # Financials / Banking (additional)
    'ACNB','AMSF','ATLC','ATLO','BFST','BKSC','BMRC','BMTC','BOCH','BPOP',
    'BRKL','BUSE','BWB','CBNK','CBTX','CCBG','CFFI','CHMG','CIZN','CLBK',
    'COBZ','COOP','COWN','DCOM','EGBN','ENVA','EVBN','FBNC','FFIN','FISI',
    'FNLC','FRST','GNTY','GSBC','HAFC','HBCP','HFWA','HOPE','HTLF','IBCP',
    'IBTX','INBK','INDB','ISBA','LAKE','LBAI','LCNB','MCBC','MFIN','MSBI',
    'NFBK','OPBK','PBFS','PFIS','PNFP','PPBI','PRAA','PVBC','RRBI',
    'SFBS','TBNK','TCBK','TFSL','TOWN','UVSP','WAFD','WSBC','FFIC','NWIN',
    'CATC','CCNE','CIVB','CZWI','HMST',
    # Consumer / Retail (additional)
    'ARKO','BBSI','BGFV','BNED','CALM','CAMP','CHUY','CONN','CPRI',
    'CRVL','CSTE','CURV','DENN','EXPR','FRPT','GIII','GPRE',
    'HAIN','HCKT','HWKN','JBSS','JOUT','KFRC','KIRK','KLIC','LACO',
    'LCII','LGIH','LOCO','LQDT','LSTR','NATH','NDLS','NHTC','PLOW','PLXS',
    'PRPL','RCKY','RICK','RMCF','RMNI','RRGB','SMPL','SONO',
    'BSET','CHEF','CRSR','DXPE','EPAC','FRPH',
    # Energy (additional)
    'AESI','CSWC','DMLP','ESTE','FWST','HNRG','INSW','KNTK','LBRT',
    'MMLP','OMP','PARR','PBF','PTEN','PVAC','REGI',
    'RNGR','SDRL','SWN','TALO','TELL','TGA','TRMD','VET','VNOM','WTTR',
    # Industrials (additional)
    'AHCO','ALCO','AMWD','APOG','ASGN','ASIX','ASTE','BCPC','BWMX','CECO',
    'CSGS','CVCO','DFIN','FELE','FNKO','FOSL','GATX','GENC','GLDD','HEES',
    'HTLD','IIIN','IRBT','JELD','JOE','KELYA','KMPR','KNSL','LAWS','LNDC',
    'LPRO','MATX','MRTN','MRCY','NVEE','OSIS','PATK','PAYA','PLPC','STRL',
    'GLOG','HLNE','MHLD','NEWT','NUS','NTIC','OTTR','SPKE','MGEE','CLNE',
    # Real Estate (additional)
    'AOMR','BXMT','EPRT','GOOD','INDP','JBGS','KREF','LAND','MACK',
    'NREF','NTST','NYMT','OLP','OPFI','ORCC','PLYM','ROIC','SILA','TRNO','APLE',
]))

# ── Index-Definitionen: (Anzeigename, Symbolliste, Warnung_anzeigen) ──────────
INDICES: list[tuple[str, list[str], bool]] = [
    ("S&P 500",            _SP500,             False),
    ("Nasdaq 100",         _NASDAQ100,         False),
    ("Nasdaq Extra",       _NASDAQ_EXTRA,      False),
    ("DAX",                _DAX,               False),
    ("SMI",                _SMI,               False),
    ("CAC 40",             _CAC40,             False),
    ("FTSE 100",           _FTSE100,           False),
    ("Nikkei 225",         _NIKKEI225,         False),
    ("TSX",                _TSX,               False),
    ("ASX 200",            _ASX200,            False),
    ("STI (Singapur)",     _STI,               False),
    ("Nifty 50 (Indien)",  _NIFTY50,           False),
    ("Hang Seng (China)",  _HANGSENG,          False),
    ("EWZ (Brasilien)",    _EWZ,               False),
    ("Skandinavien",       _SCANDINAVIA,       False),
    ("Osteuropa",          _OSTEUROPA,         False),
    ("Russell 2000 (Ausw.)",  _RUSSELL2000,         False),
    ("Russell 2000 (erw.)",   _RUSSELL2000_LARGE,   False),
]

# ── Performance-Stufen: (min%, max%) ─────────────────────────────────────────
PERF_STEPS: list[tuple[Optional[float], Optional[float]]] = [
    (None, None),  # Kein Filter
    (0,    10),
    (10,   20),
    (20,   30),
    (30,   40),
    (40,   50),
    (50,   75),
    (75,   100),
    (100,  None),
]

_PERF_WORKERS = 6
_PE_WORKERS   = 4
_NAME_WORKERS = 4


# ─────────────────────────────────────────────────────────────────────────────
# Worker-Thread
# ─────────────────────────────────────────────────────────────────────────────

class ScreenerWorker(QThread):
    progress = pyqtSignal(int, int, str)   # done, total, phase ('perf'|'kgv')
    finished = pyqtSignal(list)            # list of result dicts

    def __init__(
        self,
        symbols:  list[str],
        perf_min: Optional[float],
        perf_max: Optional[float],
        max_kgv:  Optional[float],
        use_and:  bool,
        use_or:   bool,
    ) -> None:
        super().__init__()
        self._symbols  = symbols
        self._perf_min = perf_min
        self._perf_max = perf_max
        self._max_kgv  = max_kgv
        self._use_and  = use_and
        self._use_or   = use_or
        self._abort    = False

    def abort(self) -> None:
        self._abort = True

    def _perf_ok(self, p: float) -> bool:
        if self._perf_min is not None and p < self._perf_min:
            return False
        if self._perf_max is not None and p >= self._perf_max:
            return False
        return True

    def _fetch_one(self, sym: str) -> dict | None:
        try:
            hist = yf.Ticker(sym).history(period='1y', auto_adjust=True)
            if hist is None or len(hist) < 10:
                return None
            closes = hist['Close'].dropna()
            if len(closes) < 10:
                return None
            p_now = float(closes.iloc[-1])
            p_1y  = float(closes.iloc[0])
            if p_1y <= 0:
                return None
            perf = (p_now - p_1y) / p_1y * 100
            return {'symbol': sym, 'price': p_now, 'perf_pct': perf}
        except Exception:
            return None

    def _fetch_pe(self, sym: str) -> float | None:
        try:
            info = yf.Ticker(sym).info
            pe = info.get('trailingPE') or info.get('forwardPE')
            if pe is None:
                return None
            pe = float(pe)
            return pe if 0 < pe < 10000 else None
        except Exception:
            return None

    def _fetch_name(self, sym: str) -> str:
        try:
            info = yf.Ticker(sym).info
            return info.get('longName') or info.get('shortName') or sym
        except Exception:
            return sym

    def run(self) -> None:
        total      = len(self._symbols)
        perf_data: dict[str, dict] = {}

        # ── Phase 1: Performance abrufen ─────────────────────────────────────
        for i in range(0, total, _PERF_WORKERS):
            if self._abort:
                break
            batch = self._symbols[i:i + _PERF_WORKERS]
            with concurrent.futures.ThreadPoolExecutor(max_workers=_PERF_WORKERS) as ex:
                for result in ex.map(self._fetch_one, batch):
                    if result:
                        perf_data[result['symbol']] = result
            done = min(i + _PERF_WORKERS, total)
            self.progress.emit(done, total, 'perf')

        # ── Phase 2: KGV-Filter (optional) ───────────────────────────────────
        if self._max_kgv is not None and (self._use_and or self._use_or):
            if self._use_and:
                pe_symbols = [s for s, d in perf_data.items()
                              if self._perf_ok(d['perf_pct'])]
            else:
                pe_symbols = list(perf_data.keys())

            pe_map: dict[str, float | None] = {}
            pe_total = len(pe_symbols)

            for i in range(0, pe_total, _PE_WORKERS):
                if self._abort:
                    break
                batch = pe_symbols[i:i + _PE_WORKERS]
                with concurrent.futures.ThreadPoolExecutor(max_workers=_PE_WORKERS) as ex:
                    for sym, pe in zip(batch, ex.map(self._fetch_pe, batch)):
                        pe_map[sym] = pe
                done = min(i + _PE_WORKERS, pe_total)
                self.progress.emit(done, pe_total, 'kgv')

            def passes(sym: str, d: dict) -> bool:
                pm = self._perf_ok(d['perf_pct'])
                pe = pe_map.get(sym)
                km = pe is not None and pe <= self._max_kgv
                return (pm and km) if self._use_and else (pm or km)

            candidates = {s: d for s, d in perf_data.items() if passes(s, d)}
        else:
            candidates = {s: d for s, d in perf_data.items()
                          if self._perf_ok(d['perf_pct'])}

        # ── Top 25, nach Performance sortiert ────────────────────────────────
        top = sorted(candidates.values(),
                     key=lambda d: d['perf_pct'], reverse=True)[:25]

        # ── Namen für Top-Ergebnisse abrufen ─────────────────────────────────
        if top:
            with concurrent.futures.ThreadPoolExecutor(max_workers=_NAME_WORKERS) as ex:
                names = list(ex.map(self._fetch_name, [d['symbol'] for d in top]))
            for d, name in zip(top, names):
                d['name'] = name

        self.finished.emit(top)


# ─────────────────────────────────────────────────────────────────────────────
# Dialog
# ─────────────────────────────────────────────────────────────────────────────

def _perf_label(perf_min: Optional[float], perf_max: Optional[float]) -> str:
    if perf_min is None and perf_max is None:
        return TR('scr_perf_any')
    if perf_max is None:
        return f"≥ {int(perf_min)}%"
    return f"{int(perf_min)}–{int(perf_max) - 1}%"


def _emoji_font(size: int = 10) -> QFont | None:
    """Gibt die beste verfügbare Emoji-Font zurück, oder None."""
    for name in ['Segoe UI Emoji', 'Noto Color Emoji', 'Apple Color Emoji']:
        if name in QFontDatabase.families():
            return QFont(name, size)
    return None


class StockScreenerDialog(QDialog):

    def __init__(self, parent: QWidget, app_ref, on_chart_fn=None) -> None:
        super().__init__(parent)
        self._app_ref     = app_ref
        self._on_chart_fn = on_chart_fn   # callable(sym) öffnet Zoom-Chart
        self._worker: Optional[ScreenerWorker] = None
        self._running = False

        self.setWindowTitle(TR('scr_title'))
        self.resize(980, 660)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint
        )

        self._build_ui()
        self._restore_cache()

    # ── UI aufbauen ───────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setSpacing(6)
        outer.setContentsMargins(12, 10, 12, 8)

        # ── Titelzeile ───────────────────────────────────────────────────────
        title_row = QHBoxLayout()
        title_lbl = QLabel(f"<b style='font-size:14px'>{TR('scr_title')}</b>")
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        info_btn = QPushButton("ℹ️")
        info_btn.setFixedSize(28, 28)
        _ef_ib = _emoji_font(12)
        if _ef_ib:
            info_btn.setFont(_ef_ib)
        info_btn.setToolTip(TR('scr_info_title'))
        info_btn.clicked.connect(self._show_info)
        title_row.addWidget(info_btn)
        outer.addLayout(title_row)

        # ── Filterzeile 1: Index + Performance + Suchen ──────────────────────
        f1 = QHBoxLayout(); f1.setSpacing(8)

        f1.addWidget(QLabel(f"<b>{TR('scr_lbl_index')}:</b>"))
        self._idx_combo = QComboBox()
        for name, _, _ in INDICES:
            self._idx_combo.addItem(name)
        self._idx_combo.setMinimumWidth(140)
        self._idx_combo.setMinimumHeight(28)
        f1.addWidget(self._idx_combo)

        f1.addSpacing(12)
        f1.addWidget(QLabel(f"<b>{TR('scr_lbl_perf')}:</b>"))
        self._perf_combo = QComboBox()
        for pmin, pmax in PERF_STEPS:
            self._perf_combo.addItem(_perf_label(pmin, pmax))
        self._perf_combo.setMinimumWidth(110)
        self._perf_combo.setMinimumHeight(28)
        f1.addWidget(self._perf_combo)

        f1.addStretch()

        _ef = _emoji_font(10)

        self._search_btn = QPushButton(TR('scr_btn_search'))
        if _ef: self._search_btn.setFont(_ef)
        self._search_btn.setMinimumHeight(32)
        self._search_btn.setMinimumWidth(110)
        self._search_btn.setStyleSheet(
            "QPushButton { background:#2ecc71; color:white; font-weight:bold; "
            "border-radius:5px; padding:4px 16px; }"
            "QPushButton:hover { background:#27ae60; }"
            "QPushButton:disabled { background:#aaa; }"
        )
        self._search_btn.clicked.connect(self._on_search)
        f1.addWidget(self._search_btn)

        self._abort_btn = QPushButton(TR('scr_btn_abort'))
        if _ef: self._abort_btn.setFont(_ef)
        self._abort_btn.setMinimumHeight(32)
        self._abort_btn.setMinimumWidth(110)
        self._abort_btn.setEnabled(False)
        self._abort_btn.setStyleSheet(
            "QPushButton { background:#e74c3c; color:white; font-weight:bold; "
            "border-radius:5px; padding:4px 12px; }"
            "QPushButton:hover { background:#c0392b; }"
            "QPushButton:disabled { background:#ccc; color:#888; }"
        )
        self._abort_btn.clicked.connect(self._on_abort)
        f1.addWidget(self._abort_btn)

        outer.addLayout(f1)

        # ── Filterzeile 2: KGV + AND/OR ──────────────────────────────────────
        f2 = QHBoxLayout(); f2.setSpacing(8)

        f2.addWidget(QLabel(f"<b>{TR('scr_lbl_kgv')}:</b>"))
        self._kgv_edit = QLineEdit()
        self._kgv_edit.setPlaceholderText(TR('scr_kgv_hint'))
        self._kgv_edit.setFixedWidth(90)
        self._kgv_edit.setMinimumHeight(28)
        f2.addWidget(self._kgv_edit)

        f2.addSpacing(12)
        f2.addWidget(QLabel(f"<b>{TR('scr_lbl_logic')}:</b>"))

        self._and_btn = QPushButton("AND")
        self._and_btn.setCheckable(True)
        self._and_btn.setFixedWidth(50)
        self._and_btn.setMinimumHeight(26)

        self._or_btn = QPushButton("OR")
        self._or_btn.setCheckable(True)
        self._or_btn.setFixedWidth(50)
        self._or_btn.setMinimumHeight(26)

        _chip_style = (
            "QPushButton { border:1px solid #aaa; border-radius:4px; "
            "background:#f0f0f0; color:#333; font-weight:bold; }"
            "QPushButton:checked { background:#3f51b5; color:white; border-color:#3f51b5; }"
            "QPushButton:hover:!checked { background:#e0e0e0; }"
        )
        self._and_btn.setStyleSheet(_chip_style)
        self._or_btn.setStyleSheet(_chip_style)
        self._and_btn.clicked.connect(lambda: self._on_logic_click('and'))
        self._or_btn.clicked.connect(lambda: self._on_logic_click('or'))
        f2.addWidget(self._and_btn)
        f2.addWidget(self._or_btn)

        self._logic_hint = QLabel("")
        self._logic_hint.setStyleSheet("color:#666; font-size:11px;")
        f2.addWidget(self._logic_hint)
        f2.addStretch()

        outer.addLayout(f2)

        # ── Fortschrittsbalken ────────────────────────────────────────────────
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setMaximumHeight(16)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setVisible(False)

        self._progress_lbl = QLabel("")
        self._progress_lbl.setStyleSheet("color:#555; font-size:11px;")
        self._progress_lbl.setVisible(False)

        prog_row = QHBoxLayout()
        prog_row.addWidget(self._progress_bar, stretch=1)
        prog_row.addWidget(self._progress_lbl)
        outer.addLayout(prog_row)

        # ── Status-Label ──────────────────────────────────────────────────────
        self._status_lbl = QLabel(TR('scr_lbl_hint'))
        self._status_lbl.setStyleSheet("color:#666; font-size:11px;")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(self._status_lbl)

        # ── Ergebnis-Tabelle ──────────────────────────────────────────────────
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels([
            TR('scr_col_symbol'),
            TR('scr_col_name'),
            TR('scr_col_perf'),
            TR('scr_col_price'),
            TR('scr_col_actions'),
        ])
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(0, 85)
        self._table.setColumnWidth(2, 95)
        self._table.setColumnWidth(3, 105)
        self._table.setColumnWidth(4, 130)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.setVisible(False)
        outer.addWidget(self._table, stretch=1)

        # ── Disclaimer ────────────────────────────────────────────────────────
        disc = QLabel(TR('scr_disclaimer'))
        disc.setStyleSheet("color:#999; font-size:10px;")
        disc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(disc)

        self._update_logic_hint()

    # ── Hilfsfunktionen ──────────────────────────────────────────────────────

    def _current_logic(self) -> Optional[str]:
        if self._and_btn.isChecked():
            return 'and'
        if self._or_btn.isChecked():
            return 'or'
        return None

    def _on_logic_click(self, which: str) -> None:
        if which == 'and':
            if self._or_btn.isChecked():
                self._or_btn.setChecked(False)
        else:
            if self._and_btn.isChecked():
                self._and_btn.setChecked(False)
        self._update_logic_hint()

    def _update_logic_hint(self) -> None:
        kgv = self._kgv_edit.text().strip() if hasattr(self, '_kgv_edit') else ''
        logic = self._current_logic() if hasattr(self, '_and_btn') else None
        if not kgv:
            hint = ""
        elif logic is None:
            hint = ""
        elif logic == 'and':
            hint = "Performance UND KGV müssen erfüllt sein"
        else:
            hint = "Performance ODER KGV muss erfüllt sein"
        if hasattr(self, '_logic_hint'):
            self._logic_hint.setText(hint)

    def _restore_cache(self) -> None:
        self._idx_combo.setCurrentIndex(_cache['index_idx'])
        self._perf_combo.setCurrentIndex(_cache['perf_idx'])
        self._kgv_edit.setText(_cache['kgv_text'])
        logic = _cache['logic']
        if logic == 'and':
            self._and_btn.setChecked(True)
        elif logic == 'or':
            self._or_btn.setChecked(True)
        self._update_logic_hint()
        if _cache['searched'] and _cache['results']:
            self._populate_table(_cache['results'])
            n = len(_cache['results'])
            self._status_lbl.setText(TR('scr_lbl_results', n=n))

    def _save_cache(self) -> None:
        _cache['index_idx'] = self._idx_combo.currentIndex()
        _cache['perf_idx']  = self._perf_combo.currentIndex()
        _cache['kgv_text']  = self._kgv_edit.text().strip()
        _cache['logic']     = self._current_logic()

    # ── Suchen ───────────────────────────────────────────────────────────────

    def _on_search(self) -> None:
        idx_i  = self._idx_combo.currentIndex()
        name, symbols, has_warning = INDICES[idx_i]

        if has_warning:
            mb = QMessageBox(self)
            mb.setWindowTitle(TR('scr_russell_title'))
            mb.setText(TR('scr_russell_warn', n=len(symbols)))
            mb.setIcon(QMessageBox.Icon.Warning)
            ok_btn  = mb.addButton(TR('scr_russell_confirm'), QMessageBox.ButtonRole.AcceptRole)
            mb.addButton("Abbrechen", QMessageBox.ButtonRole.RejectRole)
            mb.exec()
            if mb.clickedButton() != ok_btn:
                return

        perf_i = self._perf_combo.currentIndex()
        perf_min, perf_max = PERF_STEPS[perf_i]
        kgv_text = self._kgv_edit.text().strip()
        max_kgv  = float(kgv_text) if kgv_text else None
        logic    = self._current_logic()
        use_and  = (logic == 'and') and (max_kgv is not None)
        use_or   = (logic == 'or')  and (max_kgv is not None)

        self._save_cache()
        self._start_worker(symbols, perf_min, perf_max, max_kgv, use_and, use_or)

    def _start_worker(
        self,
        symbols:  list[str],
        perf_min: Optional[float],
        perf_max: Optional[float],
        max_kgv:  Optional[float],
        use_and:  bool,
        use_or:   bool,
    ) -> None:
        self._running = True
        self._search_btn.setEnabled(False)
        self._abort_btn.setEnabled(True)
        self._table.setVisible(False)
        self._table.setRowCount(0)
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(True)
        self._progress_lbl.setVisible(True)
        self._status_lbl.setText("")

        self._worker = ScreenerWorker(
            symbols, perf_min, perf_max, max_kgv, use_and, use_or
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_abort(self) -> None:
        if self._worker:
            self._worker.abort()
        self._abort_btn.setEnabled(False)

    def _on_progress(self, done: int, total: int, phase: str) -> None:
        pct = int(done / max(total, 1) * 100)
        self._progress_bar.setValue(pct)
        if phase == 'perf':
            self._progress_lbl.setText(TR('scr_progress_perf', done=done, total=total))
        else:
            self._progress_lbl.setText(TR('scr_progress_kgv', done=done, total=total))

    def _on_finished(self, results: list) -> None:
        self._running = False
        self._search_btn.setEnabled(True)
        self._abort_btn.setEnabled(False)
        self._progress_bar.setVisible(False)
        self._progress_lbl.setVisible(False)

        _cache['results'] = results
        _cache['searched'] = True

        n = len(results)
        if n == 0:
            self._status_lbl.setText(TR('scr_lbl_no_results'))
            self._table.setVisible(False)
            return

        # Abbruch oder vollständige Ergebnisse unterscheiden
        if self._worker and self._worker._abort:
            self._status_lbl.setText(TR('scr_lbl_aborted', n=n))
        else:
            self._status_lbl.setText(TR('scr_lbl_results', n=n))

        self._populate_table(results)

    def _populate_table(self, results: list) -> None:
        self._table.setRowCount(0)
        self._table.setVisible(True)

        for row, r in enumerate(results):
            self._table.insertRow(row)
            self._table.setRowHeight(row, 34)

            sym  = r['symbol']
            name = r.get('name', sym)
            perf = r['perf_pct']
            price = r['price']

            # Spalte 0: Symbol
            sym_item = QTableWidgetItem(sym)
            sym_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self._table.setItem(row, 0, sym_item)

            # Spalte 1: Name
            self._table.setItem(row, 1, QTableWidgetItem(name))

            # Spalte 2: Performance
            perf_item = QTableWidgetItem(f"{perf:+.1f}%")
            perf_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            perf_item.setForeground(
                QColor('#27ae60') if perf >= 0 else QColor('#e74c3c')
            )
            self._table.setItem(row, 2, perf_item)

            # Spalte 3: Kurs
            price_item = QTableWidgetItem(f"{price:,.2f}")
            price_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self._table.setItem(row, 3, price_item)

            # Spalte 4: Aktionen
            self._table.setCellWidget(row, 4, self._make_action_widget(sym))

    def _make_action_widget(self, sym: str) -> QWidget:
        container = QWidget()
        h = QHBoxLayout(container)
        h.setContentsMargins(4, 2, 4, 2)
        h.setSpacing(4)

        _ef = _emoji_font(10)
        chart_btn = QPushButton("📈")
        if _ef: chart_btn.setFont(_ef)
        chart_btn.setFixedSize(30, 26)
        chart_btn.setToolTip(TR('scr_tip_show_chart'))
        chart_btn.clicked.connect(lambda _, s=sym: self._show_chart(s))

        fav_btn = QPushButton("★")
        fav_btn.setFixedSize(30, 26)
        favs_up = [f.upper() for f in getattr(self._app_ref, 'favorites', [])]
        if sym.upper() in favs_up:
            fav_btn.setText("✓")
            fav_btn.setEnabled(False)
            fav_btn.setToolTip(TR('scr_already_fav'))
        else:
            fav_btn.setToolTip(TR('scr_tip_add_fav'))
            fav_btn.clicked.connect(lambda _, s=sym, b=fav_btn: self._add_fav(s, b))

        h.addStretch()
        h.addWidget(chart_btn)
        h.addWidget(fav_btn)
        h.addStretch()
        return container

    def _show_chart(self, sym: str) -> None:
        if self._on_chart_fn is not None:
            self._on_chart_fn(sym)

    def _add_fav(self, sym: str, btn: QPushButton) -> None:
        app = self._app_ref
        if app is None:
            return
        sym_up = sym.upper()
        favs_up = [f.upper() for f in getattr(app, 'favorites', [])]
        if sym_up not in favs_up:
            app.favorites.append(sym_up)
            app.save_favorites()
            for chart in getattr(app, 'charts', []):
                chart.update_favorites_list(app.favorites)
        btn.setText("✓")
        btn.setEnabled(False)
        btn.setToolTip(TR('scr_already_fav'))

    def _show_info(self) -> None:
        mb = QMessageBox(self)
        mb.setWindowTitle(TR('scr_info_title'))
        mb.setText(TR('scr_info_body'))
        mb.setIcon(QMessageBox.Icon.NoIcon)
        mb.exec()

    # ── Aufräumen beim Schliessen ─────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.abort()
            self._worker.wait(3000)
        super().closeEvent(event)
