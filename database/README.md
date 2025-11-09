# Instructions d'installation et de configuration

## Configuration de la base de données MariaDB

### 1. Installer MariaDB
- Télécharger et installer MariaDB depuis: https://mariadb.org/download/
- Ou utiliser XAMPP/WAMP qui inclut MariaDB

### 2. Créer la base de données
Ouvrir un terminal MySQL/MariaDB et exécuter:

```sql
CREATE DATABASE ay_hr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ay_hr_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON ay_hr.* TO 'ay_hr_user'@'localhost';
FLUSH PRIVILEGES;
```

Ou utiliser le script fourni:
```bash
mysql -u root -p < database/init.sql
```

### 3. Configurer les variables d'environnement
Copier le fichier `.env.example` vers `.env` et modifier les paramètres:

```env
DATABASE_URL=mysql+pymysql://root:votre_mot_de_passe@localhost:3306/ay_hr
```

## Installation du backend Python

### 1. Créer un environnement virtuel (recommandé)
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Lancer l'application
```bash
python main.py
```

L'API sera accessible sur: http://localhost:8000
Documentation interactive: http://localhost:8000/docs

## Fichier IRG

Le fichier `irg.xlsx` doit contenir deux colonnes:
- **Colonne A**: Salaire imposable (DA)
- **Colonne B**: Montant IRG correspondant (DA)

Exemple de structure:
```
Salaire    | IRG
-----------|-------
10000      | 0
20000      | 500
30000      | 1500
40000      | 3000
...        | ...
```

Le système utilisera ce fichier pour calculer automatiquement l'IRG lors du calcul des salaires.

## Tests de l'API

### Test avec curl
```bash
# Créer un employé
curl -X POST "http://localhost:8000/api/employes/" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "BENALI",
    "prenom": "Ahmed",
    "date_naissance": "1985-03-15",
    "lieu_naissance": "Alger",
    "adresse": "123 Rue de la République",
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

# Lister les employés
curl "http://localhost:8000/api/employes/"
```

### Test avec l'interface Swagger
Ouvrir http://localhost:8000/docs dans un navigateur pour tester interactivement toutes les routes.
