"""
Script simple pour ajouter la colonne duree_contrat avec l'environnement backend
"""
import sys
sys.path.insert(0, 'F:\\Code\\AY HR\\backend')

from database import engine
from sqlalchemy import text

def main():
    try:
        print("Connexion a la base de donnees...")
        
        with engine.connect() as connection:
            # Vérifier si la colonne existe déjà
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'employes' 
                AND COLUMN_NAME = 'duree_contrat'
            """))
            
            count = result.scalar()
            if count > 0:
                print("La colonne duree_contrat existe deja")
                return
            
            # Ajouter la colonne
            print("Ajout de la colonne duree_contrat...")
            connection.execute(text("""
                ALTER TABLE employes 
                ADD COLUMN duree_contrat INT NULL 
                COMMENT 'Duree du contrat en mois'
            """))
            
            # Ajouter l'index
            print("Ajout de l'index idx_duree_contrat...")
            connection.execute(text("CREATE INDEX idx_duree_contrat ON employes(duree_contrat)"))
            
            connection.commit()
            print("Migration reussie : colonne duree_contrat ajoutee")
        
    except Exception as e:
        print(f"Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
