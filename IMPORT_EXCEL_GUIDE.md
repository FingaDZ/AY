# Scripts d'Importation des Données Employés

Ce dossier contient des scripts Python pour importer et mettre à jour les données des employés depuis un fichier Excel.

## Scripts Disponibles

### 1. `import_employes_from_excel.py`
**Fonction**: Importe les employés depuis un fichier Excel et **remplace** toutes les données existantes.

**Colonnes Excel requises** (feuille "LIST DES EMPLOYES"):
- `MAT`: Matricule (non utilisé dans l'import)
- `NOM`: Nom de famille
- `PRENOM`: Prénom
- `N° COMPTE`: Numéro de compte bancaire
- ` NAISSANCE`: Date de naissance
- `SITUATION`: Situation familiale (Marié/Célibataire)
- `LIEU`: Lieu de naissance
- `ADRESSE`: Adresse
- `TELEPHONE`: Téléphone mobile
- `ENTRE`: Date de recrutement
- `SORTIE`: Date de fin de contrat (optionnel)
- `N Sécurité Sociale`: Numéro de sécurité sociale
- `Categorie`: Catégorie du poste
- `POSTE`: Poste de travail
- `FOF`: Femme au foyer (Oui/Non)
- `S Base`: Salaire de base

**⚠️ ATTENTION**: Ce script supprime tous les employés existants et leurs données associées (pointages, avances, crédits, missions, congés).

**Utilisation**:
```bash
# Sur le serveur 192.168.20.53
cd /opt/ay-hr
source backend/.venv/bin/activate
python import_employes_from_excel.py
```

### 2. `update_salaires_from_excel.py`
**Fonction**: Met à jour uniquement les salaires de base des employés existants.

**Colonnes Excel requises**:
- `NOM`: Pour identifier l'employé
- `PRENOM`: Pour identifier l'employé
- `S Base`: Nouveau salaire de base

**Utilisation**:
```bash
# Sur le serveur 192.168.20.53
cd /opt/ay-hr
source backend/.venv/bin/activate
python update_salaires_from_excel.py
```

## Processus d'Importation Complet

### Étape 1: Préparer le fichier Excel
1. Assurez-vous que le fichier Excel est nommé `PLAN SALAIRE OCTOBRE 2025.xlsx`
2. Vérifiez que la feuille "LIST DES EMPLOYES" existe
3. Vérifiez que toutes les colonnes requises sont présentes

### Étape 2: Transférer le fichier sur le serveur
```powershell
# Depuis votre machine locale (Windows)
scp "F:\Code\AY HR\PLAN SALAIRE OCTOBRE 2025.xlsx" root@192.168.20.53:/opt/ay-hr/
```

### Étape 3: Importer les employés
```bash
# Connexion au serveur
ssh root@192.168.20.53

# Exécution du script
cd /opt/ay-hr
source backend/.venv/bin/activate
python import_employes_from_excel.py
# Confirmer "oui" quand demandé
```

### Étape 4: Mettre à jour les salaires (si nécessaire)
```bash
python update_salaires_from_excel.py
```

### Étape 5: Vérifier l'importation
```bash
# Compter les employés
mysql -u ayhr_user -p'!Yara@2014' ay_hr -e 'SELECT COUNT(*) FROM employes;'

# Afficher quelques employés
mysql -u ayhr_user -p'!Yara@2014' ay_hr -e 'SELECT id, nom, prenom, poste_travail, salaire_base FROM employes LIMIT 10;'
```

## Notes Importantes

### Formats de Dates
Les scripts acceptent plusieurs formats de dates:
- `DD/MM/YYYY` (ex: 15/03/1990)
- `YYYY-MM-DD` (ex: 1990-03-15)
- `DD-MM-YYYY` (ex: 15-03-1990)
- Format Excel (nombre de jours depuis 1900-01-01)

### Données Manquantes
- **Date de naissance**: L'employé sera ignoré
- **N° Sécurité Sociale**: Un numéro temporaire sera généré
- **N° Compte Bancaire**: Valeur par défaut "0000000000000000"
- **Téléphone**: Valeur par défaut "0000000000"
- **Lieu/Adresse**: Valeur par défaut "N/A"
- **Poste de travail**: Valeur par défaut "Non spécifié"

### Statut Actif/Inactif
Le statut est déterminé automatiquement:
- Si `SORTIE` (date fin contrat) est dans le passé → Inactif
- Sinon → Actif

### Femme au Foyer
Valeurs acceptées pour "FOF":
- `Oui`, `yes`, `true`, `1`, `x` → True
- Autre ou vide → False

## Dépannage

### Erreur de connexion à la base de données
```
Access denied for user 'ayhr_user'@'localhost'
```
**Solution**: Vérifier le mot de passe dans le fichier `/opt/ay-hr/backend/.env`

### Dates invalides
```
Date de naissance invalide
```
**Solution**: Vérifier le format de la colonne " NAISSANCE" dans Excel

### Employé non trouvé (update_salaires)
```
Employé non trouvé: PRENOM NOM
```
**Solution**: Vérifier que le nom et prénom correspondent exactement (majuscules, espaces)

## Fichiers de Configuration

### Database URL
Les scripts utilisent l'URL de connexion:
```
mysql+pymysql://ayhr_user:%21Yara%402014@localhost/ay_hr
```

Cette configuration doit correspondre au fichier `/opt/ay-hr/backend/.env` sur le serveur.

## Sécurité

⚠️ **Ces scripts sont puissants et peuvent supprimer toutes les données**:
- Toujours faire une sauvegarde de la base de données avant l'importation
- Tester d'abord sur un environnement de développement
- Confirmer manuellement la suppression des données existantes

### Sauvegarde de la base de données
```bash
# Créer une sauvegarde
mysqldump -u ayhr_user -p'!Yara@2014' ay_hr > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurer une sauvegarde
mysql -u ayhr_user -p'!Yara@2014' ay_hr < backup_20251117_123456.sql
```

## Support

Pour toute question ou problème, contactez l'administrateur système.
