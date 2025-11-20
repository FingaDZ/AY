# Analyse du Rapport G29 - Déclaration Annuelle des Salaires

## 📋 Vue d'ensemble

Le **formulaire G29** est la déclaration annuelle obligatoire des traitements, salaires et émoluments divers payés par l'entreprise, avec les retenues à la source au titre de l'IRG (Impôt sur le Revenu Global).

## 📄 Structure des documents analysés

### G29-1.pdf (Page récapitulative)
**Informations entreprise :**
- Raison sociale : EURL ABDELKAHAR YOURT
- Activité : COMMERCE DE GROS DE LAIT, PRODUITS LAITIERS ET ŒUFS
- Adresse : DOUAR LAMGHELSSA CHELGHOUM LAID MILA
- Année : 2025
- Wilaya : MILA
- Commune : CHELGHOUM LAID

**Données globales :**
- **Total salaires bruts versés** : 15,857,433.83 DA
- **Total IRG retenu** : 1,270,988.00 DA
- Répartition mensuelle des salaires et retenues IRG

### G29-2.pdf (Détail par employé)
Liste détaillée de **52 employés** avec pour chacun :
- Nom, Prénom
- Situation familiale (M/C = Marié/Célibataire)
- Salaire net mensuel (janvier à décembre)
- Retenue IRG mensuelle
- Total annuel imposable
- Total retenue IRG annuelle

## 🔍 Données requises par le G29

### A. Informations entreprise (déjà en base)
✅ **Disponibles dans `parametres_entreprise`** :
- Raison sociale
- Adresse
- RC (Registre de Commerce)
- NIF (Numéro d'Identification Fiscale)
- NIS (Numéro d'Identification Statistique)
- Article d'imposition

### B. Informations employés (en base)
✅ **Disponibles dans `employes`** :
- Nom, Prénom
- Situation familiale
- Poste de travail
- Date de recrutement
- Salaire de base
- Statut (actif/inactif)

### C. Données mensuelles de paie
⚠️ **PARTIELLEMENT DISPONIBLES** :

**Ce que nous avons :**
- Table `pointages` : heures travaillées par jour
- Salaire de base dans `employes`

**Ce qui MANQUE dans la base actuelle :**
1. ❌ **Salaire net mensuel payé** (par mois, par employé)
2. ❌ **Montant IRG retenu** (par mois, par employé)
3. ❌ **Primes mensuelles détaillées**
4. ❌ **Déductions mensuelles**
5. ❌ **Salaire brut mensuel**
6. ❌ **Base imposable IRG**

## 💡 Solution proposée : Nouvelle table `salaires`

### Structure nécessaire

```sql
CREATE TABLE salaires (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employe_id INT NOT NULL,
    annee INT NOT NULL,
    mois INT NOT NULL, -- 1-12
    
    -- Salaire
    salaire_base DECIMAL(10,2) DEFAULT 0,
    heures_travaillees DECIMAL(8,2) DEFAULT 0,
    jours_travailles INT DEFAULT 0,
    
    -- Primes
    prime_rendement DECIMAL(10,2) DEFAULT 0,
    prime_fidelite DECIMAL(10,2) DEFAULT 0,
    prime_experience DECIMAL(10,2) DEFAULT 0,
    prime_panier DECIMAL(10,2) DEFAULT 0,
    prime_transport DECIMAL(10,2) DEFAULT 0,
    prime_nuit DECIMAL(10,2) DEFAULT 0,
    autres_primes DECIMAL(10,2) DEFAULT 0,
    
    -- Totaux
    total_primes DECIMAL(10,2) DEFAULT 0,
    salaire_brut DECIMAL(10,2) DEFAULT 0,
    
    -- Déductions
    cotisation_cnr DECIMAL(10,2) DEFAULT 0,
    cotisation_secu_sociale DECIMAL(10,2) DEFAULT 0,
    irg_retenu DECIMAL(10,2) DEFAULT 0,
    autres_deductions DECIMAL(10,2) DEFAULT 0,
    
    -- Résultat
    total_deductions DECIMAL(10,2) DEFAULT 0,
    salaire_net DECIMAL(10,2) DEFAULT 0,
    
    -- Métadonnées
    date_paiement DATE,
    statut VARCHAR(20) DEFAULT 'brouillon', -- brouillon, validé, payé
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (employe_id) REFERENCES employes(id),
    UNIQUE KEY unique_salaire (employe_id, annee, mois)
);
```

## 📊 Capacité de génération du G29

### Avec la nouvelle table `salaires` : ✅ OUI, 100% possible

**G29-1 (Récapitulatif) :**
```sql
-- Total annuel par mois
SELECT 
    mois,
    SUM(salaire_brut) as total_brut,
    SUM(irg_retenu) as total_irg
FROM salaires
WHERE annee = 2025
GROUP BY mois
ORDER BY mois;

-- Total général année
SELECT 
    SUM(salaire_brut) as total_brut_annuel,
    SUM(irg_retenu) as total_irg_annuel
FROM salaires
WHERE annee = 2025;
```

**G29-2 (Détail par employé) :**
```sql
-- Ligne par employé avec 12 mois
SELECT 
    e.nom,
    e.prenom,
    e.situation_familiale,
    -- Pour chaque mois (1 à 12)
    MAX(CASE WHEN s.mois = 1 THEN s.salaire_net END) as janvier_net,
    MAX(CASE WHEN s.mois = 1 THEN s.irg_retenu END) as janvier_irg,
    -- ... répéter pour les 12 mois
    SUM(s.salaire_brut) as total_imposable,
    SUM(s.irg_retenu) as total_irg
FROM employes e
LEFT JOIN salaires s ON e.id = s.employe_id AND s.annee = 2025
WHERE s.annee = 2025
GROUP BY e.id, e.nom, e.prenom, e.situation_familiale
ORDER BY e.nom;
```

## 🎯 Faisabilité : ÉLEVÉE ✅

### Points positifs
1. ✅ Structure de données claire et standard
2. ✅ Calculs IRG déjà implémentés (`irg_calculator.py`)
3. ✅ Logique de calcul des primes existante
4. ✅ Format PDF avec canvas ReportLab maîtrisé
5. ✅ Données entreprise complètes
6. ✅ Liste employés disponible

### Travail nécessaire

#### 1. Base de données (2-3 heures)
- Créer table `salaires`
- Migrer les données existantes si disponibles
- Ajouter index pour performance

#### 2. Backend API (3-4 heures)
- Route POST `/api/salaires/` (créer/modifier salaire mensuel)
- Route GET `/api/salaires/{annee}/{mois}` (tous les salaires du mois)
- Route GET `/api/salaires/employe/{id}/{annee}` (salaires annuels employé)
- Route GET `/api/rapports/g29/{annee}` (données pour G29)

#### 3. Service de calcul (2-3 heures)
- Automatiser calcul salaire mensuel depuis pointages
- Intégrer calcul IRG
- Calculer toutes les primes
- Gérer les déductions

#### 4. Générateur PDF G29 (4-6 heures)
- `generate_g29_page1()` : récapitulatif mensuel
- `generate_g29_page2()` : tableau détaillé employés (52 lignes)
- Gestion multi-pages automatique
- Format exact du formulaire officiel

#### 5. Frontend (3-4 heures)
- Page "Salaires mensuels" pour saisie/validation
- Page "Rapport G29" avec prévisualisation
- Filtres par année
- Bouton génération PDF

**TOTAL ESTIMÉ : 14-20 heures de développement**

## 📋 Plan d'implémentation recommandé

### Phase 1 : Base de données (Priorité 1)
```sql
-- Créer table salaires
-- Ajouter contraintes et index
-- Script de migration si données existantes
```

### Phase 2 : Calcul automatique (Priorité 2)
- Service `salaire_calculator.py` enrichi
- Intégration avec pointages
- Calcul IRG automatique
- Interface de validation

### Phase 3 : API Backend (Priorité 3)
- CRUD salaires
- Endpoints rapports
- Validation des données

### Phase 4 : Génération G29 (Priorité 4)
- PDF page 1 (récapitulatif)
- PDF page 2 (détail employés)
- Tests avec données réelles

### Phase 5 : Interface utilisateur (Priorité 5)
- Gestion salaires mensuels
- Génération G29
- Exports Excel/PDF

## ⚠️ Points d'attention

1. **Rétroactivité** : Si vous devez générer G29 pour 2024 ou années antérieures, il faudra saisir/importer les données historiques

2. **Validation légale** : Le formulaire G29 doit être conforme au modèle officiel de l'administration fiscale algérienne

3. **Calcul IRG** : Vérifier que le barème IRG dans `irg_calculator.py` est à jour (2025)

4. **Archivage** : Les G29 doivent être conservés 10 ans minimum

5. **Signature** : Le document généré devra être signé et cacheté avant envoi aux impôts

## 🎯 Conclusion

**OUI, il est TOTALEMENT POSSIBLE d'intégrer la génération du rapport G29.**

**Prérequis :**
- Créer table `salaires` pour stocker l'historique mensuel
- Implémenter le calcul/saisie des salaires mensuels
- Développer le générateur PDF G29

**Bénéfices :**
✅ Automatisation complète de la déclaration annuelle
✅ Réduction des erreurs de saisie manuelle
✅ Traçabilité totale des salaires et IRG
✅ Génération instantanée à tout moment
✅ Archivage numérique intégré

**Recommandation : Démarrer par la Phase 1 (table salaires) dès que possible pour commencer à collecter les données mensuelles.**
