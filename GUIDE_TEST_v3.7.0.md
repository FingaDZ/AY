# Guide de Test v3.7.0 - Interface Utilisateur

## 🎯 Tests à Effectuer

### 1. Test Basique: Création de Déduction

**Étapes:**
1. Se connecter à http://192.168.20.55:3000
2. Aller dans **Congés**
3. Sélectionner un employé dans le filtre (ex: SAIFI)
4. Vérifier la carte de statistiques affiche:
   - Total Acquis
   - **Total Déduit** (au lieu de Total Pris)
   - Solde Global
5. Cliquer sur le bouton **"Déduire"** (au lieu de "Éditer")
6. Un modal s'ouvre: "Créer une Déduction de Congé"
7. Remplir:
   - Jours à déduire: **1.5**
   - Mois de déduction: **Janvier**
   - Année: **2026**
   - Type: **Annuel**
   - Motif: **Test v3.7.0**
8. Cliquer **"Créer"**
9. ✅ Vérifier le message: "Déduction créée: 1.5j pour bulletin 1/2026. Nouveau solde: Xj"
10. ✅ Vérifier que le tableau se met à jour automatiquement

**Résultat attendu:**
- Message de succès avec nouveau solde
- Solde dans le tableau diminué de 1.5j
- Pas d'erreur console

---

### 2. Test Validation: Solde Insuffisant

**Étapes:**
1. Toujours sur le même employé
2. Cliquer **"Déduire"**
3. Saisir un nombre de jours > solde disponible (ex: 100j)
4. Cliquer **"Créer"**
5. ✅ Vérifier message d'erreur: "Solde insuffisant! Disponible: Xj, Demandé: 100j"

**Résultat attendu:**
- Déduction refusée
- Message d'erreur clair
- Solde inchangé

---

### 3. Test Historique: Voir les Déductions

**Étapes:**
1. Cliquer sur **"Détails"** pour un employé
2. Le modal s'ouvre avec:
   - En haut: Statistiques (Total Acquis, Solde Cumulé, Déductions)
   - Première table: **"Périodes d'Acquisition"** (lecture seule, pas de bouton Saisie)
   - Divider: **"Historique des Déductions"**
   - Deuxième table: Liste des déductions
3. ✅ Vérifier que la déduction créée à l'étape 1 apparaît
4. ✅ Vérifier les colonnes: Jours, Bulletin, Type, Motif, Créé le, Actions

**Résultat attendu:**
- Historique complet visible
- Déduction de test affichée
- Date de création correcte
- Motif "Test v3.7.0" visible

---

### 4. Test Suppression de Déduction

**Étapes:**
1. Dans le modal Détails, section "Historique des Déductions"
2. Cliquer sur **"Supprimer"** pour la déduction de test
3. Confirmer dans le Popconfirm
4. ✅ Vérifier message: "Déduction supprimée, solde recalculé"
5. ✅ Vérifier que la ligne disparaît de la table
6. Fermer et rouvrir les détails
7. ✅ Vérifier que le solde a augmenté de 1.5j

**Résultat attendu:**
- Déduction supprimée
- Solde restauré
- Calculs cohérents

---

### 5. Test Bulletin de Paie

**Étapes:**
1. Créer une déduction pour **Décembre 2025**:
   - Employé: SAIFI
   - Jours: 1.0
   - Mois: 12
   - Année: 2025
2. Aller dans **Salaires**
3. Générer le bulletin de **Décembre 2025** pour SAIFI
4. ✅ Vérifier que la ligne "Congé" dans le PDF affiche **1.0j**
5. Comparer avec l'historique des déductions:
   - Somme des déductions pour 12/2025 = 1.0j
6. ✅ Cohérence bulletin ↔ déductions

**Résultat attendu:**
- Bulletin PDF correct
- Jours de congé = somme des déductions du mois
- Calcul salaire correct

---

### 6. Test Multi-Déductions

**Étapes:**
1. Pour un même employé, créer **3 déductions** pour le même mois:
   - Déduction 1: 0.5j pour Janvier 2026
   - Déduction 2: 1.0j pour Janvier 2026
   - Déduction 3: 0.5j pour Janvier 2026
2. Vérifier l'historique (3 lignes)
3. Générer bulletin Janvier 2026
4. ✅ Vérifier: Total congé = 2.0j (somme des 3)

**Résultat attendu:**
- Plusieurs déductions possibles pour un même bulletin
- Somme correcte dans le bulletin
- Traçabilité de chaque déduction

---

### 7. Test Ancien vs Nouveau

**Comparaison avec v3.6.1:**

| Aspect | v3.6.1 (Ancien) | v3.7.0 (Nouveau) |
|--------|-----------------|------------------|
| Bouton action | "Éditer" | "Déduire" |
| Modal | Complexe (répartition intelligente) | Simple (1 déduction) |
| Champ principal | "Total de jours à prendre" (remplace tout) | "Jours à déduire" (additionne) |
| Saisie détails | Bouton "Saisie" dans chaque période | ❌ Supprimé (lecture seule) |
| Historique | ❌ Non visible | ✅ Table complète |
| Suppression | ❌ Impossible | ✅ Avec recalcul |
| Stats | Total Pris | Total Déduit |

---

## 🐛 Points de Vigilance

### Console Browser
Ouvrir F12 et vérifier qu'il n'y a pas:
- ❌ Erreurs rouges
- ⚠️ Warnings critiques
- ✅ Requêtes API qui retournent 200

### Endpoints Appelés
Avec F12 → Network:
- `GET /api/conges/synthese/{id}` → 200
- `GET /api/deductions-conges/employe/{id}` → 200
- `POST /api/deductions-conges/` → 200 (lors de création)
- `DELETE /api/deductions-conges/{id}` → 200 (lors de suppression)

### Calculs
Vérifier manuellement:
```
Solde = Total Acquis - Total Déduit

Exemple SAIFI:
  Acquis: 4.92j
  Déduit: 3.00j
  Solde: 1.92j ✅
```

---

## ✅ Checklist Validation

- [ ] Créer déduction: OK
- [ ] Validation solde insuffisant: OK
- [ ] Voir historique déductions: OK
- [ ] Supprimer déduction: OK
- [ ] Bulletin PDF cohérent: OK
- [ ] Multi-déductions même mois: OK
- [ ] Stats "Total Déduit" affichées: OK
- [ ] Détails en lecture seule: OK
- [ ] Pas d'erreur console: OK
- [ ] Performance acceptable: OK

---

## 📊 Scénario Complet Utilisateur

**Cas d'usage réel:**

1. **Novembre 2025**: Employé travaille, acquiert 2.5j
2. **Décembre 2025**: Employé travaille, acquiert 2.5j
3. **Total acquis**: 5.0j
4. **Janvier 2026**: Employé prend 3 jours de congé
5. **Action RH**:
   - Aller dans Congés
   - Sélectionner l'employé
   - Cliquer "Déduire"
   - Jours: 3.0
   - Mois: Janvier 2026
   - Créer
6. **Résultat**:
   - Solde: 5.0 - 3.0 = 2.0j
   - Bulletin Janvier 2026: -3j de congé
   - Historique: 1 déduction enregistrée
7. **Si erreur de saisie**:
   - Aller dans Détails
   - Supprimer la déduction erronée
   - Recréer avec le bon montant

---

## 🎓 Formation Utilisateurs

**Message clé:**
> "Chaque fois qu'un employé prend des congés, créez une déduction.  
> C'est comme un retrait bancaire: chaque opération est enregistrée.  
> Le solde se calcule automatiquement."

**Différence principale:**
- **Avant**: Une seule saisie "total global" qui écrasait tout
- **Maintenant**: Une déduction par prise de congé, traçable et modifiable

**Avantage:**
- Historique complet
- Corrections faciles
- Audit trail
- Plusieurs prises pour un même bulletin

---

## 📞 Support

Si problème:
1. Vérifier logs backend: `ssh root@192.168.20.55 "journalctl -u ayhr-backend -n 50"`
2. Vérifier console browser (F12)
3. Tester endpoints manuellement (voir DEBUGGING_V3.7.0.md)
4. Consulter VALIDATION_V3.7.0_COMPLETE.md
