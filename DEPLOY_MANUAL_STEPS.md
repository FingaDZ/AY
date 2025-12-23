# Déploiement Manuel AY HR v3.6.1 - Serveur 192.168.20.55

## Étape par Étape

### 1. Connexion au serveur
```powershell
ssh root@192.168.20.55
```

### 2. Sauvegarde de la base de données
```bash
mkdir -p /root/backups/ay_hr
mysqldump -u root -p ay_hr > /root/backups/ay_hr/backup_$(date +%Y%m%d_%H%M%S).sql
```

### 3. Mise à jour du code depuis GitHub
```bash
cd /root/AY_HR
git fetch origin
git reset --hard origin/main
git pull origin main
```

### 4. Vérifier la version
```bash
cd /root/AY_HR/backend
grep APP_VERSION config.py
```
Devrait afficher: `APP_VERSION: str = "3.6.1"`

### 5. Appliquer les migrations
```bash
cd /root/AY_HR/database
mysql -u root -p ay_hr < migration_v3.6.1_conges_credits_contrats.sql
```

### 6. Mettre à jour les dépendances backend
```bash
cd /root/AY_HR/backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 7. Redémarrer le backend
```bash
# Arrêter le processus existant
pkill -f 'uvicorn main:app'

# Démarrer le nouveau
cd /root/AY_HR/backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/ay_hr_backend.log 2>&1 &
```

### 8. Vérifier le démarrage
```bash
# Attendre 3 secondes
sleep 3

# Vérifier les logs
tail -20 /var/log/ay_hr_backend.log

# Vérifier que l'API répond
curl http://localhost:8000/docs
```

### 9. Tester l'API
Ouvrir dans le navigateur: http://192.168.20.55:8000/docs

## Nouvelles Fonctionnalités v3.6.1 à Tester

### 1. Gestion des congés avec déduction flexible
- Endpoint: `POST /conges`
- Test: Créer un congé avec `mois_deduction` différent du `mois` d'acquisition

### 2. Échéancier automatique des crédits
- Endpoint: `POST /credits`
- Test: Créer un crédit - les dates de début/fin sont calculées automatiquement

### 3. Auto-désactivation des contrats expirés
- Endpoint: `GET /employes/contrats-expires`
- Endpoint: `POST /employes/verifier-contrats-expires`
- Test: Vérifier les employés avec contrat expiré

## Commandes de Surveillance

### Logs en temps réel
```bash
tail -f /var/log/ay_hr_backend.log
```

### Vérifier processus
```bash
ps aux | grep uvicorn
```

### Vérifier port 8000
```bash
lsof -i :8000
```

## En cas de problème

### Restaurer la base de données
```bash
# Trouver la sauvegarde
ls -lt /root/backups/ay_hr/

# Restaurer
mysql -u root -p ay_hr < /root/backups/ay_hr/backup_YYYYMMDD_HHMMSS.sql
```

### Redémarrer complètement
```bash
pkill -9 -f 'uvicorn main:app'
cd /root/AY_HR/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Vérifier la configuration
```bash
cat /root/AY_HR/backend/.env
```

## Notes

- Le mot de passe MySQL root sera demandé pour la sauvegarde et la migration
- Le backend redémarre en arrière-plan avec nohup
- Les logs sont dans `/var/log/ay_hr_backend.log`
- L'API est accessible sur le port 8000
