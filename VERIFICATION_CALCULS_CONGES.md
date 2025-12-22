# 📋 VÉRIFICATION: Calculs dans "Détails des Périodes"

## Date: 22 Décembre 2025
## Version: v3.6.1 hotfix7

---

## 🎯 Objectif
Vérifier que les calculs affichés dans la modal "Détails des périodes" sont corrects.

---

## 📊 COLONNES AFFICHÉES

### Frontend: CongesList.jsx (ligne 234-264)

```jsx
const detailColumns = [
    { title: 'Période', render: (record) => `${record.mois}/${record.annee}` },
    { title: 'Jours Travaillés', dataIndex: 'jours_travailles' },
    { title: 'Acquis', dataIndex: 'jours_conges_acquis', render: (val) => `${Number(val).toFixed(2)} j` },
    { title: 'Pris', dataIndex: 'jours_conges_pris', render: (val) => `${Number(val).toFixed(2)} j` },
    { title: 'Solde', dataIndex: 'jours_conges_restants', render: (val) => `${Number(val).toFixed(2)} j` }
];
```

**Source de données:** API GET `/conges/?employe_id=X`

---

## ✅ VÉRIFICATIONS À EFFECTUER

### 1. **Colonne "Acquis"**
**Source:** `jours_conges_acquis` de la table `conges`
**Calcul:** `(jours_travailles / 30) * 2.5` (plafonné à 2.5j/mois)

**Formule dans Conge.calculer_jours_conges():**
```python
conges_calcules = (jours_decimal / Decimal('30')) * Decimal('2.5')
conges_arrondis = float(conges_calcules.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
return min(conges_arrondis, 2.5)
```

**Exemples de vérification:**
- 30 jours travaillés → 2.50j acquis ✅
- 29 jours travaillés → 2.42j acquis ✅
- 31 jours travaillés → 2.50j acquis (plafonné) ✅
- 15 jours travaillés → 1.25j acquis ✅

---

### 2. **Colonne "Pris"**
**Source:** `jours_conges_pris` de la table `conges`
**Mise à jour:** Via endpoint `PUT /conges/{id}/consommation`

**Logique v3.6.1 hotfix7:**
- Répartition automatique du TOTAL global
- Déduction du plus ancien au plus récent
- Ne dépasse jamais l'acquis de chaque période

**Exemple:**
- Total à prendre: 5.0j
- Acquis disponibles: Oct=2.5j, Nov=2.42j, Déc=2.5j
- Répartition: Oct=2.5j, Nov=2.42j, Déc=0.08j ✅

---

### 3. **Colonne "Solde" (CRITIQUE)**
**Source:** `jours_conges_restants` de la table `conges`
**Formule:** **SOLDE CUMULÉ** = (Total acquis depuis début) - (Total pris depuis début)

**⚠️ CE N'EST PAS:**
- ❌ Solde de période: `acquis_mois - pris_mois`
- ❌ Solde précédent + acquis - pris

**✅ C'EST:**
```sql
SELECT 
    SUM(jours_conges_acquis) - SUM(jours_conges_pris)
FROM conges
WHERE employe_id = X 
  AND (annee < periode.annee OR (annee = periode.annee AND mois <= periode.mois))
```

**Exemple concret (SAFI):**

| Période | Travaillés | Acquis | Pris | Solde Cumulé |
|---------|------------|--------|------|--------------|
| 10/2025 | 30         | 2.50   | 2.50 | 0.00         |
| 11/2025 | 29         | 2.42   | 2.42 | 0.00         |
| 12/2025 | 31         | 2.50   | 0.08 | 2.42         |

**Calcul détaillé 12/2025:**
- Total acquis jusqu'à 12/2025 = 2.50 + 2.42 + 2.50 = 7.42j
- Total pris jusqu'à 12/2025 = 2.50 + 2.42 + 0.08 = 5.00j
- **Solde cumulé 12/2025 = 7.42 - 5.00 = 2.42j** ✅

---

### 4. **Code Backend de Calcul**

**Fichier:** `backend/services/conges_calculator.py` ligne 95-110

```python
# Calcul du solde cumulé lors de mise à jour
stats = db.query(
    func.sum(Conge.jours_conges_acquis).label("total_acquis"),
    func.sum(Conge.jours_conges_pris).label("total_pris")
).filter(
    Conge.employe_id == employe_id,
    (Conge.annee < annee) | ((Conge.annee == annee) & (Conge.mois <= mois))
).first()

total_acquis = float(stats.total_acquis or 0)
total_pris = float(stats.total_pris or 0)
conge_existant.jours_conges_restants = total_acquis - total_pris
```

**Fichier:** `backend/routers/conges.py` ligne 200-209 (dans update_consommation)

```python
# Recalcul après répartition
for periode in periodes_triees:
    stats_cumul = db.query(
        func.sum(Conge.jours_conges_acquis).label("total_acquis"),
        func.sum(Conge.jours_conges_pris).label("total_pris")
    ).filter(
        Conge.employe_id == conge.employe_id,
        (Conge.annee < periode.annee) | ((Conge.annee == periode.annee) & (Conge.mois <= periode.mois))
    ).first()
    
    total_acquis_cumul = float(stats_cumul.total_acquis or 0)
    total_pris_cumul = float(stats_cumul.total_pris or 0)
    periode.jours_conges_restants = total_acquis_cumul - total_pris_cumul
```

---

## 🧪 TESTS DE VÉRIFICATION

### Test 1: Solde après saisie simple
**Scénario:**
- ZERROUG: 5j acquis total (Oct=2.5, Nov=2.5)
- Saisie: 4.5j à prendre

**Résultat attendu:**
```
Oct/2025: Acquis=2.50, Pris=2.50, Solde=0.00
Nov/2025: Acquis=2.50, Pris=2.00, Solde=0.50
Total: Acquis=5.00, Pris=4.50, Solde=0.50 ✅
```

---

### Test 2: Solde après plusieurs saisies
**Scénario:**
- SAFI: 7.42j acquis total (Oct=2.5, Nov=2.42, Déc=2.5)
- Saisie 1: 1.5j → répartit Oct=1.5j
- Saisie 2 (remplacement): 5.0j → répartit Oct=2.5j, Nov=2.42j, Déc=0.08j

**Résultat après saisie 2:**
```
Oct/2025: Acquis=2.50, Pris=2.50, Solde=0.00
Nov/2025: Acquis=2.42, Pris=2.42, Solde=0.00
Déc/2025: Acquis=2.50, Pris=0.08, Solde=2.42
Total: Acquis=7.42, Pris=5.00, Solde=2.42 ✅
```

---

### Test 3: Vérification sur bulletin
**Le bulletin de décembre 2025 doit afficher:**
```
Désignation: Congés pris ce mois
Base: 0.08 j (car déduction décembre)
Taux: (vide)
Gain: Payé
```

**Requête SQL pour vérifier:**
```sql
SELECT mois, annee, jours_conges_pris, mois_deduction, annee_deduction
FROM conges
WHERE employe_id = (SELECT id FROM employes WHERE nom='SAFI')
AND (
    (mois_deduction = 12 AND annee_deduction = 2025)
    OR (mois_deduction IS NULL AND mois = 12 AND annee = 2025)
);
```

**Résultat attendu:**
- Si répartition correcte: 1 ligne avec jours_conges_pris = 0.08
- Total déduit décembre = 0.08j

---

## 🎨 AFFICHAGE FRONTEND

### Modal "Détails des périodes"
**Fichier:** `frontend/src/pages/Conges/CongesList.jsx` ligne 414-431

```jsx
<Modal
    title={`Détails des périodes - ${detailsEmploye}`}
    open={detailsModalVisible}
    ...
>
    <Table
        columns={detailColumns}
        dataSource={detailsPeriodes}
        rowKey="id"
    />
</Modal>
```

**Source `detailsPeriodes`:** Variable d'état mise à jour par `handleShowDetails()`

```jsx
const handleShowDetails = (employe) => {
    setDetailsEmploye(employe.employe_nom);
    setDetailsPeriodes(employe.periodes);  // ← Vient du groupedData
    setDetailsModalVisible(true);
};
```

**Source `employe.periodes`:** Ligne 95-105 dans `groupCongesByEmploye()`

```jsx
const grouped = {};
conges.forEach(c => {
    if (!grouped[key]) {
        grouped[key] = {
            employe_id: c.employe_id,
            employe_nom: c.employe_nom,
            periodes: [],  // ← Tableau des périodes
            ...
        };
    }
    grouped[key].periodes.push(c);  // ← Ajout de chaque congé
});
```

**✅ Les données affichées viennent directement de l'API `/conges/`**

---

## 🔍 COMMANDES DE DIAGNOSTIC

### 1. Vérifier les données brutes dans la base
```bash
ssh root@192.168.20.55
mysql -u root -p ay_hr

SELECT 
    e.nom, e.prenom,
    c.mois, c.annee,
    c.jours_travailles,
    c.jours_conges_acquis,
    c.jours_conges_pris,
    c.jours_conges_restants,
    c.mois_deduction,
    c.annee_deduction
FROM conges c
JOIN employes e ON c.employe_id = e.id
WHERE e.nom IN ('SAFI', 'ZERROUG')
ORDER BY e.nom, c.annee, c.mois;
```

### 2. Vérifier le calcul du solde cumulé
```sql
-- Pour chaque période de SAFI, calculer le solde cumulé manuellement
SELECT 
    c1.mois, c1.annee,
    c1.jours_conges_acquis as acquis_mois,
    c1.jours_conges_pris as pris_mois,
    c1.jours_conges_restants as solde_enregistre,
    (
        SELECT SUM(c2.jours_conges_acquis)
        FROM conges c2
        WHERE c2.employe_id = c1.employe_id
        AND (c2.annee < c1.annee OR (c2.annee = c1.annee AND c2.mois <= c1.mois))
    ) as total_acquis_cumule,
    (
        SELECT SUM(c2.jours_conges_pris)
        FROM conges c2
        WHERE c2.employe_id = c1.employe_id
        AND (c2.annee < c1.annee OR (c2.annee = c1.annee AND c2.mois <= c1.mois))
    ) as total_pris_cumule,
    (
        SELECT SUM(c2.jours_conges_acquis) - SUM(c2.jours_conges_pris)
        FROM conges c2
        WHERE c2.employe_id = c1.employe_id
        AND (c2.annee < c1.annee OR (c2.annee = c1.annee AND c2.mois <= c1.mois))
    ) as solde_calcule
FROM conges c1
WHERE c1.employe_id = (SELECT id FROM employes WHERE nom='SAFI')
ORDER BY c1.annee, c1.mois;
```

### 3. Tester via API
```bash
# Récupérer les congés d'un employé
curl -H "Authorization: Bearer TOKEN" \
  http://192.168.20.55:8000/conges/?employe_id=1

# Mettre à jour la consommation
curl -X PUT \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jours_pris": 5.0, "mois_deduction": 12, "annee_deduction": 2025}' \
  http://192.168.20.55:8000/conges/123/consommation
```

---

## ✅ CHECKLIST DE VALIDATION

- [ ] Les soldes affichés sont bien des **soldes cumulés** (pas de période)
- [ ] Formule vérifiée: `SUM(acquis) - SUM(pris)` jusqu'à la période
- [ ] Cohérence: Solde final = Total Acquis - Total Pris
- [ ] Bulletin PDF affiche le bon nombre de jours dans colonne BASE
- [ ] Répartition intelligente ne perd pas les saisies (mode TOTAL)
- [ ] Interface explicite: "TOTAL de jours à prendre (remplace...)"
- [ ] Message de confirmation affiche ancien → nouveau total

---

## 🚀 DÉPLOIEMENT

1. Sur le serveur:
```bash
cd /opt/ay-hr
git pull origin main
systemctl restart ayhr-backend

cd /opt/ay-hr/frontend
npm run build
systemctl restart ayhr-frontend
```

2. Tests post-déploiement:
- Ouvrir "Détails des périodes" pour un employé
- Vérifier que les soldes sont cohérents
- Faire une saisie de congés
- Vérifier le message "Ancien: X → Nouveau: Y"
- Générer un bulletin et vérifier la ligne congés

---

**✅ Tout est maintenant corrigé et documenté!**
