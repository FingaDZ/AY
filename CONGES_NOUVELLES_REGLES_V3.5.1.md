# 📅 Système de Congés v3.5.1 - Nouvelles Règles

**Date de mise à jour** : 12 décembre 2025  
**Version** : 3.5.1  
**Statut** : ✅ Implémenté et testé

---

## 🎯 Objectif des Modifications

Simplifier le système de congés pour le rendre plus compréhensible et conforme aux règles métier de l'entreprise.

---

## 📊 Anciennes vs Nouvelles Règles

### ❌ ANCIENNES RÈGLES (v3.5.0)

```
- 30 jours travaillés = 2.5 jours de congé
- Calcul proportionnel: (jours_travailles / 30) * 2.5
- Minimum 8 jours pour avoir 1 jour
- Nouveaux: minimum 15 jours pour 2.5 jours
- Résultat avec décimales (0.3j, 0.8j, 1.2j...)
- Congés pris INCLUS dans le calcul des jours travaillés
```

**Problèmes** :
- ❌ Décimales difficiles à gérer (0.3 jour = ?)
- ❌ Logique complexe (ratio 2.5/30)
- ❌ Jours de congé comptés comme travaillés → double comptage

### ✅ NOUVELLES RÈGLES (v3.5.1)

#### **RÈGLE 1 : 8 jours travaillés = 1 jour de congé**

Arrondi intelligent par tranches :

| Jours travaillés | Jours congé acquis |
|------------------|-------------------|
| 0-7 jours        | 0 jour           |
| 8-15 jours       | 1 jour           |
| 16-23 jours      | 2 jours          |
| 24-30+ jours     | 3 jours          |

#### **RÈGLE 2 : Nouveaux recrutés (<3 mois d'ancienneté)**

Protection des nouveaux employés :

| Jours travaillés | Jours congé acquis |
|------------------|-------------------|
| 0-14 jours       | 0 jour           |
| 15-22 jours      | 1 jour           |
| 23-30 jours      | 2 jours          |

#### **RÈGLE 3 : Plus de décimales**

- ✅ Toutes les valeurs sont des **INTEGER**
- ✅ Plus de 0.3j, 0.8j, ou 1.2j
- ✅ Arrondi intelligent par tranches (pas d'arrondi mathématique)
- ✅ Cohérence avec la gestion administrative

#### **RÈGLE 4 : Exclusion des congés pris (CRITIQUE)**

**Principe** : Les jours de congé PRIS ne comptent PAS pour le calcul des droits.

**Exemple concret** :
```
Situation : Employé travaille 8 jours + prend 20 jours de congé
- jours_travailles_brut = 28 jours (8 + 20, car Congé = valeur 1)
- jours_conges_pris = 20 jours
- jours_reellement_travailles = 28 - 20 = 8 jours
- jours_conges_acquis = 1 jour (règle: 8j = 1j)
```

**Avant v3.5.1** :
- jours_travailles = 28
- jours_conges_acquis = 3 jours ❌ (28j → 3j selon ancienne règle)
- **ERREUR** : Double comptage !

**Après v3.5.1** :
- jours_reellement_travailles = 8
- jours_conges_acquis = 1 jour ✅
- **CORRECT** : Seuls les jours réellement travaillés comptent

---

## 🔧 Implémentation Technique

### **Fichiers modifiés**

#### 1. `backend/models/conge.py`

**Méthode** : `calculer_jours_conges(jours_travailles, est_nouveau_recrue) -> int`

```python
# Ancienne signature
def calculer_jours_conges(...) -> float:  # Retournait des décimales

# Nouvelle signature
def calculer_jours_conges(...) -> int:    # Retourne des entiers

# Nouvelle logique par tranches
if est_nouveau_recrue:
    if jours_travailles < 15: return 0
    elif jours_travailles < 23: return 1
    else: return 2
else:
    if jours_travailles < 8: return 0
    elif jours_travailles < 16: return 1
    elif jours_travailles < 24: return 2
    else: return 3
```

**Changements colonnes DB** :
```python
# Ancien
jours_conges_acquis = Column(Numeric(5, 2), default=0.00)  # Décimales
jours_conges_pris = Column(Numeric(5, 2), default=0.00)

# Nouveau
jours_conges_acquis = Column(Integer, default=0)  # Entiers
jours_conges_pris = Column(Integer, default=0)
```

#### 2. `backend/routers/pointages.py`

**Ajout exclusion congés pris** :

```python
# AVANT v3.5.1
jours_travailles = totaux.get('jours_travailles', 0)
jours_conges_acquis = Conge.calculer_jours_conges(jours_travailles, ...)

# APRÈS v3.5.1
jours_travailles_brut = totaux.get('jours_travailles', 0)

# Récupérer les congés PRIS ce mois
conge_existant = db.query(Conge).filter(...).first()
jours_conges_pris = int(conge_existant.jours_conges_pris) if conge_existant else 0

# IMPORTANT: Exclure les congés du calcul
jours_reellement_travailles = max(0, jours_travailles_brut - jours_conges_pris)

# Calculer les droits sur jours réels uniquement
jours_conges_acquis = Conge.calculer_jours_conges(jours_reellement_travailles, ...)
```

#### 3. `backend/routers/conges.py`

**Conversions float → int** partout :

```python
# Schemas Pydantic
class CongeUpdate(BaseModel):
    jours_pris: int  # Était: float

class CongeResponse(BaseModel):
    jours_conges_acquis: int  # Était: float
    jours_conges_pris: int
    jours_conges_restants: int

# Conversions dans les endpoints
int(conge.jours_conges_acquis or 0)  # Au lieu de float()
```

#### 4. `backend/services/pdf_generator.py`

**Ligne congés dans bulletin de paie** (déjà présente, ligne 899-902) :

```python
['Jours de congé pris ce mois',
 '',
 f"{salaire_data.get('jours_conges', 0)} j" if salaire_data.get('jours_conges', 0) > 0 else '0 j',
 'Payé',
 ''],
```

---

## 🗄️ Migration Base de Données

### **Script SQL fourni**

Fichier : `database/migration_conges_v3.5.1.sql`

```sql
-- Modifier les types de colonnes DECIMAL → INTEGER
ALTER TABLE conges 
    MODIFY COLUMN jours_conges_acquis INT DEFAULT 0,
    MODIFY COLUMN jours_conges_pris INT DEFAULT 0,
    MODIFY COLUMN jours_conges_restants INT DEFAULT 0;

-- Arrondir les valeurs existantes
UPDATE conges SET jours_conges_acquis = ROUND(jours_conges_acquis);
UPDATE conges SET jours_conges_pris = ROUND(jours_conges_pris);
UPDATE conges SET jours_conges_restants = jours_conges_acquis - jours_conges_pris;
```

### **Exécution sur le serveur**

```bash
# Connexion à la base
mysql -u root -p ay_hr

# Exécuter le script
source /opt/ay-hr/database/migration_conges_v3.5.1.sql

# Vérifier
SELECT * FROM conges ORDER BY id DESC LIMIT 10;
```

---

## 📋 Exemples de Calcul

### **Exemple 1 : Employé standard travaillant un mois complet**

```
Situation :
- 26 jours réellement travaillés
- 0 jour de congé pris

Calcul v3.5.1 :
- jours_reellement_travailles = 26
- Règle: 24-30 jours → 3 jours acquis
- jours_conges_acquis = 3 jours ✅
```

### **Exemple 2 : Employé avec congés pris**

```
Situation :
- 8 jours travaillés + 20 jours de congé = 28 jours en pointage
- jours_conges_pris = 20 (saisi manuellement)

Calcul v3.5.1 :
- jours_travailles_brut = 28
- jours_conges_pris = 20
- jours_reellement_travailles = 28 - 20 = 8
- Règle: 8-15 jours → 1 jour acquis
- jours_conges_acquis = 1 jour ✅

Calcul ANCIEN (v3.5.0) :
- jours_travailles = 28
- jours_conges_acquis = (28/30)*2.5 = 2.3 jours ❌
```

### **Exemple 3 : Nouveau recruté**

```
Situation :
- Employé recruté il y a 2 mois
- 18 jours réellement travaillés

Calcul v3.5.1 :
- est_nouveau_recrue = True (< 3 mois)
- jours_reellement_travailles = 18
- Règle nouveau: 15-22 jours → 1 jour
- jours_conges_acquis = 1 jour ✅
```

### **Exemple 4 : Nouveau recruté insuffisant**

```
Situation :
- Employé recruté il y a 1 mois
- 12 jours réellement travaillés

Calcul v3.5.1 :
- est_nouveau_recrue = True
- jours_reellement_travailles = 12
- Règle: < 15 jours → 0 jour
- jours_conges_acquis = 0 jour ✅ (protection)
```

---

## ✅ Tests de Validation

### **Test 1 : Calcul simple (8 jours)**

```python
from backend.models.conge import Conge

jours = Conge.calculer_jours_conges(8, False)
assert jours == 1  # ✅ 8-15 jours → 1 jour
```

### **Test 2 : Calcul avec congés pris**

```python
# Simulation
jours_brut = 28  # 8 réels + 20 congés
jours_conges_pris = 20
jours_reels = max(0, jours_brut - jours_conges_pris)  # = 8

jours_acquis = Conge.calculer_jours_conges(jours_reels, False)
assert jours_acquis == 1  # ✅ Correct
```

### **Test 3 : Nouveau recruté**

```python
jours = Conge.calculer_jours_conges(12, True)
assert jours == 0  # ✅ < 15 jours pour nouveau

jours = Conge.calculer_jours_conges(18, True)
assert jours == 1  # ✅ 15-22 jours → 1 jour
```

---

## 🚀 Déploiement sur Serveur

### **Étapes de déploiement**

```bash
# 1. Connexion au serveur
ssh root@192.168.20.55

# 2. Aller au répertoire du projet
cd /opt/ay-hr

# 3. Pull des dernières modifications
git pull origin main

# 4. Exécuter la migration SQL
mysql -u root -p ay_hr < database/migration_conges_v3.5.1.sql

# 5. Rebuild frontend (nouvelles fonctionnalités UI)
cd frontend
npm run build

# 6. Redémarrer les services
cd /opt/ay-hr
sudo systemctl restart ayhr-backend
sudo systemctl restart ayhr-frontend

# 7. Vérifier les logs
sudo journalctl -u ayhr-backend -n 50 --no-pager
sudo journalctl -u ayhr-frontend -n 20 --no-pager

# 8. Tester dans le frontend
# - Aller sur Congés → Vérifier les valeurs entières
# - Essayer de saisir congés > acquis (doit bloquer)
# - Générer bulletins → Vérifier notification si congés manquants
```

---

## 📊 Impact sur les Données Existantes

### **Avant migration**

```sql
SELECT * FROM conges LIMIT 3;
+----+------------+------+------+---------+---------------------+-------------------+-----------------------+
| id | employe_id | annee| mois | jours_  | jours_conges_acquis | jours_conges_pris | jours_conges_restants |
|    |            |      |      | travail |                     |                   |                       |
+----+------------+------+------+---------+---------------------+-------------------+-----------------------+
| 1  | 29         | 2025 | 11   | 26      | 2.17                | 0.00              | 2.17                  |
| 2  | 30         | 2025 | 11   | 25      | 2.08                | 5.00              | -2.92                 |
| 3  | 67         | 2025 | 11   | 30      | 2.50                | 0.00              | 2.50                  |
+----+------------+------+------+---------+---------------------+-------------------+-----------------------+
```

### **Après migration**

```sql
SELECT * FROM conges LIMIT 3;
+----+------------+------+------+---------+---------------------+-------------------+-----------------------+
| id | employe_id | annee| mois | jours_  | jours_conges_acquis | jours_conges_pris | jours_conges_restants |
|    |            |      |      | travail |                     |                   |                       |
+----+------------+------+------+---------+---------------------+-------------------+-----------------------+
| 1  | 29         | 2025 | 11   | 26      | 2                   | 0                 | 2                     |
| 2  | 30         | 2025 | 11   | 25      | 2                   | 5                 | -3                    |
| 3  | 67         | 2025 | 11   | 30      | 3                   | 0                 | 3                     |
+----+------------+------+------+---------+---------------------+-------------------+-----------------------+
```

**Note** : ✅ **v3.5.1** Soldes négatifs maintenant impossibles grâce à la validation stricte

---

## 📝 Notes Importantes

### **⚠️ Attention**

1. **Congés pris doivent être saisis** : 
   - ✅ **NOUVEAU v3.5.1** : Une notification apparaît avant la génération des bulletins de paie
   - Si des congés ne sont pas saisis, l'utilisateur est redirigé vers la page Congés
   - Le système compte sur `jours_conges_pris` pour le calcul. Si non renseigné, le calcul sera faux.

2. **Validation stricte congés pris > acquis** :
   - ✅ **NOUVEAU v3.5.1** : Le système **BLOQUE** toute saisie de congés pris supérieure aux congés acquis
   - Message d'erreur : "INTERDIT: Congés pris (Xj) > Congés acquis (Yj). Solde insuffisant!"
   - Plus de solde négatif possible

3. **Cohérence Pointages ↔ Congés** : 
   - Pointages : Congé = valeur 1 (payé)
   - Table conges : Comptage manuel via API ou UI

4. **Recalcul automatique** : À chaque génération de rapport PDF pointages mensuel

5. **Migration une seule fois** : Ne pas réexécuter le script SQL après première application

### **✅ Avantages**

- Règles simples et compréhensibles
- Plus de décimales difficiles à gérer
- Calcul correct excluant double comptage
- Cohérence avec gestion administrative
- Performance améliorée (integers vs decimals)
- **✅ v3.5.1** : Protection contre solde négatif (validation stricte)
- **✅ v3.5.1** : Notification automatique avant génération bulletins
- **✅ v3.5.1** : Redirection intelligente vers page Congés

---

## 🆕 Améliorations Supplémentaires v3.5.1

### **1. Blocage Congés Pris > Acquis**

**Problème** : Avant, il était possible de saisir plus de congés pris que de congés acquis, créant des soldes négatifs.

**Solution** : Validation stricte dans le backend

```python
# backend/routers/conges.py - update_consommation
total_acquis = int(stats.total_acquis or 0)
total_pris_prevu = int(total_pris_autres) + jours_pris

if total_pris_prevu > total_acquis:
    raise HTTPException(
        status_code=400,
        detail=f"INTERDIT: Congés pris ({total_pris_prevu}j) > Congés acquis ({total_acquis}j)"
    )
```

**Test** :
```bash
# Scénario : Employé a 3 jours acquis, essai de saisir 5 jours pris
# Résultat attendu : Erreur 400 "INTERDIT: Congés pris (5j) > Congés acquis (3j)"
```

### **2. Notification Avant Génération Bulletins**

**Problème** : Les utilisateurs oubliaient de saisir les congés pris avant de générer les bulletins.

**Solution** : Modal de vérification automatique

**Backend Endpoint** :
```python
# GET /api/conges/verifier-saisie/{annee}/{mois}
{
  "annee": 2025,
  "mois": 12,
  "conges_non_saisis": [
    {
      "employe_id": 29,
      "employe_nom": "Ahmed Benali",
      "jours_acquis": 3,
      "conge_id": 123
    }
  ],
  "count": 1,
  "a_verifier": true
}
```

**Frontend** : Modal avec redirection

```jsx
// frontend/src/pages/Salaires/SalaireCalcul.jsx
const verif = await verifierCongesAvantGeneration();

if (verif.a_verifier && verif.count > 0) {
  Modal.confirm({
    title: 'Attention : Congés non saisis',
    content: `Il y a ${verif.count} employé(s) avec congés non saisis`,
    okText: 'Oui, aller aux Congés',
    onOk: () => navigate('/conges'),
    onCancel: () => procederGenerationBulletins()
  });
}
```

**Flux** :
1. Utilisateur clique "Générer Bulletins"
2. Vérification automatique des congés
3. Si congés non saisis → Modal d'avertissement
4. Choix : Aller aux Congés OU Continuer quand même

### **3. Correction Versions**

Mise à jour cohérente de la version **3.5.1** dans :

- ✅ `backend/config.py` : `APP_VERSION = "3.5.1"`
- ✅ `frontend/package.json` : `"version": "3.5.1"`
- ✅ `frontend/src/components/Layout.jsx` : Footer version
- ✅ `frontend/src/pages/Dashboard.jsx` : Badge version
- ✅ `frontend/src/pages/Login/LoginPage.jsx` : Version login
- ✅ `README.md` : Header et changelog

---

## 🔗 Références

- **Commit principal** : `6b2612b` (feat: nouvelles règles congés)
- **Commit README** : `e957b8b` (docs: update README)
- **Fichiers modifiés** :
  - `backend/models/conge.py`
  - `backend/routers/pointages.py`
  - `backend/routers/conges.py`
  - `database/migration_conges_v3.5.1.sql`
  - `README.md`

---

**Document créé le** : 12 décembre 2025  
**Auteur** : Équipe AY HR Development  
**Version** : 3.5.1
