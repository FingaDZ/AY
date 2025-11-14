from database import SessionLocal
from models.employe import Employe, StatutContrat

db = SessionLocal()

try:
    print("\n" + "="*80)
    print("SIMULATION DU COMPORTEMENT API")
    print("="*80)
    
    # Test 1: statut=Inactif SANS inclure_inactifs (comportement par défaut)
    print("\n1. Requête: statut=Inactif (inclure_inactifs=False par défaut)")
    print("-" * 80)
    query = db.query(Employe)
    query = query.filter(Employe.actif == True)  # Par défaut
    query = query.filter(Employe.statut_contrat == StatutContrat.INACTIF)
    result = query.all()
    print(f"Résultat: {len(result)} employés")
    print("Explication: Cherche actif=True ET statut=INACTIF → IMPOSSIBLE ❌\n")
    
    # Test 2: statut=Inactif AVEC inclure_inactifs=True
    print("2. Requête: statut=Inactif&inclure_inactifs=true")
    print("-" * 80)
    query = db.query(Employe)
    # Pas de filtre actif == True
    query = query.filter(Employe.statut_contrat == StatutContrat.INACTIF)
    result = query.all()
    print(f"Résultat: {len(result)} employés")
    for e in result:
        print(f"  - ID {e.id}: {e.nom} (actif={e.actif}, statut={e.statut_contrat})")
    print("✅ CORRECT\n")
    
    # Test 3: statut=Actif (par défaut)
    print("3. Requête: statut=Actif (inclure_inactifs=False par défaut)")
    print("-" * 80)
    query = db.query(Employe)
    query = query.filter(Employe.actif == True)
    query = query.filter(Employe.statut_contrat == StatutContrat.ACTIF)
    result = query.all()
    print(f"Résultat: {len(result)} employés")
    print("✅ CORRECT\n")
    
    # Test 4: Tous (inclure_inactifs=True, pas de filtre statut)
    print("4. Requête: Tous (inclure_inactifs=true, sans filtre statut)")
    print("-" * 80)
    query = db.query(Employe)
    result = query.all()
    actifs = [e for e in result if e.actif]
    inactifs = [e for e in result if not e.actif]
    print(f"Résultat: {len(result)} employés")
    print(f"  - Actifs: {len(actifs)}")
    print(f"  - Inactifs: {len(inactifs)}")
    print("✅ CORRECT\n")
    
finally:
    db.close()
