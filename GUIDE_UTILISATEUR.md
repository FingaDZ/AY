# Guide Utilisateur - Application de Gestion RH AY HR

## 📖 Table des matières

1. [Introduction](#introduction)
2. [Gestion des Employés](#1-gestion-des-employés)
3. [Système de Pointage](#2-système-de-pointage)
4. [Gestion des Clients](#3-gestion-des-clients)
5. [Ordres de Mission](#4-ordres-de-mission)
6. [Gestion des Avances](#5-gestion-des-avances)
7. [Gestion des Crédits](#6-gestion-des-crédits)
8. [Calcul des Salaires](#7-calcul-des-salaires)
9. [Génération de Rapports](#8-génération-de-rapports)

## Introduction

Cette application permet de gérer l'ensemble du processus RH de votre entreprise, de la gestion des employés au calcul des salaires, en passant par le pointage et les avances.

**Accès à l'API** : http://localhost:8000/docs

## 1. Gestion des Employés

### Créer un employé

**Route** : `POST /api/employes/`

**Champs obligatoires** :
- Nom et Prénom
- Date et lieu de naissance
- Adresse complète
- Numéro de mobile
- Numéro de Sécurité Sociale (unique)
- Numéro de compte bancaire ou postal
- Situation familiale (Célibataire / Marié)
- Date de recrutement
- Poste de travail
- Salaire de base (en DA)

**Champs optionnels** :
- Date de fin de contrat
- Femme au foyer (Oui/Non)
- Statut du contrat (Actif/Inactif, par défaut Actif)

**Exemple** :
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
  "femme_au_foyer": false,
  "date_recrutement": "2020-01-01",
  "date_fin_contrat": null,
  "poste_travail": "Chauffeur",
  "salaire_base": 30000,
  "statut_contrat": "Actif"
}
```

### Lister les employés

**Route** : `GET /api/employes/`

**Paramètres de filtrage** :
- `statut` : Filtrer par statut (Actif/Inactif)
- `search` : Rechercher par nom ou prénom
- `poste` : Filtrer par poste
- `skip` : Pagination (nombre à sauter)
- `limit` : Nombre de résultats (max 1000)

**Exemple** : `/api/employes/?statut=Actif&search=Ahmed`

### Modifier un employé

**Route** : `PUT /api/employes/{employe_id}`

Tous les champs sont optionnels, seuls les champs fournis seront modifiés.

### Valider les contrats

**Route** : `POST /api/employes/valider-tous-contrats`

Cette route met automatiquement à jour le statut des contrats selon les dates de début et de fin.

## 2. Système de Pointage

### Créer un pointage mensuel

**Route** : `POST /api/pointages/`

```json
{
  "employe_id": 1,
  "annee": 2024,
  "mois": 11
}
```

### Obtenir les employés actifs pour un mois

**Route** : `GET /api/pointages/employes-actifs?annee=2024&mois=11`

Cette route retourne uniquement les employés avec un contrat actif et valide pour la période.

### Mettre à jour un pointage

**Route** : `PUT /api/pointages/{pointage_id}`

**Valeurs possibles pour chaque jour** :
- `Tr` : Travaillé (valeur = 1)
- `Ab` : Absent (valeur = 0)
- `Co` : Congé (valeur = 0)
- `Ma` : Maladie (valeur = 0)
- `Fe` : Férié (valeur = 1)
- `Ar` : Arrêt (valeur = 0)
- `null` : Non renseigné

**Exemple** :
```json
{
  "jours": {
    "1": "Tr",
    "2": "Tr",
    "3": "Tr",
    "4": "Tr",
    "5": "Tr",
    "6": "Co",
    "7": "Co",
    "8": "Tr",
    ...
  }
}
```

### Calculs automatiques

Le système calcule automatiquement :
- Total jours travaillés = Tr + Fe
- Total absences, congés, maladies, arrêts

### Verrouiller un pointage

**Route** : `POST /api/pointages/{pointage_id}/verrouiller`

```json
{
  "verrouille": true
}
```

Un pointage verrouillé ne peut plus être modifié.

### Copier un pointage

**Route** : `POST /api/pointages/copier`

Paramètres :
- `employe_id` : ID de l'employé
- `annee_source` : Année source
- `mois_source` : Mois source
- `annee_dest` : Année destination
- `mois_dest` : Mois destination

## 3. Gestion des Clients

### Créer un client

**Route** : `POST /api/clients/`

```json
{
  "nom": "SAIDI",
  "prenom": "Rachid",
  "distance": 25.5,
  "telephone": "0555987654"
}
```

La distance est en kilomètres depuis l'entreprise.

### Lister les clients

**Route** : `GET /api/clients/`

**Paramètre** : `search` pour rechercher par nom ou prénom

## 4. Ordres de Mission

### Configuration du tarif kilométrique

**Route** : `GET /api/missions/parametres/tarif-km`

**Route** : `PUT /api/missions/parametres/tarif-km`

```json
{
  "valeur": "3.50",
  "description": "Tarif kilométrique pour les missions (DA/km)"
}
```

### Créer une mission

**Route** : `POST /api/missions/`

```json
{
  "date_mission": "2024-11-15",
  "chauffeur_id": 1,
  "client_id": 1
}
```

Le système :
1. Vérifie que l'employé est bien un chauffeur
2. Récupère automatiquement la distance du client
3. Récupère le tarif kilométrique actuel
4. Calcule la prime : Distance × Tarif/km

### Obtenir les primes mensuelles

**Route** : `GET /api/missions/primes-mensuelles?annee=2024&mois=11`

Retourne le total des primes de déplacement par chauffeur pour le mois.

## 5. Gestion des Avances

### Créer une avance

**Route** : `POST /api/avances/`

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

### Obtenir le total des avances pour un mois

**Route** : `GET /api/avances/total-mensuel?annee=2024&mois=11`

Cette route est utilisée automatiquement lors du calcul des salaires.

## 6. Gestion des Crédits

### Créer un crédit

**Route** : `POST /api/credits/`

```json
{
  "employe_id": 1,
  "date_octroi": "2024-01-15",
  "montant_total": 120000,
  "nombre_mensualites": 12
}
```

Le système calcule automatiquement :
- Montant mensualité = Montant total ÷ Nombre mensualités
- Montant restant = Montant total - Montant retenu

### Créer une prorogation

**Route** : `POST /api/credits/{credit_id}/prorogation`

```json
{
  "credit_id": 1,
  "date_prorogation": "2024-11-01",
  "mois_initial": 11,
  "annee_initiale": 2024,
  "mois_reporte": 12,
  "annee_reportee": 2024,
  "motif": "Difficultés financières temporaires"
}
```

### Gestion automatique des retenues

Les retenues de crédit sont automatiquement :
- Calculées lors du calcul des salaires
- Enregistrées dans l'historique
- Mises à jour dans le solde du crédit
- Ignorées en cas de prorogation

Le crédit passe automatiquement en statut "Soldé" lorsque le montant total est retenu.

## 7. Calcul des Salaires

### Calculer le salaire d'un employé

**Route** : `POST /api/salaires/calculer`

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

### Calculer tous les salaires

**Route** : `POST /api/salaires/calculer-tous?annee=2024&mois=11&jours_supplementaires=0`

Calcule automatiquement les salaires de tous les employés actifs.

### Composition du salaire

#### Salaire Cotisable :
1. **Salaire de base proratisé** : Salaire × (Jours travaillés ÷ 26)
2. **Heures supplémentaires** : Jours supp. × Salaire journalier × 1,5
3. **IN** (Indemnité de Nuisance) : 5% du salaire de base
4. **IFSP** : 5% du salaire de base
5. **IEP** (Expérience) : Ancienneté × 1% du salaire de base
6. **Prime d'encouragement** : 10% si ancienneté > 1 an
7. **Prime chauffeur** : 100 DA × Jours travaillés (si poste = Chauffeur)
8. **Prime de déplacement** : Total des missions du mois
9. **Prime objectif** : Saisie manuelle
10. **Prime variable** : Saisie manuelle

#### Retenue Sécurité Sociale :
- 9% du salaire cotisable

#### Éléments supplémentaires :
- **Panier** : 100 DA × Jours travaillés
- **Prime transport** : 100 DA × Jours travaillés

#### IRG :
Calculé selon le barème du fichier `irg.xlsx`

#### Salaire Imposable :
Salaire Cotisable + Panier + Prime Transport - Retenue SS - IRG

#### Déductions :
- Total des avances du mois
- Retenue mensuelle du crédit

#### Salaire Net :
Salaire Imposable - Avances - Crédit + Prime Femme au Foyer (1000 DA)

## 8. Génération de Rapports

### Rapport des pointages

**Format PDF** : `GET /api/rapports/pointages/pdf?annee=2024&mois=11`

**Format Excel** : `GET /api/rapports/pointages/excel?annee=2024&mois=11`

Contient :
- Liste des employés
- Détail des jours travaillés, absences, congés, etc.

### Rapport des salaires

**Format PDF** : `GET /api/rapports/salaires/pdf?annee=2024&mois=11`

**Format Excel** : `GET /api/rapports/salaires/excel?annee=2024&mois=11`

Contient :
- Informations complètes de chaque employé
- Détail complet du calcul du salaire
- Totaux généraux

## 💡 Conseils d'utilisation

### Workflow mensuel recommandé

1. **Début du mois** :
   - Créer les pointages pour tous les employés actifs
   - Saisir le tarif kilométrique du mois (si modifié)

2. **Pendant le mois** :
   - Mettre à jour les pointages quotidiennement
   - Enregistrer les missions des chauffeurs
   - Enregistrer les avances accordées

3. **Fin du mois** :
   - Finaliser tous les pointages
   - Verrouiller les pointages
   - Calculer tous les salaires
   - Générer les rapports PDF/Excel
   - Distribuer les bulletins de paie

### Bonnes pratiques

- ✅ Toujours vérifier le pointage avant de le verrouiller
- ✅ Enregistrer les missions le jour même
- ✅ Mettre à jour le barème IRG chaque année
- ✅ Faire une sauvegarde de la base de données régulièrement
- ✅ Générer les rapports mensuels pour archivage

### Vérifications importantes

Avant de calculer les salaires, vérifier :
- [ ] Tous les pointages sont créés et à jour
- [ ] Toutes les missions sont enregistrées
- [ ] Toutes les avances sont saisies
- [ ] Les crédits sont à jour
- [ ] Le barème IRG est correct

## ❓ Questions fréquentes

**Q : Comment modifier un employé qui a déjà des données ?**
R : Utilisez la route `PUT /api/employes/{id}` avec uniquement les champs à modifier.

**Q : Peut-on supprimer un pointage verrouillé ?**
R : Non, il faut d'abord le déverrouiller.

**Q : Les retenues de crédit sont-elles automatiques ?**
R : Oui, elles sont calculées et enregistrées automatiquement lors du calcul des salaires.

**Q : Comment gérer un employé en arrêt maladie prolongé ?**
R : Utiliser le type "Ma" pour les jours de maladie, ou "Ar" pour un arrêt.

**Q : Le système gère-t-il les jours fériés ?**
R : Oui, utilisez le type "Fe" qui compte comme jour travaillé (valeur = 1).
