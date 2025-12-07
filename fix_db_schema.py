import sys
import os
sys.path.append('/opt/ay-hr/backend')
from sqlalchemy import create_engine, text

# Database URL (URL Encoded password for special chars: ! -> %21, @ -> %40)
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://ayhr_user:%21Yara%402014@localhost/ay_hr")

def fix_schema():
    print("🔧 Starting Universal Schema Verification...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        
        # ==============================================================================
        # TABLE: SALAIRES
        # ==============================================================================
        print("\nChecking 'salaires' table...")
        if _table_exists(conn, 'salaires'):
            _check_and_add_columns(conn, 'salaires', [
                ("irg_base_30j", "DECIMAL(10,2) NULL COMMENT 'IRG calculé sur base 30j'"),
                ("avances_reportees", "DECIMAL(10,2) DEFAULT 0"),
                ("credits_reportes", "DECIMAL(10,2) DEFAULT 0"),
                ("alerte_insuffisance", "VARCHAR(50) NULL"),
                ("prime_femme_foyer", "DECIMAL(10,2) DEFAULT 0")
            ])
        else:
            print("❌ Table 'salaires' does not exist!")

        # ==============================================================================
        # TABLE: USERS
        # ==============================================================================
        print("\nChecking 'users' table...")
        if _table_exists(conn, 'users'):
            # 1. Gestion des renommages (Migration V2 -> V3)
            columns = _get_columns(conn, 'users')
            
            # password -> password_hash
            if 'password' in columns and 'password_hash' not in columns:
                print("   ⚠️  Renaming column 'password' to 'password_hash'...")
                try:
                    conn.execute(text("ALTER TABLE users CHANGE COLUMN password password_hash VARCHAR(255) NOT NULL"))
                    print("   ✅ Renamed password -> password_hash")
                except Exception as e:
                    print(f"   ❌ Failed to rename password: {e}")
            
            # name -> nom
            if 'name' in columns and 'nom' not in columns:
                 print("   ⚠️  Renaming column 'name' to 'nom'...")
                 try:
                    conn.execute(text("ALTER TABLE users CHANGE COLUMN name nom VARCHAR(100) NOT NULL"))
                    print("   ✅ Renamed name -> nom")
                 except Exception as e:
                    print(f"   ❌ Failed to rename name: {e}")

            # 2. Ajout des colonnes manquantes
            _check_and_add_columns(conn, 'users', [
                ("nom", "VARCHAR(100) NOT NULL DEFAULT ''"),
                ("prenom", "VARCHAR(100) NOT NULL DEFAULT ''"),
                ("role", "VARCHAR(20) NOT NULL DEFAULT 'Utilisateur'"),
                ("actif", "TINYINT(1) DEFAULT 1"),
                ("date_creation", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
                ("derniere_connexion", "DATETIME NULL")
            ])
        else:
            print("❌ Table 'users' does not exist!")

        conn.commit()
        print("\n🎉 Schema Verification Complete.")

def _table_exists(conn, table_name):
    try:
        conn.execute(text(f"DESCRIBE {table_name}"))
        return True
    except Exception:
        return False

def _get_columns(conn, table_name):
    try:
        result = conn.execute(text(f"DESCRIBE {table_name}"))
        return [row[0] for row in result.fetchall()]
    except:
        return []

def _check_and_add_columns(conn, table_name, schema_updates):
    columns = _get_columns(conn, table_name)
    print(f"   Current columns: {columns}")
    
    for col_name, col_def in schema_updates:
        if col_name not in columns:
            print(f"   ➕ Adding missing column: {col_name}...")
            try:
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}"))
                print(f"   ✅ Added {col_name}")
            except Exception as e:
                print(f"   ❌ Failed to add {col_name}: {e}")
        else:
            print(f"   ✓ Column {col_name} exists.")

if __name__ == "__main__":
    fix_schema()
