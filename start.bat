@echo off
REM Script de démarrage de l'application AY HR Management pour Windows CMD
REM Utilisation : start.bat

echo ========================================
echo   AY HR Management - Demarrage
echo ========================================
echo.

echo [1/5] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python n'est pas installe ou n'est pas dans le PATH
    echo   Telechargez Python depuis https://www.python.org/downloads/
    pause
    exit /b 1
)
echo V Python trouve

echo.
echo [2/5] Navigation vers le dossier backend...
cd backend
if errorlevel 1 (
    echo X Dossier backend non trouve
    pause
    exit /b 1
)
echo V Dossier backend trouve

echo.
echo [3/5] Verification de l'environnement virtuel...
if exist venv (
    echo V Environnement virtuel trouve
) else (
    echo ! Environnement virtuel non trouve
    echo   Creation de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo X Erreur lors de la creation de l'environnement virtuel
        pause
        exit /b 1
    )
    echo V Environnement virtuel cree
)

echo.
echo [4/5] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo X Erreur lors de l'activation de l'environnement virtuel
    pause
    exit /b 1
)
echo V Environnement virtuel active

echo.
echo [5/5] Verification des dependances...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo ! Installation des dependances...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo X Erreur lors de l'installation des dependances
        pause
        exit /b 1
    )
    echo V Dependances installees avec succes
) else (
    echo V Dependances installees
)

echo.
echo Verification du fichier IRG...
if exist data\irg.xlsx (
    echo V Fichier IRG trouve
) else (
    echo ! Fichier IRG non trouve
    echo   Creation du fichier IRG...
    python data\create_irg.py
    echo V Fichier IRG cree
    echo ** IMPORTANT: Verifiez et ajustez le bareme dans data\irg.xlsx
)

echo.
echo ========================================
echo   Demarrage de l'application...
echo ========================================
echo.
echo L'API sera accessible sur:
echo   * API: http://localhost:8000
echo   * Documentation: http://localhost:8000/docs
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo.

python main.py
