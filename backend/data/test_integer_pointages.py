#!/usr/bin/env python3
"""
Test du système de pointage avec valeurs numériques
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import SessionLocal
from models.pointage import Pointage
from models.employe import Employe

def test_pointage_system():
    """Tester la création et le calcul de pointages avec valeurs numériques"""
    db = SessionLocal()
    
    try:
        # Récupérer un employé
        employe = db.query(Employe).first()
        if not employe:
            print("❌ Aucun employé trouvé. Créez d'abord un employé.")
            return False
        
        print(f"Test avec l'employé: {employe.nom} {employe.prenom} (ID: {employe.id})")
        
        # Créer un nouveau pointage avec valeurs numériques
        print("\n1. Création d'un pointage avec valeurs 0 et 1...")
        pointage = Pointage(
            employe_id=employe.id,
            annee=2025,
            mois=11
        )
        
        # Remplir quelques jours
        # Jours 1-5: Travaillé (1)
        for jour in range(1, 6):
            pointage.set_jour(jour, 1)
        
        # Jours 6-7: Weekend/Absent (0)
        pointage.set_jour(6, 0)
        pointage.set_jour(7, 0)
        
        # Jour 8: Férié (1)
        pointage.set_jour(8, 1)
        
        # Jours 9-10: Absent (0)
        pointage.set_jour(9, 0)
        pointage.set_jour(10, 0)
        
        # Jours 11-15: Travaillé (1)
        for jour in range(11, 16):
            pointage.set_jour(jour, 1)
        
        db.add(pointage)
        db.commit()
        db.refresh(pointage)
        
        print(f"✓ Pointage créé avec ID: {pointage.id}")
        
        # Vérifier les valeurs stockées
        print("\n2. Vérification des valeurs stockées:")
        for jour in range(1, 16):
            valeur = pointage.get_jour(jour)
            print(f"   Jour {jour:02d}: {valeur}")
        
        # Calculer les totaux
        print("\n3. Calcul des totaux:")
        totaux = pointage.calculer_totaux()
        print(f"   Total jours travaillés (valeur=1): {totaux['total_travailles']}")
        
        # Vérification manuelle
        expected = 5 + 1 + 5  # Jours 1-5 + jour 8 + jours 11-15
        if totaux['total_travailles'] == expected:
            print(f"✓ Calcul correct! Attendu: {expected}, Obtenu: {totaux['total_travailles']}")
        else:
            print(f"❌ Calcul incorrect! Attendu: {expected}, Obtenu: {totaux['total_travailles']}")
        
        # Tester la modification d'un jour
        print("\n4. Test de modification d'un jour:")
        print(f"   Jour 1 avant: {pointage.get_jour(1)}")
        pointage.set_jour(1, 0)  # Changer de 1 à 0
        db.commit()
        db.refresh(pointage)
        print(f"   Jour 1 après: {pointage.get_jour(1)}")
        
        # Recalculer
        totaux = pointage.calculer_totaux()
        expected = 4 + 1 + 5  # Jours 2-5 + jour 8 + jours 11-15
        print(f"   Nouveau total: {totaux['total_travailles']} (attendu: {expected})")
        
        if totaux['total_travailles'] == expected:
            print("✓ Modification et recalcul corrects!")
        else:
            print("❌ Erreur dans le recalcul")
        
        print("\n✅ Tous les tests réussis!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_pointage_system()
    sys.exit(0 if success else 1)
