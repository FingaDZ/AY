# Guide de Débogage v3.7.0

## ✅ Migration Réussie

```
Nombre de congés avec jours_pris > 0    5.00
Nombre de déductions migrées            5.00
Total jours pris (ancien)               8.50
Total jours déduits (nouveau)           8.50
```

Migration cohérente ✅

## ❌ Tests des Endpoints

### Test 1: Synthèse - ÉCHOUÉ ❌
```
GET /api/conges/synthese/1
```

### Test 2: Solde - ÉCHOUÉ ❌
```
GET /api/deductions-conges/solde/1
```

### Test 3: Liste déductions - OK ✅
```
GET /api/deductions-conges/employe/1
Nombre de déductions: 0
```

### Test 4: Liste congés - OK ✅
```
GET /api/conges/?employe_id=1
Nombre de périodes: 0
```

## 🔍 Diagnostic

L'employé ID=1 n'existe pas ou n'a pas de données. Testons avec un autre ID.

## 📋 Commandes de Diagnostic sur le Serveur

### 1. Vérifier les logs backend
```bash
ssh root@192.168.20.55
journalctl -u ayhr-backend -n 50 --no-pager
```

### 2. Vérifier les données en base
```bash
mysql -u root -p ay_hr
```

```sql
-- Lister les employés
SELECT id, nom, prenom, statut FROM employes LIMIT 10;

-- Vérifier les congés
SELECT employe_id, COUNT(*) as nb_periodes, SUM(jours_conges_acquis) as total_acquis
FROM conges 
GROUP BY employe_id;

-- Vérifier les déductions migrées
SELECT d.*, e.nom, e.prenom 
FROM deductions_conges d 
JOIN employes e ON e.id = d.employe_id 
LIMIT 10;

-- Trouver un employé avec des déductions
SELECT employe_id, COUNT(*) as nb_deductions, SUM(jours_deduits) as total_deduit
FROM deductions_conges
GROUP BY employe_id;
```

### 3. Tester avec un vrai employé_id
```bash
# Remplacer {id} par un ID réel d'employé avec données
curl http://192.168.20.55:8000/api/conges/synthese/{id}
curl http://192.168.20.55:8000/api/deductions-conges/solde/{id}
curl http://192.168.20.55:8000/api/deductions-conges/employe/{id}
```

### 4. Vérifier que le backend a bien démarré
```bash
systemctl status ayhr-backend
ps aux | grep uvicorn
netstat -tlnp | grep 8000
```

### 5. Tester la connectivité
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/docs  # Swagger UI
```

## 🐛 Problèmes Possibles

### Erreur 1: ImportError
Si le backend n'a pas démarré à cause d'un import manquant:
```bash
journalctl -u ayhr-backend -n 50 | grep "ImportError\|ModuleNotFoundError"
```

**Solution:**
```bash
cd /opt/ay-hr/backend
source venv/bin/activate  # Si virtualenv
pip install -r requirements.txt
systemctl restart ayhr-backend
```

### Erreur 2: Relation manquante
Si le backend crashe sur les relations SQLAlchemy:
```bash
journalctl -u ayhr-backend -n 50 | grep "relationship\|AttributeError"
```

**Solution:** Vérifier que tous les imports sont présents dans `models/__init__.py`

### Erreur 3: Employé ID=1 n'existe pas
Les endpoints fonctionnent mais retournent 404 car l'employé n'existe pas.

**Solution:** Utiliser un ID valide depuis la base:
```sql
SELECT MIN(id) as premier_employe FROM employes WHERE statut = 'Actif';
```

## ✅ Validation Finale

Une fois un employé_id valide trouvé, re-tester:

```powershell
# Depuis Windows
$EMPLOYE_ID = 5  # Remplacer par ID réel

Invoke-RestMethod "http://192.168.20.55:8000/api/conges/synthese/$EMPLOYE_ID"
Invoke-RestMethod "http://192.168.20.55:8000/api/deductions-conges/solde/$EMPLOYE_ID"
Invoke-RestMethod "http://192.168.20.55:8000/api/deductions-conges/employe/$EMPLOYE_ID"
```

Résultat attendu:
```json
{
  "employe": "Prenom Nom",
  "total_acquis": 15.0,
  "total_deduit": 2.5,
  "solde": 12.5,
  "periodes": [...]
}
```

## 🚀 Prochaines Étapes

1. ✅ Backend déployé
2. ✅ Migration SQL exécutée
3. ⏳ Tests avec données réelles (trouver bon employe_id)
4. ⏳ Modifier le frontend (voir FRONTEND_MODIFICATIONS_V3.7.0.md)
5. ⏳ Déployer frontend
6. ⏳ Tests utilisateur complets
