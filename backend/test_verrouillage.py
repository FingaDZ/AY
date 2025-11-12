"""
Script de test pour la fonctionnalité de verrouillage des pointages
"""
from database import SessionLocal
from models import Pointage, Employe

def test_verrouillage():
    db = SessionLocal()
    
    print("=" * 60)
    print("TEST DE LA FONCTIONNALITÉ DE VERROUILLAGE")
    print("=" * 60)
    print()
    
    # Récupérer le premier pointage
    pointage = db.query(Pointage).first()
    
    if not pointage:
        print("❌ Aucun pointage trouvé pour tester")
        db.close()
        return
    
    employe = db.query(Employe).filter(Employe.id == pointage.employe_id).first()
    
    print(f"📋 Pointage testé:")
    print(f"   - ID: {pointage.id}")
    print(f"   - Employé: {employe.nom} {employe.prenom}")
    print(f"   - Période: {pointage.mois}/{pointage.annee}")
    print(f"   - État initial: {'🔒 Verrouillé' if pointage.verrouille else '🔓 Déverrouillé'}")
    print()
    
    # Test 1: Changer l'état
    print("📝 Test 1: Changement d'état de verrouillage")
    etat_initial = pointage.verrouille
    pointage.verrouille = not etat_initial
    db.commit()
    db.refresh(pointage)
    
    if pointage.verrouille != etat_initial:
        print(f"   ✅ État changé avec succès: {etat_initial} → {pointage.verrouille}")
    else:
        print(f"   ❌ Erreur: l'état n'a pas changé")
    print()
    
    # Test 2: Vérifier que verrouille est un boolean
    print("📝 Test 2: Type de données")
    print(f"   - Type de verrouille: {type(pointage.verrouille).__name__}")
    print(f"   - Valeur: {pointage.verrouille}")
    if isinstance(pointage.verrouille, (bool, int)):
        print(f"   ✅ Type correct (bool ou int)")
    else:
        print(f"   ⚠️  Type inattendu")
    print()
    
    # Test 3: Remettre l'état initial
    print("📝 Test 3: Restauration de l'état initial")
    pointage.verrouille = etat_initial
    db.commit()
    db.refresh(pointage)
    
    if pointage.verrouille == etat_initial:
        print(f"   ✅ État restauré avec succès: {pointage.verrouille}")
    else:
        print(f"   ❌ Erreur: l'état n'a pas été restauré")
    print()
    
    # Test 4: Afficher tous les pointages avec leur état
    print("📝 Test 4: État de tous les pointages")
    all_pointages = db.query(Pointage).all()
    print(f"   Nombre total de pointages: {len(all_pointages)}")
    for p in all_pointages:
        emp = db.query(Employe).filter(Employe.id == p.employe_id).first()
        icone = "🔒" if p.verrouille else "🔓"
        print(f"   {icone} ID={p.id} | Employé #{emp.id}: {emp.nom} | {p.mois}/{p.annee} | verrouille={p.verrouille}")
    print()
    
    print("=" * 60)
    print("✅ TESTS TERMINÉS")
    print("=" * 60)
    
    db.close()

if __name__ == "__main__":
    test_verrouillage()
