"""
Test de suppression d'un employé pour déboguer l'erreur 500
"""
import sys
sys.path.append('F:/Code/AY HR/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Employe
from services.logging_service import clean_data_for_logging
from decimal import Decimal

# Connexion à la base de données
DATABASE_URL = "mysql+pymysql://n8n:%21Yara%402014@192.168.20.52:3306/ay_hr"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_clean_data():
    """Test de la fonction clean_data_for_logging"""
    db = SessionLocal()
    try:
        # Récupérer un employé (l'employé 1 devrait exister)
        employe = db.query(Employe).first()
        if not employe:
            print("❌ Aucun employé trouvé")
            return
        
        print(f"✅ Employé trouvé: {employe.nom} {employe.prenom}")
        print(f"   ID: {employe.id}")
        print(f"   Salaire: {employe.salaire_base} (type: {type(employe.salaire_base)})")
        
        # Tester clean_data_for_logging
        print("\n🔧 Test de clean_data_for_logging...")
        cleaned = clean_data_for_logging(employe)
        
        if cleaned:
            print("✅ Nettoyage réussi!")
            print(f"   Nombre de champs: {len(cleaned)}")
            print(f"   Salaire nettoyé: {cleaned.get('salaire_base')} (type: {type(cleaned.get('salaire_base'))})")
            
            # Tester la sérialisation JSON
            import json
            try:
                json_str = json.dumps(cleaned)
                print("✅ Sérialisation JSON réussie!")
                print(f"   Longueur JSON: {len(json_str)} caractères")
            except Exception as e:
                print(f"❌ Erreur sérialisation JSON: {e}")
        else:
            print("❌ Nettoyage a retourné None")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=== Test de suppression d'employé ===\n")
    test_clean_data()
