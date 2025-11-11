# Relations de la Base de Données AY HR

## Vue d'ensemble des Relations

### 1. **Employe** (Table Principale)
- **Relations sortantes:**
  - `pointages` → Pointage (One-to-Many) - CASCADE DELETE
  - `avances` → Avance (One-to-Many) - CASCADE DELETE
  - `credits` → Credit (One-to-Many) - CASCADE DELETE
  - `missions` → Mission (One-to-Many) - CASCADE DELETE

### 2. **Pointage**
- **Relations entrantes:**
  - `employe_id` → Employe.id (Many-to-One)
- **Clés uniques:**
  - (employe_id, annee, mois) - Un seul pointage par employé/mois

### 3. **Client** (Table Indépendante)
- **Pas de relations bidirectionnelles**
- **Utilisé par:**
  - Mission.client_id (référence via ForeignKey)

### 4. **Mission**
- **Relations entrantes:**
  - `chauffeur_id` → Employe.id (Many-to-One)
  - `client_id` → Client.id (Many-to-One) - RESTRICT DELETE
- **Relations sortantes:**
  - `chauffeur` → Employe (via back_populates)
  - `client` → Client (pas de back_populates côté Client)

### 5. **Avance**
- **Relations entrantes:**
  - `employe_id` → Employe.id (Many-to-One) - CASCADE DELETE
- **Relations sortantes:**
  - `employe` → Employe (via back_populates)

### 6. **Credit**
- **Relations entrantes:**
  - `employe_id` → Employe.id (Many-to-One) - CASCADE DELETE
- **Relations sortantes:**
  - `employe` → Employe (via back_populates)
  - `retenues` → RetenueCredit (One-to-Many) - CASCADE DELETE
  - `prorogations` → ProrogationCredit (One-to-Many) - CASCADE DELETE

### 7. **RetenueCredit**
- **Relations entrantes:**
  - `credit_id` → Credit.id (Many-to-One) - CASCADE DELETE
- **Relations sortantes:**
  - `credit` → Credit (via back_populates)

### 8. **ProrogationCredit**
- **Relations entrantes:**
  - `credit_id` → Credit.id (Many-to-One) - CASCADE DELETE
- **Relations sortantes:**
  - `credit` → Credit (via back_populates)

## Configuration des Relations dans SQLAlchemy

### Chargement des Relations

Par défaut, les relations utilisent **lazy loading** (chargement à la demande).

```python
# Exemple dans Employe
pointages = relationship("Pointage", back_populates="employe", cascade="all, delete-orphan")
```

### Options de Chargement

1. **Lazy Loading** (par défaut):
   - Les relations sont chargées uniquement quand on y accède
   - Peut causer des erreurs si la session DB est fermée

2. **Eager Loading** (recommandé pour les API):
   ```python
   from sqlalchemy.orm import joinedload
   
   employes = db.query(Employe).options(
       joinedload(Employe.pointages)
   ).all()
   ```

3. **Select In Loading**:
   ```python
   from sqlalchemy.orm import selectinload
   
   employes = db.query(Employe).options(
       selectinload(Employe.avances),
       selectinload(Employe.credits)
   ).all()
   ```

## Stratégies de Cascade

### CASCADE DELETE
Utilisé pour les entités dépendantes qui n'ont pas de sens sans leur parent:
- Employe → Pointages, Avances, Credits, Missions
- Credit → Retenues, Prorogations

### RESTRICT DELETE
Utilisé pour empêcher la suppression si des références existent:
- Client dans Mission (un client ne peut pas être supprimé s'il a des missions)

## Bonnes Pratiques

1. **Toujours utiliser `back_populates`** pour les relations bidirectionnelles
2. **Utiliser `joinedload` ou `selectinload`** dans les routes API pour éviter N+1 queries
3. **Définir explicitement `ondelete`** sur les ForeignKey
4. **Utiliser des index** sur les colonnes de foreign key
5. **Documenter les contraintes d'intégrité** dans les schemas Pydantic

## Exemples de Requêtes Optimisées

### Récupérer un employé avec toutes ses relations
```python
from sqlalchemy.orm import selectinload

employe = db.query(Employe).options(
    selectinload(Employe.pointages),
    selectinload(Employe.avances),
    selectinload(Employe.credits).selectinload(Credit.retenues),
    selectinload(Employe.missions)
).filter(Employe.id == employe_id).first()
```

### Récupérer les missions avec chauffeur et client
```python
from sqlalchemy.orm import joinedload

missions = db.query(Mission).options(
    joinedload(Mission.chauffeur),
    joinedload(Mission.client)
).all()
```

### Compter les relations sans les charger
```python
from sqlalchemy import func

employe_stats = db.query(
    Employe.id,
    func.count(Pointage.id).label('nb_pointages')
).outerjoin(Pointage).group_by(Employe.id).all()
```

## Vérification de l'Intégrité

Utilisez ce script pour vérifier l'intégrité des relations:

```python
from database import SessionLocal
from models import *

db = SessionLocal()

# Vérifier les employés orphelins (aucun ne devrait exister)
orphaned_pointages = db.query(Pointage).filter(
    ~Pointage.employe_id.in_(db.query(Employe.id))
).count()

print(f"Pointages orphelins: {orphaned_pointages}")
```
