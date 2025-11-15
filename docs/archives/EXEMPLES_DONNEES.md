# Exemples de Données de Test - AY HR

Ce fichier contient des exemples de données pour tester l'application.

## 🔄 Importer les données de test

### Option 1 : Via l'interface Swagger (http://localhost:8000/docs)

### Option 2 : Via PowerShell/CMD avec curl

## 👥 Employés

### Employé 1 - Chauffeur
```json
{
  "nom": "BENALI",
  "prenom": "Ahmed",
  "date_naissance": "1985-03-15",
  "lieu_naissance": "Alger",
  "adresse": "123 Rue de la République, Alger",
  "mobile": "0555123456",
  "numero_secu_sociale": "198503123456789",
  "numero_compte_bancaire": "CCP1234567890",
  "situation_familiale": "Marié",
  "femme_au_foyer": true,
  "date_recrutement": "2020-01-01",
  "poste_travail": "Chauffeur",
  "salaire_base": 30000,
  "statut_contrat": "Actif"
}
```

### Employé 2 - Comptable
```json
{
  "nom": "KACI",
  "prenom": "Fatima",
  "date_naissance": "1990-07-22",
  "lieu_naissance": "Oran",
  "adresse": "456 Boulevard Zabana, Oran",
  "mobile": "0661234567",
  "numero_secu_sociale": "199007223456789",
  "numero_compte_bancaire": "00799123456789012",
  "situation_familiale": "Célibataire",
  "femme_au_foyer": false,
  "date_recrutement": "2021-06-15",
  "poste_travail": "Comptable",
  "salaire_base": 35000,
  "statut_contrat": "Actif"
}
```

### Employé 3 - Responsable RH
```json
{
  "nom": "HAMIDI",
  "prenom": "Mohamed",
  "date_naissance": "1988-11-10",
  "lieu_naissance": "Constantine",
  "adresse": "789 Avenue Didouche, Constantine",
  "mobile": "0770123456",
  "numero_secu_sociale": "198811103456789",
  "numero_compte_bancaire": "CCP9876543210",
  "situation_familiale": "Marié",
  "femme_au_foyer": true,
  "date_recrutement": "2019-03-01",
  "poste_travail": "Responsable RH",
  "salaire_base": 45000,
  "statut_contrat": "Actif"
}
```

## 👤 Clients

### Client 1
```json
{
  "nom": "SAIDI",
  "prenom": "Rachid",
  "distance": 25.5,
  "telephone": "0555987654"
}
```

### Client 2
```json
{
  "nom": "BOUZID",
  "prenom": "Samira",
  "distance": 50.0,
  "telephone": "0661876543"
}
```

### Client 3
```json
{
  "nom": "MAMMERI",
  "prenom": "Karim",
  "distance": 15.0,
  "telephone": "0770456789"
}
```

## 📝 Pointages

### Pointage pour Employé 1 - Novembre 2024
```json
{
  "employe_id": 1,
  "annee": 2024,
  "mois": 11
}
```

Puis mettre à jour avec :
```json
{
  "jours": {
    "1": "Co",
    "2": "Co",
    "3": "Co",
    "4": "Tr",
    "5": "Tr",
    "6": "Tr",
    "7": "Tr",
    "8": "Tr",
    "9": "Co",
    "10": "Co",
    "11": "Tr",
    "12": "Tr",
    "13": "Tr",
    "14": "Tr",
    "15": "Tr",
    "16": "Co",
    "17": "Co",
    "18": "Tr",
    "19": "Tr",
    "20": "Tr",
    "21": "Tr",
    "22": "Tr",
    "23": "Co",
    "24": "Co",
    "25": "Tr",
    "26": "Tr",
    "27": "Tr",
    "28": "Tr",
    "29": "Tr",
    "30": "Co"
  }
}
```

## 🚗 Missions (Ordres de Mission)

### Mission 1 - Chauffeur 1 vers Client 1
```json
{
  "date_mission": "2024-11-05",
  "chauffeur_id": 1,
  "client_id": 1
}
```

### Mission 2 - Chauffeur 1 vers Client 2
```json
{
  "date_mission": "2024-11-12",
  "chauffeur_id": 1,
  "client_id": 2
}
```

### Mission 3 - Chauffeur 1 vers Client 3
```json
{
  "date_mission": "2024-11-18",
  "chauffeur_id": 1,
  "client_id": 3
}
```

## 💰 Avances

### Avance 1 - Employé 1
```json
{
  "employe_id": 1,
  "date_avance": "2024-11-10",
  "montant": 5000,
  "mois_deduction": 11,
  "annee_deduction": 2024,
  "motif": "Avance pour urgence familiale"
}
```

### Avance 2 - Employé 2
```json
{
  "employe_id": 2,
  "date_avance": "2024-11-15",
  "montant": 3000,
  "mois_deduction": 11,
  "annee_deduction": 2024,
  "motif": "Avance exceptionnelle"
}
```

## 🏦 Crédits

### Crédit 1 - Employé 3
```json
{
  "employe_id": 3,
  "date_octroi": "2024-01-15",
  "montant_total": 120000,
  "nombre_mensualites": 12
}
```

### Crédit 2 - Employé 1
```json
{
  "employe_id": 1,
  "date_octroi": "2024-06-01",
  "montant_total": 60000,
  "nombre_mensualites": 6
}
```

## 📊 Calcul de Salaire

### Calculer le salaire de l'Employé 1 pour Novembre 2024
```json
{
  "employe_id": 1,
  "annee": 2024,
  "mois": 11,
  "jours_supplementaires": 2,
  "prime_objectif": 1000,
  "prime_variable": 500
}
```

### Calculer tous les salaires pour Novembre 2024
```
POST /api/salaires/calculer-tous?annee=2024&mois=11&jours_supplementaires=0
```

## 🔧 Paramètres

### Définir le tarif kilométrique
```json
{
  "valeur": "3.50",
  "description": "Tarif kilométrique pour les missions (DA/km)"
}
```

## 📋 Script PowerShell Complet

```powershell
# URL de l'API
$apiUrl = "http://localhost:8000/api"

# Fonction pour faire une requête POST
function Post-Data {
    param($endpoint, $data)
    $json = $data | ConvertTo-Json -Depth 10
    Invoke-RestMethod -Uri "$apiUrl$endpoint" -Method Post -Body $json -ContentType "application/json"
}

# 1. Créer les employés
Write-Host "Création des employés..." -ForegroundColor Yellow
$employe1 = Post-Data "/employes/" @{
    nom = "BENALI"
    prenom = "Ahmed"
    date_naissance = "1985-03-15"
    lieu_naissance = "Alger"
    adresse = "123 Rue de la République, Alger"
    mobile = "0555123456"
    numero_secu_sociale = "198503123456789"
    numero_compte_bancaire = "CCP1234567890"
    situation_familiale = "Marié"
    femme_au_foyer = $true
    date_recrutement = "2020-01-01"
    poste_travail = "Chauffeur"
    salaire_base = 30000
    statut_contrat = "Actif"
}
Write-Host "✓ Employé 1 créé (ID: $($employe1.id))" -ForegroundColor Green

# 2. Créer les clients
Write-Host "Création des clients..." -ForegroundColor Yellow
$client1 = Post-Data "/clients/" @{
    nom = "SAIDI"
    prenom = "Rachid"
    distance = 25.5
    telephone = "0555987654"
}
Write-Host "✓ Client 1 créé (ID: $($client1.id))" -ForegroundColor Green

# 3. Créer un pointage
Write-Host "Création du pointage..." -ForegroundColor Yellow
$pointage = Post-Data "/pointages/" @{
    employe_id = $employe1.id
    annee = 2024
    mois = 11
}
Write-Host "✓ Pointage créé (ID: $($pointage.id))" -ForegroundColor Green

# 4. Créer une mission
Write-Host "Création d'une mission..." -ForegroundColor Yellow
$mission = Post-Data "/missions/" @{
    date_mission = "2024-11-05"
    chauffeur_id = $employe1.id
    client_id = $client1.id
}
Write-Host "✓ Mission créée (ID: $($mission.id))" -ForegroundColor Green

Write-Host ""
Write-Host "✓ Données de test créées avec succès !" -ForegroundColor Green
```

## 📊 Générer les Rapports

### Rapport des pointages (PDF)
```
GET /api/rapports/pointages/pdf?annee=2024&mois=11
```

### Rapport des salaires (Excel)
```
GET /api/rapports/salaires/excel?annee=2024&mois=11
```

## 💡 Conseils

1. **Ordre de création recommandé** :
   - Employés
   - Clients
   - Pointages
   - Missions
   - Avances
   - Crédits
   - Calcul des salaires

2. **Vérification** :
   - Vérifier chaque création via l'interface Swagger
   - Tester les filtres et recherches
   - Vérifier les calculs de salaire

3. **Tests** :
   - Créer plusieurs employés avec différents postes
   - Tester les différents types de jours de pointage
   - Tester les prorogations de crédit
   - Générer les rapports PDF et Excel
