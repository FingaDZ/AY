"""
Script pour ajouter la colonne numero_anem à la table employes
"""
from sqlalchemy import text
from database import SessionLocal

def migrate():
    try:
        # Utiliser SQLAlchemy pour exécuter les requêtes SQL brutes
        db = SessionLocal()
        
        # Vérifier si la colonne existe déjà
        result = db.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'employes' 
            AND COLUMN_NAME = 'numero_anem'
        """))
        
        exists = result.scalar()
        
        if exists:
            print("✓ La colonne numero_anem existe déjà")
        else:
            # Ajouter la colonne
            db.execute(text("""
                ALTER TABLE employes 
                ADD COLUMN numero_anem VARCHAR(50) NULL AFTER numero_compte_bancaire
            """))
            
            # Créer l'index
            db.execute(text("""
                CREATE INDEX idx_employes_numero_anem ON employes(numero_anem)
            """))
            
            db.commit()
            print("✓ Colonne numero_anem ajoutée avec succès")
            print("✓ Index créé avec succès")
        
        db.close()
        
    except Exception as e:
        print(f"✗ Erreur lors de la migration: {e}")
        raise

if __name__ == "__main__":
    migrate()
