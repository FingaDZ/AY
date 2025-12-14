# 🚀 GUIDE DÉPLOIEMENT RAPIDE - Correctifs v3.5.3

**Date** : 14 décembre 2025  
**Serveur** : 192.168.20.55  
**Durée estimée** : 5 minutes

---

## ⚡ ÉTAPES DE DÉPLOIEMENT

### **1. Connexion et Pull**

```bash
ssh root@192.168.20.55
cd /opt/ay-hr
git pull origin main
```

**Résultat attendu** :
```
From https://github.com/FingaDZ/AY
 * branch            main       -> FETCH_HEAD
Updating 4705811..e074d25
Fast-forward
 backend/routers/conges.py           |   32 ++
 backend/routers/pointages.py        |   26 ++
 backend/services/conges_calculator.py | 189 +++++++++++++
 6 files changed, 1810 insertions(+)
```

---

### **2. Redémarrage Backend**

```bash
cd /opt/ay-hr
sudo systemctl restart ayhr-backend
```

**Vérifier démarrage** :
```bash
sudo journalctl -u ayhr-backend -n 50 --no-pager | grep -E "startup|version|error"
```

**Attendu** : Aucune erreur, version 3.5.3 visible

---

### **3. Recalcul Congés (SI BASE VIDE)**

**Vérifier si congés existent** :
```bash
mysql -u root -p -e "SELECT COUNT(*) FROM ay_hr.conges;"
```

**Si COUNT = 0** (base vide après vidage) :
```bash
# Recalculer décembre 2025
curl -X POST "http://localhost:8000/api/conges/recalculer-periode?annee=2025&mois=12" \
  -H "Content-Type: application/json"

# Recalculer novembre 2025 (si nécessaire)
curl -X POST "http://localhost:8000/api/conges/recalculer-periode?annee=2025&mois=11" \
  -H "Content-Type: application/json"
```

**Résultat attendu** :
```json
{
  "message": "Recalcul terminé pour 12/2025",
  "recalcules": 46,
  "erreurs": 0,
  "details": [...]
}
```

---

### **4. Tests Fonctionnels**

#### **Test A : Création pointage + calcul auto**

1. Aller sur interface : http://192.168.20.55
2. Pointages → Créer un nouveau pointage pour un employé
3. Remplir quelques jours (ex: 26 jours)
4. Sauvegarder

**Vérification** :
```bash
# Vérifier congés créés automatiquement
mysql -u root -p -e "
SELECT e.nom, e.prenom, c.jours_travailles, c.jours_conges_acquis, c.jours_conges_pris
FROM ay_hr.conges c
JOIN ay_hr.employes e ON c.employe_id = e.id
WHERE c.annee = 2025 AND c.mois = 12
ORDER BY c.id DESC
LIMIT 5;
"
```

**Attendu** : Nouvel enregistrement avec `jours_conges_acquis` calculé

---

#### **Test B : Affectation congés pris (ancien problème)**

1. Aller sur Congés
2. Sélectionner un employé avec quelques jours de pointages
3. Affecter 1 ou 2 jours de congés pris
4. Sauvegarder

**Avant** : ❌ Erreur 500 `Enregistrement congé non trouvé`  
**Après** : ✅ Succès `Consommation mise à jour`

---

#### **Test C : Logs en temps réel**

```bash
# Suivre les logs pendant les tests
sudo journalctl -u ayhr-backend -f | grep -E "CONGES|ERROR"
```

**Logs attendus lors création pointage** :
```
[CONGES] Employé 29, 12/2025: jours_travailles_brut = 26
[CONGES] jours_conges_pris = 0.0, jours_reellement_travailles = 26
[CONGES] jours_conges_acquis calculés = 2.17
[CONGES] Création nouveau conge #123
```

---

## 🔍 VÉRIFICATIONS POST-DÉPLOIEMENT

### **1. Backend opérationnel**

```bash
systemctl status ayhr-backend
```

**Attendu** : `active (running)`

---

### **2. API accessible**

```bash
curl http://localhost:8000/ | grep "3.5.3"
```

**Attendu** : Version 3.5.3 dans la réponse

---

### **3. Congés dans la base**

```bash
mysql -u root -p -e "
SELECT 
    COUNT(*) as total_enregistrements,
    SUM(jours_conges_acquis) as total_acquis,
    SUM(jours_conges_pris) as total_pris
FROM ay_hr.conges
WHERE annee = 2025 AND mois = 12;
"
```

**Attendu** : 
- `total_enregistrements` > 0
- `total_acquis` > 0

---

### **4. Pas d'erreurs dans logs**

```bash
sudo journalctl -u ayhr-backend --since "5 minutes ago" | grep -i "error"
```

**Attendu** : Aucune erreur critique

---

## 🆘 RÉSOLUTION PROBLÈMES

### **Problème 1 : Backend ne démarre pas**

```bash
# Vérifier logs détaillés
sudo journalctl -u ayhr-backend -n 100 --no-pager

# Vérifier imports Python
cd /opt/ay-hr
source venv/bin/activate
python -c "from services.conges_calculator import calculer_et_enregistrer_conges"
```

**Solution** : Vérifier que le fichier `backend/services/conges_calculator.py` existe et est accessible

---

### **Problème 2 : Endpoint recalcul ne fonctionne pas**

```bash
# Vérifier que le endpoint existe
curl http://localhost:8000/docs | grep "recalculer-periode"

# Test avec logs
tail -f /var/log/ayhr-backend.log &
curl -X POST "http://localhost:8000/api/conges/recalculer-periode?annee=2025&mois=12"
```

---

### **Problème 3 : Congés non calculés automatiquement**

```bash
# Vérifier que le calculateur est appelé
sudo journalctl -u ayhr-backend -f | grep CONGES

# Créer un pointage de test via interface et observer logs
```

**Solution** : Vérifier que l'import `from services.conges_calculator import ...` fonctionne dans `routers/pointages.py`

---

### **Problème 4 : Erreur 500 persiste**

**Vérifier manuellement la base** :
```bash
mysql -u root -p

USE ay_hr;

# Vérifier qu'un enregistrement Conge existe pour l'employé testé
SELECT * FROM conges WHERE employe_id = 204 AND annee = 2025 AND mois = 12;

# Si aucun enregistrement, créer manuellement
INSERT INTO conges (employe_id, annee, mois, jours_travailles, jours_conges_acquis, jours_conges_pris, jours_conges_restants)
VALUES (204, 2025, 12, 0, 0, 0, 0);
```

---

## 📋 CHECKLIST FINALE

- [ ] ✅ `git pull` exécuté avec succès
- [ ] ✅ Backend redémarré (`systemctl restart ayhr-backend`)
- [ ] ✅ Logs sans erreur critique
- [ ] ✅ API répond (curl http://localhost:8000/)
- [ ] ✅ Version 3.5.3 visible
- [ ] ✅ Recalcul congés batch exécuté (si nécessaire)
- [ ] ✅ Test création pointage → Congés calculés auto
- [ ] ✅ Test affectation congés pris → Pas d'erreur 500
- [ ] ✅ Base de données contient des enregistrements `conges`

---

## 🎯 COMMANDES RAPIDES (COPIER-COLLER)

```bash
# Tout en une fois
ssh root@192.168.20.55 << 'EOF'
cd /opt/ay-hr
git pull origin main
sudo systemctl restart ayhr-backend
sleep 3
sudo journalctl -u ayhr-backend -n 30 --no-pager | tail -15
echo "✅ Déploiement terminé !"
EOF

# Vérifier version
curl http://192.168.20.55/ 2>/dev/null | grep -o "3.5.3"

# Recalculer congés décembre 2025
curl -X POST "http://192.168.20.55/api/conges/recalculer-periode?annee=2025&mois=12" \
  -H "Content-Type: application/json" 2>/dev/null | python -m json.tool
```

---

## 📞 SUPPORT

**En cas de problème** :
1. Consulter [ANALYSE_LOGIQUE_CONGES_V3.5.3.md](ANALYSE_LOGIQUE_CONGES_V3.5.3.md) pour comprendre la logique
2. Consulter [CORRECTIFS_CALCUL_AUTO_CONGES_V3.5.3.md](CORRECTIFS_CALCUL_AUTO_CONGES_V3.5.3.md) pour les détails techniques
3. Vérifier logs backend : `sudo journalctl -u ayhr-backend -n 100`

---

**Déploiement créé le** : 14 décembre 2025  
**Version cible** : 3.5.3  
**Temps estimé** : 5 minutes
