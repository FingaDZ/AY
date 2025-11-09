#!/usr/bin/env python
"""Script d'initialisation avec des données d'exemple pour tester l'application"""

import requests
from datetime import date, timedelta
import sys

BASE_URL = "http://localhost:8000/api"

def test_api():
    """Vérifie que l'API est accessible"""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ API accessible")
            return True
        else:
            print(f"❌ API retourne le code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Impossible de contacter l'API: {e}")
        print("   Assurez-vous que le serveur est démarré (python main.py)")
        return False

def create_employes():
    """Crée des employés de test"""
    print("\n📋 Création des employés...")
    
    employes = [
        {
            "nom": "BENALI",
            "prenom": "Ahmed",
            "date_naissance": "1985-03-15",
            "lieu_naissance": "Alger",
            "adresse": "Rue de la Liberté, Bab Ezzouar, Alger",
            "mobile": "0555123456",
            "numero_secu_sociale": "185031234567890",
            "numero_compte_bancaire": "00799999012345678901",
            "situation_familiale": "MARIE",
            "femme_au_foyer": True,
            "date_recrutement": "2015-01-10",
            "date_fin_contrat": None,
            "poste_travail": "Chauffeur",
            "salaire_base": 40000.00
        },
        {
            "nom": "KACI",
            "prenom": "Fatima",
            "date_naissance": "1990-07-20",
            "lieu_naissance": "Oran",
            "adresse": "Cité des 1000 logements, Oran",
            "mobile": "0661234567",
            "numero_secu_sociale": "290072034567891",
            "numero_compte_bancaire": "00799999098765432109",
            "situation_familiale": "CELIBATAIRE",
            "femme_au_foyer": False,
            "date_recrutement": "2018-05-15",
            "date_fin_contrat": None,
            "poste_travail": "Comptable",
            "salaire_base": 45000.00
        },
        {
            "nom": "HAMZA",
            "prenom": "Mohamed",
            "date_naissance": "1988-11-30",
            "lieu_naissance": "Constantine",
            "adresse": "Résidence El Amir, Constantine",
            "mobile": "0771234567",
            "numero_secu_sociale": "188113034567892",
            "numero_compte_bancaire": "00799999055555555555",
            "situation_familiale": "MARIE",
            "femme_au_foyer": False,
            "date_recrutement": "2016-09-01",
            "date_fin_contrat": None,
            "poste_travail": "Chauffeur",
            "salaire_base": 38000.00
        }
    ]
    
    employes_crees = []
    for emp in employes:
        try:
            response = requests.post(f"{BASE_URL}/employes/", json=emp)
            if response.status_code == 200:
                employe_id = response.json()["id"]
                employes_crees.append(employe_id)
                print(f"   ✅ {emp['prenom']} {emp['nom']} (ID: {employe_id})")
            else:
                print(f"   ❌ Erreur pour {emp['prenom']} {emp['nom']}: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception pour {emp['prenom']} {emp['nom']}: {e}")
    
    return employes_crees

def create_clients():
    """Crée des clients de test"""
    print("\n🏢 Création des clients...")
    
    clients = [
        {"nom": "SARL", "prenom": "Transport Express", "distance": 45.5, "telephone": "021234567"},
        {"nom": "EURL", "prenom": "Logistique Plus", "distance": 32.0, "telephone": "021345678"},
        {"nom": "SPA", "prenom": "Distribution Nationale", "distance": 78.3, "telephone": "021456789"}
    ]
    
    clients_crees = []
    for client in clients:
        try:
            response = requests.post(f"{BASE_URL}/clients/", json=client)
            if response.status_code == 200:
                client_id = response.json()["id"]
                clients_crees.append(client_id)
                print(f"   ✅ {client['prenom']} {client['nom']} (ID: {client_id})")
            else:
                print(f"   ❌ Erreur pour {client['prenom']}: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception pour {client['prenom']}: {e}")
    
    return clients_crees

def set_tarif_km():
    """Configure le tarif kilométrique"""
    print("\n💰 Configuration du tarif kilométrique...")
    
    try:
        response = requests.put(f"{BASE_URL}/missions/parametres/tarif-km?nouveau_tarif=15.50")
        if response.status_code == 200:
            print(f"   ✅ Tarif configuré: 15.50 DA/km")
            return True
        else:
            print(f"   ❌ Erreur: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def create_pointage(employe_id, annee=2025, mois=11):
    """Crée un pointage pour un employé"""
    pointage = {
        "employe_id": employe_id,
        "annee": annee,
        "mois": mois,
        "jour_01": "TRAVAILLE", "jour_02": "TRAVAILLE", "jour_03": "TRAVAILLE",
        "jour_04": "TRAVAILLE", "jour_05": "TRAVAILLE", "jour_06": "TRAVAILLE",
        "jour_07": "TRAVAILLE", "jour_08": "TRAVAILLE", "jour_09": "TRAVAILLE",
        "jour_10": "TRAVAILLE", "jour_11": "TRAVAILLE", "jour_12": "TRAVAILLE",
        "jour_13": "TRAVAILLE", "jour_14": "TRAVAILLE", "jour_15": "TRAVAILLE",
        "jour_16": "TRAVAILLE", "jour_17": "TRAVAILLE", "jour_18": "CONGE",
        "jour_19": "TRAVAILLE", "jour_20": "TRAVAILLE", "jour_21": "TRAVAILLE",
        "jour_22": "TRAVAILLE", "jour_23": "TRAVAILLE", "jour_24": "TRAVAILLE",
        "jour_25": "TRAVAILLE", "jour_26": "TRAVAILLE", "jour_27": "TRAVAILLE",
        "jour_28": "TRAVAILLE", "jour_29": "TRAVAILLE", "jour_30": "TRAVAILLE",
        "jour_31": None
    }
    
    try:
        response = requests.post(f"{BASE_URL}/pointages/", json=pointage)
        if response.status_code == 200:
            return response.json()["id"]
        else:
            print(f"   ⚠️  Pointage déjà existant ou erreur")
            return None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def create_pointages(employes_ids):
    """Crée les pointages pour tous les employés"""
    print("\n📅 Création des pointages novembre 2025...")
    
    for emp_id in employes_ids:
        pointage_id = create_pointage(emp_id)
        if pointage_id:
            print(f"   ✅ Pointage créé pour employé {emp_id} (ID: {pointage_id})")

def create_missions(employes_ids, clients_ids):
    """Crée des missions de test"""
    print("\n🚗 Création des missions...")
    
    if len(employes_ids) == 0 or len(clients_ids) == 0:
        print("   ⚠️  Pas d'employés ou clients disponibles")
        return
    
    missions = [
        {"date_mission": "2025-11-05", "chauffeur_id": employes_ids[0], "client_id": clients_ids[0]},
        {"date_mission": "2025-11-06", "chauffeur_id": employes_ids[0], "client_id": clients_ids[1]},
        {"date_mission": "2025-11-07", "chauffeur_id": employes_ids[2], "client_id": clients_ids[2]},
    ]
    
    for mission in missions:
        try:
            response = requests.post(f"{BASE_URL}/missions/", json=mission)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Mission ID {data['id']} - Prime: {data['prime_calculee']} DA")
            else:
                print(f"   ❌ Erreur: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def create_avances(employes_ids):
    """Crée des avances de test"""
    print("\n💵 Création des avances...")
    
    if len(employes_ids) == 0:
        print("   ⚠️  Pas d'employés disponibles")
        return
    
    avances = [
        {
            "employe_id": employes_ids[0],
            "date_avance": "2025-11-03",
            "montant": 5000.00,
            "mois_deduction": 11,
            "annee_deduction": 2025,
            "motif": "Urgence familiale"
        }
    ]
    
    for avance in avances:
        try:
            response = requests.post(f"{BASE_URL}/avances/", json=avance)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Avance ID {data['id']} - {data['montant']} DA")
            else:
                print(f"   ❌ Erreur: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def create_credits(employes_ids):
    """Crée des crédits de test"""
    print("\n🏦 Création des crédits...")
    
    if len(employes_ids) == 0:
        print("   ⚠️  Pas d'employés disponibles")
        return
    
    credits = [
        {
            "employe_id": employes_ids[1],
            "date_octroi": "2025-11-01",
            "montant_total": 100000.00,
            "nombre_mensualites": 10
        }
    ]
    
    for credit in credits:
        try:
            response = requests.post(f"{BASE_URL}/credits/", json=credit)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Crédit ID {data['id']} - {data['montant_total']} DA sur {data['nombre_mensualites']} mois")
                print(f"      Mensualité: {data['montant_mensualite']} DA")
            else:
                print(f"   ❌ Erreur: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def main():
    """Fonction principale"""
    print("="*60)
    print("🚀 Initialisation des données de test - AY HR Management")
    print("="*60)
    
    # Vérifier que l'API est accessible
    if not test_api():
        sys.exit(1)
    
    # Créer les données de test
    employes_ids = create_employes()
    clients_ids = create_clients()
    set_tarif_km()
    create_pointages(employes_ids)
    create_missions(employes_ids, clients_ids)
    create_avances(employes_ids)
    create_credits(employes_ids)
    
    print("\n" + "="*60)
    print("✅ Initialisation terminée avec succès !")
    print("="*60)
    print("\n📚 Prochaines étapes:")
    print("   1. Accédez à http://localhost:8000/docs")
    print("   2. Testez les différentes routes API")
    print("   3. Calculez les salaires: POST /api/salaires/calculer-tous")
    print("   4. Générez des rapports: GET /api/rapports/...")
    print()

if __name__ == "__main__":
    main()
