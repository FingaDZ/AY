@echo off
REM ====================================
REM Arrêter tous les services AY HR
REM ====================================

echo ========================================
echo      AY HR System - Arret
echo ========================================
echo.

REM Vérifier les privilèges admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERREUR] Ce script necessite les privileges administrateur.
    echo [INFO] Clic droit sur le fichier et selectionnez "Executer en tant qu'administrateur"
    pause
    exit /b 1
)

echo [INFO] Arret des services...
echo.

REM Arrêter Nginx
echo [1/3] Arret du serveur Web...
net stop AYHR_Nginx >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Serveur Web arrete
) else (
    sc query AYHR_Nginx | find "STOPPED" >nul
    if %errorLevel% equ 0 (
        echo [OK] Serveur Web est deja arrete
    ) else (
        echo [AVERTISSEMENT] Impossible d'arreter le serveur Web
    )
)
echo.

REM Arrêter le Backend
echo [2/3] Arret du Backend API...
net stop AYHR_Backend >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Backend arrete
) else (
    sc query AYHR_Backend | find "STOPPED" >nul
    if %errorLevel% equ 0 (
        echo [OK] Backend est deja arrete
    ) else (
        echo [AVERTISSEMENT] Impossible d'arreter le Backend
    )
)
echo.

REM Arrêter MariaDB
echo [3/3] Arret de MariaDB...
net stop AYHR_MySQL >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] MariaDB arrete
) else (
    sc query AYHR_MySQL | find "STOPPED" >nul
    if %errorLevel% equ 0 (
        echo [OK] MariaDB est deja arrete
    ) else (
        echo [AVERTISSEMENT] Impossible d'arreter MariaDB
    )
)
echo.

echo ========================================
echo [SUCCESS] Tous les services sont arretes !
echo ========================================
echo.
pause

exit /b 0
