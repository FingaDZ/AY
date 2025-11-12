# Guide de Démarrage Rapide - AY HR

## 🚀 Lancement du Projet

### 1. Démarrer le Backend
```powershell
cd "F:\Code\AY HR\backend"
..\.venv\Scripts\uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Démarrer le Frontend
```powershell
cd "F:\Code\AY HR\frontend"
npm run dev
```

### 3. Accéder à l'Application
Ouvrir: **http://localhost:3000**

## 🔐 Connexion

L'application redirige automatiquement vers la page de login.

**Identifiants Administrateur:**
- Email: `admin@ayhr.dz`
- Mot de passe: `admin123`

## ✅ Après Connexion

Une fois connecté, vous êtes redirigé vers le **Dashboard**.

### Menu Disponible (Admin):
- 📊 **Tableau de Bord** - Vue d'ensemble
- 👥 **Employés** - Gestion des employés
- 📅 **Pointages** - Suivi de présence
- 🏢 **Clients** - Gestion des clients
- 🚗 **Missions** - Affectation des chauffeurs
- 💰 **Avances** - Gestion des avances
- 🏦 **Crédits** - Suivi des crédits
- 💵 **Calcul Salaires** - Génération bulletins
- ⚙️ **Paramètres** - Configuration entreprise
- 👤 **Utilisateurs** - Gestion des accès
- 📋 **Logs** - Historique activité

### Menu Limité (Utilisateur Standard):
- 📊 **Tableau de Bord**
- 🚗 **Missions** uniquement (affectation chauffeurs)

## 🏢 Configuration Initiale

### 1. Configurer les Informations Entreprise
Aller dans **Paramètres** et renseigner:
- Raison sociale
- Nom entreprise
- Adresse
- RC, NIF, NIS, ART
- Téléphone
- Compte bancaire

Ces informations apparaîtront sur tous les rapports PDF.

### 2. Créer des Utilisateurs
Aller dans **Utilisateurs** pour:
- Créer des comptes utilisateurs
- Définir les rôles (Admin / Utilisateur)
- Gérer les statuts (Actif / Inactif)

## 🔒 Sécurité

### Rôles et Permissions

**Administrateur (Admin):**
- Accès complet à tous les modules
- Création/Modification/Suppression
- Gestion des paramètres
- Gestion des utilisateurs

**Utilisateur Standard:**
- Accès au Dashboard
- Accès aux Missions uniquement
- Peut affecter des chauffeurs
- Pas d'accès aux autres modules

### Déconnexion
Cliquer sur votre **avatar** en haut à droite → **Déconnexion**

## 📝 Rapports PDF

Chaque module a un bouton **"Générer Rapport"**:
- **Employés** - Liste avec détails
- **Pointages** - Résumé mensuel
- **Clients** - Liste clients actifs
- **Avances** - Historique des avances

Les rapports incluent automatiquement:
- Logo/En-tête entreprise (si configuré)
- Date de génération
- QR Code de validation

## 🔧 Tests API

Script de test disponible:
```powershell
cd "F:\Code\AY HR"
.\test_api_complet.ps1
```

## ⚠️ Troubleshooting

### Le frontend me redirige vers login en boucle
✅ **RÉSOLU** - Vérifier que:
- Le backend est démarré (port 8000)
- Les credentials sont corrects
- Le localStorage du navigateur n'est pas corrompu

### 401 Non Autorisé
- Vérifier que vous êtes bien connecté
- Le token expire après déconnexion
- Reconnecter si nécessaire

### Erreur CORS
Le backend utilise `/api` comme proxy via Vite, configuré dans `vite.config.js`

## 📦 Base de Données

**MySQL** - Base: `ay_hr`

### Tables Principales:
- `employes` - Employés
- `pointages` - Présences
- `clients` - Clients
- `missions` - Missions chauffeurs
- `avances` - Avances employés
- `credits` - Crédits employés
- `users` - Utilisateurs système
- `parametres_entreprise` - Configuration
- `parametres` - Config missions (tarif km, etc.)

## 🎯 Workflow Typique

1. **Configuration Initiale**
   - Paramètres entreprise
   - Créer utilisateurs

2. **Gestion RH**
   - Ajouter employés
   - Enregistrer pointages quotidiens
   - Suivre les congés

3. **Gestion Missions**
   - Créer clients
   - Affecter missions aux chauffeurs
   - Calculer frais kilométriques

4. **Gestion Financière**
   - Enregistrer avances
   - Suivre crédits
   - Calculer salaires mensuels
   - Générer bulletins PDF

5. **Rapports**
   - Exporter PDF selon besoin
   - Archiver documents

## 📞 Support

En cas de problème, consulter:
- `TESTS_AUTHENTIFICATION.md` - Tests système
- `TROUBLESHOOTING.md` - Guide dépannage
- Logs backend dans le terminal
- Console navigateur (F12)
