"""Test direct de suppression d'employé avec logging"""
import sys
sys.path.insert(0, '.')

from database import SessionLocal
from models import Employe
from services.logging_service import clean_data_for_logging
import json

# Créer une session
db = SessionLocal()

try:
    # Charger un employé
    employe = db.query(Employe).filter(Employe.id == 26).first()
    
    if not employe:
        print("❌ Employé ID 26 introuvable")
        sys.exit(1)
    
    print(f"✅ Employé trouvé: {employe.nom} {employe.prenom}")
    print(f"   Salaire base: {employe.salaire_base} (type: {type(employe.salaire_base).__name__})")
    
    # Tester le nettoyage
    print("\n🧪 Test de clean_data_for_logging...")
    cleaned = clean_data_for_logging(employe)
    
    if cleaned:
        print(f"✅ Nettoyage réussi!")
        print(f"   Salaire après nettoyage: {cleaned.get('salaire_base')} (type: {type(cleaned.get('salaire_base')).__name__})")
        
        # Tester la sérialisation JSON
        print("\n🧪 Test de sérialisation JSON...")
        try:
            json_str = json.dumps(cleaned)
            print(f"✅ Sérialisation JSON réussie! ({len(json_str)} caractères)")
        except Exception as e:
            print(f"❌ Erreur de sérialisation: {e}")
            sys.exit(1)
    else:
        print("❌ Nettoyage a retourné None")
        sys.exit(1)
    
    print("\n✅ TOUS LES TESTS PASSÉS - Le code de logging fonctionne correctement")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()
