"""
Test de la fonction _pointage_to_response
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import SessionLocal
from models import Pointage
from routers.pointages import _pointage_to_response

def test_pointage_conversion():
    """Tester la conversion d'un pointage"""
    db = SessionLocal()
    try:
        # Récupérer un pointage
        pointage = db.query(Pointage).first()
        
        if not pointage:
            print("❌ Aucun pointage trouvé dans la base")
            return
        
        print(f"✅ Pointage trouvé : ID={pointage.id}, Employé={pointage.employe_id}, {pointage.annee}/{pointage.mois}")
        
        # Tester la conversion
        print("\n🔄 Test de conversion...")
        response = _pointage_to_response(pointage)
        
        print(f"✅ Conversion réussie !")
        print(f"   - ID: {response.id}")
        print(f"   - Jours: {len(response.jours)} jours")
        print(f"   - Premier jour: {response.jours.get(1)}")
        print(f"   - Totaux: {response.totaux}")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_pointage_conversion()
