# Guide d'Installation - Application de Gestion RH AY HR

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python 3.9 ou supérieur** : [Télécharger Python](https://www.python.org/downloads/)
- **MariaDB 10.5 ou supérieur** : [Télécharger MariaDB](https://mariadb.org/download/)
  - Alternative : XAMPP (inclut MariaDB) : [Télécharger XAMPP](https://www.apachefriends.org/)
- **Git** (optionnel) : [Télécharger Git](https://git-scm.com/downloads/)

## 🚀 Installation Pas à Pas

### Étape 1 : Configuration de la Base de Données

#### Option A : Avec MariaDB standalone

1. Ouvrir le client MariaDB (ou MySQL Workbench)
2. Exécuter les commandes suivantes :

```sql
CREATE DATABASE ay_hr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ay_hr_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON ay_hr.* TO 'ay_hr_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Option B : Avec XAMPP

1. Démarrer XAMPP
2. Démarrer les services MySQL/Apache
3. Ouvrir phpMyAdmin : http://localhost/phpmyadmin
4. Créer une nouvelle base de données nommée `ay_hr`
5. Sélectionner l'encodage `utf8mb4_unicode_ci`

### Étape 2 : Installation du Backend Python

1. **Naviguer vers le dossier backend**

```powershell
cd "F:\Code\AY HR\backend"
```

2. **Créer un environnement virtuel Python** (recommandé)

```powershell
python -m venv venv
```

3. **Activer l'environnement virtuel**

```powershell
.\venv\Scripts\activate
```

Vous devriez voir `(venv)` apparaître dans votre terminal.

4. **Installer les dépendances**

```powershell
pip install -r requirements.txt
```

⏳ Cette étape peut prendre quelques minutes.

5. **Configurer les variables d'environnement**

Ouvrir le fichier `backend\.env` et modifier les paramètres :

```env
# Si vous utilisez XAMPP (par défaut, pas de mot de passe)
DATABASE_URL=mysql+pymysql://root:@localhost:3306/ay_hr

# Si vous avez créé un utilisateur spécifique
DATABASE_URL=mysql+pymysql://ay_hr_user:votre_mot_de_passe@localhost:3306/ay_hr
```

6. **Créer le fichier IRG**

```powershell
cd data
python create_irg.py
cd ..
```

Ce script crée le fichier `irg.xlsx` avec un barème par défaut.

⚠️ **IMPORTANT** : Ouvrez le fichier `data\irg.xlsx` et vérifiez/ajustez le barème IRG selon la législation en vigueur.

### Étape 3 : Démarrer l'Application

1. **Lancer le serveur API**

```powershell
# Assurez-vous d'être dans le dossier backend avec l'environnement virtuel activé
python main.py
```

2. **Vérifier que l'API fonctionne**

Ouvrir un navigateur et aller sur :
- API : http://localhost:8000
- Documentation interactive : http://localhost:8000/docs

Vous devriez voir la documentation Swagger de l'API.

## 📊 Utilisation de l'API

### Accéder à la documentation

L'API dispose d'une documentation interactive complète accessible via :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Tester l'API

Vous pouvez tester l'API directement depuis l'interface Swagger :

1. Ouvrir http://localhost:8000/docs
2. Cliquer sur une route (par exemple `/api/employes/`)
3. Cliquer sur "Try it out"
4. Remplir les paramètres nécessaires
5. Cliquer sur "Execute"

### Exemples de requêtes

#### Créer un employé

```powershell
curl -X POST "http://localhost:8000/api/employes/" -H "Content-Type: application/json" -d '{
  "nom": "BENALI",
  "prenom": "Ahmed",
  "date_naissance": "1985-03-15",
  "lieu_naissance": "Alger",
  "adresse": "123 Rue de la République, Alger",
  "mobile": "0555123456",
  "numero_secu_sociale": "198503123456789",
  "numero_compte_bancaire": "CCP1234567890",
  "situation_familiale": "Marié",
  "femme_au_foyer": false,
  "date_recrutement": "2020-01-01",
  "poste_travail": "Chauffeur",
  "salaire_base": 30000,
  "statut_contrat": "Actif"
}'
```

#### Lister les employés

```powershell
curl "http://localhost:8000/api/employes/"
```

## 🔧 Configuration Avancée

### Modifier le port du serveur

Par défaut, l'API écoute sur le port 8000. Pour changer :

1. Ouvrir `backend\main.py`
2. Modifier la ligne :
```python
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
```

### Activer/Désactiver le mode Debug

Dans le fichier `.env` :
```env
DEBUG=True   # Mode développement (rechargement automatique)
DEBUG=False  # Mode production
```

## 📝 Structure de l'Application

```
AY HR/
├── backend/
│   ├── main.py              # Point d'entrée de l'application
│   ├── config.py            # Configuration
│   ├── database.py          # Configuration base de données
│   ├── models/              # Modèles de données
│   ├── schemas/             # Schémas de validation
│   ├── routers/             # Routes API
│   ├── services/            # Logique métier
│   └── data/                # Fichiers de données (IRG)
├── database/
│   ├── init.sql             # Script d'initialisation
│   └── README.md            # Documentation DB
└── README.md                # Ce fichier
```

## 🔐 Sécurité

### Changer la clé secrète

Dans le fichier `.env`, modifier :
```env
SECRET_KEY=votre-nouvelle-cle-secrete-tres-longue-et-aleatoire
```

Pour générer une clé secrète sécurisée :
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🐛 Dépannage

### Erreur de connexion à la base de données

**Symptôme** : `Can't connect to MySQL server`

**Solution** :
1. Vérifier que MariaDB/MySQL est démarré
2. Vérifier les identifiants dans `.env`
3. Tester la connexion :
```powershell
mysql -u root -p -h localhost ay_hr
```

### Erreur d'import Python

**Symptôme** : `ModuleNotFoundError: No module named 'xxx'`

**Solution** :
```powershell
pip install -r requirements.txt
```

### Port 8000 déjà utilisé

**Solution** : Modifier le port dans `main.py` ou arrêter l'application qui utilise le port 8000

### Erreur IRG

**Symptôme** : Calculs de salaire incorrects

**Solution** :
1. Vérifier que le fichier `backend/data/irg.xlsx` existe
2. Vérifier la structure du fichier (2 colonnes : Salaire, IRG)
3. Recréer le fichier : `python data/create_irg.py`

## 📞 Support

Pour toute question ou problème :
1. Consulter la documentation API : http://localhost:8000/docs
2. Vérifier les logs dans le terminal
3. Consulter les fichiers README dans chaque dossier

## 🎯 Prochaines Étapes

Une fois l'installation terminée, vous pouvez :

1. ✅ Créer des employés
2. ✅ Créer des clients
3. ✅ Saisir des pointages mensuels
4. ✅ Enregistrer des missions (chauffeurs)
5. ✅ Gérer les avances et crédits
6. ✅ Calculer les salaires
7. ✅ Générer des rapports PDF/Excel

Consultez la documentation API pour découvrir toutes les fonctionnalités disponibles !
