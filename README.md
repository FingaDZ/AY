# Application de Gestion des Ressources Humaines

## 📋 Description
Application complète de gestion RH avec :
- ✅ Gestion des employés (CRUD complet)
- ✅ Système de pointage mensuel automatisé
- ✅ Gestion des clients et distances
- ✅ Ordres de mission pour chauffeurs avec calcul de primes
- ✅ Gestion des avances salariales
- ✅ Système de crédits avec retenues mensuelles et prorogations
- ✅ Calcul automatique des salaires (cotisable, imposable, net)
- ✅ Génération de rapports PDF/Excel
- ✅ Calcul IRG selon barème personnalisable

## 🚀 Démarrage Rapide

### Option 1 : Script automatique - Backend + Frontend (Recommandé)

**Démarrer toute l'application (Backend + Frontend) :**
```powershell
.\start_all.ps1
```

**Ou séparément :**

Backend seulement :
```powershell
.\start_backend.ps1
```

Frontend seulement :
```powershell
.\start_frontend.ps1
```

### Option 2 : Démarrage manuel

#### Backend
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend
```powershell
cd frontend
npm run dev
```

## 🔗 URLs d'Accès

- **Frontend (Interface utilisateur)** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Documentation API (Swagger)** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Option 3 : Démarrage manuel (Backend seul)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python data\create_irg.py
python main.py
```

**L'API sera accessible sur :**
- 🌐 API : http://localhost:8000
- 📚 Documentation : http://localhost:8000/docs

## 📖 Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Guide d'installation détaillé
- **[GUIDE_UTILISATEUR.md](GUIDE_UTILISATEUR.md)** - Guide d'utilisation complet
- **[database/README.md](database/README.md)** - Configuration de la base de données

## 🛠️ Stack Technique
- **Backend**: FastAPI (Python 3.9+)
- **Base de données**: MariaDB 10.5+
- **ORM**: SQLAlchemy
- **Rapports**: ReportLab (PDF), XlsxWriter (Excel)
- **Validation**: Pydantic

## 📁 Structure du Projet
```
AY HR/
├── backend/
│   ├── main.py              # Point d'entrée de l'application
│   ├── config.py            # Configuration
│   ├── database.py          # Configuration base de données
│   ├── models/              # Modèles SQLAlchemy
│   ├── schemas/             # Schémas Pydantic
│   ├── routers/             # Routes API
│   │   ├── employes.py     # Gestion des employés
│   │   ├── pointages.py    # Système de pointage
│   │   ├── clients.py      # Gestion des clients
│   │   ├── missions.py     # Ordres de mission
│   │   ├── avances.py      # Gestion des avances
│   │   ├── credits.py      # Gestion des crédits
│   │   ├── salaires.py     # Calcul des salaires
│   │   └── rapports.py     # Génération de rapports
│   ├── services/            # Logique métier
│   │   ├── salaire_calculator.py    # Calcul des salaires
│   │   ├── irg_calculator.py        # Calcul IRG
│   │   ├── rapport_generator.py     # Génération PDF
│   │   └── excel_generator.py       # Génération Excel
│   └── data/                # Fichiers de données
│       ├── irg.xlsx         # Barème IRG
│       └── create_irg.py    # Script de création IRG
├── database/
│   ├── init.sql             # Script d'initialisation DB
│   └── README.md            # Documentation DB
├── start.ps1                # Script de démarrage PowerShell
├── start.bat                # Script de démarrage CMD
├── INSTALLATION.md          # Guide d'installation
├── GUIDE_UTILISATEUR.md     # Guide utilisateur
└── README.md                # Ce fichier
```

## 🎯 Fonctionnalités Détaillées

### 1. Gestion des Employés
- Création avec validation complète
- Recherche et filtrage avancés
- Validation automatique des contrats selon dates
- Suivi complet des informations personnelles et professionnelles

### 2. Système de Pointage
- Grille de pointage mensuel (31 jours)
- Types : Travaillé, Absent, Congé, Maladie, Férié, Arrêt
- Calculs automatiques des totaux
- Verrouillage des pointages finalisés
- Copie de pointages entre mois

### 3. Gestion des Clients
- Liste des clients avec distances
- Utilisation pour calcul des primes de déplacement

### 4. Ordres de Mission (Chauffeurs)
- Enregistrement des missions
- Calcul automatique : Distance × Tarif/km
- Totaux mensuels par chauffeur
- Tarif kilométrique paramétrable

### 5. Gestion des Avances
- Enregistrement avec mois de déduction
- Déduction automatique lors du calcul des salaires
- Historique complet

### 6. Gestion des Crédits
- Crédits à long terme
- Calcul automatique des mensualités
- Retenues mensuelles automatiques
- Système de prorogation (report de mensualité)
- Suivi du solde restant
- Statut automatique (En cours / Soldé)

### 7. Calcul des Salaires
**Salaire Cotisable :**
- Salaire de base proratisé selon jours travaillés
- Heures supplémentaires (majoration 50%)
- IN (Indemnité de Nuisance) - 5%
- IFSP - 5%
- IEP (Expérience) - 1% par année
- Prime d'encouragement - 10% si > 1 an
- Prime chauffeur - 100 DA/jour si applicable
- Prime de déplacement (missions)
- Primes objectif et variable

**Retenues :**
- Sécurité Sociale - 9%
- IRG selon barème

**Salaire Net :**
- Salaire imposable - Avances - Crédit + Prime Femme au Foyer

### 8. Génération de Rapports
- **Rapport Pointages** : PDF et Excel
  - Détail par employé
  - Totaux des présences/absences

- **Rapport Salaires** : PDF et Excel
  - Détail complet du calcul
  - Informations employé
  - Totaux généraux

## 🔧 Configuration

### Base de Données
Fichier `.env` :
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/ay_hr
```

### Barème IRG
Le fichier `backend/data/irg.xlsx` contient le barème fiscal :
- Colonne A : Salaire imposable (DA)
- Colonne B : Montant IRG (DA)

Le système effectue une interpolation linéaire entre les valeurs.

## 📊 API Endpoints

### Employés
- `POST /api/employes/` - Créer un employé
- `GET /api/employes/` - Lister les employés
- `GET /api/employes/{id}` - Obtenir un employé
- `PUT /api/employes/{id}` - Modifier un employé
- `DELETE /api/employes/{id}` - Supprimer un employé
- `POST /api/employes/valider-tous-contrats` - Valider tous les contrats

### Pointages
- `POST /api/pointages/` - Créer un pointage
- `GET /api/pointages/` - Lister les pointages
- `PUT /api/pointages/{id}` - Modifier un pointage
- `POST /api/pointages/{id}/verrouiller` - Verrouiller
- `POST /api/pointages/copier` - Copier un pointage
- `GET /api/pointages/employes-actifs` - Employés actifs du mois

### Clients
- `POST /api/clients/` - Créer un client
- `GET /api/clients/` - Lister les clients
- `PUT /api/clients/{id}` - Modifier un client

### Missions
- `POST /api/missions/` - Créer une mission
- `GET /api/missions/` - Lister les missions
- `GET /api/missions/primes-mensuelles` - Primes mensuelles
- `GET /api/missions/parametres/tarif-km` - Obtenir le tarif
- `PUT /api/missions/parametres/tarif-km` - Modifier le tarif

### Avances
- `POST /api/avances/` - Créer une avance
- `GET /api/avances/` - Lister les avances
- `GET /api/avances/total-mensuel` - Total mensuel

### Crédits
- `POST /api/credits/` - Créer un crédit
- `GET /api/credits/` - Lister les crédits
- `POST /api/credits/{id}/prorogation` - Créer une prorogation
- `GET /api/credits/{id}/historique` - Historique complet

### Salaires
- `POST /api/salaires/calculer` - Calculer un salaire
- `POST /api/salaires/calculer-tous` - Calculer tous les salaires
- `GET /api/salaires/rapport/{annee}/{mois}` - Rapport mensuel

### Rapports
- `GET /api/rapports/pointages/pdf` - Rapport pointages PDF
- `GET /api/rapports/pointages/excel` - Rapport pointages Excel
- `GET /api/rapports/salaires/pdf` - Rapport salaires PDF
- `GET /api/rapports/salaires/excel` - Rapport salaires Excel

## 🔐 Sécurité

- Validation des données avec Pydantic
- Protection CORS configurable
- Variables d'environnement pour les secrets
- Validation des contraintes métier

## 🐛 Dépannage

Consultez le fichier [INSTALLATION.md](INSTALLATION.md) pour les problèmes courants.

## 📝 Workflow Mensuel

1. Créer les pointages pour tous les employés actifs
2. Saisir les pointages quotidiennement
3. Enregistrer les missions des chauffeurs
4. Enregistrer les avances accordées
5. Finaliser et verrouiller les pointages en fin de mois
6. Calculer tous les salaires
7. Générer les rapports PDF/Excel
8. Archiver les documents

## 💡 Recommandations

- ✅ Sauvegarder la base de données régulièrement
- ✅ Vérifier le barème IRG annuellement
- ✅ Verrouiller les pointages après validation
- ✅ Archiver les rapports mensuels
- ✅ Tester les calculs sur quelques employés avant le calcul global

## 📞 Support

- Documentation API interactive : http://localhost:8000/docs
- Guide utilisateur : [GUIDE_UTILISATEUR.md](GUIDE_UTILISATEUR.md)
- Guide d'installation : [INSTALLATION.md](INSTALLATION.md)

## 🎓 Licence

Cette application est développée pour un usage interne de gestion RH.

---

**Version** : 1.0.0  
**Dernière mise à jour** : Novembre 2025
