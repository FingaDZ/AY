# GUIDE DE DÉPLOIEMENT v3.6.0-alpha
## Gestion Camions

### Date: 15 décembre 2025

---

## ✅ PHASE 1 COMPLÉTÉE: Gestion Camions

### Commits déployés:
- **4f26113**: Backend gestion camions (modèles, API, migration)
- **6df7a23**: Frontend gestion camions (page complète + sidebar)

---

## 📦 CE QUI A ÉTÉ AJOUTÉ

### Backend

**Fichiers créés:**
- `backend/models/camion.py` - Modèle SQLAlchemy Camion
- `backend/schemas/camion.py` - Schémas Pydantic validation
- `backend/routers/camions.py` - API REST complète
- `backend/migrate_v3.6.0_camions.py` - Script de migration DB

**Fichiers modifiés:**
- `backend/models/mission.py` - Ajout `camion_id` (relation)
- `backend/models/__init__.py` - Export Camion
- `backend/schemas/__init__.py` - Export schémas camion
- `backend/main.py` - Enregistrement router `/api/camions`

**Endpoints API ajoutés:**
- `GET /api/camions` - Liste camions (avec filtres)
- `GET /api/camions/{id}` - Détails camion
- `POST /api/camions` - Créer camion
- `PUT /api/camions/{id}` - Modifier camion
- `DELETE /api/camions/{id}` - Supprimer camion
- `GET /api/camions/{id}/missions` - Missions d'un camion

### Frontend

**Fichiers créés:**
- `frontend/src/pages/Camions/Camions.jsx` - Page complète gestion camions

**Fichiers modifiés:**
- `frontend/src/App.jsx` - Route `/camions` (protégée admin)
- `frontend/src/components/Sidebar.jsx` - Lien "Camions" avec icône 🚛
- `frontend/src/components/Layout.jsx` - Version `v3.6.0-alpha`

---

## 🚀 ÉTAPES DE DÉPLOIEMENT

### Sur le serveur (192.168.20.55)

```bash
# 1. Connexion SSH
ssh root@192.168.20.55

# 2. Pull dernières modifications
cd /opt/ay-hr
git pull origin main

# 3. Exécuter la migration
cd /opt/ay-hr/backend
python3 migrate_v3.6.0_camions.py

# 4. Vérifier la migration
# Doit afficher:
# ✅ MIGRATION v3.6.0 TERMINÉE AVEC SUCCÈS
# - Table 'camions' créée
# - Colonne 'camion_id' ajoutée à 'missions'
# - 3 camion(s) dans la base (données test)

# 5. Redémarrer le backend
sudo systemctl restart ayhr-backend
sudo systemctl status ayhr-backend

# 6. Vérifier logs
sudo journalctl -u ayhr-backend --since "1 minute ago" --no-pager | tail -20

# 7. Rebuild frontend
cd /opt/ay-hr/frontend
npm run build

# 8. Redémarrer nginx (si nécessaire)
sudo systemctl restart nginx
```

---

## 🧪 TESTS POST-DÉPLOIEMENT

### Test Backend API

```bash
# Test 1: Liste camions
curl http://localhost:8000/api/camions

# Test 2: Créer camion
curl -X POST http://localhost:8000/api/camions \
  -H "Content-Type: application/json" \
  -d '{
    "marque": "RENAULT",
    "modele": "Master",
    "immatriculation": "189765-109-16",
    "actif": true
  }'

# Test 3: Détails camion
curl http://localhost:8000/api/camions/1
```

### Test Frontend

1. **Accéder à l'application**: http://192.168.20.55
2. **Se connecter** avec compte admin
3. **Vérifier sidebar**: Lien "Camions" présent (🚛)
4. **Accéder à `/camions`**
5. **Vérifier affichage**: 3 camions de test doivent apparaître
6. **Tester création**: Ajouter un nouveau camion
7. **Tester édition**: Modifier un camion existant
8. **Tester suppression**: Supprimer (ou désactiver si missions liées)

---

## 📊 DONNÉES DE TEST CRÉÉES

La migration crée automatiquement 3 camions:

| Marque    | Modèle   | Immatriculation | Capacité | Statut |
|-----------|----------|-----------------|----------|--------|
| HYUNDAI   | HD35     | 152455-109-43   | 3500 kg  | Actif  |
| ISUZU     | NQR      | 165432-109-16   | 5000 kg  | Actif  |
| MERCEDES  | Sprinter | 178965-109-16   | 2000 kg  | Actif  |

---

## ⚙️ SCHÉMA BASE DE DONNÉES

### Table `camions`

```sql
CREATE TABLE camions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    marque VARCHAR(50) NOT NULL,
    modele VARCHAR(50) NOT NULL,
    immatriculation VARCHAR(20) UNIQUE NOT NULL,
    annee_fabrication INT,
    capacite_charge INT,
    actif BOOLEAN DEFAULT TRUE NOT NULL,
    date_acquisition DATE,
    date_revision DATE,
    notes TEXT
);
```

### Modification table `missions`

```sql
ALTER TABLE missions 
ADD COLUMN camion_id INT NULL,
ADD CONSTRAINT fk_missions_camion 
FOREIGN KEY (camion_id) REFERENCES camions(id) ON DELETE RESTRICT;
```

---

## 🔒 PERMISSIONS

- **Page Camions**: Accessible **uniquement aux administrateurs**
- **API Camions**: Nécessite authentification (token JWT)
- **Suppression**: Impossible si camion a des missions (désactivation auto)

---

## 🎯 PROCHAINES ÉTAPES

✅ **Phase 1 TERMINÉE** (Camions)

**Phase 2** (à venir): Calcul kilométrage multi-clients
- Paramètre `km_supplementaire_par_client`
- Logique calcul: dernier client + km supp × (nb clients - 1)
- Interface missions multi-clients

---

## 📝 NOTES IMPORTANTES

### Sécurité
- Immatriculation convertie en MAJUSCULES automatiquement
- Unicité garantie par contrainte DB
- Validation formulaire côté frontend ET backend

### Performance
- Index sur `immatriculation` (recherches rapides)
- Pagination API (limite 100 par défaut)
- Comptage missions optimisé (query séparée)

### UX
- Filtres: Tous / Actifs / Inactifs
- Statistiques en temps réel
- Modal formulaire réutilisable (création + édition)
- Messages toast pour feedback utilisateur

---

## 🐛 TROUBLESHOOTING

### Erreur "Table camions already exists"
```bash
# Normal si migration déjà exécutée
# Le script gère les tables existantes
```

### Camion ne se supprime pas
```bash
# Normal si missions liées
# Le camion est automatiquement désactivé
# Vérifier: actif = FALSE
```

### Frontend ne charge pas
```bash
# 1. Vérifier build
cd /opt/ay-hr/frontend
npm run build

# 2. Vérifier nginx
sudo nginx -t
sudo systemctl reload nginx

# 3. Vérifier logs
sudo tail -f /var/log/nginx/error.log
```

### API retourne 404
```bash
# 1. Vérifier backend
sudo systemctl status ayhr-backend

# 2. Vérifier logs
sudo journalctl -u ayhr-backend -n 50

# 3. Tester direct
curl http://localhost:8000/api/camions
```

---

## ✅ CHECKLIST VALIDATION

- [ ] Migration exécutée sans erreur
- [ ] Backend redémarré et actif
- [ ] API `/api/camions` répond
- [ ] Frontend build réussi
- [ ] Sidebar affiche lien "Camions"
- [ ] Page camions accessible
- [ ] 3 camions de test présents
- [ ] Création camion fonctionne
- [ ] Édition camion fonctionne
- [ ] Suppression/désactivation fonctionne
- [ ] Logs enregistrés correctement
- [ ] Version `v3.6.0-alpha` affichée

---

## 📞 SUPPORT

En cas de problème:
1. Vérifier les logs backend: `sudo journalctl -u ayhr-backend -f`
2. Vérifier les logs nginx: `sudo tail -f /var/log/nginx/error.log`
3. Consulter la documentation: [PLAN_V3.6.0.md](PLAN_V3.6.0.md)
4. Rollback possible: `git checkout <commit-avant-v3.6.0>`

---

**Version**: v3.6.0-alpha  
**Date**: 15 décembre 2025  
**Status**: ✅ PHASE 1 COMPLÉTÉE
