"""
Script de migration pour ajouter la colonne duree_contrat à la table employes.
La durée est stockée en mois et permet le calcul automatique de date_fin_contrat.
"""
from sqlalchemy import create_engine, text
from config import settings

def main():
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        print("Connexion a la base de donnees reussie")
        
        with engine.connect() as connection:
            # Vérifier si la colonne existe déjà
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'employes' 
                AND COLUMN_NAME = 'duree_contrat'
            """))
            
            if result.scalar() > 0:
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
        raise

if __name__ == "__main__":
    main()
