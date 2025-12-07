import sys
import os
sys.path.append('/opt/ay-hr/backend')
from sqlalchemy import create_engine, text
# from config import settings (removed to avoid validation error)

# Database URL (URL Encoded password for special chars: ! -> %21, @ -> %40)
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://ayhr_user:%21Yara%402014@localhost/ay_hr")

def fix_salaire_schema():
    print("🔧 Checking 'salaires' table schema...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check columns
        result = conn.execute(text("DESCRIBE salaires"))
        columns = [row[0] for row in result.fetchall()]
        print(f"Current columns: {columns}")
        
        # Columns to check and add if missing
        updates = [
            ("irg_base_30j", "DECIMAL(10,2) NULL COMMENT 'IRG calculé sur base 30j'"),
            ("avances_reportees", "DECIMAL(10,2) DEFAULT 0 COMMENT 'Avances reportées'"),
            ("credits_reportes", "DECIMAL(10,2) DEFAULT 0 COMMENT 'Crédits reportés'"),
            ("alerte_insuffisance", "VARCHAR(50) NULL COMMENT 'Alerte'"),
            ("prime_femme_foyer", "DECIMAL(10,2) DEFAULT 0")
        ]
        
        for col_name, col_def in updates:
            if col_name not in columns:
                print(f"➕ Adding missing column: {col_name}...")
                try:
                    conn.execute(text(f"ALTER TABLE salaires ADD COLUMN {col_name} {col_def}"))
                    print(f"✅ Added {col_name}")
                except Exception as e:
                    print(f"❌ Failed to add {col_name}: {e}")
            else:
                print(f"✓ Column {col_name} exists.")
        
        conn.commit()
        print("🎉 Verify/Fix complete.")

if __name__ == "__main__":
    fix_salaire_schema()
