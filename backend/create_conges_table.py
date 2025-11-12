"""Script pour créer la table conges"""
import sys
sys.path.insert(0, '.')

from sqlalchemy import text
from database import engine

# Script SQL
sql_script = """
CREATE TABLE IF NOT EXISTS conges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employe_id INT NOT NULL,
    annee INT NOT NULL,
    mois INT NOT NULL,
    jours_travailles INT DEFAULT 0,
    jours_conges_acquis DECIMAL(5,2) DEFAULT 0.00,
    jours_conges_pris DECIMAL(5,2) DEFAULT 0.00,
    jours_conges_restants DECIMAL(5,2) DEFAULT 0.00,
    date_calcul DATETIME DEFAULT CURRENT_TIMESTAMP,
    derniere_mise_a_jour DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (employe_id) REFERENCES employes(id) ON DELETE CASCADE,
    UNIQUE KEY unique_employe_mois (employe_id, annee, mois),
    INDEX idx_employe (employe_id),
    INDEX idx_periode (annee, mois)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

try:
    with engine.connect() as connection:
        connection.execute(text(sql_script))
        connection.commit()
    print("✅ Table 'conges' créée avec succès!")
except Exception as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)
