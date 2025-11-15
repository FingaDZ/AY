# Guide de Démarrage - AY HR Management

## 🚀 Démarrage Rapide

### Méthode 1: Script Automatique (Recommandé)
```powershell
# Démarrer Backend + Frontend automatiquement
.\start_all.ps1
```

### Méthode 2: Démarrage Manuel

#### Backend
```powershell
# Option A: Via script
.\start_backend.ps1

# Option B: Manuellement
cd backend
..\\.venv\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend
```powershell
# Option A: Via script
.\start_frontend.ps1

# Option B: Manuellement
cd frontend
npm run dev
```

## 📍 URLs d'Accès

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Documentation API:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## ✅ Vérification du Système

### Test des Endpoints API
```powershell
.\test_api.ps1
```

Ce script vérifie que tous les endpoints backend répondent correctement.

### Vérification Manuelle
```powershell
# Health check
curl http://localhost:8000/health

# Liste des employés
curl http://localhost:8000/api/employes/

# Avec PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/api/employes/" -UseBasicParsing | Select-Object StatusCode, Content
```

## 🔧 Résolution des Problèmes Courants

### 1. Backend ne démarre pas

**Symptôme:** Le serveur backend s'arrête immédiatement après le démarrage

**Solutions:**
```powershell
# Vérifier si un autre processus utilise le port 8000
netstat -ano | findstr :8000

# Arrêter le processus si nécessaire
taskkill /PID <PID> /F

# Relancer dans une nouvelle fenêtre PowerShell
Start-Process powershell -ArgumentList "-NoExit", "-File", ".\start_backend.ps1"
```

### 2. Erreur 500 sur les Endpoints

**Symptôme:** Le frontend affiche "Request failed with status code 500"

**Causes possibles:**
- Backend non démarré
- Problème de connexion à la base de données
- Erreur dans les relations SQLAlchemy

**Solutions:**
```powershell
# Vérifier que le backend est actif
curl http://localhost:8000/health

# Voir les logs du backend dans le terminal
# Les erreurs détaillées s'affichent dans la console backend

# Tester directement l'endpoint
curl http://localhost:8000/api/employes/
```

### 3. Frontend ne communique pas avec le Backend

**Symptôme:** Erreur CORS ou requêtes vers localhost:3000/api au lieu de localhost:8000/api

**Vérifications:**
1. Le proxy Vite est-il configuré? → Oui dans `frontend/vite.config.js`
2. Le backend autorise-t-il CORS? → Oui dans `backend/main.py`
3. Les URLs sont-elles correctes? → Utiliser `/api` (proxy) et non `http://localhost:8000/api`

**Solution:**
```javascript
// ✅ CORRECT - frontend/src/services/api.js
const API_BASE_URL = '/api';  // Proxy Vite redirige vers :8000

// ❌ INCORRECT
const API_BASE_URL = 'http://localhost:8000/api';  // Contourne le proxy
```

### 4. Erreur "Cannot import TypeJour"

**Symptôme:** `ImportError: cannot import name 'TypeJour' from 'models'`

**Cause:** Ancien code référençant l'enum TypeJour qui a été supprimé lors de la migration numérique

**Solution:** Vérifier que tous les fichiers n'importent plus TypeJour:
```powershell
# Rechercher les références restantes
Get-ChildItem -Path .\backend -Recurse -Filter *.py | Select-String "TypeJour"
```

### 5. Données n'apparaissent pas dans le Frontend

**Symptômes possibles:**
- Tableaux vides
- Erreurs dans la console du navigateur
- Status 200 OK mais pas de données affichées

**Solutions:**
```powershell
# 1. Vérifier que la DB contient des données
cd backend
python
>>> from database import SessionLocal
>>> from models import Employe
>>> db = SessionLocal()
>>> db.query(Employe).count()  # Doit être > 0
>>> exit()

# 2. Tester l'API directement
curl http://localhost:8000/api/employes/

# 3. Rafraîchir le frontend (Ctrl+F5 dans le navigateur)

# 4. Vérifier les logs du navigateur (F12 → Console)
```

### 6. Relations de Base de Données Incorrectes

**Symptôme:** Erreurs lors de la récupération de données liées (ex: pointages d'un employé)

**Documentation:** Voir `backend/RELATIONS_DATABASE.md` pour la documentation complète des relations

**Vérification:**
```python
# Dans Python
from database import SessionLocal
from models import Employe
from sqlalchemy.orm import selectinload

db = SessionLocal()
# Charger avec relations
employe = db.query(Employe).options(
    selectinload(Employe.pointages),
    selectinload(Employe.avances)
).first()

print(f"Employé: {employe.nom}")
print(f"Pointages: {len(employe.pointages)}")
print(f"Avances: {len(employe.avances)}")
```

## 📊 Structure du Projet

```
AY HR/
├── backend/
│   ├── models/          # Modèles SQLAlchemy (DB)
│   ├── schemas/         # Schémas Pydantic (validation)
│   ├── routers/         # Routes API FastAPI
│   ├── services/        # Logique métier
│   ├── database.py      # Configuration DB
│   ├── config.py        # Configuration app
│   └── main.py          # Point d'entrée
├── frontend/
│   ├── src/
│   │   ├── pages/       # Pages React
│   │   ├── components/  # Composants réutilisables
│   │   └── services/    # API calls
│   └── vite.config.js   # Config Vite (proxy)
├── start_all.ps1        # Démarrage complet
├── start_backend.ps1    # Backend seul
├── start_frontend.ps1   # Frontend seul
└── test_api.ps1         # Tests API
```

## 🔍 Logs et Débogage

### Backend
- **Terminal:** Les logs s'affichent directement dans le terminal PowerShell du backend
- **Niveau de détail:** Contrôlé par `DEBUG=True` dans `backend/config.py`
- **SQL Queries:** Activées quand DEBUG=True (via SQLAlchemy echo=True)

### Frontend
- **Console navigateur:** F12 → Console
- **Network tab:** F12 → Network (voir les requêtes HTTP)
- **React DevTools:** Extension recommandée pour le débogage React

## 📝 Notes Importantes

1. **Migration Pointage Numérique:** Le système utilise maintenant des valeurs 0/1 au lieu de texte (Tr, Ab, etc.). Voir `MIGRATION_POINTAGE_NUMERIQUE.md`

2. **Base de Données:** 
   - Host: 192.168.20.52:3306
   - Database: ay_hr
   - Credentials: Voir `backend/config.py`

3. **CORS:** Configuré pour accepter toutes les origines en développement (à restreindre en production)

4. **Hot Reload:**
   - Backend: Uvicorn --reload (redémarre automatiquement)
   - Frontend: Vite HMR (rafraîchissement instantané)

## 🆘 Support

Si les problèmes persistent:
1. Vérifier les logs du backend (terminal PowerShell)
2. Vérifier la console du navigateur (F12)
3. Tester les endpoints avec `test_api.ps1`
4. Consulter `backend/RELATIONS_DATABASE.md` pour les problèmes de relations
5. Consulter `MIGRATION_POINTAGE_NUMERIQUE.md` pour les questions sur le système de pointage
