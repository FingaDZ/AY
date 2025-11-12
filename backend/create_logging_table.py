"""
Script pour créer la table logging
"""
from database import engine
from sqlalchemy import text

def create_logging_table():
    try:
        # Lire le fichier SQL
        with open('../database/add_logging_table.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Exécuter le script avec SQLAlchemy
        with engine.connect() as connection:
            connection.execute(text(sql_script))
            connection.commit()
        
        print("✅ Table 'logging' créée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la table: {e}")

if __name__ == "__main__":
    create_logging_table()
