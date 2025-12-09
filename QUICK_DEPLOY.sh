#!/bin/bash
# =============================================================================
# AIDE-MÉMOIRE RAPIDE - Déploiement AY HR v2.5.0 sur 192.168.20.55
# =============================================================================

echo "
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║         🚀 DÉPLOIEMENT AY HR v2.5.0 - Serveur 192.168.20.55         ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

📋 COMMANDES RAPIDES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  CONNEXION SSH
   ssh root@192.168.20.55

2️⃣  VÉRIFIER ÉTAT ACTUEL
   cd /opt/ay-hr
   git status
   git log --oneline -3
   systemctl status ayhr-backend ayhr-frontend

3️⃣  LANCER MISE À JOUR
   chmod +x update.sh
   ./update.sh

4️⃣  SUIVRE LES LOGS (autre terminal)
   tail -f /opt/ay-hr/logs/update_*.log
   # ou
   journalctl -u ayhr-backend -f
   journalctl -u ayhr-frontend -f

5️⃣  VÉRIFIER APRÈS MISE À JOUR
   systemctl status ayhr-backend ayhr-frontend
   curl http://192.168.20.55:8000/docs
   curl http://192.168.20.55:3000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 CE QUE FAIT update.sh
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/8] ✅ Backup base de données → /opt/ay-hr/backups/
[2/8] ✅ Backup configuration (.env) → /opt/ay-hr/backups/
[3/8] ✅ Arrêt des services (ayhr-backend, ayhr-frontend)
[4/8] ✅ Git pull origin main (récupère v2.5.0)
[5/8] ✅ Mise à jour backend (pip install -r requirements.txt)
[6/8] ✅ Mise à jour frontend (npm install + build)
[7/8] ✅ Correction des permissions
[8/8] ✅ Redémarrage des services

⏱️  Durée totale: ~3-4 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🆘 EN CAS DE PROBLÈME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Voir les logs:
   cat /opt/ay-hr/logs/update_*.log | tail -100
   journalctl -u ayhr-backend -n 100 --no-pager
   journalctl -u ayhr-frontend -n 100 --no-pager

Restaurer backup DB:
   cd /opt/ay-hr/backups
   gunzip -c db_backup_YYYYMMDD_HHMMSS.sql.gz | mysql -u ay_hr -p ay_hr

Restaurer config:
   tar -xzf config_backup_YYYYMMDD_HHMMSS.tar.gz -C /

Redémarrer manuellement:
   systemctl restart ayhr-backend
   systemctl restart ayhr-frontend

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ VÉRIFICATIONS POST-DÉPLOIEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ Services actifs: systemctl status ayhr-backend ayhr-frontend
□ API fonctionne: curl http://192.168.20.55:8000/docs
□ Frontend charge: curl http://192.168.20.55:3000
□ Version correcte: grep APP_VERSION /opt/ay-hr/backend/config.py
□ Logs sans erreur: journalctl -u ayhr-backend -n 50
□ Accès navigateur: http://192.168.20.55:3000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 DOCUMENTATION COMPLÈTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• DEPLOYMENT_STEPS.md → Guide complet étape par étape
• ANALYSE_PROJET.md → Architecture et relations DB
• SESSION_RAPPORT.md → Commandes utiles et stats
• GITHUB_UPDATE_SUMMARY.md → Résumé mise à jour GitHub

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 VERSION CIBLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Version: v2.5.0
Commit: 9c2e3c1
Date: 9 Décembre 2025
GitHub: https://github.com/FingaDZ/AY

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 BACKUP AUTOMATIQUE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Base de données: /opt/ay-hr/backups/db_backup_*.sql.gz
Configuration: /opt/ay-hr/backups/config_backup_*.tar.gz
Logs: /opt/ay-hr/logs/update_*.log
Rétention: 30 jours (nettoyage automatique)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 SUPPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Consulter DEPLOYMENT_STEPS.md (procédure complète)
2. Vérifier journalctl -u ayhr-backend -f (logs temps réel)
3. Rollback avec backups si nécessaire
4. Vérifier GitHub Issues: https://github.com/FingaDZ/AY/issues

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Tout est prêt ! Bonne mise à jour ! ✨

"
