from database import SessionLocal
from models.employe import Employe

db = SessionLocal()
try:
    employes = db.query(Employe).all()
    print(f'\n✅ Total employés: {len(employes)}\n')
    
    actifs = [e for e in employes if e.actif == True]
    inactifs = [e for e in employes if e.actif == False]
    
    print(f'📊 Actifs: {len(actifs)}')
    print(f'📊 Inactifs: {len(inactifs)}\n')
    
    print('=' * 80)
    for e in employes:
        print(f'ID: {e.id:3d} | Nom: {e.nom:20s} | Actif: {str(e.actif):5s} | Statut: {e.statut_contrat}')
    print('=' * 80)
    
finally:
    db.close()
