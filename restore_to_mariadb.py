"""
Script pour restaurer le dump sur la base de données MariaDB distante (192.168.20.52)
"""
import subprocess
import sys
import os

# Configuration
MARIADB_SERVER = "192.168.20.52"
SSH_USER = "n8n"  # Utilisateur SSH
MARIADB_USER = "root"  # Utilisateur MySQL/MariaDB
MARIADB_PASSWORD = "Lamicro@4000"
DB_NAME = "ay_hr"

# Fichier dump le plus récent
DUMP_FILE = "ay_hr_backup_20251117_190626.sql"

def restore_to_remote_mariadb():
    """Restaurer le dump sur le serveur MariaDB distant"""
    
    print("=" * 70)
    print("RESTAURATION DU DUMP SUR MARIADB DISTANT")
    print("=" * 70)
    print(f"Serveur MariaDB: {MARIADB_SERVER}")
    print(f"Base de données: {DB_NAME}")
    print(f"Fichier dump: {DUMP_FILE}")
    print("=" * 70)
    
    # Vérifier que le fichier dump existe
    if not os.path.exists(DUMP_FILE):
        print(f"\n❌ Erreur: Le fichier {DUMP_FILE} n'existe pas!")
        print(f"   Chemin recherché: {os.path.abspath(DUMP_FILE)}")
        return False
    
    file_size = os.path.getsize(DUMP_FILE) / 1024
    print(f"\n✓ Fichier dump trouvé: {file_size:.2f} KB")
    
    # Confirmer la restauration
    print(f"\n⚠️  ATTENTION: Cette opération va:")
    print(f"   1. Se connecter à MariaDB sur {MARIADB_SERVER}")
    print(f"   2. SUPPRIMER toutes les données de la base '{DB_NAME}'")
    print(f"   3. Restaurer les données depuis le dump du serveur 192.168.20.53")
    
    response = input("\n   Voulez-vous continuer? (oui/non): ")
    if response.lower() != 'oui':
        print("❌ Restauration annulée")
        return False
    
    # 1. Transférer le dump sur le serveur MariaDB
    print(f"\n📤 Étape 1: Transfert du dump vers {MARIADB_SERVER}...")
    remote_dump = f"/tmp/{DUMP_FILE}"
    
    scp_cmd = [
        "scp",
        DUMP_FILE,
        f"{SSH_USER}@{MARIADB_SERVER}:{remote_dump}"
    ]
    
    try:
        result = subprocess.run(scp_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Dump transféré sur le serveur MariaDB")
        else:
            print(f"❌ Erreur lors du transfert: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # 2. Créer la base de données si elle n'existe pas
    print(f"\n🗄️  Étape 2: Préparation de la base de données...")
    
    create_db_cmd = [
        "ssh",
        f"{SSH_USER}@{MARIADB_SERVER}",
        f"mysql -u {MARIADB_USER} -p'{MARIADB_PASSWORD}' -e 'CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'"
    ]
    
    try:
        result = subprocess.run(create_db_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Base de données prête")
        else:
            print(f"⚠️  La base existe déjà ou erreur: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Erreur: {e}")
    
    # 3. Restaurer le dump
    print(f"\n📥 Étape 3: Restauration du dump...")
    
    restore_cmd = [
        "ssh",
        f"{SSH_USER}@{MARIADB_SERVER}",
        f"mysql -u {MARIADB_USER} -p'{MARIADB_PASSWORD}' {DB_NAME} < {remote_dump}"
    ]
    
    try:
        result = subprocess.run(restore_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Dump restauré avec succès")
        else:
            print(f"❌ Erreur lors de la restauration: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # 4. Vérifier la restauration
    print(f"\n✅ Étape 4: Vérification de la restauration...")
    
    verify_cmd = [
        "ssh",
        f"{SSH_USER}@{MARIADB_SERVER}",
        f"mysql -u {MARIADB_USER} -p'{MARIADB_PASSWORD}' {DB_NAME} -e 'SELECT COUNT(*) as total_employes FROM employes; SELECT COUNT(*) as total_postes FROM postes_travail;'"
    ]
    
    try:
        result = subprocess.run(verify_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Vérification réussie:")
            print(result.stdout)
        else:
            print(f"⚠️  Impossible de vérifier: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Erreur de vérification: {e}")
    
    # 5. Nettoyer le fichier temporaire
    print(f"\n🧹 Étape 5: Nettoyage...")
    
    cleanup_cmd = [
        "ssh",
        f"{SSH_USER}@{MARIADB_SERVER}",
        f"rm {remote_dump}"
    ]
    
    try:
        subprocess.run(cleanup_cmd, capture_output=True)
        print("✓ Fichier temporaire supprimé")
    except:
        print("⚠️  Impossible de supprimer le fichier temporaire (pas critique)")
    
    print(f"\n✅ RESTAURATION TERMINÉE!")
    print(f"\nℹ️  La base de données {DB_NAME} sur {MARIADB_SERVER} contient maintenant")
    print(f"   les mêmes données que le serveur 192.168.20.53")
    
    return True

if __name__ == "__main__":
    success = restore_to_remote_mariadb()
    
    if success:
        print("\n✅ Opération réussie!")
        print("\n📝 Prochaines étapes:")
        print("   1. Mettre à jour le fichier backend/.env avec:")
        print(f"      DATABASE_URL=mysql+pymysql://{MARIADB_USER}:Lamicro%404000@{MARIADB_SERVER}:3306/{DB_NAME}")
        print("   2. Redémarrer le backend si nécessaire")
    else:
        print("\n❌ L'opération a échoué")
        sys.exit(1)
