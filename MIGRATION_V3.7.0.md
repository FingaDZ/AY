# Migration v3.7.0 - Nouvelle Architecture des Congés

## 🎯 Objectif

Refonte complète de la gestion des congés avec séparation claire entre:
- **Acquisition** (table `conges`): Jours acquis par période (immutable après pointage)
- **Consommation** (table `deductions_conges`): Enregistrements de prises de congés (audit trail)

## ❌ Problème de v3.6.1

L'ancienne approche mélangait acquisition et consommation dans la même table:
- `jours_conges_acquis` = ce qu'on gagne
- `jours_conges_pris` = ce qu'on prend

**Problèmes identifiés:**
1. Confusion entre période d'acquisition et période de déduction
2. Difficulté à tracer l'historique des prises de congés
3. Calculs complexes et sources d'erreurs
4. Impossible de voir quelles prises de congés impactent quel bulletin

## ✅ Solution v3.7.0

### Nouvelle Structure

#### Table `conges` (inchangée)
```sql
- id
- employe_id
- annee, mois
- jours_travailles
- jours_conges_acquis  ← Seul champ pertinent
- jours_conges_pris    ← DEPRECATED (sera supprimé en v4.0)
- mois_deduction       ← DEPRECATED
- annee_deduction      ← DEPRECATED
```

#### Table `deductions_conges` (NOUVELLE)
```sql
CREATE TABLE deductions_conges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employe_id INT NOT NULL,
    jours_deduits DECIMAL(5,2) NOT NULL,
    mois_deduction INT NOT NULL,      ← Bulletin concerné
    annee_deduction INT NOT NULL,     ← Bulletin concerné
    date_debut DATE,
    date_fin DATE,
    type_conge VARCHAR(50),
    motif TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (employe_id) REFERENCES employes(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### Logique de Calcul

**Solde Global:**
```
Solde = SUM(conges.jours_conges_acquis) - SUM(deductions_conges.jours_deduits)
WHERE employe_id = X
```

**Solde Cumulé (par période):**
```
Solde_cumule(mois, annee) = 
    SUM(conges.jours_conges_acquis WHERE date <= (mois,annee))
    - SUM(deductions_conges.jours_deduits)  ← Global!
```

**Bulletin de Paie:**
```sql
SELECT SUM(jours_deduits) 
FROM deductions_conges 
WHERE employe_id = X 
  AND mois_deduction = M 
  AND annee_deduction = A
```

## 📋 Étapes de Migration

### 1. Créer la Nouvelle Table

```bash
ssh root@192.168.20.55
cd /opt/ay-hr
mysql -u root -p ay_hr < database/migration_v3.7.0_deductions_conges.sql
```

La migration SQL va:
1. Créer la table `deductions_conges`
2. Migrer les données existantes de `conges.jours_conges_pris` vers `deductions_conges`
3. Créer une vue `v_conges_avec_deductions` pour compatibilité
4. Afficher des statistiques de vérification

### 2. Déployer le Nouveau Code Backend

```bash
cd /opt/ay-hr/backend
git pull origin main
systemctl restart ayhr-backend
```

**Nouveaux fichiers:**
- `backend/models/deduction_conge.py` - Nouveau modèle
- `backend/routers/deductions_conges.py` - Nouveaux endpoints
- `backend/services/salaire_calculator.py` - Utilise deductions_conges

**Modifications:**
- `backend/models/__init__.py` - Import DeductionConge
- `backend/models/employe.py` - Relation deductions_conges
- `backend/routers/conges.py` - Endpoint synthese modifié
- `backend/main.py` - Router deductions_conges ajouté

### 3. Mettre à Jour le Frontend (À FAIRE)

**Modifications nécessaires dans `frontend/src/pages/Conges/CongesList.jsx`:**

#### A. Supprimer la logique "Saisie" dans les détails
```jsx
// AVANT (v3.6.1):
const detailColumns = [
  // ...
  { 
    title: 'Actions', 
    render: (_, record) => <Button onClick={handleSave}>Saisie</Button>
  }
];

// APRÈS (v3.7.0):
const detailColumns = [
  // ... (juste affichage, pas de bouton Saisie)
];
```

#### B. Modifier le bouton "Éditer" pour créer une déduction
```jsx
// AVANT: Modal complexe avec répartition intelligente

// APRÈS: Modal simple
<Modal title="Créer une Déduction de Congé">
  <Form onFinish={handleCreateDeduction}>
    <Form.Item label="Jours à déduire" name="jours_deduits">
      <InputNumber min={0.1} step={0.5} />
    </Form.Item>
    <Form.Item label="Mois de déduction" name="mois_deduction">
      <Select>
        {[1,2,3,...,12].map(m => <Option value={m}>{m}</Option>)}
      </Select>
    </Form.Item>
    <Form.Item label="Année" name="annee_deduction">
      <InputNumber min={2024} max={2030} />
    </Form.Item>
    <Button type="primary" htmlType="submit">Créer</Button>
  </Form>
</Modal>
```

#### C. Appeler le nouveau endpoint
```jsx
const handleCreateDeduction = async (values) => {
  try {
    await axios.post('/api/deductions-conges/', {
      employe_id: selectedEmploye.id,
      jours_deduits: values.jours_deduits,
      mois_deduction: values.mois_deduction,
      annee_deduction: values.annee_deduction
    });
    message.success('Déduction créée avec succès');
    fetchConges(); // Recharger
  } catch (error) {
    message.error(error.response.data.detail);
  }
};
```

#### D. Afficher les déductions dans les détails
```jsx
// Récupérer les déductions
const [deductions, setDeductions] = useState([]);

useEffect(() => {
  if (selectedEmploye) {
    axios.get(`/api/deductions-conges/employe/${selectedEmploye.id}`)
      .then(res => setDeductions(res.data));
  }
}, [selectedEmploye]);

// Dans le modal de détails
<Table 
  title={() => "Historique des Déductions"}
  dataSource={deductions}
  columns={[
    { title: 'Jours', dataIndex: 'jours_deduits' },
    { title: 'Bulletin', render: (_, r) => `${r.mois_deduction}/${r.annee_deduction}` },
    { title: 'Type', dataIndex: 'type_conge' },
    { title: 'Date', dataIndex: 'created_at' },
    { 
      title: 'Actions', 
      render: (_, r) => (
        <Popconfirm onConfirm={() => deleteDeduction(r.id)}>
          <Button danger size="small">Supprimer</Button>
        </Popconfirm>
      )
    }
  ]}
/>
```

#### E. Mettre à jour l'affichage des totaux
```jsx
// Appeler le nouvel endpoint synthese
const [synthese, setSynthese] = useState(null);

useEffect(() => {
  if (selectedEmploye) {
    axios.get(`/api/conges/synthese/${selectedEmploye.id}`)
      .then(res => setSynthese(res.data));
  }
}, [selectedEmploye]);

// Affichage
<Descriptions>
  <Descriptions.Item label="Total Acquis">
    {synthese?.total_acquis}j
  </Descriptions.Item>
  <Descriptions.Item label="Total Déduit">
    {synthese?.total_deduit}j
  </Descriptions.Item>
  <Descriptions.Item label="Solde Disponible">
    <span style={{ color: synthese?.solde >= 0 ? 'green' : 'red' }}>
      {synthese?.solde}j
    </span>
  </Descriptions.Item>
</Descriptions>
```

## 🧪 Tests de Validation

### 1. Vérifier la Migration des Données
```sql
-- Comparer l'ancien et le nouveau
SELECT 
    e.nom,
    SUM(c.jours_conges_pris) as ancien_total_pris,
    (SELECT SUM(jours_deduits) FROM deductions_conges WHERE employe_id = e.id) as nouveau_total_deduit
FROM employes e
LEFT JOIN conges c ON c.employe_id = e.id
GROUP BY e.id
HAVING ancien_total_pris != nouveau_total_deduit;
-- Doit retourner 0 lignes!
```

### 2. Tester la Création de Déduction
```bash
curl -X POST http://192.168.20.55:8000/api/deductions-conges/ \
  -H "Content-Type: application/json" \
  -d '{
    "employe_id": 1,
    "jours_deduits": 2.5,
    "mois_deduction": 12,
    "annee_deduction": 2024,
    "type_conge": "ANNUEL"
  }'
```

### 3. Vérifier le Calcul du Solde
```bash
curl http://192.168.20.55:8000/api/deductions-conges/solde/1
```

Doit retourner:
```json
{
  "employe_id": 1,
  "employe_nom": "Prenom Nom",
  "total_acquis": 15.0,
  "total_deduit": 5.5,
  "solde_disponible": 9.5,
  "periodes": [...]
}
```

### 4. Tester le Bulletin de Paie
Créer un bulletin pour Décembre 2024 et vérifier que la ligne "Congé" affiche le bon nombre de jours déduits.

## 📊 Nouveaux Endpoints API

### POST /api/deductions-conges/
Créer une nouvelle déduction
- Body: `{ employe_id, jours_deduits, mois_deduction, annee_deduction, ... }`
- Validation du solde automatique
- Retourne: ancien_solde, nouveau_solde

### GET /api/deductions-conges/employe/{id}
Lister toutes les déductions d'un employé
- Query params: `?annee=2024` (optionnel)
- Retourne: liste des déductions avec détails

### GET /api/deductions-conges/solde/{id}
Calculer le solde actuel d'un employé
- Retourne: total_acquis, total_deduit, solde_disponible, periodes

### DELETE /api/deductions-conges/{id}
Supprimer une déduction (annuler)
- Recalcule automatiquement les soldes

### GET /api/conges/synthese/{id} (MODIFIÉ)
Nouveau format avec déductions_conges
- Retourne: total_acquis, total_deduit (au lieu de total_pris)

## 🔍 Points de Vigilance

1. **Migration de Données**: Les `jours_conges_pris` existants seront transformés en `deductions_conges` avec `mois_deduction` = mois d'acquisition si non spécifié

2. **Compatibilité Temporaire**: La vue `v_conges_avec_deductions` permet de garder l'ancien format pendant la transition

3. **Suppression des Champs Deprecated**: En v4.0.0, on supprimera `jours_conges_pris`, `mois_deduction`, `annee_deduction` de la table `conges`

4. **Validation du Solde**: Le système empêche automatiquement la création de déductions si le solde est insuffisant

5. **Audit Trail**: Chaque déduction enregistre `created_by` et `created_at` pour traçabilité

## 📈 Avantages de la Nouvelle Architecture

✅ **Clarté**: Séparation nette acquisition vs consommation  
✅ **Traçabilité**: Historique complet des prises de congés  
✅ **Flexibilité**: Déductions multiples pour un même bulletin  
✅ **Simplicité**: Plus besoin de "répartition intelligente"  
✅ **Audit**: Qui a créé quelle déduction et quand  
✅ **Correction**: Possibilité d'annuler une déduction (DELETE)  

## 🚀 Prochaines Étapes

1. ✅ Créer la table `deductions_conges` (SQL)
2. ✅ Créer le modèle `DeductionConge` (Python)
3. ✅ Créer le router `deductions_conges.py` (API)
4. ✅ Modifier `salaire_calculator.py` (Bulletin)
5. ✅ Modifier `conges.py::synthese` (Affichage)
6. ⏳ Modifier le frontend `CongesList.jsx` (UI)
7. ⏳ Tester la migration sur données réelles
8. ⏳ Déployer en production
9. ⏳ Former les utilisateurs

## 📝 Notes de Version

**v3.7.0** - Architecture des Congés Réinventée
- Nouvelle table `deductions_conges` pour l'audit trail
- Endpoints API dédiés aux déductions
- Calcul de solde basé sur les déductions réelles
- Simplicité de saisie: un formulaire, une déduction
- Bulletin de paie: agrégation par mois/année de déduction
