@echo off
setlocal EnableDelayedExpansion
title Stock Monitor – EXE Builder v5.x

:: ============================================================
::  Stock Monitor – Portable EXE Builder
::  Erstellt eine portable stock_monitor.exe die zusammen mit
::  dem ganzen Ordner auf USB/SSD kopiert werden kann.
::
::  Voraussetzungen:
::    - Python 3.10+ im PATH  (python --version)
::    - Alle Abhängigkeiten installiert (siehe INSTALL unten)
::    - PyInstaller installiert: pip install pyinstaller
::
::  Verwendung:
::    1. Diese .bat in denselben Ordner wie stock_monitor.py legen
::    2. Doppelklick oder aus CMD starten
::    3. Fertiger Ordner: dist\StockMonitor_Portable\
::    4. Diesen Ordner auf USB/SSD kopieren → stock_monitor.exe starten
:: ============================================================

echo.
echo ============================================================
echo   Stock Monitor  –  Portable EXE Builder v5.x
echo ============================================================
echo.

:: ── Arbeitsverzeichnis = Ordner dieser .bat ──────────────────
cd /d "%~dp0"

:: ── Python prüfen ────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python nicht gefunden!
    echo         Bitte Python 3.10+ installieren und zum PATH hinzufuegen.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK]  %PYVER% gefunden

:: ── PyInstaller prüfen / installieren ────────────────────────
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller wird installiert...
    pip install pyinstaller --quiet
    if errorlevel 1 (
        echo [FEHLER] PyInstaller Installation fehlgeschlagen!
        pause
        exit /b 1
    )
)
for /f "tokens=*" %%v in ('python -c "import PyInstaller; print(PyInstaller.__version__)"') do set PIVER=%%v
echo [OK]  PyInstaller %PIVER% bereit

:: ── Quelldateien prüfen ──────────────────────────────────────
echo.
echo [CHECK] Quelldateien...
set MISSING=0
for %%f in (
    stock_monitor.py
    portfolio_db.py
    config.py
    translations.py
    tax_module.py
    tax_translations.py
    help_texts.py
    market_data.py
    world_map.py
    dividend_lists.json
) do (
    if not exist "%%f" (
        echo [FEHLER] Fehlende Datei: %%f
        set MISSING=1
    ) else (
        echo [OK]    %%f
    )
)
if !MISSING! == 1 (
    echo.
    echo [FEHLER] Bitte alle Dateien in denselben Ordner wie diese .bat legen.
    pause
    exit /b 1
)

:: ── Icon prüfen / aus Chart.png erstellen ────────────────────
set ICO_ARG=
set ICO_DATA_ARG=
if not exist "stock_monitor.ico" (
    if exist "Chart.png" (
        echo [INFO] stock_monitor.ico wird aus Chart.png erstellt...
        python -c "from PIL import Image; img=Image.open('Chart.png').convert('RGBA'); img.save('stock_monitor.ico',format='ICO',sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])"
    )
)
if exist "stock_monitor.ico" (
    echo [OK]    stock_monitor.ico gefunden
    set ICO_ARG=--icon="stock_monitor.ico"
    set ICO_DATA_ARG=--add-data "stock_monitor.ico;."
) else (
    echo [WARN]  stock_monitor.ico nicht gefunden – kein Icon
)

:: ── Altes Build aufräumen ────────────────────────────────────
echo.
echo [BUILD] Alte Build-Artefakte werden entfernt...
if exist "build"                    rmdir /s /q "build"
if exist "dist\StockMonitor_Portable" rmdir /s /q "dist\StockMonitor_Portable"
if exist "stock_monitor.spec"       del /q "stock_monitor.spec"

:: ── PyInstaller-Aufruf ───────────────────────────────────────
echo.
echo [BUILD] Starte PyInstaller...
echo         (Kann 2-5 Minuten dauern – bitte warten)
echo.

python -m PyInstaller ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --name "stock_monitor" ^
    %ICO_ARG% ^
    %ICO_DATA_ARG% ^
    --distpath "dist\StockMonitor_Portable" ^
    --add-data "portfolio_db.py;." ^
    --add-data "config.py;." ^
    --add-data "translations.py;." ^
    --add-data "tax_module.py;." ^
    --add-data "tax_translations.py;." ^
    --add-data "help_texts.py;." ^
    --add-data "market_data.py;." ^
    --add-data "world_map.py;." ^
    --add-data "dividend_lists.json;." ^
    --hidden-import "PyQt6.QtCore" ^
    --hidden-import "PyQt6.QtGui" ^
    --hidden-import "PyQt6.QtWidgets" ^
    --hidden-import "PyQt6.QtWebEngineWidgets" ^
    --hidden-import "PyQt6.QtWebEngineCore" ^
    --hidden-import "PyQt6.QtNetwork" ^
    --hidden-import "PyQt6.QtPrintSupport" ^
    --hidden-import "matplotlib.backends.backend_qt5agg" ^
    --hidden-import "matplotlib.backends.backend_agg" ^
    --hidden-import "mpl_toolkits.mplot3d" ^
    --hidden-import "pyqtgraph" ^
    --hidden-import "pyqtgraph.graphicsItems" ^
    --hidden-import "yfinance" ^
    --hidden-import "pandas" ^
    --hidden-import "numpy" ^
    --hidden-import "cryptography" ^
    --hidden-import "cryptography.hazmat.primitives.kdf.pbkdf2" ^
    --hidden-import "cryptography.hazmat.primitives.ciphers.aead" ^
    --hidden-import "cryptography.hazmat.backends" ^
    --hidden-import "openpyxl" ^
    --hidden-import "openpyxl.styles" ^
    --hidden-import "openpyxl.chart" ^
    --hidden-import "openpyxl.drawing.image" ^
    --hidden-import "odf" ^
    --hidden-import "odf.opendocument" ^
    --hidden-import "odf.table" ^
    --hidden-import "odf.text" ^
    --hidden-import "odf.style" ^
    --hidden-import "odf.draw" ^
    --hidden-import "reportlab" ^
    --hidden-import "reportlab.pdfgen.canvas" ^
    --hidden-import "reportlab.lib.pagesizes" ^
    --hidden-import "reportlab.lib.styles" ^
    --hidden-import "reportlab.lib.units" ^
    --hidden-import "reportlab.lib.colors" ^
    --hidden-import "reportlab.platypus" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "certifi" ^
    --collect-all "certifi" ^
    --hidden-import "concurrent.futures" ^
    --collect-all "yfinance" ^
    --collect-all "pyqtgraph" ^
    stock_monitor.py

if errorlevel 1 (
    echo.
    echo [FEHLER] PyInstaller hat einen Fehler gemeldet!
    echo         Siehe Ausgabe oben fuer Details.
    pause
    exit /b 1
)

:: ── Icon ins Dist-Verzeichnis kopieren (für Laufzeit) ────────
if exist "stock_monitor.ico" (
    copy /y "stock_monitor.ico" "dist\StockMonitor_Portable\stock_monitor\" >nul
    echo [OK]  Icon in EXE-Ordner kopiert
)

:: ── Optionale Extra-Dateien kopieren ─────────────────────────
:: Splash-Screen falls vorhanden
if exist "splash.png"  copy /y "splash.png"  "dist\StockMonitor_Portable\stock_monitor\" >nul
if exist "splash.jpg"  copy /y "splash.jpg"  "dist\StockMonitor_Portable\stock_monitor\" >nul

:: README falls vorhanden
if exist "README.md"   copy /y "README.md"   "dist\StockMonitor_Portable\stock_monitor\" >nul
if exist "README.txt"  copy /y "README.txt"  "dist\StockMonitor_Portable\stock_monitor\" >nul

:: Changelog falls vorhanden
if exist "CHANGELOG.md" copy /y "CHANGELOG.md" "dist\StockMonitor_Portable\stock_monitor\" >nul

:: ── Starte-Skript für bequemen Doppelklick ───────────────────
(
echo @echo off
echo cd /d "%%~dp0"
echo start "" "stock_monitor.exe"
) > "dist\StockMonitor_Portable\stock_monitor\Start Stock Monitor.bat"

:: ── Ergebnis ─────────────────────────────────────────────────
echo.
echo ============================================================
echo   BUILD ERFOLGREICH!
echo ============================================================
echo.
echo   Portabler Ordner:
echo   %~dp0dist\StockMonitor_Portable\stock_monitor\
echo.
echo   Zum Verteilen:
echo   Den gesamten Ordner  "stock_monitor"  auf USB/SSD kopieren.
echo   Starten mit:  stock_monitor.exe
echo               oder  "Start Stock Monitor.bat"
echo.
echo   HINWEIS: Der Ordner enthaelt alle noetigen Dateien.
echo            Python muss auf dem Ziel-PC NICHT installiert sein.
echo ============================================================
echo.

:: Ordner direkt im Explorer öffnen
explorer "dist\StockMonitor_Portable\stock_monitor"

pause
