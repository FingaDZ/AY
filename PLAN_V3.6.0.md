# PLAN DE DÉVELOPPEMENT v3.6.0
## Date: 15 décembre 2025

## 📋 RÉSUMÉ DES DEMANDES

### 1. Missions - Calcul Kilométrage Multi-Clients (PRIORITÉ HAUTE)
**Option retenue**: Option 1 - Calcul intelligent
- Dernier client (km max) + km supplémentaire par client intermédiaire
- Exemple: 3 clients (50km, 60km, 80km) → 80 + (2×10) = 100 km
- Paramètre configurable pour km supplémentaire (défaut: 10 km)

### 2. Gestion des Camions (PRIORITÉ HAUTE)
- Table camions: Marque, Modèle, Immatriculation
- Association camion → mission
- Suivi entrées/sorties parc camions

### 3. Congés - Affichage Décimal (PRIORITÉ MOYENNE)
- Corriger affichage Integer → Decimal
- Règle: 30j travaillés = 2.5j congés

### 4. Paramètres Salaires - Réorganisation UI (PRIORITÉ MOYENNE)
- Meilleure organisation visuelle indemnités/primes
- Alignement et clarté

### 5. Logs - Améliorations (PRIORITÉ MOYENNE)
- Affichage obligatoire: utilisateur + ID enregistrement
- Nouvelle fonctionnalité: suivi connexions utilisateurs

### 6. Nouveau Rôle "Gestionnaire" (PRIORITÉ HAUTE)
- Accès limité: Missions, Clients, Avances, Crédits
- Hiérarchie: Admin > Gestionnaire > Utilisateur

---

## 🎯 PHASES DE DÉVELOPPEMENT

### PHASE 1: Gestion Camions (v3.6.0-alpha)
**Objectif**: Infrastructure camions + association missions

#### Backend
- [ ] 1.1. Créer modèle `Camion` (marque, modele, immatriculation, actif)
- [ ] 1.2. Créer table `camions` (migration Alembic)
- [ ] 1.3. Router `/api/camions` (CRUD complet)
- [ ] 1.4. Modifier modèle `Mission` → ajouter `camion_id`
- [ ] 1.5. Modifier router missions → inclure camion_id
- [ ] 1.6. Schémas Pydantic pour camions

#### Frontend
- [ ] 1.7. Page Camions (liste, ajout, édition, suppression)
- [ ] 1.8. Modifier formulaire Mission → select camion
- [ ] 1.9. Afficher camion dans liste missions
- [ ] 1.10. Sidebar: ajouter "Camions" (icône 🚛)

#### Tests
- [ ] 1.11. Créer 3 camions test
- [ ] 1.12. Assigner camion à mission
- [ ] 1.13. Vérifier affichage

**Commit**: `feat(v3.6.0): Gestion complète des camions`

---

### PHASE 2: Calcul Kilométrage Multi-Clients (v3.6.0-beta)
**Objectif**: Optimisation calcul prime missions

#### Backend
- [ ] 2.1. Ajouter paramètre `km_supplementaire_par_client` dans `ParametresSalaire` (défaut: 10)
- [ ] 2.2. Modifier `Mission` → supporter liste clients avec km individuels
  - Option A: Nouveau modèle `MissionClient` (mission_id, client_id, km_distance, ordre)
  - Option B: JSON field `clients_details` dans Mission
- [ ] 2.3. Fonction calcul kilométrage:
  ```python
  def calculer_km_mission(clients: List[Dict]) -> int:
      # clients = [{"client_id": 1, "km": 50}, {"client_id": 2, "km": 60}, {"client_id": 3, "km": 80}]
      km_max = max(c["km"] for c in clients)
      nb_clients_intermediaires = len(clients) - 1
      km_supplementaire = parametres.km_supplementaire_par_client * nb_clients_intermediaires
      return km_max + km_supplementaire
  ```
- [ ] 2.4. Modifier calcul prime déplacement dans `salaire_calculator.py`

#### Frontend
- [ ] 2.5. Modifier formulaire Mission → multi-clients avec km individuels
  - Interface: tableau dynamique (ajouter/retirer clients)
  - Colonnes: Client, Distance (km), Ordre
- [ ] 2.6. Afficher calcul km dans preview mission
- [ ] 2.7. Paramètres Salaires → ajouter champ "Km supplémentaire/client"

#### Tests
- [ ] 2.8. Mission 1 client: 80 km → prime = 80 km
- [ ] 2.9. Mission 3 clients (50, 60, 80) → prime = 100 km
- [ ] 2.10. Modifier paramètre à 15 km → recalculer

**Commit**: `feat(v3.6.0): Calcul kilométrage intelligent multi-clients`

---

### PHASE 3: Nouveau Rôle Gestionnaire (v3.6.0-rc1)
**Objectif**: Contrôle d'accès granulaire

#### Backend
- [ ] 3.1. Ajouter enum `Role.GESTIONNAIRE` dans models
- [ ] 3.2. Créer middleware `require_gestionnaire`
- [ ] 3.3. Mettre à jour permissions:
  - Admin: tout
  - Gestionnaire: missions, clients, avances, crédits (lecture + écriture)
  - Utilisateur: lecture seule (selon besoins)
- [ ] 3.4. Protéger endpoints sensibles (salaires, paramètres) → admin only

#### Frontend
- [ ] 3.5. Formulaire utilisateur → select role avec 3 options
- [ ] 3.6. Sidebar dynamique selon rôle:
  ```javascript
  const menuItems = {
    admin: [...all],
    gestionnaire: ['missions', 'clients', 'avances', 'credits'],
    utilisateur: ['dashboard', 'pointages']
  }
  ```
- [ ] 3.7. Cacher boutons selon permissions

#### Tests
- [ ] 3.8. Créer utilisateur gestionnaire
- [ ] 3.9. Vérifier accès missions, clients OK
- [ ] 3.10. Vérifier blocage salaires, paramètres

**Commit**: `feat(v3.6.0): Ajout rôle Gestionnaire avec permissions`

---

### PHASE 4: Logs Connexions + Corrections (v3.6.0-rc2)
**Objectif**: Traçabilité complète

#### Backend
- [ ] 4.1. Nouveau type action `ActionType.LOGIN`
- [ ] 4.2. Endpoint `/api/auth/login` → log connexion réussie
- [ ] 4.3. Logger IP utilisateur, timestamp, user_agent
- [ ] 4.4. Corriger logs existants → s'assurer user_id + record_id présents

#### Frontend
- [ ] 4.5. Page Logs → colonnes obligatoires: Utilisateur, ID Enregistrement
- [ ] 4.6. Filtre par type: Connexion, Création, Modification, Suppression
- [ ] 4.7. Afficher icône 🔐 pour connexions

#### Tests
- [ ] 4.8. Se connecter → vérifier log créé
- [ ] 4.9. Modifier employé → vérifier user_id + employe_id
- [ ] 4.10. Filtrer logs connexions uniquement

**Commit**: `feat(v3.6.0): Logs connexions + corrections affichage`

---

### PHASE 5: Congés Décimal + Paramètres UI (v3.6.0-rc3)
**Objectif**: Corrections UX

#### Backend
- [ ] 5.1. Vérifier type retour API congés → doit être float/decimal
- [ ] 5.2. S'assurer que `jours_conges_acquis` utilise formule décimale

#### Frontend
- [ ] 5.3. Tableau Congés → formater `.toFixed(2)` pour affichage
- [ ] 5.4. Paramètres Salaires → réorganiser en sections:
  ```
  📊 INDEMNITÉS
  - IN (Nuisance)
  - IFSP (Service Permanent)
  - IEP (Expérience)
  
  💰 PRIMES
  - Prime Encouragement
  - Prime Chauffeur
  - Prime Nuit Sécurité
  - Prime Femme Foyer
  - Prime Transport
  - Panier
  
  ⚙️ PARAMÈTRES CALCUL
  - Jours ouvrables base
  - Calculer heures supp
  - Km supp/client missions
  ```

#### Tests
- [ ] 5.5. Vérifier affichage congés: 2.5j, 1.25j (pas 2j, 1j)
- [ ] 5.6. Vérifier organisation paramètres claire

**Commit**: `fix(v3.6.0): Affichage décimal congés + UI paramètres`

---

## 📦 VERSIONING STRATEGY

### v3.5.3 (ACTUEL)
✅ Congés décimaux 30j
✅ Affichage congés bulletins

### v3.6.0-alpha (Phase 1)
- Gestion camions

### v3.6.0-beta (Phase 2)
- Calcul kilométrage multi-clients

### v3.6.0-rc1 (Phase 3)
- Rôle Gestionnaire

### v3.6.0-rc2 (Phase 4)
- Logs connexions

### v3.6.0-rc3 (Phase 5)
- Corrections UX

### v3.6.0 (RELEASE FINALE)
- Toutes fonctionnalités intégrées
- Documentation complète
- Tests validés

---

## 🔧 RECOMMANDATIONS TECHNIQUES

### Option Missions - Ma Proposition

**Je recommande OPTION 1** pour plusieurs raisons:

✅ **Avantages Option 1**:
1. Simple à implémenter (1-2 jours)
2. Flexible: paramètre modifiable
3. Logique métier claire
4. Pas de dépendance géographique externe

❌ **Inconvénients Option 2** (Routes):
1. Complexité élevée (5-7 jours)
2. Nécessite données géographiques précises
3. Maintenance routes si clients changent
4. Surengineering pour besoin actuel

**Amélioration suggérée Option 1**:
- Ajouter champ `notes_itineraire` dans Mission
- Logger historique km (pour audit)
- Alerte si km calculés > 500 km (validation)

### Architecture Camions

**Modèle proposé**:
```python
class Camion(Base):
    __tablename__ = "camions"
    
    id = Column(Integer, primary_key=True)
    marque = Column(String(50), nullable=False)
    modele = Column(String(50), nullable=False)
    immatriculation = Column(String(20), unique=True, nullable=False)
    annee_fabrication = Column(Integer)
    capacite_charge = Column(Integer)  # kg
    actif = Column(Boolean, default=True)
    date_acquisition = Column(Date)
    date_revision = Column(Date)  # prochaine révision
    notes = Column(Text)
    
    # Relations
    missions = relationship("Mission", back_populates="camion")
```

### Permissions Gestionnaire

**Matrice d'accès proposée**:

| Fonctionnalité | Admin | Gestionnaire | Utilisateur |
|----------------|-------|--------------|-------------|
| Dashboard | ✅ | ✅ | ✅ |
| Employés | ✅ | ❌ | ❌ |
| Pointages | ✅ | ❌ | 👁️ (lecture) |
| Congés | ✅ | ❌ | 👁️ (lecture) |
| **Missions** | ✅ | ✅ | 👁️ |
| **Clients** | ✅ | ✅ | 👁️ |
| **Avances** | ✅ | ✅ | ❌ |
| **Crédits** | ✅ | ✅ | ❌ |
| Salaires | ✅ | ❌ | ❌ |
| Paramètres | ✅ | ❌ | ❌ |
| Utilisateurs | ✅ | ❌ | ❌ |
| Logs | ✅ | 👁️ (lecture) | ❌ |

---

## 📅 PLANNING ESTIMÉ

| Phase | Durée | Date cible |
|-------|-------|------------|
| Phase 1 (Camions) | 2 jours | 17 déc 2025 |
| Phase 2 (Km multi-clients) | 2 jours | 19 déc 2025 |
| Phase 3 (Rôle Gestionnaire) | 1 jour | 20 déc 2025 |
| Phase 4 (Logs) | 1 jour | 21 déc 2025 |
| Phase 5 (UX fixes) | 1 jour | 22 déc 2025 |
| **Tests & Documentation** | 1 jour | 23 déc 2025 |
| **TOTAL** | **8 jours** | **v3.6.0** |

---

## 🚀 ORDRE D'EXÉCUTION RECOMMANDÉ

1. **Phase 1 (Camions)** - Infrastructure nouvelle
2. **Phase 3 (Gestionnaire)** - Sécurité avant fonctionnalités
3. **Phase 2 (Km multi-clients)** - Logique métier complexe
4. **Phase 4 (Logs)** - Traçabilité
5. **Phase 5 (UX)** - Polish final

---

## 📝 NOTES IMPORTANTES

### Base de données
- Créer backup avant migrations
- Tester migrations sur copie dev
- Prévoir rollback si erreur

### Frontend
- Sidebar version → "v3.6.0-alpha" visible
- Changelog accessible depuis UI
- Messages utilisateur pour nouvelles fonctionnalités

### Documentation
- README_V3.6.0.md à chaque phase
- Captures d'écran nouvelles pages
- Guide utilisateur mis à jour

### Tests
- Données test cohérentes (3 camions, 5 missions multi-clients)
- Scripts de test automatisés (pytest)
- Validation manuelle avant chaque commit version

---

## ✅ VALIDATION FINALE v3.6.0

- [ ] Tous les tests passent
- [ ] Documentation à jour
- [ ] Changelog complet
- [ ] Backup DB production
- [ ] Déploiement staging OK
- [ ] Validation utilisateur
- [ ] **Déploiement production**

---

## 🎯 PRIORITÉ IMMÉDIATE

**Commencer par Phase 1 (Camions)?**
- Infrastructure la plus importante
- Impacte le moins de code existant
- Valeur métier immédiate

**Confirmez pour démarrer! 🚀**
