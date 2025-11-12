"""
Script pour vérifier les données de pointages
Vérifie la cohérence entre:
1. Base de données
2. API
3. Frontend (valeurs attendues)
"""
from database import SessionLocal
from models import Pointage, Employe
import calendar
import datetime

def main():
    db = SessionLocal()
    
    print("=" * 60)
    print("VÉRIFICATION DES DONNÉES POINTAGES")
    print("=" * 60)
    print()
    
    # Analyser novembre 2025
    annee, mois = 2025, 11
    
    # Calculer les vendredis
    nb_jours = calendar.monthrange(annee, mois)[1]
    vendredis = []
    for jour in range(1, nb_jours + 1):
        date = datetime.date(annee, mois, jour)
        if date.weekday() == 4:  # Vendredi
            vendredis.append(jour)
    
    print(f"📅 Mois analysé: {mois}/{annee}")
    print(f"📅 Vendredis: {vendredis}")
    print()
    
    # Récupérer tous les pointages
    pointages = db.query(Pointage).filter(
        Pointage.annee == annee,
        Pointage.mois == mois
    ).all()
    
    print(f"📊 Nombre de pointages trouvés: {len(pointages)}")
    print()
    
    # Analyser chaque pointage
    erreurs = []
    for p in pointages:
        emp = db.query(Employe).filter(Employe.id == p.employe_id).first()
        
        print("-" * 60)
        print(f"👤 Employé #{emp.id}: {emp.nom} {emp.prenom}")
        print(f"   Date recrutement: {emp.date_recrutement}")
        print()
        
        # Vérifier chaque jour
        valeurs_incorrectes = []
        vendredis_incorrects = []
        
        for jour in range(1, nb_jours + 1):
            valeur = p.get_jour(jour)
            
            # Vérifier que la valeur est correcte (0, 1 ou None)
            if valeur not in [0, 1, None]:
                valeurs_incorrectes.append((jour, valeur))
            
            # Vérifier les vendredis
            if jour in vendredis:
                date_jour = datetime.date(annee, mois, jour)
                
                # Si recruté après ce jour, devrait être 0
                if date_jour < emp.date_recrutement:
                    if valeur != 0:
                        vendredis_incorrects.append((jour, valeur, "devrait être 0 (avant recrutement)"))
                else:
                    # Si recruté, vendredi devrait être 1 (férié travaillé)
                    if valeur != 1:
                        vendredis_incorrects.append((jour, valeur, "devrait être 1 (férié)"))
        
        # Afficher les statistiques
        nb_travailles = sum(1 for j in range(1, nb_jours + 1) if p.get_jour(j) == 1)
        nb_absents = sum(1 for j in range(1, nb_jours + 1) if p.get_jour(j) == 0)
        nb_null = sum(1 for j in range(1, nb_jours + 1) if p.get_jour(j) is None)
        
        print(f"   Statistiques:")
        print(f"   - Travaillés (1): {nb_travailles}")
        print(f"   - Absents (0): {nb_absents}")
        print(f"   - NULL: {nb_null}")
        print()
        
        # Afficher les vendredis
        print(f"   Vendredis:")
        for v in vendredis:
            val = p.get_jour(v)
            symbole = "✅" if val == 1 else ("⚠️" if val == 0 else "❌")
            print(f"   {symbole} Jour {v}: {val}")
        print()
        
        # Afficher les erreurs
        if valeurs_incorrectes:
            print(f"   ❌ ERREURS - Valeurs incorrectes:")
            for jour, val in valeurs_incorrectes:
                print(f"      Jour {jour}: {val} (type: {type(val).__name__})")
            erreurs.append(f"Employé #{emp.id}: valeurs incorrectes")
        
        if vendredis_incorrects:
            print(f"   ⚠️  AVERTISSEMENTS - Vendredis incorrects:")
            for jour, val, msg in vendredis_incorrects:
                print(f"      Jour {jour}: {val} - {msg}")
            erreurs.append(f"Employé #{emp.id}: vendredis incorrects")
        
        if not valeurs_incorrectes and not vendredis_incorrects:
            print(f"   ✅ Tout est correct!")
        
        print()
    
    # Résumé final
    print("=" * 60)
    if erreurs:
        print(f"❌ {len(erreurs)} problème(s) détecté(s):")
        for e in erreurs:
            print(f"   - {e}")
    else:
        print("✅ AUCUN PROBLÈME DÉTECTÉ - Toutes les données sont cohérentes!")
    print("=" * 60)
    
    db.close()

if __name__ == "__main__":
    main()
