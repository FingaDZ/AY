# 🔍 ANALYSE COMPLÈTE: FLUX CONGÉS → SALAIRE → BULLETIN

## Date: 22 Décembre 2025
## Version: v3.6.1 hotfix6
## Problème Rapporté: Incohérence entre congés affichés et bulletin de paie

---

## 📊 ARCHITECTURE ACTUELLE

### 1. TABLE `conges` - Structure
```sql
CREATE TABLE conges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employe_id INT NOT NULL,
    annee INT NOT NULL,
    mois INT NOT NULL,                      -- Mois d'ACQUISITION des congés
    jours_travailles INT DEFAULT 0,
    jours_conges_acquis DECIMAL(5,2),
    jours_conges_pris DECIMAL(5,2),         -- Jours consommés
    jours_conges_restants DECIMAL(5,2),     -- Solde cumulé
    mois_deduction INT,                     -- Mois où déduire du bulletin (NOUVEAU v3.6.1)
    annee_deduction INT,                    -- Année où déduire du bulletin (NOUVEAU v3.6.1)
    ...
);
```

**LOGIQUE v3.6.1:**
- `mois/annee` = Période d'acquisition (quand les jours sont gagnés)
- `mois_deduction/annee_deduction` = Période de déduction sur bulletin (quand ils sont déduits du salaire)
- Si `mois_deduction` NULL → comportement par défaut (déduction sur mois d'acquisition)

---

### 2. ÉTAPE 1: Saisie des congés (Frontend → Backend)

**Endpoint:** `PUT /conges/{conge_id}/consommation`

**Flux actuel (hotfix6):**
1. Utilisateur clique "Saisie" sur n'importe quelle période
2. Saisit: `jours_pris`, `mois_deduction`, `annee_deduction`
3. Backend appelle `repartir_conges_intelligemment()`:
   - ⚠️ **PROBLÈME IDENTIFIÉ:** Réinitialise TOUS les `jours_conges_pris` à 0
   - Répartit le nouveau montant sur périodes anciennes → récentes
   - Met `mois_deduction` et `annee_deduction` pour TOUTES les périodes touchées

**CODE ACTUEL:**
```python
# backend/routers/conges.py ligne 157-162
for p in periodes_employe:
    p.jours_conges_pris = 0.0  # ⚠️ RÉINITIALISATION TOTALE

# Puis répartition
repartition = repartir_conges_intelligemment(
    db=db,
    employe_id=conge.employe_id,
    jours_a_prendre=jours_pris,  # ⚠️ Seulement la nouvelle saisie!
    ...
)
```

**🔴 PROBLÈME CRITIQUE:**
- Si l'employé a pris 1.5j en octobre (saisie précédente)
- Puis veut prendre 4.5j en décembre (nouvelle saisie)
- Le système EFFACE les 1.5j d'octobre
- Ne répartit QUE les 4.5j nouveaux
- **RÉSULTAT:** Perte des saisies antérieures!

---

### 3. ÉTAPE 2: Calcul du salaire

**Service:** `backend/services/salaire_calculator.py`

**Logique ligne 67-89:**
```python
conges_a_deduire = self.db.query(Conge).filter(
    Conge.employe_id == employe_id,
    or_(
        # Cas 1: mois_deduction défini
        and_(
            Conge.mois_deduction == mois,
            Conge.annee_deduction == annee
        ),
        # Cas 2: mois_deduction NULL (ancien comportement)
        and_(
            Conge.mois_deduction.is_(None),
            Conge.mois == mois,
            Conge.annee == annee
        )
    )
).all()

jours_conges = sum(float(c.jours_conges_pris or 0) for c in conges_a_deduire)
```

**✅ Cette partie est CORRECTE:**
- Récupère toutes les périodes dont `mois_deduction` pointe vers le bulletin
- Somme les `jours_conges_pris`
- Exemple: Si 3 périodes ont `mois_deduction=12`, les 3 sont additionnées

---

### 4. ÉTAPE 3: Génération du bulletin PDF

**Service:** `backend/services/pdf_generator.py`

**Bulletin individuel (ligne 1083-1087):**
```python
['Jours de congé pris ce mois',
 '',
 f"{salaire_data.get('jours_conges', 0):.1f} j" if salaire_data.get('jours_conges', 0) > 0 else '0 j',
 'Payé',
 ''],
```

**Bulletin combiné (ligne 3754-3758):**
```python
['Congés pris ce mois',
 '',
 f"{sal_data.get('jours_conges', 0):.1f} j",
 '(Payé)',
 ''],
```

**⚠️ OBSERVATION:**
- Les bulletins affichent `(Payé)` dans colonne GAIN
- Le nombre de jours devrait être dans colonne TAUX
- Sur vos screenshots: on ne voit QUE "(Payé)", pas le nombre de jours!

**🔍 HYPOTHÈSE:**
- Soit `salaire_data.get('jours_conges')` retourne 0
- Soit le PDF est mal formaté et cache la colonne TAUX

---

## 🐛 PROBLÈMES IDENTIFIÉS

### Problème #1: Réinitialisation des saisies précédentes
**Gravité:** 🔴 CRITIQUE

**Description:**
- La fonction `repartir_conges_intelligemment()` réinitialise TOUS les `jours_pris`
- Puis ne répartit que la NOUVELLE saisie
- Perte des saisies antérieures

**Exemple concret (selon vos screenshots):**
1. SAFI a pris 1.5j (visible dans l'interface)
2. Quelqu'un fait une nouvelle saisie
3. Les 1.5j sont effacés
4. Seule la nouvelle saisie reste

**Solution:**
```python
# Au lieu de réinitialiser, on doit:
# 1. Calculer le TOTAL cumulé que l'employé veut prendre
# 2. Répartir CE total sur toutes les périodes
# 3. OU: ne pas réinitialiser, juste ajouter la nouvelle consommation
```

---

### Problème #2: Affichage bulletin PDF
**Gravité:** 🟡 MOYEN

**Description:**
- Le bulletin n'affiche que "(Payé)" sans le nombre de jours
- Ligne 1085: condition `if > 0` peut masquer le 0
- Formatage peut cacher la valeur

**Solution:**
```python
# Améliorer l'affichage:
['Congés pris ce mois',
 f"{salaire_data.get('jours_conges', 0):.2f} j",  # BASE
 '',  # TAUX
 'Payé',  # GAIN
 ''],  # RETENUE
```

---

### Problème #3: Logique de répartition incohérente
**Gravité:** 🟠 IMPORTANT

**Description:**
- La répartition "intelligente" suppose qu'on saisit TOUT d'un coup
- Mais l'interface permet des saisies multiples sur différentes périodes
- Conflit entre "saisie période par période" vs "répartition automatique globale"

**Deux approches possibles:**

**Approche A: Saisie globale unique**
- Un seul bouton "Prendre X jours"
- Système répartit automatiquement
- Simple mais moins flexible

**Approche B: Saisie période par période**
- Chaque période peut être éditée indépendamment
- Validation: ne pas dépasser l'acquis de la période
- Plus complexe mais plus précis

---

## ✅ SOLUTIONS PROPOSÉES

### Solution #1: Corriger la répartition intelligente

**Option 1.A: Mode "Additionnel"**
```python
# Ne pas réinitialiser, ajouter à l'existant
def update_consommation(...):
    # Calculer le total actuel
    total_actuel = sum(p.jours_conges_pris for p in periodes_employe)
    
    # Nouveau total demandé
    nouveau_total = total_actuel + jours_pris
    
    # Réinitialiser puis répartir le NOUVEAU TOTAL
    for p in periodes_employe:
        p.jours_conges_pris = 0.0
    
    repartition = repartir_conges_intelligemment(
        jours_a_prendre=nouveau_total  # ✅ Total cumulé
    )
```

**Option 1.B: Mode "Remplacement total"**
```python
# Demander à l'utilisateur le TOTAL à prendre (pas l'ajout)
# Interface: "Total jours à prendre: [5.0]" au lieu de "Ajouter: [2.0]"
def update_consommation(...):
    # Réinitialiser
    for p in periodes_employe:
        p.jours_conges_pris = 0.0
    
    # Répartir le total saisi (qui est déjà le total global)
    repartition = repartir_conges_intelligemment(
        jours_a_prendre=jours_pris  # = Total global voulu
    )
```

---

### Solution #2: Améliorer l'affichage du bulletin

```python
# backend/services/pdf_generator.py ligne 1083
['Congés pris ce mois',
 f"{float(salaire_data.get('jours_conges', 0)):.2f} j",  # Colonne BASE
 '',                                                       # Colonne TAUX
 'Payé',                                                   # Colonne GAIN
 ''],                                                      # Colonne RETENUE
```

---

### Solution #3: Clarifier l'interface utilisateur

**Dans la modal de saisie:**
```jsx
<Alert type="info">
  <strong>Mode: Répartition automatique TOTALE</strong><br/>
  Saisissez le nombre TOTAL de jours que l'employé doit prendre.<br/>
  Le système répartira automatiquement sur les périodes disponibles.<br/>
  <strong>Attention:</strong> Cette saisie remplace toutes les saisies précédentes!
</Alert>

<Form.Item label="Total jours à prendre (remplace les saisies précédentes)">
  <InputNumber ... />
</Form.Item>
```

---

## 🎯 RECOMMANDATION FINALE

**Je recommande l'Option 1.B avec Solution #2 et #3:**

1. **Répartition globale:**
   - L'utilisateur saisit le TOTAL global de jours à prendre
   - Le système répartit intelligemment
   - Une seule saisie remplace toutes les précédentes
   - ✅ Simple et prévisible

2. **Affichage bulletin amélioré:**
   - Nombre de jours visible dans colonne BASE
   - Format cohérent entre bulletin individuel et combiné

3. **Interface explicite:**
   - Message clair: "Cette saisie remplace les précédentes"
   - Affichage du total actuel avant modification
   - Confirmation avant écrasement

---

## 📝 VÉRIFICATIONS À FAIRE SUR LE SERVEUR

1. **Vérifier les données actuelles:**
```sql
SELECT employe_id, mois, annee, jours_conges_pris, mois_deduction, annee_deduction
FROM conges
WHERE employe_id IN (SELECT id FROM employes WHERE nom IN ('SAFI', 'ZERROUG'))
ORDER BY employe_id, annee, mois;
```

2. **Vérifier ce qui est déduit pour décembre 2025:**
```sql
SELECT e.nom, c.mois, c.annee, c.jours_conges_pris, c.mois_deduction, c.annee_deduction
FROM conges c
JOIN employes e ON c.employe_id = e.id
WHERE e.nom IN ('SAFI', 'ZERROUG')
AND (
    (c.mois_deduction = 12 AND c.annee_deduction = 2025)
    OR (c.mois_deduction IS NULL AND c.mois = 12 AND c.annee = 2025)
);
```

3. **Tester le calcul du salaire en Python:**
```python
from backend.services.salaire_calculator import SalaireCalculator
# ... calcul pour décembre 2025
# Vérifier jours_conges retourné
```

---

## 🔄 PROCHAINES ÉTAPES

1. ✅ Analyser les données actuelles sur le serveur
2. ⏳ Choisir l'approche (1.A ou 1.B)
3. ⏳ Implémenter les corrections
4. ⏳ Tester avec cas réels
5. ⏳ Déployer et valider

