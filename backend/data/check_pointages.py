"""
Vérifier le contenu de la table pointages
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import engine
from sqlalchemy import text

def check_pointages():
    """Vérifier les valeurs dans la table pointages"""
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, employe_id, annee, mois, jour_01, jour_02, jour_07 FROM pointages LIMIT 5"))
        rows = result.fetchall()
        
        if not rows:
            print("❌ Aucun pointage dans la table")
            return
        
        print(f"✅ {len(rows)} pointages trouvés\n")
        for row in rows:
            print(f"ID {row[0]} - Employé {row[1]} - {row[2]}/{row[3]}")
            print(f"  jour_01: {row[4]}")
            print(f"  jour_02: {row[5]}")
            print(f"  jour_07: {row[6]}")
            print()

if __name__ == "__main__":
    check_pointages()
