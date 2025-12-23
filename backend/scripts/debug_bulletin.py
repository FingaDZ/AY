#!/usr/bin/env python3
"""Debug script to test jours_conges flow"""

import sys
sys.path.insert(0, '/opt/ay-hr/backend')

from database import SessionLocal
from services.salaire_calculator import SalaireCalculator

db = SessionLocal()
try:
    calc = SalaireCalculator(db)
    
    # Tester pour SAIFI (employe_id=29) en Décembre 2025
    result = calc.calculer_salaire(29, 2025, 12)
    
    print("=" * 60)
    print("Test calcul salaire SAIFI (ID=29) - Décembre 2025")
    print("=" * 60)
    print(f"Status: {result.get('status')}")
    print(f"jours_conges: {result.get('jours_conges', 'ABSENT')}")
    print(f"jours_travailles: {result.get('jours_travailles')}")
    print(f"salaire_net: {result.get('salaire_net')}")
    print("=" * 60)
    
    # Vérifier si jours_conges est dans les clés
    if 'jours_conges' in result:
        print("✅ jours_conges EST présent dans le résultat")
    else:
        print("❌ jours_conges ABSENT du résultat!")
        print("Clés présentes:", list(result.keys()))
        
finally:
    db.close()
