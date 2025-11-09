#!/usr/bin/env python
"""Script de test de connexion à la base de données"""

import sys
import pymysql

# Configuration depuis .env
DB_CONFIG = {
    'host': '192.168.20.52',
    'port': 3306,
    'user': 'n8n',
    'password': '!Yara@2014',
    'database': 'ay_hr'
}

def test_connection():
    """Teste la connexion à MariaDB"""
    print("="*50)
    print("Test de connexion à MariaDB")
    print("="*50)
    print(f"Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"User: {DB_CONFIG['user']}")
    print(f"Database: {DB_CONFIG['database']}")
    print()
    
    try:
        print("Tentative de connexion...")
        conn = pymysql.connect(**DB_CONFIG)
        print("✅ Connexion réussie !")
        
        # Test de requête
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ Version MariaDB/MySQL: {version[0]}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✅ Nombre de tables: {len(tables)}")
            if tables:
                print("   Tables existantes:")
                for table in tables:
                    print(f"   - {table[0]}")
        
        conn.close()
        print("\n✅ Test de connexion terminé avec succès !")
        return True
        
    except pymysql.err.OperationalError as e:
        error_code, error_msg = e.args
        print(f"\n❌ Erreur de connexion ({error_code}): {error_msg}")
        print("\n📝 Solutions possibles:")
        print("   1. Vérifier que MariaDB est démarré sur 192.168.20.52")
        print("   2. Vérifier les identifiants (user/password)")
        print("   3. Créer l'utilisateur si nécessaire:")
        print(f"      CREATE USER '{DB_CONFIG['user']}'@'%' IDENTIFIED BY '{DB_CONFIG['password']}';")
        print(f"      GRANT ALL PRIVILEGES ON {DB_CONFIG['database']}.* TO '{DB_CONFIG['user']}'@'%';")
        print("   4. Vérifier que le firewall autorise la connexion depuis cette IP")
        return False
        
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
