@echo off
REM ====================================
REM Script d'initialisation de la base de données
REM ====================================

echo [INFO] Initialisation de la base de données AY HR...

REM Attendre que MariaDB soit prêt
echo [INFO] Attente du démarrage de MariaDB...
timeout /t 10 /nobreak >nul

REM Variables
set MYSQL_BIN=%~dp0..\mariadb\bin\mysql.exe
set DB_NAME=ay_hr
set DB_USER=ayhr_user
set DB_PASSWORD=ayhr_password_2024
set DB_ROOT_PASSWORD=ayhr_root_2024

REM Créer la base de données et l'utilisateur
echo [INFO] Création de la base de données...
"%MYSQL_BIN%" -u root --port=3307 -e "CREATE DATABASE IF NOT EXISTS %DB_NAME% CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

echo [INFO] Création de l'utilisateur...
"%MYSQL_BIN%" -u root --port=3307 -e "CREATE USER IF NOT EXISTS '%DB_USER%'@'localhost' IDENTIFIED BY '%DB_PASSWORD%';"
"%MYSQL_BIN%" -u root --port=3307 -e "GRANT ALL PRIVILEGES ON %DB_NAME%.* TO '%DB_USER%'@'localhost';"
"%MYSQL_BIN%" -u root --port=3307 -e "FLUSH PRIVILEGES;"

REM Définir le mot de passe root
echo [INFO] Configuration du mot de passe root...
"%MYSQL_BIN%" -u root --port=3307 -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '%DB_ROOT_PASSWORD%';"

REM Importer le schéma de base de données
echo [INFO] Importation du schéma...
"%MYSQL_BIN%" -u %DB_USER% -p%DB_PASSWORD% --port=3307 %DB_NAME% < "%~dp0..\database\create_database.sql"

REM Importer les données initiales
if exist "%~dp0..\database\init.sql" (
    echo [INFO] Importation des données initiales...
    "%MYSQL_BIN%" -u %DB_USER% -p%DB_PASSWORD% --port=3307 %DB_NAME% < "%~dp0..\database\init.sql"
)

echo [SUCCESS] Base de données initialisée avec succès !
echo [INFO] Base de données: %DB_NAME%
echo [INFO] Utilisateur: %DB_USER%
echo [INFO] Port: 3307

exit /b 0
