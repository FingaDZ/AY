@echo off
REM ====================================
REM Vérifier le statut des services AY HR
REM ====================================

echo ========================================
echo      AY HR System - Status
echo ========================================
echo.

echo [MariaDB Database]
sc query AYHR_MySQL | findstr "STATE"
echo.

echo [Backend API]
sc query AYHR_Backend | findstr "STATE"
echo.

echo [Nginx Web Server]
sc query AYHR_Nginx | findstr "STATE"
echo.

echo ========================================
echo.
echo Pour plus de details, utilisez:
echo   sc query AYHR_MySQL
echo   sc query AYHR_Backend
echo   sc query AYHR_Nginx
echo.

pause
exit /b 0
