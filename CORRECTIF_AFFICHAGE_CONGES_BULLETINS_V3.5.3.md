# 🔧 CORRECTIF v3.5.3 - Affichage Congés dans Bulletins de Paie

**Date** : 14 décembre 2025  
**Version** : 3.5.3  
**Type** : Correctif Calcul Congés

---

## 🎯 PROBLÈME IDENTIFIÉ

**Symptôme** : Les jours de congés pris ne s'affichent pas dans les bulletins de paie PDF.

**Cause racine** : Le système ne récupérait pas les congés réels depuis la table `conges`.

### **Analyse Technique**

#### **1. Flux Actuel (Avant Correctif)**

```
┌─────────────┐
│  Pointages  │  ← Saisie quotidienne (valeur 0 ou 1)
└──────┬──────┘
       │
       │ calculer_totaux() → jours_travailles, heures_supp
       │ ❌ PAS de jours_conges
       │
       ▼
┌─────────────┐
│   Salaire   │  ← jours_conges = totaux.get("jours_conges", 0)
│  Processor  │     Résultat: 0 (car pas dans calculer_totaux())
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ PDF Bulletin│  ← jours_conges = 0 TOUJOURS
└─────────────┘     Ligne congés commentée (v3.5.3)
```

**Problèmes** :
1. ❌ `pointage.calculer_totaux()` ne retourne PAS `jours_conges`
2. ❌ Le `SalaireProcessor` utilise `totaux.get("jours_conges", 0)` → toujours 0
3. ❌ Les congés réels (table `conges`) ne sont JAMAIS consultés
4. ❌ La ligne congés était commentée dans le PDF

#### **2. Données Disponibles**

**Table `conges`** :
```sql
CREATE TABLE conges (
    id INT PRIMARY KEY,
    employe_id INT,
    annee INT,
    mois INT,
    jours_conges_acquis DECIMAL(5,2),  -- Calculés automatiquement
    jours_conges_pris DECIMAL(5,2),    -- ⭐ SAISIS manuellement (page Congés)
    jours_conges_restants DECIMAL(5,2)
);
```

**Exemple** :
```
Employé: Ahmed (ID 29)
Mois: Décembre 2025

Table conges:
- jours_conges_acquis: 2.17  (calculé: (26/30)*2.5)
- jours_conges_pris: 1.5     (saisi manuellement par utilisateur)
- jours_conges_restants: 0.67
```

**Problème** : Ces données existaient mais n'étaient PAS utilisées pour le bulletin !

---

## ✅ SOLUTION IMPLÉMENTÉE

### **1. Récupération Congés Réels** ⭐

**Fichier** : `backend/services/salary_processor.py` ligne 93

**AVANT** :
```python
# 4. Calcul totaux pointage
totaux = pointage.calculer_totaux()
jours_travailles = totaux.get("jours_travailles", 0)
jours_conges = totaux.get("jours_conges", 0)  # ❌ Toujours 0
heures_supplementaires_pointage = totaux.get("heures_supplementaires", 0)
jours_ouvrables = 30
```

**APRÈS** :
```python
# 4. Calcul totaux pointage
totaux = pointage.calculer_totaux()
jours_travailles = totaux.get("jours_travailles", 0)
heures_supplementaires_pointage = totaux.get("heures_supplementaires", 0)
jours_ouvrables = 30

# ⭐ NOUVEAU v3.5.3: Récupérer les congés RÉELS depuis la table conges
from models import Conge
conge_record = self.db.query(Conge).filter(
    Conge.employe_id == employe_id,
    Conge.annee == annee,
    Conge.mois == mois
).first()

jours_conges = float(conge_record.jours_conges_pris or 0) if conge_record else 0
```

**Impact** :
- ✅ Récupération des congés RÉELS depuis la table `conges`
- ✅ Utilise `jours_conges_pris` (saisi par utilisateur page Congés)
- ✅ Valeur correcte transmise au calcul de salaire
- ✅ Gère le cas où aucun enregistrement conge n'existe (0 congés)

---

### **2. Réactivation Ligne PDF** ⭐

**Fichier** : `backend/services/pdf_generator.py` ligne 899-903

**AVANT (v3.5.3)** :
```python
# v3.5.3: Ligne congés supprimée (masquée du bulletin)
# ['Jours de congé pris ce mois', '', ..., 'Payé', ''],
# Heures supplémentaires
```

**APRÈS** :
```python
# ⭐ RÉACTIVÉ: Affichage congés pris ce mois
['Jours de congé pris ce mois',
 '',
 f"{salaire_data.get('jours_conges', 0):.1f} j" if salaire_data.get('jours_conges', 0) > 0 else '0 j',
 'Payé',
 ''],
# Heures supplémentaires
```

**Impact** :
- ✅ Ligne congés visible dans le bulletin PDF
- ✅ Affiche le nombre de jours avec 1 décimale (ex: "1.5 j")
- ✅ Si aucun congé pris → affiche "0 j"
- ✅ Statut "Payé" (congés payés, pas de retenue salaire)

---

## 🔄 FLUX CORRIGÉ

```
┌─────────────┐
│  Pointages  │  ← Saisie quotidienne
└──────┬──────┘
       │
       │ calculer_totaux() → jours_travailles, heures_supp
       │
       ▼
┌─────────────┐
│   Congés    │  ← Saisie manuelle jours_conges_pris
│  (Table)    │     Ex: 1.5 jours pris en décembre
└──────┬──────┘
       │
       │ ⭐ NOUVEAU: Query Conge.jours_conges_pris
       │
       ▼
┌─────────────┐
│   Salaire   │  ← jours_conges = conge_record.jours_conges_pris
│  Processor  │     Résultat: 1.5 (valeur réelle)
└──────┬──────┘
       │
       │ salaire_data['jours_conges'] = 1.5
       │
       ▼
┌─────────────┐
│ PDF Bulletin│  ← Affiche "1.5 j" (Payé)
└─────────────┘     Ligne visible et correcte
```

---

## 📊 EXEMPLES CONCRETS

### **Exemple 1 : Employé avec 1.5 jours de congés**

**Données** :
```
Employé: Ahmed Benali (ID 29)
Période: Décembre 2025
Pointages: 26 jours travaillés
Congés saisis: 1.5 jours pris
```

**Table conges** :
```sql
employe_id | annee | mois | jours_conges_pris
    29     | 2025  |  12  |      1.50
```

**Bulletin PDF** (section Salaire Base) :
```
┌────────────────────────────────┬────────────┬────────┬──────────┬──────────┐
│ Éléments                       │    Base    │  Taux  │  Montant │  Déduct. │
├────────────────────────────────┼────────────┼────────┼──────────┼──────────┤
│ Salaire de Base                │ 30 000,00  │ 26/30j │ 26 000,00│          │
│ Jours de congé pris ce mois    │            │ 1.5 j  │   Payé   │          │  ← ⭐ VISIBLE
│ Heures supplémentaires         │            │        │        0 │          │
└────────────────────────────────┴────────────┴────────┴──────────┴──────────┘
```

---

### **Exemple 2 : Employé sans congés**

**Données** :
```
Employé: Fatima Zohra (ID 30)
Période: Décembre 2025
Pointages: 30 jours travaillés
Congés saisis: 0 jour pris
```

**Table conges** :
```sql
employe_id | annee | mois | jours_conges_pris
    30     | 2025  |  12  |      0.00
```

**Bulletin PDF** :
```
│ Jours de congé pris ce mois    │            │  0 j   │   Payé   │          │  ← Affiche 0 j
```

---

### **Exemple 3 : Employé sans enregistrement congé**

**Données** :
```
Employé: Nouveau (ID 45)
Période: Décembre 2025
Pointages: 15 jours travaillés
Congés: Aucun enregistrement dans table conges
```

**Code** :
```python
conge_record = db.query(Conge).filter(...).first()  # → None
jours_conges = float(conge_record.jours_conges_pris or 0) if conge_record else 0  # → 0
```

**Bulletin PDF** :
```
│ Jours de congé pris ce mois    │            │  0 j   │   Payé   │          │
```

---

## 🧪 TESTS À EFFECTUER

### **Test 1 : Employé avec congés saisis**

**Prérequis** :
1. Employé avec pointages du mois
2. Congés saisis dans page Congés (ex: 1.5j)

**Action** :
1. Générer bulletin de paie pour cet employé
2. Télécharger le PDF

**Vérification** :
- ✅ Ligne "Jours de congé pris ce mois" visible
- ✅ Affiche "1.5 j" (valeur saisie)
- ✅ Statut "Payé"

---

### **Test 2 : Employé sans congés**

**Prérequis** :
1. Employé avec pointages du mois
2. Aucun congé saisi (0 jour)

**Action** :
1. Générer bulletin de paie
2. Télécharger PDF

**Vérification** :
- ✅ Ligne "Jours de congé pris ce mois" visible
- ✅ Affiche "0 j"
- ✅ Statut "Payé"

---

### **Test 3 : Vérification calcul salaire**

**Scénario** :
```
Salaire base: 30 000 DA
Jours travaillés: 26
Jours congés pris: 2
```

**Calcul attendu** :
```python
# Avec congés → pas de proratisation
if jours_conges > 0:
    salaire_base_proratis = salaire_base  # = 30 000 DA
else:
    salaire_base_proratis = (30000 / 30) * 26  # = 26 000 DA
```

**Résultat** : Si congés > 0 → Salaire plein (pas de perte)

---

## 📝 NOTES IMPORTANTES

### **Cohérence Données**

**Ordre de saisie recommandé** :
1. ✅ Saisir pointages du mois
2. ✅ Générer rapport pointages PDF (crée/met à jour congés)
3. ✅ Aller dans Congés → Saisir jours_conges_pris
4. ✅ Générer bulletins de paie

**Pourquoi** : Le rapport pointages crée les enregistrements `conges` avec `jours_conges_acquis` calculés. Ensuite, l'utilisateur saisit `jours_conges_pris`. Enfin, le bulletin utilise cette donnée.

---

### **Impact Proratisation**

**AVANT** :
```python
# jours_conges = 0 TOUJOURS
if jours_conges > 0:  # ❌ Jamais vrai
    salaire_base_proratis = salaire_base
else:
    salaire_base_proratis = (salaire_base / 30) * jours_travailles  # Toujours proratis
```

**APRÈS** :
```python
# jours_conges = valeur réelle (ex: 1.5)
if jours_conges > 0:  # ✅ Vrai si congés saisis
    salaire_base_proratis = salaire_base  # Salaire plein
else:
    salaire_base_proratis = (salaire_base / 30) * jours_travailles
```

**Règle** : Si l'employé a pris des congés → salaire de base NON proratisé (congés payés).

---

### **Compatibilité**

| Composant | Impact | Action requise |
|-----------|--------|----------------|
| **Backend** | Modification | ✅ Redémarrage |
| **Frontend** | Aucun | ❌ Rien |
| **Base de données** | Aucun | ❌ Rien |
| **Bulletins PDF** | Affichage modifié | ℹ️ Régénérer |

---

## 🚀 DÉPLOIEMENT

### **Étape 1 : Pull + Redémarrage**

```bash
ssh root@192.168.20.55

cd /opt/ay-hr
git pull origin main

# Redémarrer backend
sudo systemctl restart ayhr-backend

# Vérifier
sudo journalctl -u ayhr-backend -n 20 --no-pager
```

---

### **Étape 2 : Test Génération Bulletin**

```bash
# Via interface ou API
curl -X POST "http://localhost:8000/api/salaires/generer-bulletins" \
  -H "Content-Type: application/json" \
  -d '{
    "annee": 2025,
    "mois": 12,
    "jours_supplementaires": 0
  }'
```

**Vérification** :
- Ouvrir le PDF généré
- Vérifier présence ligne "Jours de congé pris ce mois"
- Vérifier valeur correcte (ex: "1.5 j")

---

## 🎯 RÉSUMÉ

### **Problème**
Les congés ne s'affichaient pas dans les bulletins car :
1. Le système ne consultait pas la table `conges`
2. La ligne PDF était commentée

### **Solution**
1. ✅ Récupération `jours_conges_pris` depuis table `conges`
2. ✅ Réactivation ligne congés dans PDF bulletin
3. ✅ Affichage avec décimale (ex: "1.5 j")

### **Fichiers Modifiés**
1. `backend/services/salary_processor.py` - Ligne 93 (récupération congés)
2. `backend/services/pdf_generator.py` - Ligne 899 (affichage ligne)

### **Impact**
- ✅ Congés affichés correctement dans bulletins
- ✅ Données réelles utilisées (saisie utilisateur)
- ✅ Proratisation salaire correcte (congés payés)

---

**Document créé le** : 14 décembre 2025  
**Auteur** : GitHub Copilot  
**Version** : 3.5.3
