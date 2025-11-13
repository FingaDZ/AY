"""
Migration pour créer la table postes_travail
"""
import sys
sys.path.insert(0, 'F:\\Code\\AY HR\\backend')

from database import engine
from sqlalchemy import text

def main():
    try:
        print("Connexion a la base de donnees...")
        
        with engine.connect() as connection:
            # Vérifier si la table existe déjà
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'postes_travail'
            """))
            
            if result.scalar() > 0:
                print("La table postes_travail existe deja")
                return
            
            print("Creation de la table postes_travail...")
            connection.execute(text("""
                CREATE TABLE postes_travail (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    libelle VARCHAR(100) NOT NULL UNIQUE COMMENT 'Nom du poste',
                    est_chauffeur BOOLEAN DEFAULT FALSE NOT NULL COMMENT 'Indique si le poste est chauffeur',
                    modifiable BOOLEAN DEFAULT TRUE NOT NULL COMMENT 'Indique si le poste peut être modifié/supprimé',
                    actif BOOLEAN DEFAULT TRUE NOT NULL COMMENT 'Soft delete',
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    
                    INDEX idx_actif (actif),
                    INDEX idx_est_chauffeur (est_chauffeur),
                    INDEX idx_libelle (libelle)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                COMMENT='Table des postes de travail avec gestion des chauffeurs et soft delete'
            """))
            
            print("Insertion des postes de base...")
            connection.execute(text("""
                INSERT INTO postes_travail (libelle, est_chauffeur, modifiable, actif) VALUES
                ('Chauffeur', TRUE, FALSE, TRUE),
                ('Agent de sécurité', FALSE, TRUE, TRUE),
                ('Gardien', FALSE, TRUE, TRUE),
                ('Technicien', FALSE, TRUE, TRUE)
            """))
            
            connection.commit()
            print("Migration reussie : table postes_travail creee avec 4 postes de base")
        
    except Exception as e:
        print(f"Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
