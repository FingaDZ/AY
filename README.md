# AY HR System v3.5.1

## 🎉 Nouveautés Version 3.5.1 (Décembre 2025)
- 🐛 **Pointages Fix** : Correction sauvegarde manuelle - ne plus écraser les jours NULL
- 📅 **NOUVELLES RÈGLES CONGÉS** : Système simplifié sans décimales
  - **8 jours travaillés = 1 jour de congé** (plus de 2.5j/30j)
  - Nouveaux: minimum 15 jours pour 1 jour
  - **Plus de décimales** : valeurs entières avec arrondi intelligent
  - **Exclusion critiques** : Congés pris exclus du calcul des droits
- 🔧 **Backend** : API retourne seulement les jours avec valeur (pas NULL)
- 🎯 **Frontend** : N'envoie que les jours modifiés lors de la sauvegarde
- 📝 **Logs** : Ajout logs de debug pour tracer les mises à jour
- ✨ **Vendredi Intelligent** : Logique automatique basée sur Jeudi/Samedi

## 📋 Historique des Versions

### v3.5.1 - 12 décembre 2025
- 🐛 **CORRECTIF CRITIQUE** : Pointages - Sauvegarde manuelle ne fonctionne pas
  - Backend : `_pointage_to_response` n'envoie que les jours non-NULL
  - Frontend : `handleSaveAll` envoie seulement les jours avec valeur
  - Logs : Ajout de debug dans `update_pointage`
  - Résultat : Les modifications sont maintenant bien enregistrées en DB

- 📅 **REFONTE SYSTÈME CONGÉS** : Nouvelles règles simplifiées
  - **Règle 1** : 8 jours travaillés = 1 jour de congé
    * 8-15 jours → 1 jour
    * 16-23 jours → 2 jours
    * 24-30+ jours → 3 jours
  - **Règle 2** : Nouveaux recrutés (<3 mois) : minimum 15 jours pour 1 jour
  - **Règle 3** : Plus de décimales (0.3j, 0.8j), uniquement valeurs entières
  - **Règle 4** : Jours de congé PRIS exclus du calcul des jours travaillés
  - Migration SQL : `database/migration_conges_v3.5.1.sql`

### v3.5.0 - 11 décembre 2025
- 📄 **PDF Enhancement** : Footers automatiques, marges étroites, QR codes
- 🆔 **ANEM Integration** : Numéro ANEM dans tous les documents
- 📋 **Contrats v13** : 13 types de contrats avec numérotation unique
- 🎫 **Congés** : Ligne congé dans bulletins de paie
- 🔧 **Pointages** : Congé = valeur 1 (jour travaillé payé)

### v3.0.0 - 09 décembre 2025
- 🧮 **Traitement Salaires** : Module complet de calcul proratisé avec filtres avancés
- 🔢 **Proratisation Base 30j** : Toutes primes/indemnités calculées proportionnellement
- 📊 **Statistiques Enrichies** : 4 cartes (Masse Nette, Cotisable, Imposable, IRG)
- 🔍 **Filtres Multi-Critères** : Recherche par Nom, Statut, Salaire Min/Max
- 🐛 **Correctifs** : Fix Credit.montant_mensualite et Mission.prime_calculee

### v2.5.0 - 08 décembre 2025
- 🧮 **Traitement Salaires** : Première version (architecture + backend + frontend)
- 🚫 **Désactivation** : Ancien module "Edition Salaires" désactivé

### v2.4.3 - 07 décembre 2025
- 📝 **PDF Ordre Mission** : Correction erreur 500 + améliorations mise en page
- 📦 **Logistique** : Ajout cases Montant versé (x3) et Observations (x2.5)
- 🔗 **API Logistique** : Route `/clients/{id}/logistics-balance` pour soldes
- 🎨 **UI Clients** : Modal affichage soldes logistiques par client

### v2.3.0 - 29 novembre 2025
- 🗑️ **Nettoyage** : Suppression du module "Logs Incomplets"
- 🔄 **Version** : Passage global à la version 2.3.0

### v2.2.0 - 29 novembre 2025
- 🔄 **Refactoring Majeur** : Système d'import complètement refactoré
- 📊 **Calculs Journaliers** : 1 entrée + 1 sortie par jour avec règles métier
- ⚖️ **Règles Business** : Vendredis travaillés par défaut, règle "Vendredi entre Absences"
- 🎯 **Estimation Intelligente** : Entrée/sortie manquante estimée automatiquement
- 🗑️ **Nettoyage** : Suppression pages redondantes
- 🔍 **Filtres Avancés** : Statut + Employé + Date
- 📋 **Colonnes Améliorées** : Date, Jour, Entrée, Sortie, Durée, H.Sup, Statut, Pointage
- ⚡ **Import Direct** : Option import rapide sans prévisualisation

### v2.1.0 - 29 novembre 2025
- 🎯 **Import Preview** : Prévisualisation et validation avant import
- 🧠 **Matching Intelligent** : Fuzzy matching avec Levenshtein (auto-match ≥85%)
- ⚠️ **Validation Avancée** : Détection conflits, doublons, logs incomplets
- 📊 **Statistiques** : Résumé complet (OK/Warning/Error)
- 🔗 **Nouveaux Endpoints** : `/import-preview`, `/import-confirm`

### v2.0.3 - 29 novembre 2025
- 🐛 **Correctif Critique** : Fix compatibilité Pydantic v2 pour endpoint conflits (erreur 500)
- ✨ **Amélioration** : Affichage noms et postes employés sur page Conflits Import
- 📊 **UX** : Meilleure lisibilité des conflits d'importation

### v2.0.2 - 29 novembre 2025
- ✨ **Import Excel** : Ajout de l'importation manuelle de fichiers Excel pour les pointages
- 🐛 **Correctif** : Validation et parsing améliorés pour les fichiers d'import

### v2.0.1 - 29 novembre 2025
- 🐛 **Correctif** : Résolution des problèmes de cache navigateur après mise à jour
- 🐛 **Correctif** : Affichage de la version et branding sur tous les écrans
- 🔄 **Système** : Amélioration du script de déploiement

### v1.7.0 - 29 novembre 2025
- 🛡️ **Gestion Logs Incomplets** : Solution hybride (Calcul Smart + Validation RH)
- 📊 **Dashboard** : Interface de validation des estimations
- 🚀 **Fiabilité** : Import robuste sans perte de données
- 📱 **UI** : Notifications et badges pour actions requises

### v1.3.0 - 25 novembre 2025
- 🔗 **Intégration Attendance** : Backend complet (sync employés, import logs, gestion conflits)
- 🗄️ **Database** : 3 nouvelles tables + colonne heures_supplementaires

### v1.2.4 - 25 novembre 2025
- ✨ **Gestion Utilisateurs** : Restauration du module Admin
- 📄 **Documentation** : Analyse système Attendance
- 🔧 **Scripts** : install.sh et update.sh automatisés

[Voir le changelog complet](CHANGELOG.md)

## 🔗 Intégration Attendance

### Fonctionnalités (v1.3.0-beta)

- ✅ **Sync Employés** : HR → Attendance (nom, poste, PIN)
- ✅ **Import Pointages** : Attendance → HR (conversion minutes → jours)
- ✅ **Heures Supplémentaires** : Calcul automatique (>8h/jour)
- ✅ **Gestion Conflits** : Détection et résolution manuelle
- ✅ **Mapping Intelligent** : Par numéro sécu sociale ou nom+prénom+date

### Documentation

- [ATTENDANCE_INTEGRATION.md](ATTENDANCE_INTEGRATION.md) - Stratégie d'intégration
- [ATTENDANCE_FRONTEND_GUIDE.md](ATTENDANCE_FRONTEND_GUIDE.md) - Guide implémentation UI
- [DEPLOYMENT_V1.3.0-BETA.md](DEPLOYMENT_V1.3.0-BETA.md) - Guide déploiement

### API Endpoints

Accédez à la documentation interactive : `http://192.168.20.53:8000/docs`

Section **"Attendance Integration"** :
- `POST /sync-employee` - Synchroniser un employé
- `POST /sync-all-employees` - Synchroniser tous les employés
- `POST /import-logs` - Importer les pointages
- `GET /conflicts` - Lister les conflits
- `POST /conflicts/{id}/resolve` - Résoudre un conflit

## 🤝 Support

Pour toute question ou problème:
1. Consultez la [documentation API](http://192.168.20.53:8000/docs)
2. Vérifiez le [CHANGELOG.md](CHANGELOG.md)
3. Consultez les guides de déploiement
4. Intégration Attendance : voir [ATTENDANCE_INTEGRATION.md](ATTENDANCE_INTEGRATION.md)

## 📜 Licence

Usage interne - Tous droits réservés

---

**Développé par AIRBAND**  
**Version** : 2.4.3  
**Date** : 06 décembre 2025
