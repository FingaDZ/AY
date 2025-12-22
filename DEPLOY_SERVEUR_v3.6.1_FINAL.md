# 🚀 COMMANDES SERVEUR 192.168.20.55 - Déploiement Final v3.6.1

## Date: 22 décembre 2025

---

## ✅ ÉTAPE 1: Pull du Dernier Hotfix (missions.py)

```bash
cd /opt/ay-hr
git pull origin main

# Vérifier le commit (devrait être 965404c)
git log --oneline -1
```

**Résultat attendu**:
```
965404c Fix v3.6.1-hotfix2: Correction IndentationError missions.py ligne 116
```

---

## ✅ ÉTAPE 2: Redémarrer le Backend

```bash
sudo systemctl stop ayhr-backend
sleep 2
sudo systemctl start ayhr-backend
sleep 3
sudo systemctl status ayhr-backend
```

**Résultat attendu**: `Active: active (running)`

---

## ✅ ÉTAPE 3: Tests de Validation

### Test 1: API Backend Fonctionne

```bash
# Test sur localhost
curl http://localhost:8000/

# Test sur IP interne
curl http://192.168.20.55:8000/
```

**Résultat attendu**: JSON avec version 3.6.1

### Test 2: Imports Python OK

```bash
cd /opt/ay-hr/backend
source venv/bin/activate
python -c "from routers import clients, missions, conges; print('✅ Tous les imports OK')"
```

### Test 3: Certificat de Travail (Employés Inactifs)

```bash
# Trouver un employé inactif
mysql -u root -p ay_hr -e "SELECT id, nom, prenom, actif FROM employes WHERE actif=0 LIMIT 1;"

# Supposons ID = 50 (inactif)
# Test certificat (devrait fonctionner)
curl -I http://localhost:8000/employes/50/certificat-travail

# Test attestation (devrait échouer avec 400)
curl -I http://localhost:8000/employes/50/attestation-travail
```

### Test 4: Congés - Mois de Déduction

```bash
# Vérifier qu'un congé existe
mysql -u root -p ay_hr -e "SELECT id, employe_id, mois, annee, jours_conges_pris, mois_deduction FROM conges LIMIT 1;"

# Résultat exemple:
# id=250, mois=11, annee=2025, jours_pris=X, mois_deduction=11
```

**Note**: Le mois_deduction est déjà utilisé dans les bulletins de paie générés.

---

## ✅ ÉTAPE 4: Vérification des Ports

```bash
# Vérifier que le port 8000 est ouvert
sudo netstat -tlnp | grep 8000

# Résultat attendu:
# tcp  0  0 0.0.0.0:8000  0.0.0.0:*  LISTEN  XXXXX/python
```

Si le port n'est pas ouvert:

```bash
# Voir les logs en temps réel
sudo journalctl -u ayhr-backend -n 50 --no-pager

# Redémarrer manuellement
cd /opt/ay-hr/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## ✅ ÉTAPE 5: Test Frontend

```bash
# Vérifier que le frontend est accessible
curl http://192.168.20.55:3000

# Devrait retourner du HTML
```

---

## ✅ ÉTAPE 6: Vérification Complète

```bash
# 1. Version backend
curl http://localhost:8000/ | grep -o '"version":"[^"]*"'

# 2. Nouveaux endpoints v3.6.1
curl http://localhost:8000/employes/contrats-expires

# 3. Base de données - colonnes v3.6.1
mysql -u root -p ay_hr -e "DESCRIBE conges;" | grep -E "mois_deduction|annee_deduction"
mysql -u root -p ay_hr -e "DESCRIBE credits;" | grep -E "mois_debut|annee_debut"

# 4. Service actif
sudo systemctl is-active ayhr-backend
sudo systemctl is-active ayhr-frontend
```

---

## 🐛 Troubleshooting

### Problème: Backend ne démarre pas

```bash
# Voir l'erreur exacte
sudo journalctl -u ayhr-backend -n 100 --no-pager | grep -A 5 "Error\|Exception"

# Vérifier les fichiers Python
cd /opt/ay-hr/backend
source venv/bin/activate
python -m py_compile routers/clients.py
python -m py_compile routers/missions.py
python -m py_compile routers/employes.py
```

### Problème: Port 8000 en conflit

```bash
# Trouver le processus qui utilise le port
sudo lsof -i :8000

# Tuer le processus si nécessaire
sudo kill -9 <PID>

# Redémarrer
sudo systemctl restart ayhr-backend
```

### Problème: Permission denied

```bash
# Vérifier les permissions
ls -la /opt/ay-hr/backend

# Corriger si nécessaire
sudo chown -R ayhr:ayhr /opt/ay-hr/backend
```

---

## 📊 Checklist Finale

- [ ] Git pull réussi (commit 965404c)
- [ ] Backend démarre sans erreur
- [ ] Port 8000 répond
- [ ] Imports Python OK
- [ ] Certificat de travail fonctionne pour inactifs
- [ ] Attestation de travail fonctionne pour actifs
- [ ] Colonnes mois_deduction présentes dans DB
- [ ] Frontend accessible sur port 3000
- [ ] Logs ne montrent pas d'erreurs

---

## ✅ Statut Final

Une fois toutes les étapes validées:

```bash
# Vérifier l'uptime du service
sudo systemctl status ayhr-backend | grep "Active:"

# Dernière vérification API
curl http://localhost:8000/ && echo "\n✅ Backend v3.6.1 déployé avec succès!"
```

---

## 📞 Support

En cas de problème, vérifier:
1. [HOTFIX_v3.6.1.md](HOTFIX_v3.6.1.md) - Corrections appliquées
2. [VERIFICATION_CERTIFICATS_CONGES.md](VERIFICATION_CERTIFICATS_CONGES.md) - Détails fonctionnalités
3. Logs: `sudo journalctl -u ayhr-backend -f`
