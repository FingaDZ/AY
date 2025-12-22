@echo off
REM ====================================
REM Sauvegarde de la base de données AY HR
REM ====================================

echo ========================================
echo      AY HR System - Backup
echo ========================================
echo.

REM Variables
set MYSQL_BIN=%~dp0..\mariadb\bin\mysqldump.exe
set DB_NAME=ay_hr
set DB_USER=ayhr_user
set DB_PASSWORD=ayhr_password_2024
set BACKUP_DIR=%~dp0..\backups

REM Créer le dossier de sauvegarde s'il n'existe pas
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Générer le nom du fichier avec la date
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YYYY=%dt:~0,4%"
set "MM=%dt:~4,2%"
set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%"
set "Min=%dt:~10,2%"
set "Sec=%dt:~12,2%"

set "BACKUP_FILE=%BACKUP_DIR%\ay_hr_backup_%YYYY%%MM%%DD%_%HH%%Min%%Sec%.sql"

echo [INFO] Sauvegarde de la base de donnees...
echo [INFO] Fichier: %BACKUP_FILE%
echo.

REM Créer la sauvegarde
"%MYSQL_BIN%" -u %DB_USER% -p%DB_PASSWORD% --port=3307 %DB_NAME% > "%BACKUP_FILE%"

if %errorLevel% equ 0 (
    echo [SUCCESS] Sauvegarde reussie !
    echo [INFO] Taille du fichier:
    dir "%BACKUP_FILE%" | find ".sql"
) else (
    echo [ERREUR] Echec de la sauvegarde
)

echo.
echo ========================================
pause
exit /b 0
