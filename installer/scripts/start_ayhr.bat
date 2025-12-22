@echo off
REM ====================================
REM Démarrer tous les services AY HR
REM ====================================

echo ========================================
echo      AY HR System - Demarrage
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

echo [INFO] Demarrage des services...
echo.

REM Démarrer MariaDB
echo [1/3] Demarrage de MariaDB...
net start AYHR_MySQL >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] MariaDB demarre avec succes
) else (
    sc query AYHR_MySQL | find "RUNNING" >nul
    if %errorLevel% equ 0 (
        echo [OK] MariaDB est deja en cours d'execution
    ) else (
        echo [ERREUR] Impossible de demarrer MariaDB
    )
)
timeout /t 3 /nobreak >nul
echo.

REM Démarrer le Backend
echo [2/3] Demarrage du Backend API...
net start AYHR_Backend >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Backend demarre avec succes
) else (
    sc query AYHR_Backend | find "RUNNING" >nul
    if %errorLevel% equ 0 (
        echo [OK] Backend est deja en cours d'execution
    ) else (
        echo [ERREUR] Impossible de demarrer le Backend
    )
)
timeout /t 3 /nobreak >nul
echo.

REM Démarrer Nginx
echo [3/3] Demarrage du serveur Web...
net start AYHR_Nginx >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Serveur Web demarre avec succes
) else (
    sc query AYHR_Nginx | find "RUNNING" >nul
    if %errorLevel% equ 0 (
        echo [OK] Serveur Web est deja en cours d'execution
    ) else (
        echo [ERREUR] Impossible de demarrer le serveur Web
    )
)
echo.

echo ========================================
echo [SUCCESS] Tous les services sont demarres !
echo ========================================
echo.
echo L'application est accessible a l'adresse:
echo   http://localhost
echo.
echo Identifiants par defaut:
echo   Email: admin@ayhr.dz
echo   Mot de passe: admin123
echo.
echo Appuyez sur une touche pour ouvrir l'application...
pause >nul

REM Ouvrir l'application dans le navigateur
start http://localhost

exit /b 0
