@echo off
setlocal EnableDelayedExpansion
title Stock Monitor – Release ZIP erstellen

:: ============================================================
::  Erstellt ein sauberes stock_monitor.zip ohne persönliche
::  Benutzerdaten (Config, Session, Log-Dateien).
::  Voraussetzung: build_exe.bat wurde bereits ausgeführt.
:: ============================================================

cd /d "%~dp0"

set SRC=dist\stock_monitor
set ZIP=stock_monitor.zip

:: Prüfen ob Build vorhanden
if not exist "%SRC%\stock_monitor.exe" (
    echo [FEHLER] Zuerst build_exe.bat ausfuehren!
    pause
    exit /b 1
)

echo.
echo [CLEAN] Benutzerdaten aus Build-Ordner entfernen...

:: Persönliche Daten löschen (werden beim ersten App-Start neu erstellt)
if exist "%SRC%\_internal\.stock_monitor_config.json"      del /q "%SRC%\_internal\.stock_monitor_config.json"
if exist "%SRC%\_internal\.stock_monitor_active_portfolio" del /q "%SRC%\_internal\.stock_monitor_active_portfolio"
if exist "%SRC%\_internal\.stock_monitor_portfolio.json"   del /q "%SRC%\_internal\.stock_monitor_portfolio.json"
if exist "%SRC%\_internal\.stock_monitor_companies.json"   del /q "%SRC%\_internal\.stock_monitor_companies.json"
if exist "%SRC%\_internal\.stock_monitor_sectors.json"     del /q "%SRC%\_internal\.stock_monitor_sectors.json"
if exist "%SRC%\_internal\.stock_monitor_configs"          rmdir /s /q "%SRC%\_internal\.stock_monitor_configs"

:: Alle .smpf-Portfolios ausser Demo löschen
if exist "%SRC%\_internal\.stock_monitor_portfolios" (
    for %%f in ("%SRC%\_internal\.stock_monitor_portfolios\*.smpf") do (
        if /i not "%%~nxf"=="Demo.smpf" del /q "%%f"
    )
)

if exist "%SRC%\stock_monitor.log"                         del /q "%SRC%\stock_monitor.log"

echo [OK]  Benutzerdaten entfernt

:: Altes ZIP löschen
if exist "%ZIP%" del /q "%ZIP%"

echo [ZIP]  Erstelle %ZIP%...

:: ZIP erstellen mit PowerShell (auf jedem Windows verfügbar)
powershell -Command "Compress-Archive -Path '%SRC%' -DestinationPath '%ZIP%' -Force"

if errorlevel 1 (
    echo [FEHLER] ZIP-Erstellung fehlgeschlagen!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   FERTIG: %ZIP% wurde erstellt
echo ============================================================
echo.

:: Dateigrösse anzeigen
for %%f in ("%ZIP%") do echo   Groesse: %%~zf Bytes

echo.
pause
