"""
Script pour créer un dump de la base de données du serveur 192.168.20.53
"""
import subprocess
from datetime import datetime
import os

# Configuration
SERVER = "192.168.20.53"
SERVER_USER = "root"
DB_USER = "ayhr_user"
DB_PASSWORD = "!Yara@2014"
DB_NAME = "ay_hr"

def create_dump():
    """Créer un dump du serveur"""
    
    print("=" * 70)
    print("CRÉATION DU DUMP DE LA BASE DE DONNÉES")
    print("=" * 70)
    print(f"Serveur: {SERVER}")
    print(f"Base de données: {DB_NAME}")
    print("=" * 70)
    
    # 1. Créer le dump sur le serveur avec un nom de fichier fixe
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_filename = f"ay_hr_backup_{timestamp}.sql"
    remote_dump = f"/tmp/ay_hr_current.sql"
    local_dump = f"F:\\Code\\AY HR\\{dump_filename}"
    
    print(f"\n📊 Étape 1: Création du dump sur le serveur...")
    print(f"   Fichier distant: {remote_dump}")
    
    # Créer le dump via SSH (commande bash correcte)
    dump_cmd = [
        "ssh",
        f"{SERVER_USER}@{SERVER}",
        f"mysqldump -u {DB_USER} -p'{DB_PASSWORD}' {DB_NAME} > {remote_dump}"
    ]
    
    try:
        result = subprocess.run(dump_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Dump créé sur le serveur")
        else:
            print(f"❌ Erreur lors de la création du dump: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # 2. Télécharger le dump
    print(f"\n📥 Étape 2: Téléchargement du dump...")
    print(f"   Fichier local: {local_dump}")
    
    scp_cmd = [
        "scp",
        f"{SERVER_USER}@{SERVER}:{remote_dump}",
        local_dump
    ]
    
    try:
        result = subprocess.run(scp_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Dump téléchargé")
        else:
            print(f"❌ Erreur lors du téléchargement: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # 3. Vérifier la taille du fichier
    if os.path.exists(local_dump):
        size = os.path.getsize(local_dump)
        print(f"\n✅ Fichier téléchargé: {size / 1024:.2f} KB")
        print(f"📁 Emplacement: {local_dump}")
        
        # Afficher quelques statistiques
        with open(local_dump, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            print(f"   Total de lignes: {len(lines)}")
            
            # Compter les INSERT
            insert_count = sum(1 for line in lines if 'INSERT INTO' in line)
            print(f"   Nombre d'INSERT: {insert_count}")
    else:
        print("❌ Fichier non trouvé après téléchargement")
        return False
    
    # 4. Nettoyer le fichier temporaire sur le serveur
    print(f"\n🧹 Étape 3: Nettoyage du fichier temporaire...")
    cleanup_cmd = [
        "ssh",
        f"{SERVER_USER}@{SERVER}",
        f"rm {remote_dump}"
    ]
    
    try:
        subprocess.run(cleanup_cmd, capture_output=True)
        print("✓ Fichier temporaire supprimé du serveur")
    except:
        print("⚠️  Impossible de supprimer le fichier temporaire (pas critique)")
    
    print(f"\n✅ DUMP CRÉÉ AVEC SUCCÈS!")
    print(f"\n📝 Note: Pour restaurer ce dump sur localhost:")
    print(f"   1. Installez MySQL/MariaDB si ce n'est pas déjà fait")
    print(f"   2. Créez la base de données: CREATE DATABASE ay_hr;")
    print(f"   3. Restaurez: mysql -u root -p ay_hr < {dump_filename}")
    
    return True

if __name__ == "__main__":
    import sys
    success = create_dump()
    
    if success:
        print("\n✅ Opération réussie!")
    else:
        print("\n❌ L'opération a échoué")
        sys.exit(1)
