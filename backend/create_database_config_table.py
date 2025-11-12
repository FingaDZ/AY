from database import SessionLocal, engine
from sqlalchemy import text

def create_database_config_table():
    """Créer la table database_config"""
    
    with open('../database/add_database_config_table.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Diviser le SQL en statements individuels
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]
    
    db = SessionLocal()
    try:
        for statement in statements:
            if statement:
                db.execute(text(statement))
        db.commit()
        print("✅ Table 'database_config' créée avec succès!")
    except Exception as e:
        print(f"❌ Erreur lors de la création de la table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_database_config_table()
