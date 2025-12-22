; ====================================
; AY HR System - Installateur NSIS
; Version 3.6.0
; ====================================

!define APP_NAME "AY HR System"
!define APP_VERSION "3.6.0"
!define APP_PUBLISHER "AY Company"
!define APP_URL "http://www.aycompany.dz"
!define APP_INSTALL_DIR "$PROGRAMFILES64\AY HR System"
!define APP_DATA_DIR "$APPDATA\AY HR System"

; Includes
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"

; Configuration
Name "${APP_NAME} ${APP_VERSION}"
OutFile "AY_HR_Setup_v${APP_VERSION}.exe"
InstallDir "${APP_INSTALL_DIR}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "InstallDir"
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING
!if /FileExists "package\resources\app.ico"
    !define MUI_ICON "package\resources\app.ico"
    !define MUI_UNICON "package\resources\app.ico"
!endif
!define MUI_HEADERIMAGE
!if /FileExists "package\resources\header.bmp"
    !define MUI_HEADERIMAGE_BITMAP "package\resources\header.bmp"
!endif
!if /FileExists "package\resources\wizard.bmp"
    !define MUI_WELCOMEFINISHPAGE_BITMAP "package\resources\wizard.bmp"
!endif

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "package\resources\LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\start_ayhr.bat"
!define MUI_FINISHPAGE_RUN_TEXT "Démarrer AY HR System maintenant"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "French"

; ====================================
; Sections
; ====================================

Section "Core Application (Requis)" SecCore
    SectionIn RO
    
    SetOutPath "$INSTDIR"
    
    DetailPrint "Installation des fichiers principaux..."
    File /r "package\backend"
    File /r "package\frontend"
    File /r "package\database"
    File /r "package\resources"
    
    ; Copier les scripts
    SetOutPath "$INSTDIR"
    File /nonfatal "package\*.md"
    File "package\.env.example"
    
    ; Créer les scripts dans l'installation
    SetOutPath "$INSTDIR"
    File "scripts\*.bat"
    File "scripts\*.ps1"
    
    ; Créer la structure de données
    CreateDirectory "$INSTDIR\data"
    CreateDirectory "$INSTDIR\data\mysql"
    CreateDirectory "$INSTDIR\logs"
    CreateDirectory "$INSTDIR\static"
    CreateDirectory "$INSTDIR\backups"
    
    ; Copier le fichier de configuration
    CopyFiles "$INSTDIR\.env.example" "$INSTDIR\.env"
    
    ; Écrire les informations de désinstallation
    WriteRegStr HKLM "Software\${APP_NAME}" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "URLInfoAbout" "${APP_URL}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
SectionEnd

Section "Python 3.11 Embedded" SecPython
    DetailPrint "Installation de Python 3.11 embarqué..."
    SetOutPath "$INSTDIR\python"
    File /r "package\python\*.*"
    
    ; Configurer Python
    DetailPrint "Configuration de Python..."
    nsExec::ExecToLog '"$INSTDIR\python\python.exe" -m pip install --upgrade pip'
    
    ; Installer les dépendances Python
    DetailPrint "Installation des dépendances Python..."
    nsExec::ExecToLog '"$INSTDIR\python\python.exe" -m pip install --no-index --find-links "$INSTDIR\python\packages" -r "$INSTDIR\backend\requirements.txt"'
SectionEnd

Section "Node.js & Frontend Build" SecNodeJS
    DetailPrint "Installation de Node.js portable..."
    SetOutPath "$INSTDIR\nodejs"
    File /r "package\nodejs\*.*"
    
    ; Le frontend est déjà compilé, on copie juste les fichiers statiques
    DetailPrint "Copie du frontend compilé..."
    SetOutPath "$INSTDIR\frontend\dist"
    File /r "package\frontend-dist\*.*"
SectionEnd

Section "MariaDB 10.11" SecMariaDB
    DetailPrint "Installation de MariaDB..."
    SetOutPath "$INSTDIR\mariadb"
    File /r "package\mariadb\*.*"
    
    ; Initialiser la base de données
    DetailPrint "Initialisation de la base de données..."
    nsExec::ExecToLog '"$INSTDIR\mariadb\bin\mysql_install_db.exe" --datadir="$INSTDIR\data\mysql" --service=AYHR_MySQL --port=3307'
    
    ; Installer le service Windows
    DetailPrint "Installation du service MariaDB..."
    nsExec::ExecToLog '"$INSTDIR\mariadb\bin\mysqld.exe" --install AYHR_MySQL --defaults-file="$INSTDIR\mariadb\my.ini"'
    
    ; Démarrer le service
    DetailPrint "Démarrage de MariaDB..."
    nsExec::ExecToLog 'net start AYHR_MySQL'
    
    ; Attendre que le service démarre
    Sleep 5000
    
    ; Créer la base de données et l'utilisateur
    DetailPrint "Configuration de la base de données..."
    nsExec::ExecToLog '"$INSTDIR\scripts\init_database.bat"'
SectionEnd

Section "NSSM - Service Manager" SecNSSM
    DetailPrint "Installation de NSSM..."
    SetOutPath "$INSTDIR\nssm"
    File /r "package\nssm\*.*"
    
    ; Créer le service pour le backend
    DetailPrint "Installation du service Backend..."
    nsExec::ExecToLog '"$INSTDIR\nssm\nssm.exe" install AYHR_Backend "$INSTDIR\python\python.exe" "-m" "uvicorn" "main:app" "--host" "0.0.0.0" "--port" "8000"'
    nsExec::ExecToLog '"$INSTDIR\nssm\nssm.exe" set AYHR_Backend AppDirectory "$INSTDIR\backend"'
    nsExec::ExecToLog '"$INSTDIR\nssm\nssm.exe" set AYHR_Backend DisplayName "AY HR Backend API"'
    nsExec::ExecToLog '"$INSTDIR\nssm\nssm.exe" set AYHR_Backend Description "Backend API pour AY HR System"'
    nsExec::ExecToLog '"$INSTDIR\nssm\nssm.exe" set AYHR_Backend Start SERVICE_AUTO_START"'
    nsExec::ExecToLog '"$INSTDIR\nssm\nssm.exe" set AYHR_Backend AppStdout "$INSTDIR\logs\backend.log"'
    nsExec::ExecToLog '"$INSTDIR\nssm\nssm.exe" set AYHR_Backend AppStderr "$INSTDIR\logs\backend_error.log"'
SectionEnd

Section "Nginx Web Server" SecNginx
    DetailPrint "Installation de Nginx..."
    SetOutPath "$INSTDIR\nginx"
    File /r "package\nginx\*.*"
    
    ; Copier la configuration
    DetailPrint "Configuration de Nginx..."
    SetOutPath "$INSTDIR\nginx\conf"
    File "package\nginx-config\nginx.conf"
    
    ; Créer le service pour Nginx
    DetailPrint "Installation du service Nginx..."
    nsExec::ExecToLog '"$INSTDIR\nssm\nssm.exe" install AYHR_Nginx "$INSTDIR\nginx\nginx.exe"'
    nsExec::ExecToLog '"$INSTDIR\nssm\nssm.exe" set AYHR_Nginx AppDirectory "$INSTDIR\nginx"'
    nsExec::ExecToLog '"$INSTDIR\nssm\nssm.exe" set AYHR_Nginx DisplayName "AY HR Web Server"'
    nsExec::ExecToLog '"$INSTDIR\nssm\nssm.exe" set AYHR_Nginx Description "Serveur web pour AY HR System"'
    nsExec::ExecToLog '"$INSTDIR\nssm\nssm.exe" set AYHR_Nginx Start SERVICE_AUTO_START"'
SectionEnd

Section "Configuration et Démarrage" SecConfig
    DetailPrint "Configuration finale..."
    
    ; Générer la clé secrète
    nsExec::ExecToLog 'powershell -ExecutionPolicy Bypass -File "$INSTDIR\scripts\generate_secret.ps1"'
    
    ; Démarrer les services
    DetailPrint "Démarrage des services..."
    nsExec::ExecToLog 'net start AYHR_Backend'
    Sleep 3000
    nsExec::ExecToLog 'net start AYHR_Nginx'
    
    ; Créer les raccourcis
    DetailPrint "Création des raccourcis..."
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\AY HR System.lnk" "http://localhost"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\Démarrer les services.lnk" "$INSTDIR\start_ayhr.bat"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\Arrêter les services.lnk" "$INSTDIR\stop_ayhr.bat"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\Logs.lnk" "$INSTDIR\logs"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\Configuration.lnk" "$INSTDIR\.env"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\Désinstaller.lnk" "$INSTDIR\uninstall.exe"
    
    CreateShortcut "$DESKTOP\AY HR System.lnk" "http://localhost"
SectionEnd

; ====================================
; Descriptions
; ====================================

LangString DESC_SecCore ${LANG_FRENCH} "Fichiers principaux de l'application (requis)"
LangString DESC_SecPython ${LANG_FRENCH} "Python 3.11 embarqué avec toutes les dépendances"
LangString DESC_SecNodeJS ${LANG_FRENCH} "Node.js portable et frontend compilé"
LangString DESC_SecMariaDB ${LANG_FRENCH} "Serveur de base de données MariaDB 10.11"
LangString DESC_SecNSSM ${LANG_FRENCH} "Gestionnaire de services Windows"
LangString DESC_SecNginx ${LANG_FRENCH} "Serveur web Nginx"
LangString DESC_SecConfig ${LANG_FRENCH} "Configuration et démarrage automatique"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} $(DESC_SecCore)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecPython} $(DESC_SecPython)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecNodeJS} $(DESC_SecNodeJS)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMariaDB} $(DESC_SecMariaDB)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecNSSM} $(DESC_SecNSSM)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecNginx} $(DESC_SecNginx)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecConfig} $(DESC_SecConfig)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; ====================================
; Uninstaller Section
; ====================================

Section "Uninstall"
    ; Arrêter les services
    DetailPrint "Arrêt des services..."
    nsExec::ExecToLog 'net stop AYHR_Nginx'
    nsExec::ExecToLog 'net stop AYHR_Backend'
    nsExec::ExecToLog 'net stop AYHR_MySQL'
    
    ; Supprimer les services
    DetailPrint "Suppression des services..."
    nsExec::ExecToLog '"$INSTDIR\nssm\nssm.exe" remove AYHR_Nginx confirm'
    nsExec::ExecToLog '"$INSTDIR\nssm\nssm.exe" remove AYHR_Backend confirm'
    nsExec::ExecToLog '"$INSTDIR\mariadb\bin\mysqld.exe" --remove AYHR_MySQL'
    
    ; Supprimer les fichiers
    DetailPrint "Suppression des fichiers..."
    RMDir /r "$INSTDIR\backend"
    RMDir /r "$INSTDIR\frontend"
    RMDir /r "$INSTDIR\python"
    RMDir /r "$INSTDIR\nodejs"
    RMDir /r "$INSTDIR\mariadb"
    RMDir /r "$INSTDIR\nginx"
    RMDir /r "$INSTDIR\nssm"
    RMDir /r "$INSTDIR\scripts"
    RMDir /r "$INSTDIR\resources"
    RMDir /r "$INSTDIR\logs"
    RMDir /r "$INSTDIR\static"
    
    ; Demander si on supprime les données
    MessageBox MB_YESNO "Voulez-vous supprimer la base de données et les fichiers de configuration ?$\n$\nATTENTION: Cette action est irréversible !" IDYES DeleteData IDNO KeepData
    DeleteData:
        RMDir /r "$INSTDIR\data"
        RMDir /r "$INSTDIR\backups"
        Delete "$INSTDIR\.env"
    KeepData:
    
    Delete "$INSTDIR\*.bat"
    Delete "$INSTDIR\*.ps1"
    Delete "$INSTDIR\*.md"
    Delete "$INSTDIR\uninstall.exe"
    
    RMDir "$INSTDIR"
    
    ; Supprimer les raccourcis
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    Delete "$DESKTOP\AY HR System.lnk"
    
    ; Supprimer les clés de registre
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegKey HKLM "Software\${APP_NAME}"
    
    MessageBox MB_OK "AY HR System a été désinstallé avec succès."
SectionEnd

; ====================================
; Functions
; ====================================

Function .onInit
    ; Vérifier si déjà installé
    ReadRegStr $0 HKLM "Software\${APP_NAME}" "InstallDir"
    ${If} $0 != ""
        MessageBox MB_YESNO "AY HR System est déjà installé dans $0.$\n$\nVoulez-vous le désinstaller d'abord ?" IDYES Uninstall IDNO Cancel
        Uninstall:
            ExecWait '"$0\uninstall.exe" /S'
            Goto Continue
        Cancel:
            Abort
        Continue:
    ${EndIf}
    
    ; Vérifier les privilèges admin
    UserInfo::GetAccountType
    Pop $0
    ${If} $0 != "admin"
        MessageBox MB_OK "Vous devez exécuter cet installateur en tant qu'administrateur."
        Abort
    ${EndIf}
FunctionEnd

Function .onInstSuccess
    MessageBox MB_OK "Installation terminée avec succès !$\n$\nL'application sera accessible à l'adresse: http://localhost$\n$\nIdentifiants par défaut:$\nEmail: admin@ayhr.dz$\nMot de passe: admin123"
FunctionEnd
