# Améliorations - Employés et Avances

## 📋 Résumé des Modifications

### 1. N° ANEM pour les Employés ✅
- Ajout du champ `numero_anem` (alphanumérique, optionnel)
- Colonne VARCHAR(50) avec index pour performances
- Visible dans la liste et le formulaire des employés

### 2. Validation Anti-Doublon Employés ✅
- 3 critères de vérification lors de la création/modification :
  1. **Nom + Prénom + Date de naissance**
  2. **N° Sécurité Sociale**
  3. **N° Compte Bancaire**

### 3. Limite 70% pour les Avances ✅
- Vérification que chaque avance ne dépasse pas 70% du salaire de base
- Vérification du total mensuel des avances
- Plusieurs avances possibles dans le même mois (tant que total ≤ 70%)

---

## 🎯 1. N° ANEM - Numéro ANEM

### Modification de la Base de Données

**Fichier**: `database/add_numero_anem.sql`
```sql
ALTER TABLE employes 
ADD COLUMN numero_anem VARCHAR(50) NULL AFTER numero_compte_bancaire;

CREATE INDEX idx_employes_numero_anem ON employes(numero_anem);
```

**Script de migration**: `backend/migrate_add_numero_anem.py`
```bash
cd backend
python migrate_add_numero_anem.py
# ✓ Colonne numero_anem ajoutée avec succès
# ✓ Index créé avec succès
```

### Backend

**Modèle** (`models/employe.py`):
```python
numero_anem = Column(String(50), nullable=True, index=True)
```

**Schema** (`schemas/employe.py`):
```python
numero_anem: Optional[str] = Field(None, max_length=50)
```

### Frontend

**Liste des employés** (`EmployesList.jsx`):
```jsx
{
  title: 'N° ANEM',
  dataIndex: 'numero_anem',
  key: 'numero_anem',
  render: (value) => value || '-',
}
```

**Formulaire** (`EmployeForm.jsx`):
```jsx
<Form.Item
  label="N° ANEM"
  name="numero_anem"
  rules={[{ required: false }]}
>
  <Input placeholder="N° ANEM (optionnel)" />
</Form.Item>
```

---

## 🔒 2. Validation Anti-Doublon Employés

### Critères de Vérification

#### Critère 1: Nom + Prénom + Date de Naissance
```python
existing_by_identity = db.query(Employe).filter(
    Employe.nom == employe.nom,
    Employe.prenom == employe.prenom,
    Employe.date_naissance == employe.date_naissance
).first()

if existing_by_identity:
    raise HTTPException(
        status_code=400,
        detail=f"Un employé avec le même nom ({employe.nom}), "
               f"prénom ({employe.prenom}) et date de naissance existe déjà"
    )
```

**Logique**: Évite les doublons de personnes (homonymes différenciés par la date de naissance)

#### Critère 2: N° Sécurité Sociale
```python
existing_by_secu = db.query(Employe).filter(
    Employe.numero_secu_sociale == employe.numero_secu_sociale
).first()

if existing_by_secu:
    raise HTTPException(
        status_code=400,
        detail=f"Un employé avec ce numéro de sécurité sociale "
               f"({employe.numero_secu_sociale}) existe déjà"
    )
```

**Logique**: N° Sécu unique par employé (identifiant national)

#### Critère 3: N° Compte Bancaire
```python
existing_by_compte = db.query(Employe).filter(
    Employe.numero_compte_bancaire == employe.numero_compte_bancaire
).first()

if existing_by_compte:
    raise HTTPException(
        status_code=400,
        detail=f"Un employé avec ce numéro de compte bancaire "
               f"({employe.numero_compte_bancaire}) existe déjà"
    )
```

**Logique**: Évite qu'un même compte soit utilisé par plusieurs employés

### Modification d'Employé

Lors de la mise à jour (`PUT /employes/{id}`), les mêmes validations s'appliquent **en excluant l'employé courant** :

```python
# Exemple pour le N° Sécu
existing_by_secu = db.query(Employe).filter(
    Employe.numero_secu_sociale == employe_update.numero_secu_sociale,
    Employe.id != employe_id  # ← Exclure l'employé actuel
).first()
```

### Messages d'Erreur

```
❌ Erreur 400: Un employé avec le même nom (BENALI), prénom (Ahmed) et date de naissance existe déjà

❌ Erreur 400: Un employé avec ce numéro de sécurité sociale (123456789012345) existe déjà

❌ Erreur 400: Un employé avec ce numéro de compte bancaire (00123456789012345678) existe déjà
```

---

## 💰 3. Limite 70% pour les Avances Salariales

### Règles de Gestion

1. **Limite individuelle**: Chaque avance ≤ 70% du salaire de base
2. **Limite mensuelle**: Total des avances du mois ≤ 70% du salaire de base
3. **Avances multiples**: Plusieurs avances autorisées dans le même mois (si total respecte la limite)

### Implémentation Backend

**Fichier**: `routers/avances.py`

```python
@router.post("/", response_model=AvanceResponse, status_code=201)
def create_avance(avance: AvanceCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle avance"""
    
    # Récupérer l'employé
    employe = db.query(Employe).filter(Employe.id == avance.employe_id).first()
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Calculer la limite autorisée (70% du salaire de base)
    limite_autorisee = employe.salaire_base * Decimal('0.70')
    
    # Calculer le total des avances déjà accordées pour ce mois
    total_avances_mois = db.query(func.sum(Avance.montant)).filter(
        Avance.employe_id == avance.employe_id,
        Avance.mois_deduction == avance.mois_deduction,
        Avance.annee_deduction == avance.annee_deduction
    ).scalar() or Decimal('0')
    
    # Vérifier que le total ne dépasse pas 70%
    total_avec_nouvelle = total_avances_mois + avance.montant
    
    if total_avec_nouvelle > limite_autorisee:
        raise HTTPException(
            status_code=400,
            detail=f"Le total des avances pour {avance.mois_deduction}/{avance.annee_deduction} "
                   f"({total_avec_nouvelle:.2f} DA) dépasserait la limite autorisée de 70% "
                   f"du salaire ({limite_autorisee:.2f} DA). "
                   f"Avances déjà accordées: {total_avances_mois:.2f} DA. "
                   f"Montant maximum restant: {(limite_autorisee - total_avances_mois):.2f} DA"
        )
    
    # Créer l'avance
    db_avance = Avance(**avance.model_dump())
    db.add(db_avance)
    db.commit()
    db.refresh(db_avance)
    
    return db_avance
```

### Exemples de Scénarios

#### ✅ Scénario 1: Avance Simple (OK)
```
Salaire de base: 30,000 DA
Limite autorisée: 21,000 DA (70%)

Avance demandée: 15,000 DA
Total mensuel: 15,000 DA

Résultat: ✓ APPROUVÉE (15,000 < 21,000)
```

#### ✅ Scénario 2: Avances Multiples (OK)
```
Salaire de base: 30,000 DA
Limite autorisée: 21,000 DA (70%)

Avance 1: 10,000 DA → Total: 10,000 DA ✓
Avance 2: 8,000 DA  → Total: 18,000 DA ✓
Avance 3: 2,000 DA  → Total: 20,000 DA ✓

Résultat: ✓ TOUTES APPROUVÉES (20,000 < 21,000)
```

#### ❌ Scénario 3: Dépassement de Limite (REFUSÉ)
```
Salaire de base: 30,000 DA
Limite autorisée: 21,000 DA (70%)

Avance 1: 15,000 DA → Total: 15,000 DA ✓
Avance 2: 10,000 DA → Total: 25,000 DA ✗

Erreur: Le total des avances pour 11/2025 (25,000.00 DA) dépasserait 
la limite autorisée de 70% du salaire (21,000.00 DA). 
Avances déjà accordées: 15,000.00 DA. 
Montant maximum restant: 6,000.00 DA
```

#### ✅ Scénario 4: Avance Maximale Restante (OK)
```
Salaire de base: 30,000 DA
Limite autorisée: 21,000 DA (70%)

Avance 1: 15,000 DA → Total: 15,000 DA ✓
Avance 2: 6,000 DA  → Total: 21,000 DA ✓ (exactement la limite)

Résultat: ✓ APPROUVÉES (21,000 = 21,000)
```

### Messages d'Erreur Détaillés

```
❌ Erreur 400: Le total des avances pour 11/2025 (25,000.00 DA) dépasserait 
la limite autorisée de 70% du salaire (21,000.00 DA). 
Avances déjà accordées: 15,000.00 DA. 
Montant maximum restant: 6,000.00 DA
```

**Informations fournies**:
- Total avec nouvelle avance
- Limite autorisée (70%)
- Montant déjà accordé ce mois
- Montant maximum restant disponible

---

## 🧪 Tests

### Test 1: N° ANEM

```bash
# Créer un employé avec N° ANEM
POST /api/employes/
{
  "nom": "BENALI",
  "prenom": "Ahmed",
  "numero_anem": "ANEM-2025-001ABC",
  ...
}

# Vérifier dans la liste
GET /api/employes/
# → Colonne "N° ANEM" affichée avec la valeur
```

### Test 2: Anti-Doublon Employés

```bash
# Créer employé 1
POST /api/employes/
{
  "nom": "BENALI",
  "prenom": "Ahmed",
  "date_naissance": "1990-01-15",
  "numero_secu_sociale": "123456789012345",
  "numero_compte_bancaire": "00123456789012345678",
  ...
}

# Tentative doublon par identité
POST /api/employes/
{
  "nom": "BENALI",
  "prenom": "Ahmed",
  "date_naissance": "1990-01-15",  # ← Même combinaison
  ...
}
# → Erreur 400: Un employé avec le même nom, prénom et date de naissance existe déjà

# Tentative doublon par N° Sécu
POST /api/employes/
{
  "nom": "MEZIANE",
  "prenom": "Ali",
  "numero_secu_sociale": "123456789012345",  # ← Même N° Sécu
  ...
}
# → Erreur 400: Un employé avec ce numéro de sécurité sociale existe déjà

# Tentative doublon par compte bancaire
POST /api/employes/
{
  "nom": "SAID",
  "prenom": "Mohamed",
  "numero_compte_bancaire": "00123456789012345678",  # ← Même compte
  ...
}
# → Erreur 400: Un employé avec ce numéro de compte bancaire existe déjà
```

### Test 3: Limite 70% Avances

```bash
# Créer un employé avec salaire 30,000 DA
POST /api/employes/
{ ..., "salaire_base": 30000.00 }
# → Limite: 21,000 DA (70%)

# Avance 1: 15,000 DA (OK)
POST /api/avances/
{
  "employe_id": 1,
  "montant": 15000.00,
  "mois_deduction": 11,
  "annee_deduction": 2025
}
# → ✓ Créée (total: 15,000 DA)

# Avance 2: 10,000 DA (REFUSÉ)
POST /api/avances/
{
  "employe_id": 1,
  "montant": 10000.00,
  "mois_deduction": 11,
  "annee_deduction": 2025
}
# → ✗ Erreur 400: Dépassement de limite (25,000 > 21,000)
#    Montant maximum restant: 6,000 DA

# Avance 2: 6,000 DA (OK)
POST /api/avances/
{
  "employe_id": 1,
  "montant": 6000.00,
  "mois_deduction": 11,
  "annee_deduction": 2025
}
# → ✓ Créée (total: 21,000 DA - exactement la limite)

# Avance 3: 1,000 DA (REFUSÉ)
POST /api/avances/
{
  "employe_id": 1,
  "montant": 1000.00,
  "mois_deduction": 11,
  "annee_deduction": 2025
}
# → ✗ Erreur 400: Limite atteinte (22,000 > 21,000)
#    Montant maximum restant: 0 DA
```

---

## 📝 Fichiers Modifiés

### Backend

1. **models/employe.py**
   - Ajout: `numero_anem = Column(String(50), nullable=True, index=True)`

2. **schemas/employe.py**
   - Ajout dans `EmployeBase`: `numero_anem: Optional[str] = Field(None, max_length=50)`
   - Ajout dans `EmployeUpdate`: `numero_anem: Optional[str] = Field(None, max_length=50)`

3. **routers/employes.py**
   - Fonction `create_employe()`: 3 validations anti-doublon
   - Fonction `update_employe()`: 3 validations anti-doublon (exclure employé actuel)

4. **routers/avances.py**
   - Fonction `create_avance()`: Validation limite 70% (individuelle + mensuelle)

5. **database/add_numero_anem.sql** (nouveau)
   - Script SQL pour migration manuelle

6. **backend/migrate_add_numero_anem.py** (nouveau)
   - Script Python pour migration automatique

### Frontend

1. **pages/Employes/EmployesList.jsx**
   - Ajout colonne "N° ANEM" dans le tableau

2. **pages/Employes/EmployeForm.jsx**
   - Ajout champ "N° ANEM" dans le formulaire (optionnel)

---

## 🎯 Résultats

✅ **N° ANEM**: Champ alphanumérique optionnel pour identifier les employés ANEM

✅ **Anti-Doublon**: Protection contre les doublons sur 3 critères (identité, N° Sécu, compte bancaire)

✅ **Limite 70%**: Contrôle strict des avances pour ne pas dépasser 70% du salaire

✅ **Avances Multiples**: Plusieurs avances autorisées dans le même mois (total ≤ 70%)

✅ **Messages Clairs**: Erreurs détaillées avec montants et limites explicites

---

## 💡 Notes Importantes

### N° ANEM
- **Format libre**: Accepte texte, chiffres, caractères spéciaux (VARCHAR 50)
- **Optionnel**: Pas obligatoire lors de la création
- **Indexé**: Recherche rapide par N° ANEM

### Anti-Doublon
- **3 critères indépendants**: Chaque critère est vérifié séparément
- **Messages explicites**: L'erreur indique quel critère a échoué et avec quelle valeur
- **Création ET modification**: Validations appliquées dans les deux cas

### Limite 70% Avances
- **Base de calcul**: Salaire de base (pas le salaire net)
- **Période**: Par mois de déduction (pas le mois d'octroi)
- **Cumul**: Toutes les avances du même mois sont comptabilisées
- **Message détaillé**: Indique le montant déjà accordé et le montant maximum restant

---

## 🚀 Prochaines Étapes

### Améliorations Possibles

1. **Validation format N° ANEM**: Regex pour format spécifique
2. **Historique doublon**: Logger les tentatives de doublons
3. **Dashboard avances**: Vue par employé avec % utilisé
4. **Alerte 70%**: Warning quand on approche la limite
5. **Export avances**: Rapport mensuel des avances par employé

---

✅ **Toutes les fonctionnalités ont été implémentées et testées avec succès !**
