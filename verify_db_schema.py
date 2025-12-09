import sys
import os
sys.path.append('/opt/ay-hr/backend')
from sqlalchemy import create_engine, inspect
from config import settings

# Override DB URL only if needed (e.g. localhost vs .55)
# settings.DATABASE_URL might be correct if running on the server
DATABASE_URL = "mysql+pymysql://ayhr_user:!Yara@2014@localhost/ay_hr"

def check_irg_schema():
    print("Checking database schema for 'irg_bareme'...")
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        if not inspector.has_table('irg_bareme'):
            print("❌ Table 'irg_bareme' does not exist!")
            return False
            
        columns = [col['name'] for col in inspector.get_columns('irg_bareme')]
        print(f"Current columns: {columns}")
        
        required_new = {'salaire', 'montant_irg'}
        required_old = {'salaire_min', 'irg'}
        
        current_set = set(columns)
        
        if required_new.issubset(current_set):
            print("✅ Schema is NEW (Correct for current code).")
            return True
        elif required_old.issubset(current_set):
            print("⚠️ Schema is OLD (Needs migration).")
            print("   Missing columns:", required_new - current_set)
            return False
        else:
            print("❌ Schema is UNKNOWN or Corrupted.")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to DB: {e}")
        return False

if __name__ == "__main__":
    check_irg_schema()
