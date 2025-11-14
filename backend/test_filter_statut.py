from database import SessionLocal
from models.employe import Employe, StatutContrat

db = SessionLocal()

try:
    print("\n" + "="*80)
    print("TEST: Filtrage par StatutContrat.INACTIF")
    print("="*80)
    
    # Test du filtre comme dans le router
    query = db.query(Employe)
    query = query.filter(Employe.statut_contrat == StatutContrat.INACTIF)
    
    employes_inactifs = query.all()
    
    print(f"\nNombre d'employés inactifs trouvés: {len(employes_inactifs)}\n")
    
    for emp in employes_inactifs:
        print(f"ID: {emp.id:3d} | Nom: {emp.nom:20s} | Actif: {emp.actif} | Statut: {emp.statut_contrat}")
    
    print("\n" + "="*80)
    print("TEST: Filtrage par StatutContrat.ACTIF")
    print("="*80)
    
    query = db.query(Employe)
    query = query.filter(Employe.statut_contrat == StatutContrat.ACTIF)
    
    employes_actifs = query.all()
    
    print(f"\nNombre d'employés actifs trouvés: {len(employes_actifs)}\n")
    
finally:
    db.close()
