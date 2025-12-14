# 📊 ANALYSE COMPLÈTE - Logique Congés v3.5.3

**Date** : 14 décembre 2025  
**Contexte** : Problèmes identifiés après vidage DB + traitement salaires

---

## 🚨 PROBLÈMES IDENTIFIÉS

### **Problème 1 : Calcul des congés UNIQUEMENT lors génération rapport PDF**

**Situation actuelle** :
- Les congés sont calculés **SEULEMENT** quand on génère le rapport PDF mensuel (`GET /pointages/rapport-pdf/mensuel`)
- Quand on enregistre/modifie un pointage → **AUCUN recalcul automatique**
- Impact : Base de données vide (pas d'enregistrements `Conge`) tant qu'on ne génère pas le rapport

**Code actuel** (dans `backend/routers/pointages.py` ligne 407-463) :
```python
@router.get("/rapport-pdf/mensuel")
def generer_rapport_pointages_mensuel(...):
    # ... récupération pointages ...
    
    for idx, (emp_id, data) in enumerate(employes_pointages.items(), 1):
        # ... calculs ...
        
        # C'EST ICI que les congés sont calculés et enregistrés
        conge_record = db.query(Conge).filter(...).first()
        
        if conge_existant:
            # Mise à jour
            conge_existant.jours_conges_acquis = jours_conges_acquis
        else:
            # Création
            conge_record = Conge(...)
            db.add(conge_record)
        
        db.commit()  # ← ENREGISTREMENT ICI SEULEMENT
```

**Problème** : Si l'utilisateur :
1. Crée/modifie pointages
2. Va dans Congés avant de générer le rapport
3. Essaie d'affecter des jours de congés pris

→ **Erreur 500** car l'enregistrement `Conge` n'existe pas encore !

---

### **Problème 2 : Erreur 500 lors de l'affectation de congés pris**

**Erreur observée** :
```
PUT https://.../api/conges/204/consommation 500 (Internal Server Error)
```

**Cause identifiée** :

1. **Absence d'enregistrement Conge** :
   - L'employé a des pointages
   - Mais pas encore d'enregistrement dans `conges` (table vide après vidage)
   - Le endpoint `update_consommation` fait un `db.query(Conge).filter(Conge.id == conge_id).first()`
   - Retourne `None` → HTTPException 404 **OU** erreur plus bas dans le code

2. **Problème de validation** :
   ```python
   # Ligne 107-119 de backend/routers/conges.py
   stats = db.query(
       func.sum(Conge.jours_conges_acquis).label("total_acquis")
   ).filter(Conge.employe_id == conge.employe_id).first()
   
   total_acquis = float(stats.total_acquis or 0)  # ← Si table vide, stats.total_acquis = None
   ```
   
   **Si aucun `Conge` n'existe** → `total_acquis = 0.0`
   
   Ensuite :
   ```python
   if total_pris_prevu > total_acquis:  # Si on veut affecter 1j et total_acquis = 0
       raise HTTPException(status_code=400, ...)  # ← BLOCAGE !
   ```

3. **Impact traitement salaires** :
   - Si vous avez généré les salaires AVANT les congés
   - Les congés n'ont pas été créés
   - Le système bloque toute saisie car `total_acquis = 0`

---

## 🔍 LOGIQUE ACTUELLE DES CONGÉS

### **1. Création/Enregistrement des Congés**

#### **A. Quand sont créés les enregistrements `Conge` ?**

**Méthode 1 : Génération rapport PDF pointages** ✅ PRINCIPAL
```
GET /pointages/rapport-pdf/mensuel?annee=2025&mois=12

1. Récupère tous les pointages du mois
2. Pour chaque employé :
   - Calcule jours_travailles (totaux depuis pointages)
   - Récupère conge_existant (si existe)
   - Calcule jours_reellement_travailles = jours_brut - jours_pris
   - Calcule jours_conges_acquis = Conge.calculer_jours_conges(...)
   - INSERT/UPDATE dans table `conges`
3. Génère le PDF
```

**Méthode 2 : Endpoint création depuis dates** (rarement utilisé)
```
POST /conges/creer-depuis-dates
Body: {
  "employe_id": 123,
  "date_debut": "2025-12-01",
  "date_fin": "2025-12-05",
  "type_conge": "ANNUEL"
}

→ Crée les enregistrements Conge pour chaque mois concerné
→ Marque les jours dans les Pointages (valeur = 1)
```

#### **B. Données stockées dans table `conges`**

```sql
CREATE TABLE conges (
    id INT PRIMARY KEY,
    employe_id INT,
    annee INT,
    mois INT,
    jours_travailles INT,           -- Jours RÉELLEMENT travaillés (sans congés pris)
    jours_conges_acquis DECIMAL(5,2), -- v3.5.3: Calculé avec formule (jours/30)*2.5
    jours_conges_pris DECIMAL(5,2),   -- v3.5.3: Saisi manuellement par utilisateur
    jours_conges_restants DECIMAL(5,2), -- = acquis - pris
    date_debut DATE,                -- Si congé planifié
    date_fin DATE,
    type_conge VARCHAR(50),
    commentaire VARCHAR(500)
);
```

---

### **2. Calcul des Congés Acquis**

**Formule v3.5.3** (dans `backend/models/conge.py`) :

```python
@staticmethod
def calculer_jours_conges(jours_travailles: int, est_nouveau_recrue: bool = False) -> float:
    """
    v3.5.3: Maximum 2.5j/mois
    Formule: (jours_travaillés / 30) * 2.5
    """
    from decimal import Decimal, ROUND_HALF_UP
    
    if jours_travailles <= 0:
        return 0.0
    
    # (jours / 30) * 2.5
    jours_decimal = Decimal(str(jours_travailles))
    conges_calcules = (jours_decimal / Decimal('30')) * Decimal('2.5')
    
    # Arrondi à 2 décimales
    conges_arrondis = float(conges_calcules.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    # Maximum 2.5 jours/mois
    return min(conges_arrondis, 2.5)
```

**Exemples** :
| Jours travaillés | Calcul | Résultat |
|------------------|--------|----------|
| 15j | (15/30)*2.5 | 1.25j |
| 20j | (20/30)*2.5 | 1.67j |
| 26j | (26/30)*2.5 | 2.17j |
| 30j | (30/30)*2.5 | 2.50j |

---

### **3. Consommation des Congés**

#### **A. Saisie manuelle (Interface Congés)**

**Endpoint** : `PUT /conges/{conge_id}/consommation`

```python
def update_consommation(conge_id: int, update: CongeUpdate, ...):
    # 1. Récupérer l'enregistrement Conge
    conge = db.query(Conge).filter(Conge.id == conge_id).first()
    if not conge:
        raise HTTPException(404, "Enregistrement congé non trouvé")  # ← ERREUR SI PAS CRÉÉ !
    
    # 2. Valider jours_pris <= total_acquis
    jours_pris = float(update.jours_pris)
    
    stats = db.query(func.sum(Conge.jours_conges_acquis)...).first()
    total_acquis = float(stats.total_acquis or 0)
    
    total_pris_autres = db.query(func.sum(Conge.jours_conges_pris)...).scalar() or 0
    total_pris_prevu = float(total_pris_autres) + jours_pris
    
    if total_pris_prevu > total_acquis:  # ← BLOQUE SI total_acquis = 0 !
        raise HTTPException(400, "INTERDIT: Congés pris > acquis")
    
    # 3. Mise à jour
    conge.jours_conges_pris = jours_pris
    conge.jours_conges_restants = conge.jours_conges_acquis - conge.jours_conges_pris
    
    db.commit()
```

**Conditions de succès** :
1. ✅ L'enregistrement `Conge` DOIT exister (créé via rapport PDF)
2. ✅ `total_acquis` > 0 (au moins un mois avec congés calculés)
3. ✅ `jours_pris <= total_acquis`

#### **B. Impact sur le calcul des jours travaillés**

**RÈGLE 4 v3.5.1** : Les congés PRIS ne comptent PAS pour les droits

```python
# Dans generer_rapport_pointages_mensuel()
jours_travailles_brut = totaux.get('jours_travailles', 0)  # Ex: 28j (inclut congés car valeur=1)

# Récupérer congés PRIS
jours_conges_pris = int(conge_existant.jours_conges_pris) if conge_existant else 0  # Ex: 20j

# IMPORTANT: Exclure les congés du calcul
jours_reellement_travailles = max(0, jours_travailles_brut - jours_conges_pris)  # = 8j

# Calculer droits SEULEMENT sur jours réels
jours_conges_acquis = Conge.calculer_jours_conges(jours_reellement_travailles, ...)  # = 1j (v3.5.1) ou 0.67j (v3.5.3)
```

---

### **4. Relations et Dépendances**

```
┌─────────────┐
│  Pointages  │  ← Saisie manuelle (valeur 0 ou 1 par jour)
└──────┬──────┘
       │
       │ 1. Génération rapport PDF
       │ 2. Calcul totaux (jours_travailles)
       │
       ▼
┌─────────────┐
│   Congés    │  ← Création/MAJ automatique lors rapport
└──────┬──────┘
       │
       │ 3. Saisie manuelle jours_pris (Interface Congés)
       │ 4. Validation (pris <= acquis)
       │
       ▼
┌─────────────┐
│  Salaires   │  ← Utilise jours_conges_pris pour PDF bulletin
└─────────────┘
```

**Dépendances** :
1. **Pointages** → Calcul congés acquis (via rapport PDF)
2. **Congés** → Validation consommation
3. **Congés** → Génération salaires (jours_conges_pris affiché sur bulletin)

---

## ✅ SOLUTIONS PROPOSÉES

### **Solution 1 : Calcul automatique des congés à chaque modification de pointage** ⭐ RECOMMANDÉ

**Objectif** : Ne plus dépendre de la génération du rapport PDF

#### **A. Créer une fonction helper**

Nouveau fichier : `backend/services/conges_calculator.py`

```python
from sqlalchemy.orm import Session
from models import Conge, Pointage, Employe
from datetime import datetime

def calculer_et_enregistrer_conges(
    db: Session,
    employe_id: int,
    annee: int,
    mois: int
) -> Conge:
    """
    Calculer et enregistrer/mettre à jour les congés pour un employé/période
    
    Retourne: L'enregistrement Conge créé/mis à jour
    """
    # 1. Récupérer le pointage
    pointage = db.query(Pointage).filter(
        Pointage.employe_id == employe_id,
        Pointage.annee == annee,
        Pointage.mois == mois
    ).first()
    
    if not pointage:
        # Pas de pointage = pas de congés
        return None
    
    # 2. Calculer totaux
    totaux = pointage.calculer_totaux()
    jours_travailles_brut = totaux.get('jours_travailles', 0)
    
    # 3. Récupérer congés existants (pour jours_pris)
    conge_existant = db.query(Conge).filter(
        Conge.employe_id == employe_id,
        Conge.annee == annee,
        Conge.mois == mois
    ).first()
    
    jours_conges_pris = float(conge_existant.jours_conges_pris or 0) if conge_existant else 0.0
    
    # 4. RÈGLE 4: Exclure congés pris du calcul
    jours_reellement_travailles = max(0, jours_travailles_brut - int(jours_conges_pris))
    
    # 5. Vérifier si nouveau recruté
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    est_nouveau_recrue = False
    if employe and employe.date_recrutement:
        mois_anciennete = (datetime.now().year - employe.date_recrutement.year) * 12 + \
                         (datetime.now().month - employe.date_recrutement.month)
        est_nouveau_recrue = mois_anciennete < 3
    
    # 6. Calculer congés acquis
    jours_conges_acquis = Conge.calculer_jours_conges(jours_reellement_travailles, est_nouveau_recrue)
    
    # 7. Enregistrer/Mettre à jour
    if conge_existant:
        conge_existant.jours_travailles = jours_reellement_travailles
        conge_existant.jours_conges_acquis = jours_conges_acquis
        # jours_conges_pris reste inchangé (saisi manuellement)
        conge_existant.jours_conges_restants = jours_conges_acquis - float(conge_existant.jours_conges_pris or 0)
        db.commit()
        db.refresh(conge_existant)
        return conge_existant
    else:
        nouveau_conge = Conge(
            employe_id=employe_id,
            annee=annee,
            mois=mois,
            jours_travailles=jours_reellement_travailles,
            jours_conges_acquis=jours_conges_acquis,
            jours_conges_pris=0.0,
            jours_conges_restants=jours_conges_acquis
        )
        db.add(nouveau_conge)
        db.commit()
        db.refresh(nouveau_conge)
        return nouveau_conge
```

#### **B. Appeler cette fonction après chaque opération pointage**

**Modifier `backend/routers/pointages.py`** :

```python
from services.conges_calculator import calculer_et_enregistrer_conges

# Dans create_pointage() - APRÈS db.commit()
@router.post("/", response_model=PointageResponse, status_code=201)
def create_pointage(...):
    # ... code existant ...
    db.add(db_pointage)
    db.commit()
    db.refresh(db_pointage)
    
    # ⭐ NOUVEAU: Calculer congés automatiquement
    calculer_et_enregistrer_conges(
        db=db,
        employe_id=pointage.employe_id,
        annee=pointage.annee,
        mois=pointage.mois
    )
    
    # ... rest of code ...
    return _pointage_to_response(db_pointage)

# Dans update_pointage() - APRÈS db.commit()
@router.put("/{pointage_id}")
def update_pointage(...):
    # ... code existant ...
    db.commit()
    db.refresh(pointage)
    
    # ⭐ NOUVEAU: Recalculer congés automatiquement
    calculer_et_enregistrer_conges(
        db=db,
        employe_id=pointage.employe_id,
        annee=pointage.annee,
        mois=pointage.mois
    )
    
    # ... rest of code ...
    return _pointage_to_response(pointage)
```

**Avantages** :
- ✅ Congés calculés en temps réel
- ✅ Plus besoin de générer le rapport avant d'affecter congés
- ✅ Base de données toujours à jour
- ✅ Pas de changement dans l'interface

---

### **Solution 2 : Gérer l'absence d'enregistrement Conge dans l'endpoint consommation**

**Modifier `backend/routers/conges.py`** ligne 86-95 :

```python
@router.put("/{conge_id}/consommation")
def update_consommation(
    conge_id: int,
    update: CongeUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour la consommation de congés pour un mois donné"""
    conge = db.query(Conge).filter(Conge.id == conge_id).first()
    if not conge:
        # ⭐ NOUVEAU: Message explicite
        raise HTTPException(
            status_code=404,
            detail="Enregistrement congé non trouvé. Veuillez d'abord générer le rapport de pointages mensuel pour créer les congés."
        )
    
    # ⭐ ALTERNATIVE: Créer automatiquement l'enregistrement
    if not conge:
        # Récupérer infos depuis l'ID ou via paramètres supplémentaires
        # Puis appeler calculer_et_enregistrer_conges()
        raise HTTPException(400, "Impossible de créer automatiquement. Générez d'abord le rapport.")
    
    # ... rest of code ...
```

**OU mieux** : Changer l'endpoint pour accepter employe_id/annee/mois au lieu de conge_id :

```python
@router.put("/consommation")  # Plus de conge_id dans l'URL
def update_consommation(
    employe_id: int,
    annee: int,
    mois: int,
    update: CongeUpdate,
    ...
):
    """Mettre à jour la consommation de congés"""
    
    # Chercher/Créer l'enregistrement
    conge = db.query(Conge).filter(
        Conge.employe_id == employe_id,
        Conge.annee == annee,
        Conge.mois == mois
    ).first()
    
    if not conge:
        # ⭐ Créer automatiquement avec calcul
        from services.conges_calculator import calculer_et_enregistrer_conges
        conge = calculer_et_enregistrer_conges(db, employe_id, annee, mois)
        
        if not conge:
            raise HTTPException(
                400,
                "Aucun pointage trouvé pour cette période. Impossible de créer les congés."
            )
    
    # ... rest of validation and update ...
```

---

### **Solution 3 : Endpoint de recalcul batch** (Complément)

**Ajouter endpoint pour recalculer tous les congés** :

```python
@router.post("/recalculer-periode")
def recalculer_conges_periode(
    annee: int,
    mois: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recalculer tous les congés pour une période donnée
    Utile après vidage DB ou corrections
    """
    from services.conges_calculator import calculer_et_enregistrer_conges
    
    # Récupérer tous les pointages de la période
    pointages = db.query(Pointage).filter(
        Pointage.annee == annee,
        Pointage.mois == mois
    ).all()
    
    results = []
    for p in pointages:
        conge = calculer_et_enregistrer_conges(
            db=db,
            employe_id=p.employe_id,
            annee=annee,
            mois=mois
        )
        
        if conge:
            results.append({
                "employe_id": p.employe_id,
                "jours_acquis": float(conge.jours_conges_acquis),
                "status": "recalculé"
            })
    
    return {
        "message": f"Recalcul terminé pour {mois}/{annee}",
        "count": len(results),
        "details": results
    }
```

**Utilisation** :
```bash
# Après vidage DB, recalculer tous les congés
curl -X POST http://localhost:8000/api/conges/recalculer-periode?annee=2025&mois=12
```

---

## 📋 PLAN D'IMPLÉMENTATION

### **Étape 1 : Créer le service calculateur** ✅

1. Créer `backend/services/conges_calculator.py`
2. Implémenter `calculer_et_enregistrer_conges()`
3. Tester avec un employé de test

### **Étape 2 : Intégrer dans les pointages** ✅

1. Modifier `create_pointage()` → Appeler calculateur
2. Modifier `update_pointage()` → Appeler calculateur
3. Tester création/modification pointage

### **Étape 3 : Sécuriser l'endpoint consommation** ✅

1. Changer endpoint `/conges/{conge_id}/consommation`
2. Utiliser `employe_id/annee/mois` au lieu de `conge_id`
3. Créer automatiquement si manquant
4. Tester affectation congés

### **Étape 4 : Ajouter endpoint recalcul** ⏳

1. Créer `/conges/recalculer-periode`
2. Tester sur période complète
3. Documenter utilisation

### **Étape 5 : Mise à jour frontend** ⏳

1. Modifier appel API (si changement endpoint)
2. Tester workflow complet
3. Ajouter message si aucun pointage

---

## 🎯 RÉSUMÉ DES PROBLÈMES ET SOLUTIONS

| Problème | Cause | Solution |
|----------|-------|----------|
| **Congés calculés SEULEMENT lors génération rapport** | Logique dans `generer_rapport_pointages_mensuel()` uniquement | ⭐ Créer service `conges_calculator` + appeler dans `create_pointage()` et `update_pointage()` |
| **Erreur 500 sur `/conges/{id}/consommation`** | Enregistrement `Conge` n'existe pas (DB vide) | ⭐ Changer endpoint pour créer automatiquement si manquant OU message explicite |
| **`total_acquis = 0` bloque saisie** | Aucun congé calculé = validation échoue | ⭐ Recalculer congés AVANT d'autoriser saisie (via calculateur) |
| **DB vide après vidage** | Pas de mécanisme de recalcul batch | ⭐ Endpoint `/recalculer-periode` pour régénérer |

---

## 📝 NOTES IMPORTANTES

1. **Préservation de `jours_conges_pris`** :
   - Lors du recalcul automatique, `jours_conges_pris` **ne change PAS**
   - Seul `jours_conges_acquis` est recalculé
   - Garantit que la saisie manuelle reste

2. **Ordre des opérations** :
   ```
   1. Pointage créé/modifié
   2. Commit DB
   3. Calcul congés (avec jours_pris existant si présent)
   4. Commit congés
   5. Retour réponse
   ```

3. **Impact performance** :
   - Calcul supplémentaire à chaque modification pointage
   - Mais évite N+1 queries lors génération rapport
   - Trade-off acceptable

4. **Compatibilité v3.5.1 vs v3.5.3** :
   - v3.5.1 : INTEGER, tranches (8j→1j, 16j→2j, 24j→3j)
   - v3.5.3 : DECIMAL, proportionnel (jours/30*2.5, max 2.5)
   - Le service calculateur utilise la méthode du modèle (compatible)

---

**Document créé le** : 14 décembre 2025  
**Auteur** : GitHub Copilot  
**Version analysée** : 3.5.3
