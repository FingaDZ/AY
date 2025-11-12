# 📋 Système de Logging - Guide d'Utilisation

## Vue d'Ensemble

Le système de logging d'AY HR Management enregistre automatiquement toutes les opérations CRUD (Création, Modification, Suppression) sur les modules principaux.

## Caractéristiques

### ✅ Fonctionnalités
- **Traçabilité complète**: Qui, Quand, Quoi, Où (IP)
- **Historique des données**: Avant/Après pour les modifications
- **Filtres avancés**: Module, Action, Utilisateur, Dates, Recherche
- **Read-only**: Impossible de modifier ou supprimer les logs via l'interface
- **Sécurisé**: Accès admin uniquement, données sensibles masquées

### 🔒 Sécurité
- Champs sensibles automatiquement masqués (password, token)
- Logs accessibles uniquement par les administrateurs
- IP address enregistrée pour chaque action
- Aucune modification possible via API

## Modules Loggés

### ✅ Actuellement Implémentés
- **Employés**: Création, Modification, Suppression

### 🔄 À Implémenter
- Pointages
- Clients
- Missions
- Avances
- Crédits
- Salaires
- Paramètres
- Configuration Base de Données
- Utilisateurs

## Structure de Données

### Table: `logging`

| Colonne | Type | Description |
|---------|------|-------------|
| id | INT | Identifiant unique |
| timestamp | DATETIME | Date/heure de l'action |
| user_id | INT | ID utilisateur |
| user_email | VARCHAR(255) | Email utilisateur |
| module_name | VARCHAR(100) | Module concerné |
| action_type | ENUM | CREATE, UPDATE, DELETE |
| record_id | INT | ID de l'enregistrement |
| old_data | JSON | Données avant modification |
| new_data | JSON | Nouvelles données |
| description | TEXT | Description textuelle |
| ip_address | VARCHAR(45) | Adresse IP |

### Index
- `idx_timestamp`: Sur timestamp (tri chronologique)
- `idx_user_id`: Sur user_id (filtrage utilisateur)
- `idx_module`: Sur module_name (filtrage module)
- `idx_action`: Sur action_type (filtrage action)
- `idx_record`: Sur record_id (retrouver logs d'un enregistrement)

## API Endpoints

### GET /api/logs/
Récupère la liste des logs avec filtres et pagination.

**Paramètres:**
- `page` (int): Numéro de page (défaut: 1)
- `limit` (int): Nombre par page (défaut: 100, max: 1000)
- `module_name` (string): Filtrer par module
- `action_type` (string): CREATE, UPDATE ou DELETE
- `user_id` (int): Filtrer par utilisateur
- `date_debut` (ISO string): Date de début
- `date_fin` (ISO string): Date de fin
- `search` (string): Recherche dans email et description

**Réponse:**
```json
{
  "total": 42,
  "page": 1,
  "limit": 100,
  "logs": [
    {
      "id": 1,
      "timestamp": "2025-11-12T18:30:00",
      "user_id": 1,
      "user_email": "admin@ayhr.dz",
      "module_name": "employes",
      "action_type": "CREATE",
      "record_id": 5,
      "old_data": null,
      "new_data": {...},
      "description": "Création employé: Dupont Jean",
      "ip_address": "192.168.1.10"
    }
  ]
}
```

### GET /api/logs/modules
Liste des modules disponibles dans les logs.

**Réponse:**
```json
["employes", "pointages", "clients", ...]
```

### GET /api/logs/users
Liste des utilisateurs ayant effectué des actions.

**Réponse:**
```json
[
  {"id": 1, "email": "admin@ayhr.dz"},
  {"id": 2, "email": "user@ayhr.dz"}
]
```

### GET /api/logs/{log_id}
Détail d'un log spécifique.

**Réponse:**
```json
{
  "id": 1,
  "timestamp": "2025-11-12T18:30:00",
  "user_id": 1,
  "user_email": "admin@ayhr.dz",
  "module_name": "employes",
  "action_type": "CREATE",
  "record_id": 5,
  "old_data": null,
  "new_data": {
    "id": 5,
    "nom": "Dupont",
    "prenom": "Jean",
    "salaire_base": 50000,
    ...
  },
  "description": "Création employé: Dupont Jean",
  "ip_address": "192.168.1.10"
}
```

## Interface Utilisateur

### Page Logs (/logs)

#### Barre de Filtres
1. **Module**: Dropdown liste des modules disponibles
2. **Action**: Création / Modification / Suppression
3. **Utilisateur**: Dropdown liste des utilisateurs
4. **Dates**: Sélecteur de plage de dates
5. **Recherche**: Champ texte libre
6. **Boutons**: "Appliquer" et "Effacer"

#### Tableau
- **Date/Heure**: Format DD/MM/YYYY HH:mm:ss
- **Module**: Badge violet
- **Action**: Badge coloré (vert/bleu/rouge)
- **Utilisateur**: Email
- **ID Enregistrement**: Numéro
- **Description**: Texte
- **Actions**: Bouton "Détail"

#### Modal Détail
Affiche toutes les informations du log:
- Informations générales (ID, date, user, IP)
- Anciennes données (JSON formaté)
- Nouvelles données (JSON formaté)

## Guide d'Intégration

### Ajouter le Logging à un Router

#### Étape 1: Imports
```python
from fastapi import Request
from models import ActionType
from services.logging_service import log_action, clean_data_for_logging
```

#### Étape 2: Ajouter Request au Endpoint
```python
@router.post("/")
def create_item(
    data: ItemCreate,
    request: Request,  # ← Ajouter ici
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
```

#### Étape 3: Logger la Création
```python
# Créer l'item
item = Item(**data.dict())
db.add(item)
db.commit()
db.refresh(item)

# Logger
try:
    log_action(
        db=db,
        module_name="items",  # Nom du module
        action_type=ActionType.CREATE,
        record_id=item.id,
        new_data=clean_data_for_logging(item),  # Nettoie les données
        description=f"Création item: {item.name}",
        user=current_user,
        request=request
    )
except Exception as e:
    print(f"Erreur logging: {e}")  # Ne pas bloquer l'opération si logging échoue

return item
```

#### Étape 4: Logger la Modification
```python
# Récupérer l'item
item = db.query(Item).filter(Item.id == item_id).first()
if not item:
    raise HTTPException(404, "Item non trouvé")

# Sauvegarder ancien état
old_data = clean_data_for_logging(item)

# Modifier
update_data = item_update.dict(exclude_unset=True)
for field, value in update_data.items():
    setattr(item, field, value)

db.commit()
db.refresh(item)

# Logger
try:
    log_action(
        db=db,
        module_name="items",
        action_type=ActionType.UPDATE,
        record_id=item.id,
        old_data=old_data,  # État avant
        new_data=clean_data_for_logging(item),  # État après
        description=f"Modification item: {item.name}",
        user=current_user,
        request=request
    )
except Exception as e:
    print(f"Erreur logging: {e}")

return item
```

#### Étape 5: Logger la Suppression
```python
# Récupérer l'item
item = db.query(Item).filter(Item.id == item_id).first()
if not item:
    raise HTTPException(404, "Item non trouvé")

# Sauvegarder données avant suppression
item_data = clean_data_for_logging(item)
item_name = item.name  # Pour la description

# Supprimer
db.delete(item)
db.commit()

# Logger
try:
    log_action(
        db=db,
        module_name="items",
        action_type=ActionType.DELETE,
        record_id=item_id,
        old_data=item_data,  # Données supprimées
        description=f"Suppression item: {item_name}",
        user=current_user,
        request=request
    )
except Exception as e:
    print(f"Erreur logging: {e}")

return None
```

## Maintenance

### Nettoyage des Logs

Les logs s'accumulent avec le temps. Voici une requête SQL pour supprimer les logs de plus de 1 an:

```sql
DELETE FROM logging 
WHERE timestamp < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

### Archivage

Pour archiver les vieux logs avant suppression:

```sql
-- Créer table d'archive
CREATE TABLE logging_archive LIKE logging;

-- Copier les vieux logs
INSERT INTO logging_archive 
SELECT * FROM logging 
WHERE timestamp < DATE_SUB(NOW(), INTERVAL 1 YEAR);

-- Supprimer de la table principale
DELETE FROM logging 
WHERE timestamp < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

### Statistiques

Requête pour voir l'activité par module:

```sql
SELECT 
    module_name,
    action_type,
    COUNT(*) as total,
    MIN(timestamp) as first_action,
    MAX(timestamp) as last_action
FROM logging
GROUP BY module_name, action_type
ORDER BY total DESC;
```

Activité par utilisateur:

```sql
SELECT 
    user_email,
    COUNT(*) as total_actions,
    SUM(CASE WHEN action_type = 'CREATE' THEN 1 ELSE 0 END) as creations,
    SUM(CASE WHEN action_type = 'UPDATE' THEN 1 ELSE 0 END) as modifications,
    SUM(CASE WHEN action_type = 'DELETE' THEN 1 ELSE 0 END) as suppressions
FROM logging
WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY user_email
ORDER BY total_actions DESC;
```

## Troubleshooting

### Problème: Logs ne s'enregistrent pas

**Solutions:**
1. Vérifier que la table existe:
   ```bash
   python backend/create_logging_table.py
   ```

2. Vérifier les imports dans le router:
   ```python
   from models import ActionType
   from services.logging_service import log_action
   ```

3. Vérifier que le try/except ne masque pas une erreur:
   ```python
   try:
       log_action(...)
   except Exception as e:
       print(f"Erreur logging: {e}")  # Afficher l'erreur
   ```

### Problème: Page Logs ne charge pas

**Solutions:**
1. Vérifier que le router est chargé dans main.py:
   ```python
   from routers import logs
   app.include_router(logs.router, prefix="/api")
   ```

2. Vérifier l'authentification:
   ```javascript
   // Dans logs.js
   return api.get('/logs/', { params });  // Utilise automatiquement le token
   ```

3. Vérifier les droits admin:
   ```python
   # Dans logs.py
   async def get_logs(..., current_user: User = Depends(require_admin)):
   ```

### Problème: Données sensibles visibles

**Solutions:**
Vérifier la fonction `clean_data_for_logging()`:
```python
sensitive_fields = ['password', 'password_hash', 'token', 'secret']
for field in sensitive_fields:
    if field in data_dict:
        data_dict[field] = '***HIDDEN***'
```

## Best Practices

### ✅ À Faire
- Logger TOUTES les opérations CRUD
- Utiliser `clean_data_for_logging()` pour nettoyer les données
- Mettre le logging dans un try/except pour ne pas bloquer l'opération
- Fournir des descriptions claires et concises
- Toujours passer `request` pour capturer l'IP

### ❌ À Éviter
- Ne pas logger les opérations de lecture (GET)
- Ne pas logger les données sensibles en clair
- Ne pas bloquer une opération si le logging échoue
- Ne pas faire de logging dans les boucles (performance)
- Ne pas modifier/supprimer les logs via code applicatif

## Support

Pour toute question ou problème:
1. Consulter la documentation dans le code
2. Vérifier les logs du serveur backend
3. Tester avec un utilisateur admin
4. Vérifier la connexion à la base de données

---

**Dernière mise à jour**: 12 Novembre 2025  
**Version**: 1.1.0  
**Auteur**: AI Assistant
