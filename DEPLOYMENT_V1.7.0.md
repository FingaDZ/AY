# Guide de Déploiement v1.7.0

**Date** : 26 Novembre 2025
**Version** : 1.7.0 (Stable)
**Feature** : Hybrid Incomplete Logs Management

## 📋 Nouveautés

Cette version introduit une gestion robuste des logs de pointage incomplets (Entrée sans Sortie ou inversement).

### Fonctionnalités
- **Calcul Intelligent** : Estimation automatique des heures travaillées pour les logs incomplets.
- **Dashboard RH** : Interface dédiée pour valider ou corriger les estimations.
- **Notifications** : Alertes lors de l'import si des logs nécessitent une validation.

## 🚀 Mise à Jour (Production)

Si vous utilisez le script de mise à jour automatique :

```bash
cd /opt/ay-hr
sudo ./update.sh
```

### Mise à Jour Manuelle

1. **Mettre à jour le code**
   ```bash
   cd /opt/ay-hr
   git pull origin main
   ```

2. **Mettre à jour le Backend**
   La nouvelle table `incomplete_attendance_logs` sera créée automatiquement au redémarrage.
   ```bash
   # Redémarrer le service backend
   sudo systemctl restart ay-hr-backend
   ```

3. **Reconstruire le Frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

4. **Vérification**
   - Accédez à `http://votre-serveur:3000`
   - Vérifiez que le numéro de version en bas du menu est **v1.7.0**
   - Vérifiez la présence du nouveau menu **Logs Incomplets**

## ⚠️ Notes Importantes

- **Base de Données** : Une nouvelle table `incomplete_attendance_logs` est ajoutée. Aucune migration complexe n'est requise, `init_db()` s'en charge.
- **Configuration** : Aucune nouvelle variable d'environnement requise.

## 🤝 Support

En cas de problème, consultez les logs du backend :
```bash
journalctl -u ay-hr-backend -f
```
