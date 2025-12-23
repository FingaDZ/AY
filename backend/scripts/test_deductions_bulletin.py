#!/usr/bin/env python3
"""Test de récupération des déductions pour SAIFI Décembre 2025"""
import sys
sys.path.insert(0, '/opt/ay-hr/backend')

from database import SessionLocal
from models import DeductionConge

db = SessionLocal()

# Test pour SAIFI (employe_id=29) en Décembre 2025
employe_id = 29
mois = 12
annee = 2025

print(f"Recherche déductions pour employé {employe_id}, {mois}/{annee}")
print("="*60)

deductions = db.query(DeductionConge).filter(
    DeductionConge.employe_id == employe_id,
    DeductionConge.mois_deduction == mois,
    DeductionConge.annee_deduction == annee
).all()

print(f"Nombre de déductions trouvées: {len(deductions)}")

for d in deductions:
    print(f"\nDéduction #{d.id}:")
    print(f"  - Jours déduits: {d.jours_deduits}")
    print(f"  - Mois: {d.mois_deduction}/{d.annee_deduction}")
    print(f"  - Type: {d.type_conge}")
    print(f"  - Créé le: {d.created_at}")

jours_conges = sum(float(d.jours_deduits or 0) for d in deductions)
print(f"\n{'='*60}")
print(f"TOTAL jours_conges pour ce bulletin: {jours_conges}j")

db.close()
