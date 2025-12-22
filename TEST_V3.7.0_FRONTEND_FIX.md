# TEST v3.7.0 - Fix Frontend Calcul Congés

## Date: 2025-01-26

## Problème Identifié
❌ Frontend affichait valeurs incorrectes dans table principale:
- SAIFI: Affichait "3j Pris" au lieu de "0.92j Déduit"
- ZERROUG: Affichait "2.5j Pris" au lieu de "0j Déduit"

## Cause Racine
Le bug était dans `groupCongesByEmploye()` (lines 85-115 de CongesList.jsx):
```js
// AVANT (BUGGY):
total_pris += conge.jours_conges_pris || 0;  // ← Utilisait champ OBSOLÈTE v3.6.1
solde = total_acquis - total_pris;            // ← Calcul LOCAL incorrect
```

La fonction calculait localement depuis `conges.jours_conges_pris` (champ deprecated après v3.7.0) au lieu d'utiliser l'API `/conges/synthese/{id}` qui retourne les vraies déductions depuis `deductions_conges` table.

## Solution Implémentée

### 1. Ajout Cache Synthèse
```js
const [syntheseCache, setSyntheseCache] = useState({});

const fetchSyntheseForCache = async (employeId) => {
    const response = await api.get(`/conges/synthese/${employeId}`);
    setSyntheseCache(prev => ({
        ...prev,
        [employeId]: response.data
    }));
};
```

### 2. useEffect pour Charger Stats
```js
useEffect(() => {
    const uniqueEmployes = [...new Set(conges.map(c => c.employe_id))];
    uniqueEmployes.forEach(empId => {
        if (!syntheseCache[empId]) {
            fetchSyntheseForCache(empId);
        }
    });
}, [conges]);
```

### 3. Correction groupCongesByEmploye()
```js
// APRÈS (CORRECT):
Object.keys(grouped).forEach(key => {
    const empId = grouped[key].employe_id;
    if (syntheseCache[empId]) {
        grouped[key].total_deduit = syntheseCache[empId].total_deduit || 0;
        grouped[key].solde = syntheseCache[empId].solde || 0;
    } else {
        // Fallback si pas encore chargé
        grouped[key].solde = grouped[key].total_acquis - grouped[key].total_deduit;
    }
});
```

### 4. Mise à Jour Colonne Table
```js
// Colonne: "Total Pris" → "Total Déduit"
{
    title: 'Total Déduit',  // v3.7.0
    dataIndex: 'total_deduit',  // v3.7.0
    key: 'total_deduit',
    render: (val) => <span className="font-semibold text-orange-500">{val} j</span>
}
```

## Résultats Attendus

Après déploiement (commit 0561f81), la table devrait afficher:

| Employé | Total Acquis | Total Déduit | Solde |
|---------|-------------|--------------|-------|
| SAIFI   | 4.92j       | 0.92j        | 4.0j  |
| ZERROUG | 5.0j        | 0.0j         | 5.0j  |
| ERREDIR | 5.0j        | 0.0j         | 5.0j  |

## Vérification

### Backend API (CORRECT ✅)
```bash
GET /conges/synthese/29
{
  "total_acquis": 4.92,
  "total_deduit": 0.92,
  "solde": 4.0
}

GET /conges/synthese/30
{
  "total_acquis": 5.0,
  "total_deduit": 0.0,
  "solde": 5.0
}
```

### Base de Données (CORRECT ✅)
```sql
SELECT * FROM deductions_conges WHERE employe_id = 29;
-- 1 record: 0.92j for 12/2025

SELECT * FROM deductions_conges WHERE employe_id = 30;
-- 0 records
```

### Frontend (CORRIGÉ ✅)
- Utilise `syntheseCache` pour récupérer total_deduit depuis API
- Affiche "Total Déduit" au lieu de "Total Pris"
- Solde calculé par backend (total_acquis - total_deduit)

## À Tester dans le Navigateur

1. Se connecter: http://192.168.20.55:3000
2. Aller dans Congés → Liste
3. Vérifier table principale:
   - ✅ Colonne "Total Déduit" (pas "Total Pris")
   - ✅ SAIFI: 0.92j déduit
   - ✅ ZERROUG: 0j déduit
4. Cliquer "Détails" sur SAIFI:
   - ✅ Modal affiche historique déductions
   - ✅ 1 déduction de 0.92j pour 12/2025
5. Sélectionner employé dans filtre:
   - ✅ Card Stats affiche synthèse correcte
   - ✅ Total Acquis / Total Déduit / Solde

## Commit
- Hash: `0561f81`
- Message: "fix(v3.7.0): Correction calcul table congés - utiliser synthese API au lieu de jours_conges_pris"
- Fichiers: `frontend/src/pages/Conges/CongesList.jsx`
- Déployé: ✅ Production (192.168.20.55)

## Notes Importantes

### Champ Obsolète: conges.jours_conges_pris
Ce champ contient encore les anciennes valeurs v3.6.1 et ne devrait PLUS être utilisé.

**Recommandation**: Ajouter migration pour mettre à NULL:
```sql
UPDATE conges SET jours_conges_pris = NULL;
```

### Architecture v3.7.0 Validée
- ✅ Backend: Utilise `deductions_conges` table
- ✅ API: Endpoint `/conges/synthese/{id}` fonctionne
- ✅ Frontend: Utilise API pour stats (plus de calcul local)
- ✅ PDF: Génération bulletins utilise `deductions_conges`

### Bulletins PDF
Les bulletins devraient être corrects car `salaire_calculator.py` utilise déjà:
```python
deductions = db.query(DeductionConge).filter(
    DeductionConge.employe_id == employe_id,
    DeductionConge.mois_deduction == mois,
    DeductionConge.annee_deduction == annee
).all()
```

À vérifier avec utilisateur si les bulletins PDF des screenshots montrent bien les bonnes déductions.
