# AY HR - Frontend React

Interface utilisateur moderne pour l'application de gestion des ressources humaines AY HR.

## 🎨 Technologies

- **React 18.3.1** - Framework UI
- **Vite 5.4.21** - Build tool et dev server
- **Ant Design 5.18.0** - Bibliothèque de composants UI
- **React Router 6.23.1** - Navigation
- **Axios 1.7.2** - Client HTTP
- **date-fns 3.6.0** - Manipulation de dates
- **Day.js** - Parser de dates pour Ant Design
- **Recharts 2.12.7** - Graphiques et visualisations

## 📁 Structure du Projet

```
frontend/
├── public/             # Assets statiques
├── src/
│   ├── components/     # Composants réutilisables
│   │   └── Layout/
│   │       └── MainLayout.jsx
│   ├── pages/          # Pages de l'application
│   │   ├── Dashboard.jsx
│   │   ├── Employes/
│   │   │   ├── EmployesList.jsx
│   │   │   └── EmployeForm.jsx
│   │   ├── Pointages/
│   │   │   ├── PointagesList.jsx
│   │   │   └── PointageForm.jsx
│   │   ├── Clients/
│   │   │   └── ClientsList.jsx
│   │   ├── Missions/
│   │   │   └── MissionsList.jsx
│   │   ├── Avances/
│   │   │   └── AvancesList.jsx
│   │   ├── Credits/
│   │   │   └── CreditsList.jsx
│   │   ├── Salaires/
│   │   │   └── SalaireCalcul.jsx
│   │   └── Rapports/
│   │       └── Rapports.jsx
│   ├── services/       # Services API
│   │   ├── api.js
│   │   └── index.js
│   ├── App.jsx         # Routeur principal
│   ├── main.jsx        # Point d'entrée
│   └── index.css       # Styles globaux
├── package.json
├── vite.config.js
└── index.html
```

## 🚀 Démarrage Rapide

### 1. Installation des dépendances

```powershell
cd "F:\Code\AY HR\frontend"
npm install
```

### 2. Démarrer le serveur de développement

```powershell
npm run dev
```

L'application sera accessible sur **http://localhost:3000**

### 3. Build pour production

```powershell
npm run build
```

Les fichiers de production seront générés dans le dossier `dist/`

### 4. Prévisualiser le build de production

```powershell
npm run preview
```

## 🔌 Configuration API

Le frontend communique avec le backend via un proxy Vite configuré dans `vite.config.js` :

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

**Backend attendu :** http://localhost:8000

## 📋 Fonctionnalités

### 1. Dashboard
- Vue d'ensemble des statistiques RH
- 6 cartes de métriques (employés, pointages, clients, missions, avances, crédits)
- Boutons d'actions rapides
- Visualisation graphique des données

### 2. Gestion des Employés
- **Liste :** Table complète avec filtres et recherche
- **Formulaire :** 14 champs incluant :
  - Informations personnelles (nom, prénom, date de naissance, etc.)
  - Informations professionnelles (poste, type contrat, salaire de base)
  - Coordonnées (téléphone, email, adresse)
- **Validation** complète des champs
- **Actions :** Création, modification, suppression

### 3. Pointages (Fiche de présence)
- **Grille mensuelle** de 31 jours
- **Types de journée :**
  - P (Présent)
  - AB (Absent)
  - CP (Congé payé)
  - CM (Congé maladie)
  - R (Repos)
  - CNP (Congé non payé)
- **Remplissage rapide :** Sélection de type et application à plusieurs jours
- **Calcul automatique** des totaux par type
- Filtrage par employé et période (mois/année)

### 4. Clients
- Liste complète des clients
- Formulaire modal pour création/modification
- Informations : Nom, téléphone, email, adresse
- Gestion des contrats et factures

### 5. Missions
- Attribution de missions aux chauffeurs
- Sélection de client et chauffeur
- Calcul automatique des primes :
  - Distance × Tarif au kilomètre
  - Tarif configuré dans les paramètres système
- Historique complet des missions

### 6. Avances sur Salaire
- Création d'avances avec :
  - Montant
  - Mois et année de déduction
  - Motif
- Suivi des avances en cours
- Association automatique lors du calcul de salaire

### 7. Crédits
- Gestion de prêts avec mensualités
- Calcul automatique :
  - Montant mensualité = Total / Nombre de mensualités
  - Montant retenu cumulé
  - Statut (En cours / Soldé)
- Suivi des remboursements

### 8. Calcul des Salaires
- **Sélection** de période (mois/année)
- **Calcul automatique** pour tous les employés actifs
- **Détails complets** par employé :
  - Salaire base proratisé (selon jours travaillés)
  - Heures supplémentaires
  - Indemnités (IN 5%, IFSP 5%, IEP)
  - Primes (encouragement, chauffeur, déplacement, panier, transport)
  - Cotisations sociales (9%)
  - IRG (Impôt sur le revenu - barème progressif)
  - Déductions (avances, crédits)
  - **Salaire Net final**
- **Vue extensible** pour voir le détail de chaque ligne de paie

### 9. Génération de Rapports
- **Types disponibles :**
  - Rapport de pointages mensuel
  - Bulletins de paie (salaires)
- **Formats :**
  - PDF (imprimable)
  - Excel (exploitable)
- Sélection de période
- Téléchargement automatique

## 🎨 Interface Utilisateur

### Design
- **Thème sombre** professionnel
- **Sidebar** avec icônes et menu déroulant
- **Layout responsive** (adaptable mobile/tablette/desktop)
- **Composants Ant Design** cohérents

### Navigation
- Menu latéral avec 9 sections
- Breadcrumb pour la localisation
- Retour rapide au dashboard

### Feedback Utilisateur
- Messages de succès/erreur (Ant Design)
- Loading states pour toutes les opérations
- Confirmations pour les actions critiques
- Validation en temps réel des formulaires

## 🔐 Sécurité

- Validation côté client avant envoi API
- Gestion des erreurs réseau
- Messages d'erreur clairs pour l'utilisateur
- Protection contre les injections (utilisation de composants Ant Design)

## 📊 Gestion des Données

### Services API
Tous les appels API sont centralisés dans `src/services/index.js` :

```javascript
// Exemple d'utilisation
import { employeService } from './services';

// Récupérer tous les employés
const employes = await employeService.getAll({ statut: 'Actif' });

// Créer un employé
await employeService.create(employeData);

// Mettre à jour
await employeService.update(id, employeData);

// Supprimer
await employeService.delete(id);
```

### State Management
- **useState** pour l'état local des composants
- **useEffect** pour le chargement des données
- Pas de Redux (application de taille moyenne)

## 🐛 Débogage

### Console du navigateur
Ouvrez les DevTools (F12) pour voir :
- Requêtes réseau (onglet Network)
- Erreurs JavaScript (onglet Console)
- Composants React (React DevTools extension)

### Logs Vite
Le terminal affiche :
- Hot Module Replacement (HMR) updates
- Erreurs de build
- Warnings ESLint

## 📦 Dépendances Principales

```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "react-router-dom": "^6.23.1",
  "antd": "^5.18.0",
  "axios": "^1.7.2",
  "dayjs": "^1.11.11",
  "date-fns": "^3.6.0",
  "recharts": "^2.12.7",
  "@ant-design/icons": "^5.3.7"
}
```

## 🔧 Configuration Vite

### vite.config.js
```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

### Port personnalisé
Pour changer le port, modifiez `server.port` dans `vite.config.js`

## 🚨 Prérequis

- **Node.js** : Version 16+ recommandée
- **npm** : Version 7+
- **Backend AY HR** : Doit être démarré sur http://localhost:8000

## 📝 Notes de Développement

### Hot Module Replacement (HMR)
Vite supporte le HMR natif - les modifications sont reflétées instantanément sans rechargement complet.

### Conventions de Code
- **Composants** : PascalCase (ex: `EmployesList.jsx`)
- **Fichiers services** : camelCase (ex: `employeService`)
- **Constantes** : UPPER_SNAKE_CASE
- **Fonctions** : camelCase

### Performance
- Lazy loading des routes (possibilité d'ajout)
- Pagination des listes volumineuses
- Debouncing des champs de recherche (à ajouter si besoin)

## 🤝 Intégration Backend

Le frontend communique avec les endpoints suivants :

```
GET    /api/employes              - Liste des employés
POST   /api/employes              - Créer employé
GET    /api/employes/{id}         - Détails employé
PUT    /api/employes/{id}         - Modifier employé
DELETE /api/employes/{id}         - Supprimer employé

GET    /api/pointages             - Liste pointages
POST   /api/pointages             - Créer pointage

GET    /api/clients               - Liste clients
POST   /api/clients               - Créer client

GET    /api/missions              - Liste missions
POST   /api/missions              - Créer mission

GET    /api/avances               - Liste avances
POST   /api/avances               - Créer avance

GET    /api/credits               - Liste crédits
POST   /api/credits               - Créer crédit

GET    /api/salaires/calculer-tous - Calculer tous les salaires

GET    /api/rapports/pointages/pdf    - Rapport pointages PDF
GET    /api/rapports/pointages/excel  - Rapport pointages Excel
GET    /api/rapports/salaires/pdf     - Bulletins de paie PDF
GET    /api/rapports/salaires/excel   - Bulletins de paie Excel
```

## 📱 Responsive Design

L'application s'adapte automatiquement :
- **Desktop** : Sidebar permanente, tableaux larges
- **Tablet** : Sidebar collapsible
- **Mobile** : Menu hamburger, colonnes adaptées

## 🎯 Roadmap Futures Améliorations

- [ ] Authentification utilisateur (login/logout)
- [ ] Gestion des rôles et permissions
- [ ] Mode sombre/clair (toggle)
- [ ] Export CSV des tableaux
- [ ] Notifications push
- [ ] Historique des modifications
- [ ] Recherche globale
- [ ] Favoris/bookmarks

## 📄 Licence

Propriétaire - AY HR © 2024

## 👥 Support

Pour toute question ou problème :
- Vérifiez que le backend est démarré
- Consultez les logs du terminal Vite
- Vérifiez la console du navigateur (F12)

---

**Développé avec ❤️ pour AY HR**
