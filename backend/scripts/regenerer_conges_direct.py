#!/usr/bin/env python3
"""
Script direct de régénération des congés depuis pointages
Bypass l'API et appelle directement les fonctions Python
"""

import sys
sys.path.insert(0, '/opt/ay-hr/backend')

from database import SessionLocal
from services.conges_calculator import recalculer_conges_periode

def main():
    print("🔄 Régénération de TOUS les congés pour 2025")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        total_recalcules = 0
        total_erreurs = 0
        
        for mois in range(1, 13):  # Janvier à Décembre
            print(f"\n📅 Mois {mois:02d}/2025...")
            
            result = recalculer_conges_periode(db, 2025, mois)
            
            total_recalcules += result.get('recalcules', 0)
            total_erreurs += result.get('erreurs', 0)
            
            print(f"   ✅ {result['recalcules']} recalculés, ❌ {result['erreurs']} erreurs")
            
            # Afficher détails si erreurs
            if result['erreurs'] > 0:
                for detail in result['details']:
                    if detail.get('status') == 'erreur':
                        print(f"      ⚠️  Employé {detail['employe_id']}: {detail.get('message')}")
        
        print("\n" + "="*60)
        print(f"✅ TERMINÉ!")
        print(f"   Total congés régénérés: {total_recalcules}")
        print(f"   Total erreurs: {total_erreurs}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
