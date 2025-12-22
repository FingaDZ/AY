# Frontend - Modifications Requises pour v3.7.0

## 📁 Fichier Principal: `frontend/src/pages/Conges/CongesList.jsx`

### 🔴 Modifications à Effectuer

#### 1. SUPPRIMER la Logique Intelligente de Répartition

**Lignes à supprimer:**
- Fonction `repartirCongesIntelligemment()` (environ lignes 125-155)
- Fonction `handleSave()` dans les détails (logique de mise à jour consommation)
- Bouton "Saisie" dans `detailColumns`

```jsx
// ❌ SUPPRIMER CETTE LOGIQUE
const repartirCongesIntelligemment = async () => { ... };
const handleSave = async () => {
  await axios.put(`/api/conges/${record.id}/consommation`, ...);
};

// ❌ SUPPRIMER CE BOUTON DES DETAILS
detailColumns = [
  // ...
  {
    title: 'Actions',
    render: (_, record) => (
      <Button onClick={() => handleSave(record)}>Saisie</Button>
    )
  }
];
```

#### 2. MODIFIER le Bouton "Éditer"

**Actuellement:** Ouvre un modal complexe avec répartition  
**Nouveau:** Ouvre un simple formulaire de création de déduction

```jsx
// ✅ NOUVEAU CODE
const [deductionModalVisible, setDeductionModalVisible] = useState(false);
const [selectedEmployeForDeduction, setSelectedEmployeForDeduction] = useState(null);

const handleOpenDeductionModal = (employe_id) => {
  setSelectedEmployeForDeduction(employe_id);
  setDeductionModalVisible(true);
};

const handleCreateDeduction = async (values) => {
  try {
    const response = await axios.post('/api/deductions-conges/', {
      employe_id: selectedEmployeForDeduction,
      jours_deduits: values.jours_deduits,
      mois_deduction: values.mois_deduction,
      annee_deduction: values.annee_deduction,
      type_conge: values.type_conge || 'ANNUEL',
      motif: values.motif
    });
    
    message.success(
      `Déduction créée: ${response.data.jours_deduits}j pour bulletin ${values.mois_deduction}/${values.annee_deduction}. ` +
      `Nouveau solde: ${response.data.nouveau_solde}j`
    );
    
    setDeductionModalVisible(false);
    fetchConges(); // Recharger les données
  } catch (error) {
    message.error(error.response?.data?.detail || 'Erreur lors de la création de la déduction');
  }
};
```

#### 3. AJOUTER le Modal de Création de Déduction

```jsx
<Modal
  title="Créer une Déduction de Congé"
  open={deductionModalVisible}
  onCancel={() => setDeductionModalVisible(false)}
  footer={null}
  width={500}
>
  <Form
    layout="vertical"
    onFinish={handleCreateDeduction}
    initialValues={{
      mois_deduction: new Date().getMonth() + 1,
      annee_deduction: new Date().getFullYear(),
      type_conge: 'ANNUEL'
    }}
  >
    <Alert
      message="Nouvelle Architecture v3.7.0"
      description="Cette déduction sera enregistrée séparément et impactera le bulletin du mois sélectionné."
      type="info"
      showIcon
      style={{ marginBottom: 16 }}
    />
    
    <Form.Item
      label="Nombre de jours à déduire"
      name="jours_deduits"
      rules={[
        { required: true, message: 'Requis' },
        { type: 'number', min: 0.1, message: 'Minimum 0.1j' }
      ]}
    >
      <InputNumber
        style={{ width: '100%' }}
        min={0.1}
        max={30}
        step={0.5}
        precision={2}
        placeholder="Ex: 2.5"
      />
    </Form.Item>
    
    <Form.Item
      label="Mois de déduction (bulletin)"
      name="mois_deduction"
      rules={[{ required: true, message: 'Requis' }]}
    >
      <Select placeholder="Sélectionnez le mois">
        {[
          { value: 1, label: 'Janvier' },
          { value: 2, label: 'Février' },
          { value: 3, label: 'Mars' },
          { value: 4, label: 'Avril' },
          { value: 5, label: 'Mai' },
          { value: 6, label: 'Juin' },
          { value: 7, label: 'Juillet' },
          { value: 8, label: 'Août' },
          { value: 9, label: 'Septembre' },
          { value: 10, label: 'Octobre' },
          { value: 11, label: 'Novembre' },
          { value: 12, label: 'Décembre' }
        ].map(m => (
          <Select.Option key={m.value} value={m.value}>
            {m.label}
          </Select.Option>
        ))}
      </Select>
    </Form.Item>
    
    <Form.Item
      label="Année de déduction"
      name="annee_deduction"
      rules={[{ required: true, message: 'Requis' }]}
    >
      <InputNumber
        style={{ width: '100%' }}
        min={2020}
        max={2030}
        placeholder="2024"
      />
    </Form.Item>
    
    <Form.Item
      label="Type de congé"
      name="type_conge"
    >
      <Select>
        <Select.Option value="ANNUEL">Annuel</Select.Option>
        <Select.Option value="MALADIE">Maladie</Select.Option>
        <Select.Option value="EXCEPTIONNEL">Exceptionnel</Select.Option>
      </Select>
    </Form.Item>
    
    <Form.Item
      label="Motif (optionnel)"
      name="motif"
    >
      <Input.TextArea rows={2} placeholder="Ex: Vacances d'été" />
    </Form.Item>
    
    <Form.Item>
      <Space>
        <Button type="primary" htmlType="submit">
          Créer la Déduction
        </Button>
        <Button onClick={() => setDeductionModalVisible(false)}>
          Annuler
        </Button>
      </Space>
    </Form.Item>
  </Form>
</Modal>
```

#### 4. AJOUTER l'Affichage des Déductions dans les Détails

```jsx
const [deductions, setDeductions] = useState([]);

// Dans useEffect ou fonction de chargement
const fetchDeductions = async (employe_id) => {
  try {
    const response = await axios.get(`/api/deductions-conges/employe/${employe_id}`);
    setDeductions(response.data);
  } catch (error) {
    console.error('Erreur chargement déductions:', error);
  }
};

// Appeler lors de l'ouverture du modal de détails
const handleShowDetails = (employe_id) => {
  // ... code existant ...
  fetchDeductions(employe_id);
};

// Dans le modal de détails, APRÈS la table des périodes:
<Divider>Historique des Déductions</Divider>

<Table
  dataSource={deductions}
  columns={[
    {
      title: 'Jours',
      dataIndex: 'jours_deduits',
      render: (val) => `${val}j`,
      width: 80
    },
    {
      title: 'Bulletin',
      render: (_, record) => `${record.mois_deduction}/${record.annee_deduction}`,
      width: 100
    },
    {
      title: 'Type',
      dataIndex: 'type_conge',
      width: 100
    },
    {
      title: 'Motif',
      dataIndex: 'motif',
      ellipsis: true
    },
    {
      title: 'Créé le',
      dataIndex: 'created_at',
      render: (val) => new Date(val).toLocaleDateString('fr-FR'),
      width: 100
    },
    {
      title: 'Actions',
      render: (_, record) => (
        <Popconfirm
          title="Supprimer cette déduction?"
          description="Le solde sera recalculé automatiquement."
          onConfirm={() => handleDeleteDeduction(record.id)}
          okText="Oui"
          cancelText="Non"
        >
          <Button danger size="small" icon={<DeleteOutlined />}>
            Supprimer
          </Button>
        </Popconfirm>
      ),
      width: 120
    }
  ]}
  pagination={false}
  size="small"
  locale={{ emptyText: 'Aucune déduction' }}
/>
```

#### 5. AJOUTER la Fonction de Suppression

```jsx
const handleDeleteDeduction = async (deduction_id) => {
  try {
    await axios.delete(`/api/deductions-conges/${deduction_id}`);
    message.success('Déduction supprimée, solde recalculé');
    fetchConges(); // Recharger tout
    fetchDeductions(selectedEmployeForDeduction); // Recharger les déductions
  } catch (error) {
    message.error(error.response?.data?.detail || 'Erreur lors de la suppression');
  }
};
```

#### 6. METTRE À JOUR l'Affichage de la Synthèse

**Endpoint changé:** `/api/conges/synthese/{employe_id}` retourne maintenant `total_deduit` au lieu de `total_pris`

```jsx
// ✅ NOUVEAU FORMAT
const [synthese, setSynthese] = useState(null);

useEffect(() => {
  if (selectedEmploye) {
    axios.get(`/api/conges/synthese/${selectedEmploye.id}`)
      .then(res => setSynthese(res.data))
      .catch(err => console.error(err));
  }
}, [selectedEmploye]);

// Affichage
<Descriptions bordered column={3}>
  <Descriptions.Item label="Total Acquis" span={1}>
    <Tag color="blue">{synthese?.total_acquis || 0}j</Tag>
  </Descriptions.Item>
  
  <Descriptions.Item label="Total Déduit" span={1}>
    <Tag color="orange">{synthese?.total_deduit || 0}j</Tag>
  </Descriptions.Item>
  
  <Descriptions.Item label="Solde Disponible" span={1}>
    <Tag color={synthese?.solde >= 0 ? 'green' : 'red'}>
      {synthese?.solde || 0}j
    </Tag>
  </Descriptions.Item>
</Descriptions>
```

#### 7. METTRE À JOUR les Colonnes du Tableau Principal

```jsx
const columns = [
  // ... colonnes existantes ...
  {
    title: 'Acquis',
    dataIndex: 'jours_conges_acquis',
    render: (val) => `${val}j`,
    sorter: (a, b) => a.jours_conges_acquis - b.jours_conges_acquis
  },
  {
    title: 'Solde Cumulé',
    dataIndex: 'jours_conges_restants',
    render: (val) => (
      <Tag color={val >= 0 ? 'green' : 'red'}>
        {val}j
      </Tag>
    ),
    sorter: (a, b) => a.jours_conges_restants - b.jours_conges_restants
  },
  {
    title: 'Actions',
    render: (_, record) => (
      <Space>
        <Button
          type="primary"
          size="small"
          onClick={() => handleOpenDeductionModal(record.employe_id)}
        >
          Éditer
        </Button>
        <Button
          size="small"
          onClick={() => handleShowDetails(record.employe_id)}
        >
          Détails
        </Button>
      </Space>
    )
  }
];
```

## 🧪 Tests Frontend

### Test 1: Créer une Déduction
1. Aller dans Congés
2. Cliquer sur "Éditer" pour un employé
3. Remplir le formulaire:
   - Jours: 2.5
   - Mois: 12
   - Année: 2024
4. Cliquer "Créer la Déduction"
5. ✅ Message de succès avec nouveau solde
6. ✅ Table mise à jour automatiquement

### Test 2: Voir l'Historique
1. Cliquer sur "Détails" pour un employé
2. ✅ Section "Historique des Déductions" affichée
3. ✅ Liste des déductions avec dates et montants

### Test 3: Supprimer une Déduction
1. Dans les détails, cliquer "Supprimer" sur une déduction
2. Confirmer
3. ✅ Déduction supprimée
4. ✅ Solde recalculé automatiquement

### Test 4: Validation Solde Insuffisant
1. Essayer de créer une déduction de 50j
2. ✅ Message d'erreur: "Solde insuffisant! Disponible: Xj, Demandé: 50j"

## 📋 Checklist Complète

- [ ] Supprimer `repartirCongesIntelligemment()` et logique associée
- [ ] Supprimer bouton "Saisie" des détails
- [ ] Créer modal de création de déduction
- [ ] Ajouter fonction `handleCreateDeduction()`
- [ ] Modifier bouton "Éditer" pour ouvrir le nouveau modal
- [ ] Ajouter table des déductions dans modal détails
- [ ] Ajouter fonction `handleDeleteDeduction()`
- [ ] Mettre à jour endpoint synthèse (total_pris → total_deduit)
- [ ] Mettre à jour affichage des colonnes
- [ ] Tester création de déduction
- [ ] Tester suppression de déduction
- [ ] Tester validation solde insuffisant
- [ ] Vérifier cohérence des calculs avec backend

## 🎨 Améliorations Visuelles (Optionnelles)

```jsx
// Badge pour indiquer le nombre de déductions
<Badge count={nb_deductions} offset={[10, 0]}>
  <Button onClick={handleShowDetails}>Détails</Button>
</Badge>

// Tooltip pour expliquer le solde cumulé
<Tooltip title="Solde calculé en tenant compte de toutes les déductions globales">
  <Tag color={val >= 0 ? 'green' : 'red'}>
    {val}j
  </Tag>
</Tooltip>

// Alert dans le modal de déduction
<Alert
  message={`Solde disponible: ${solde}j`}
  type={solde > 0 ? 'success' : 'warning'}
  showIcon
  style={{ marginBottom: 16 }}
/>
```

## 🚀 Déploiement Frontend

Une fois les modifications effectuées:

```bash
cd frontend
npm run build
rsync -avz --delete dist/ root@192.168.20.55:/opt/ay-hr/frontend/dist/
ssh root@192.168.20.55 "systemctl restart ayhr-frontend"
```

Ou utiliser le script PowerShell existant:
```powershell
.\push_v3_update.ps1 -version "3.7.0"
```
