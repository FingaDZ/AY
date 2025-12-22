# HOTFIX v3.6.1 - Correction IndentationError (MISE À JOUR 2)

## 🐛 Problèmes Résolus
- **IndentationError** dans `backend/routers/clients.py` ligne 111 ✅
- **IndentationError** dans `backend/routers/missions.py` ligne 116 ✅
- Lignes dupliquées dans `log_action()` causant le crash du backend
- Dossier `installer/` supprimé (tests Windows non requis)

## 🚀 Déploiement Rapide sur 192.168.20.55

```bash
# Sur le serveur
cd /opt/ay-hr

# Pull de la correction
git pull origin main

# Vérifier qu'on a le bon commit
git log --oneline -1
# Devrait afficher: eb4eb2a Fix v3.6.1: Correction IndentationError

# Redémarrer le backend
sudo systemctl restart ayhr-backend

# Vérifier le statut (devrait être "active (running)")
sudo systemctl status ayhr-backend

# Tester l'API
curl http://localhost:8000/
```

## ✅ Vérifications

```bash
# 1. Backend fonctionne
curl http://192.168.20.55:8000/ | grep "3.6.1"

# 2. Frontend fonctionne
curl http://192.168.20.55:3000

# 3. Nouveaux endpoints
curl http://192.168.20.55:8000/employes/contrats-expires

# 4. Base de données
mysql -u root -p ay_hr -e "SELECT id, mois_deduction FROM conges LIMIT 1;"
mysql -u root -p ay_hr -e "SELECT id, mois_debut FROM credits LIMIT 1;"
```

## 📊 Changements

**Commits:**
1. `eb4eb2a` - Fix clients.py indentation + Suppression installer/
2. `965404c` - Fix missions.py ligne 116 indentation ✅ **DERNIER**

**Fichiers modifiés:**
- ✅ `backend/routers/clients.py` - Correction indentation ligne 111
- ✅ `backend/routers/missions.py` - Correction indentation ligne 116
- ✅ Suppression dossier `installer/` (13 fichiers)

**GitHub:** https://github.com/FingaDZ/AY.git

## 🔧 Si le backend ne démarre toujours pas

```bash
# Voir les logs en temps réel
sudo journalctl -u ayhr-backend -f

# Vérifier le fichier de configuration systemd
cat /etc/systemd/system/ayhr-backend.service

# Tester l'import Python
cd /opt/ay-hr/backend
source venv/bin/activate
python -c "from routers import missions; print('OK')"

# Redémarrer manuellement dans le venv
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🔍 Vérification des Ports

```bash
# Vérifier quel processus écoute sur le port 8000
sudo netstat -tlnp | grep 8000
sudo lsof -i :8000

# Vérifier quel processus écoute sur le port 3000
sudo netstat -tlnp | grep 3000
sudo lsof -i :3000

# Vérifier les ports ouverts
sudo ss -tulpn | grep LISTEN

# Tester depuis le serveur lui-même
curl http://localhost:8000/
curl http://127.0.0.1:8000/

# Vérifier le firewall
sudo ufw status
sudo iptables -L -n | grep 8000
```

## 🚀 Redéploiement Complet

```bash
# 1. Arrêter le backend
sudo systemctl stop ayhr-backend

# 2. Pull du dernier fix
cd /opt/ay-hr
git pull origin main
git log --oneline -1
# Devrait afficher: 965404c Fix v3.6.1-hotfix2

# 3. Vérifier les fichiers Python
cd backend
source venv/bin/activate
python -c "from routers import clients, missions; print('clients OK'); print('missions OK')"

# 4. Redémarrer
sudo systemctl start ayhr-backend
sleep 3
sudo systemctl status ayhr-backend

# 5. Tester
curl http://localhost:8000/
```
