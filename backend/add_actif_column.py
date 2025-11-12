"""
Script pour ajouter une colonne 'actif' aux employés
Cette colonne sera TRUE par défaut pour les employés existants
"""

from database import engine
from sqlalchemy import text

def add_actif_column():
    """Ajouter la colonne actif à la table employes"""
    
    statements = [
        """
        ALTER TABLE employes 
        ADD COLUMN IF NOT EXISTS actif BOOLEAN DEFAULT TRUE NOT NULL 
        COMMENT 'Employé actif dans le système (soft delete)'
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_employes_actif ON employes(actif)
        """,
        """
        UPDATE employes 
        SET actif = FALSE 
        WHERE date_fin_contrat IS NOT NULL 
        AND date_fin_contrat < CURDATE()
        AND statut_contrat = 'Inactif'
        """
    ]
    
    try:
        with engine.connect() as connection:
            for stmt in statements:
                connection.execute(text(stmt))
            connection.commit()
            print("✅ Colonne 'actif' ajoutée avec succès!")
            print("✅ Index créé sur la colonne 'actif'")
            print("✅ Employés avec contrat terminé mis à jour (actif=FALSE)")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    add_actif_column()
