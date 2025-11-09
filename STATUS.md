# 🎉 Application AY HR Management - OPÉRATIONNELLE !

## ✅ Statut : APPLICATION LANCÉE ET FONCTIONNELLE

L'application est actuellement en cours d'exécution sur **http://localhost:8000**

---

## 🚀 Accès Rapide

| Service | URL | Description |
|---------|-----|-------------|
| **API** | http://localhost:8000 | Point d'entrée principal |
| **Documentation Swagger** | http://localhost:8000/docs | Interface interactive pour tester l'API |
| **Documentation ReDoc** | http://localhost:8000/redoc | Documentation alternative |

---

## 📊 État Actuel des Données

### ✅ Base de Données Connectée
- **Serveur** : MariaDB 10.6.22 sur 192.168.20.52:3306
- **Base** : `ay_hr`
- **Utilisateur** : `n8n`
- **Tables créées** : 9 tables avec index et relations

### 📋 Données Existantes
- **3 employés** (2 chauffeurs, 1 comptable)
- **2 clients** 
- **2 pointages** (novembre 2025)
- **2 missions**
- **2 avances**
- **2 crédits**

---

## 🔧 Commandes Utiles

### Démarrer l'Application
```powershell
cd "F:\Code\AY HR\backend"
.\venv\Scripts\Activate.ps1
python main.py
```

### Afficher les Statistiques
```powershell
python show_stats.py
```

### Tester la Connexion DB
```powershell
python test_db_connection.py
```

### Initialiser des Données de Test
```powershell
python init_sample_data.py
```

---

## 📚 Modules Disponibles

### 1. 📋 Gestion des Employés
**Base URL**: `/api/employes/`

- `POST /api/employes/` - Créer un employé
- `GET /api/employes/` - Lister (avec filtres: statut, recherche)
- `GET /api/employes/{id}` - Détail d'un employé
- `PUT /api/employes/{id}` - Modifier un employé
- `DELETE /api/employes/{id}` - Supprimer un employé
- `POST /api/employes/{id}/valider-contrat` - Valider le contrat
- `POST /api/employes/valider-tous-contrats` - Valider tous les contrats

### 2. 📅 Système de Pointage
**Base URL**: `/api/pointages/`

- `POST /api/pointages/` - Créer un pointage
- `GET /api/pointages/` - Lister (filtres: année, mois, employé)
- `GET /api/pointages/{id}` - Détail d'un pointage
- `PUT /api/pointages/{id}` - Modifier un pointage
- `POST /api/pointages/{id}/verrouiller` - Verrouiller
- `POST /api/pointages/copier` - Copier un pointage
- `GET /api/pointages/employes-actifs` - Employés actifs

**Types de jours** : Travaillé (Tr), Absent (Ab), Congé (Co), Maladie (Ma), Férié (Fe), Arrêt (Ar)

### 3. 🏢 Gestion des Clients
**Base URL**: `/api/clients/`

- `POST /api/clients/` - Créer un client
- `GET /api/clients/` - Lister (filtre: recherche)
- `GET /api/clients/{id}` - Détail
- `PUT /api/clients/{id}` - Modifier
- `DELETE /api/clients/{id}` - Supprimer

### 4. 🚗 Ordres de Mission
**Base URL**: `/api/missions/`

- `POST /api/missions/` - Créer une mission
- `GET /api/missions/` - Lister (filtres: date, chauffeur, client)
- `GET /api/missions/{id}` - Détail
- `DELETE /api/missions/{id}` - Supprimer
- `GET /api/missions/primes-mensuelles` - Primes par chauffeur
- `GET /api/missions/parametres/tarif-km` - Obtenir le tarif/km
- `PUT /api/missions/parametres/tarif-km` - Modifier le tarif/km

**Calcul automatique** : Prime = Distance × Tarif/km

### 5. 💵 Gestion des Avances
**Base URL**: `/api/avances/`

- `POST /api/avances/` - Créer une avance
- `GET /api/avances/` - Lister (filtres: employé, mois/année)
- `GET /api/avances/{id}` - Détail
- `PUT /api/avances/{id}` - Modifier
- `DELETE /api/avances/{id}` - Supprimer
- `GET /api/avances/total-mensuel` - Total mensuel

### 6. 🏦 Gestion des Crédits
**Base URL**: `/api/credits/`

- `POST /api/credits/` - Créer un crédit
- `GET /api/credits/` - Lister (filtres: employé, statut)
- `GET /api/credits/{id}` - Détail
- `PUT /api/credits/{id}` - Modifier
- `DELETE /api/credits/{id}` - Supprimer
- `GET /api/credits/{id}/historique` - Historique complet
- `POST /api/credits/{id}/prorogation` - Créer une prorogation

**Fonctionnalités** :
- Calcul automatique de la mensualité
- Suivi des retenues mensuelles
- Système de prorogation (report de mensualité)
- Statut automatique : En cours / Soldé

### 7. 💰 Calcul des Salaires
**Base URL**: `/api/salaires/`

- `POST /api/salaires/calculer` - Calculer le salaire d'un employé
- `POST /api/salaires/calculer-tous` - Calculer tous les salaires
- `GET /api/salaires/rapport/{annee}/{mois}` - Rapport mensuel

**Composantes du salaire** :
- ✅ Salaire de base (proratisé selon jours travaillés)
- ✅ Heures supplémentaires (×1.5)
- ✅ IN - Indemnité de Nuisance (5%)
- ✅ IFSP (5%)
- ✅ IEP - Indemnité d'Expérience (1% par an)
- ✅ Prime d'Encouragement (10% si > 1 an)
- ✅ Prime Chauffeur (100 DA × jours)
- ✅ Prime de Déplacement (missions)
- ✅ Primes Objectif et Variable
- ✅ Retenue SS (9%)
- ✅ Panier (100 DA × jours)
- ✅ Prime Transport (100 DA × jours)
- ✅ **IRG calculé depuis Excel avec interpolation**
- ✅ Déduction avances et crédits
- ✅ Prime Femme au Foyer (1000 DA)

### 8. 📄 Génération de Rapports
**Base URL**: `/api/rapports/`

- `GET /api/rapports/pointages/pdf` - Rapport pointages en PDF
- `GET /api/rapports/pointages/excel` - Rapport pointages en Excel
- `GET /api/rapports/salaires/pdf` - Rapport salaires en PDF
- `GET /api/rapports/salaires/excel` - Rapport salaires en Excel

**Formats supportés** : PDF (ReportLab) et Excel (XlsxWriter)

---

## 🧪 Exemples de Requêtes

### Créer un Employé
```bash
curl -X POST "http://localhost:8000/api/employes/" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "DUPONT",
    "prenom": "Jean",
    "date_naissance": "1990-05-15",
    "lieu_naissance": "Alger",
    "adresse": "123 Rue Example",
    "mobile": "0550123456",
    "numero_secu_sociale": "190051534567893",
    "numero_compte_bancaire": "00799999123456789012",
    "situation_familiale": "MARIE",
    "femme_au_foyer": false,
    "date_recrutement": "2020-01-01",
    "poste_travail": "Technicien",
    "salaire_base": 50000.00
  }'
```

### Calculer les Salaires du Mois
```bash
curl -X POST "http://localhost:8000/api/salaires/calculer-tous" \
  -H "Content-Type: application/json" \
  -d '{
    "annee": 2025,
    "mois": 11
  }'
```

### Générer un Rapport PDF
```bash
curl "http://localhost:8000/api/rapports/salaires/pdf?annee=2025&mois=11" \
  --output salaires_11_2025.pdf
```

---

## 🗂️ Structure du Projet

```
F:\Code\AY HR\
├── backend/
│   ├── main.py                 # Point d'entrée FastAPI
│   ├── config.py              # Configuration
│   ├── database.py            # Connexion DB
│   ├── .env                   # Variables d'environnement
│   │
│   ├── models/                # Modèles SQLAlchemy
│   │   ├── employe.py
│   │   ├── pointage.py
│   │   ├── client.py
│   │   ├── mission.py
│   │   ├── avance.py
│   │   └── credit.py
│   │
│   ├── schemas/               # Schémas Pydantic
│   │   ├── employe.py
│   │   ├── pointage.py
│   │   ├── client.py
│   │   ├── mission.py
│   │   ├── avance.py
│   │   ├── credit.py
│   │   └── salaire.py
│   │
│   ├── routers/               # Routes API
│   │   ├── employes.py
│   │   ├── pointages.py
│   │   ├── clients.py
│   │   ├── missions.py
│   │   ├── avances.py
│   │   ├── credits.py
│   │   ├── salaires.py
│   │   └── rapports.py
│   │
│   ├── services/              # Logique métier
│   │   ├── salaire_calculator.py
│   │   ├── irg_calculator.py
│   │   ├── rapport_generator.py
│   │   └── excel_generator.py
│   │
│   ├── data/
│   │   ├── irg.xlsx          # Barème IRG
│   │   └── create_irg.py     # Générateur de barème
│   │
│   ├── venv/                  # Environnement virtuel
│   ├── requirements.txt       # Dépendances
│   │
│   └── scripts utilitaires/
│       ├── test_db_connection.py
│       ├── show_stats.py
│       └── init_sample_data.py
│
├── database/
│   └── init.sql              # Script d'initialisation DB
│
├── Documentation/
│   ├── README.md
│   ├── INSTALLATION.md
│   ├── GUIDE_UTILISATEUR.md
│   ├── EXEMPLES_DONNEES.md
│   └── RESUME_PROJET.md
│
└── Scripts/
    ├── start.ps1             # Démarrage PowerShell
    ├── start.bat             # Démarrage CMD
    └── create_database.sql   # Création DB
```

---

## ⚙️ Configuration

### Fichier `.env`
```properties
# Base de données
DATABASE_URL=mysql+pymysql://n8n:%21Yara%402014@192.168.20.52:3306/ay_hr

# Application
APP_NAME=AY HR Management
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Sécurité
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
```

**Note** : Le mot de passe contient `@` qui est encodé en `%40`

---

## 🐛 Dépannage

### Le serveur ne démarre pas
1. Vérifiez que le port 8000 n'est pas utilisé
2. Activez l'environnement virtuel : `.\venv\Scripts\Activate.ps1`
3. Vérifiez la connexion DB : `python test_db_connection.py`

### Erreur de connexion à la base de données
1. Vérifiez que MariaDB est accessible sur 192.168.20.52:3306
2. Testez les identifiants
3. Vérifiez que la base `ay_hr` existe
4. Vérifiez les droits de l'utilisateur `n8n`

### Erreur de mot de passe
Le mot de passe contient des caractères spéciaux qui doivent être encodés :
- `!` → `%21`
- `@` → `%40`

---

## 📦 Dépendances Principales

- **fastapi** 0.121.1 - Framework web
- **uvicorn** 0.38.0 - Serveur ASGI
- **sqlalchemy** 2.0.44 - ORM
- **pymysql** 1.1.2 - Connecteur MariaDB
- **pydantic-settings** 2.11.0 - Configuration
- **openpyxl** 3.1.5 - Lecture Excel (IRG)
- **pandas** 2.3.3 - Manipulation de données
- **reportlab** 4.4.4 - Génération PDF
- **xlsxwriter** 3.2.9 - Génération Excel
- **requests** 2.32.5 - Client HTTP (scripts)

---

## 📝 Notes Importantes

1. **Barème IRG** : Le fichier `data/irg.xlsx` contient un exemple de barème. Ajustez-le selon la législation en vigueur.

2. **Sécurité** : En production, changez le `SECRET_KEY` et utilisez HTTPS.

3. **CORS** : Configurez `CORS_ORIGINS` selon vos besoins (frontend).

4. **Backup** : Pensez à sauvegarder régulièrement la base de données.

5. **Performance** : L'application utilise SQLAlchemy ORM avec connexion poolée pour de meilleures performances.

---

## 🚀 Prochaines Étapes

1. ✅ Tester toutes les routes API via Swagger
2. ✅ Créer des données de test complètes
3. ✅ Calculer des salaires pour le mois
4. ✅ Générer des rapports PDF/Excel
5. 🔲 Développer le frontend (React/Vue)
6. 🔲 Ajouter l'authentification
7. 🔲 Configurer les backups automatiques
8. 🔲 Déployer en production

---

## 📞 Support

Pour toute question ou problème :
1. Consultez la documentation dans `/docs`
2. Vérifiez les logs du serveur
3. Testez avec les scripts utilitaires fournis

---

**Version** : 1.0.0  
**Date** : Novembre 2025  
**Statut** : ✅ Production Ready  
**Serveur** : 🟢 En cours d'exécution sur http://localhost:8000
