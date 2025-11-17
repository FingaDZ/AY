"""
Script pour créer un dump de la base de données du serveur 
et restaurer sur localhost
"""
import sys
import subprocess
import os
from datetime import datetime

# Configuration
SERVER = "192.168.20.53"
SERVER_USER = "root"
DB_USER = "ayhr_user"
DB_PASSWORD = "!Yara@2014"
DB_NAME = "ay_hr"

# Localhost configuration (à adapter selon votre configuration)
LOCAL_DB_USER = "root"
LOCAL_DB_PASSWORD = "Lamicro@4000"
LOCAL_DB_NAME = "ay_hr"

def run_command(command, description):
    """Exécuter une commande et afficher le résultat"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ {description} réussi")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")
        if e.stderr:
            print(f"Erreur détaillée: {e.stderr}")
        return False

def create_dump_and_restore():
    """Créer un dump du serveur et restaurer sur localhost"""
    
    print("=" * 70)
    print("DUMP ET RESTAURATION DE LA BASE DE DONNÉES")
    print("=" * 70)
    print(f"Serveur source: {SERVER}")
    print(f"Base de données: {DB_NAME}")
    print("=" * 70)
    
    # 1. Créer le dump sur le serveur
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_file = f"ay_hr_dump_{timestamp}.sql"
    remote_dump = f"/tmp/{dump_file}"
    local_dump = f"F:\\Code\\AY HR\\{dump_file}"
    
    print(f"\n📊 Étape 1: Création du dump sur le serveur...")
    dump_cmd = f'ssh {SERVER_USER}@{SERVER} "mysqldump -u {DB_USER} -p\'{DB_PASSWORD}\' {DB_NAME} > {remote_dump}"'
    
    if not run_command(dump_cmd, "Création du dump"):
        return False
    
    # 2. Télécharger le dump
    print(f"\n📥 Étape 2: Téléchargement du dump...")
    scp_cmd = f'scp {SERVER_USER}@{SERVER}:{remote_dump} "{local_dump}"'
    
    if not run_command(scp_cmd, "Téléchargement du dump"):
        return False
    
    # Vérifier la taille du fichier
    if os.path.exists(local_dump):
        size = os.path.getsize(local_dump)
        print(f"✓ Fichier téléchargé: {size / 1024:.2f} KB")
    else:
        print("❌ Fichier non trouvé après téléchargement")
        return False
    
    # 3. Confirmer la restauration
    print(f"\n⚠️  ATTENTION: Cette opération va:")
    print(f"   1. SUPPRIMER toutes les données de la base '{LOCAL_DB_NAME}' sur localhost")
    print(f"   2. Restaurer les données depuis le serveur {SERVER}")
    
    response = input("\n   Voulez-vous continuer? (oui/non): ")
    if response.lower() != 'oui':
        print("❌ Restauration annulée")
        print(f"✓ Le dump est disponible dans: {local_dump}")
        return False
    
    # 4. Créer la base de données si elle n'existe pas
    print(f"\n🗄️  Étape 3: Préparation de la base de données locale...")
    create_db_cmd = f'mysql -u {LOCAL_DB_USER} -p{LOCAL_DB_PASSWORD} -e "CREATE DATABASE IF NOT EXISTS {LOCAL_DB_NAME};"'
    
    if not run_command(create_db_cmd, "Création de la base de données"):
        print("⚠️  La base existe peut-être déjà, on continue...")
    
    # 5. Restaurer le dump
    print(f"\n📤 Étape 4: Restauration du dump sur localhost...")
    restore_cmd = f'mysql -u {LOCAL_DB_USER} -p{LOCAL_DB_PASSWORD} {LOCAL_DB_NAME} < "{local_dump}"'
    
    if not run_command(restore_cmd, "Restauration du dump"):
        return False
    
    # 6. Vérifier la restauration
    print(f"\n✅ Étape 5: Vérification de la restauration...")
    verify_cmd = f'mysql -u {LOCAL_DB_USER} -p{LOCAL_DB_PASSWORD} {LOCAL_DB_NAME} -e "SELECT COUNT(*) as total_employes FROM employes; SELECT COUNT(*) as total_postes FROM postes_travail;"'
    
    run_command(verify_cmd, "Vérification")
    
    # 7. Nettoyer les fichiers temporaires sur le serveur
    print(f"\n🧹 Étape 6: Nettoyage des fichiers temporaires...")
    cleanup_cmd = f'ssh {SERVER_USER}@{SERVER} "rm {remote_dump}"'
    run_command(cleanup_cmd, "Nettoyage serveur")
    
    print(f"\n✅ RESTAURATION TERMINÉE!")
    print(f"\n📁 Le dump de sauvegarde est disponible dans:")
    print(f"   {local_dump}")
    
    return True

if __name__ == "__main__":
    success = create_dump_and_restore()
    
    if success:
        print("\n✅ Opération réussie!")
    else:
        print("\n❌ L'opération a échoué")
        sys.exit(1)
