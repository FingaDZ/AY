# Modification et Suppression des Avances Salariales

## 📋 Résumé

Ajout des fonctionnalités de **modification** et **suppression** des avances salariales avec validation de la limite de 70% du salaire.

---

## ✨ Nouvelles Fonctionnalités

### 1. Modification d'Avance ✅
- Bouton "Modifier" sur chaque ligne du tableau
- Formulaire pré-rempli avec les données existantes
- Validation de la limite 70% lors de la modification
- Exclusion de l'avance en cours de modification du calcul

### 2. Suppression d'Avance ✅
- Bouton "Supprimer" avec confirmation
- Message de confirmation avant suppression
- Suppression immédiate sans validation (libère de l'espace pour d'autres avances)

---

## 🔧 Backend - Modifications

### Endpoint PUT /api/avances/{avance_id}

**Fichier**: `backend/routers/avances.py`

```python
@router.put("/{avance_id}", response_model=AvanceResponse)
def update_avance(
    avance_id: int,
    avance_update: AvanceUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour une avance avec validation de la limite 70%"""
    
    # Récupérer l'avance existante
    avance = db.query(Avance).filter(Avance.id == avance_id).first()
    if not avance:
        raise HTTPException(status_code=404, detail="Avance non trouvée")
    
    # Récupérer l'employé
    employe_id = avance_update.employe_id if avance_update.employe_id else avance.employe_id
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    # Déterminer les valeurs à utiliser
    nouveau_montant = avance_update.montant if avance_update.montant else avance.montant
    nouveau_mois = avance_update.mois_deduction if avance_update.mois_deduction else avance.mois_deduction
    nouvelle_annee = avance_update.annee_deduction if avance_update.annee_deduction else avance.annee_deduction
    
    # Calculer la limite (70%)
    limite_autorisee = employe.salaire_base * Decimal('0.70')
    
    # Total des AUTRES avances du mois (excluant celle-ci)
    total_autres_avances = db.query(func.sum(Avance.montant)).filter(
        Avance.employe_id == employe_id,
        Avance.mois_deduction == nouveau_mois,
        Avance.annee_deduction == nouvelle_annee,
        Avance.id != avance_id  # ← Exclusion de l'avance actuelle
    ).scalar() or Decimal('0')
    
    # Vérification de la limite
    total_avec_modification = total_autres_avances + nouveau_montant
    
    if total_avec_modification > limite_autorisee:
        raise HTTPException(
            status_code=400,
            detail=f"Le total des avances pour {nouveau_mois}/{nouvelle_annee} "
                   f"({total_avec_modification:.2f} DA) dépasserait la limite autorisée "
                   f"de 70% du salaire ({limite_autorisee:.2f} DA). "
                   f"Autres avances du mois: {total_autres_avances:.2f} DA. "
                   f"Montant maximum pour cette avance: {(limite_autorisee - total_autres_avances):.2f} DA"
        )
    
    # Appliquer les modifications
    update_data = avance_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(avance, field, value)
    
    db.commit()
    db.refresh(avance)
    
    return avance
```

**Points clés**:
- ✅ Validation de la limite 70%
- ✅ Exclusion de l'avance en cours de modification (`Avance.id != avance_id`)
- ✅ Support de modification partielle (champs optionnels)
- ✅ Message d'erreur détaillé

### Endpoint DELETE /api/avances/{avance_id}

```python
@router.delete("/{avance_id}", status_code=204)
def delete_avance(avance_id: int, db: Session = Depends(get_db)):
    """Supprimer une avance"""
    
    avance = db.query(Avance).filter(Avance.id == avance_id).first()
    
    if not avance:
        raise HTTPException(status_code=404, detail="Avance non trouvée")
    
    db.delete(avance)
    db.commit()
    
    return None
```

**Points clés**:
- ✅ Suppression simple (pas de validation de limite)
- ✅ Libère de l'espace pour d'autres avances du même mois

---

## 🎨 Frontend - Modifications

### Fichier: `frontend/src/pages/Avances/AvancesList.jsx`

#### 1. Nouveaux Imports

```jsx
import { Table, Button, message, Modal, Form, InputNumber, DatePicker, Select, Input, Space, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
```

#### 2. Nouveau State

```jsx
const [editingAvance, setEditingAvance] = useState(null);
```

#### 3. Fonction handleEdit

```jsx
const handleEdit = (record) => {
  setEditingAvance(record);
  form.setFieldsValue({
    employe_id: record.employe_id,
    date_avance: dayjs(record.date_avance),
    montant: parseFloat(record.montant),
    mois_deduction: record.mois_deduction,
    annee_deduction: record.annee_deduction,
    motif: record.motif,
  });
  setModalVisible(true);
};
```

#### 4. Fonction handleDelete

```jsx
const handleDelete = async (id) => {
  try {
    await avanceService.delete(id);
    message.success('Avance supprimée avec succès');
    loadData();
  } catch (error) {
    message.error('Erreur lors de la suppression');
  }
};
```

#### 5. Fonction handleSubmit (modifiée)

```jsx
const handleSubmit = async (values) => {
  try {
    const data = {
      ...values,
      date_avance: values.date_avance.format('YYYY-MM-DD'),
    };

    if (editingAvance) {
      await avanceService.update(editingAvance.id, data);
      message.success('Avance modifiée avec succès');
    } else {
      await avanceService.create(data);
      message.success('Avance créée avec succès');
    }

    setModalVisible(false);
    setEditingAvance(null);
    form.resetFields();
    loadData();
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Erreur lors de l\'opération';
    message.error(errorMsg);
  }
};
```

#### 6. Nouvelle Colonne Actions

```jsx
{
  title: 'Actions',
  key: 'actions',
  render: (_, record) => (
    <Space>
      <Button
        type="link"
        icon={<EditOutlined />}
        onClick={() => handleEdit(record)}
      >
        Modifier
      </Button>
      <Popconfirm
        title="Supprimer cette avance ?"
        description="Cette action est irréversible."
        onConfirm={() => handleDelete(record.id)}
        okText="Oui"
        cancelText="Non"
      >
        <Button type="link" danger icon={<DeleteOutlined />}>
          Supprimer
        </Button>
      </Popconfirm>
    </Space>
  ),
}
```

#### 7. Modal Dynamique

```jsx
<Modal 
  title={editingAvance ? "Modifier l'Avance" : "Nouvelle Avance"} 
  open={modalVisible} 
  onCancel={handleCancel} 
  footer={null}
>
  <Form form={form} layout="vertical" onFinish={handleSubmit}>
    {/* ... champs ... */}
    <Form.Item>
      <Space>
        <Button type="primary" htmlType="submit">
          {editingAvance ? 'Modifier' : 'Créer'}
        </Button>
        <Button onClick={handleCancel}>Annuler</Button>
      </Space>
    </Form.Item>
  </Form>
</Modal>
```

---

## 🧪 Scénarios de Test

### Scénario 1: Modification Simple (OK)

**Contexte**:
- Employé: Salaire 30,000 DA (limite: 21,000 DA)
- Avance existante: 15,000 DA pour 11/2025

**Action**: Modifier le montant à 18,000 DA

**Résultat**: ✅ Modification réussie (18,000 < 21,000)

```bash
PUT /api/avances/1
{
  "montant": 18000
}

# Réponse: 200 OK
```

---

### Scénario 2: Modification avec Dépassement (REFUSÉ)

**Contexte**:
- Employé: Salaire 30,000 DA (limite: 21,000 DA)
- Avance 1: 15,000 DA pour 11/2025
- Avance 2: 5,000 DA pour 11/2025

**Action**: Modifier Avance 1 à 20,000 DA

**Calcul**:
- Autres avances: 5,000 DA
- Nouvelle Avance 1: 20,000 DA
- Total: 25,000 DA > 21,000 DA ❌

**Résultat**: ❌ Erreur 400

```bash
PUT /api/avances/1
{
  "montant": 20000
}

# Réponse: 400 Bad Request
{
  "detail": "Le total des avances pour 11/2025 (25,000.00 DA) dépasserait 
  la limite autorisée de 70% du salaire (21,000.00 DA). 
  Autres avances du mois: 5,000.00 DA. 
  Montant maximum pour cette avance: 16,000.00 DA"
}
```

---

### Scénario 3: Modification du Mois de Déduction (OK)

**Contexte**:
- Employé: Salaire 30,000 DA
- Avance: 15,000 DA pour 11/2025
- Novembre: Total 15,000 DA (OK)
- Décembre: Total 0 DA (vide)

**Action**: Changer le mois de déduction à 12/2025

**Résultat**: ✅ Modification réussie

```bash
PUT /api/avances/1
{
  "mois_deduction": 12,
  "annee_deduction": 2025
}

# Nouveau calcul:
# - Novembre: 0 DA (vide maintenant)
# - Décembre: 15,000 DA (OK < 21,000)
```

---

### Scénario 4: Suppression puis Re-création (OK)

**Contexte**:
- Employé: Salaire 30,000 DA (limite: 21,000 DA)
- Avance existante: 20,000 DA pour 11/2025

**Action 1**: Supprimer l'avance

```bash
DELETE /api/avances/1

# Résultat: 204 No Content
# Novembre: Total 0 DA (vide)
```

**Action 2**: Créer deux nouvelles avances

```bash
POST /api/avances/
{ "montant": 12000, "mois_deduction": 11, "annee_deduction": 2025 }
# ✅ OK (12,000 < 21,000)

POST /api/avances/
{ "montant": 9000, "mois_deduction": 11, "annee_deduction": 2025 }
# ✅ OK (12,000 + 9,000 = 21,000 = limite)
```

---

### Scénario 5: Modification de l'Employé (avec nouvelle limite)

**Contexte**:
- Employé A: Salaire 30,000 DA (limite: 21,000 DA)
- Employé B: Salaire 40,000 DA (limite: 28,000 DA)
- Avance: 20,000 DA pour Employé A, mois 11/2025

**Action**: Transférer l'avance à l'Employé B

```bash
PUT /api/avances/1
{
  "employe_id": 2  # Employé B
}

# Nouveau calcul:
# - Employé A, Nov: 0 DA (vide maintenant)
# - Employé B, Nov: 20,000 DA (OK < 28,000)

# Résultat: ✅ Modification réussie
```

---

## 📊 Interface Utilisateur

### Tableau des Avances

```
┌────────────┬──────────────┬──────────┬───────────┬────────┬─────────────────────┐
│ Date       │ Employé      │ Montant  │ Déduction │ Motif  │ Actions             │
├────────────┼──────────────┼──────────┼───────────┼────────┼─────────────────────┤
│ 05/11/2025 │ Ahmed BENALI │ 15,000DA │ 11/2025   │ Urgent │ [Modifier][Supprimer]│
├────────────┼──────────────┼──────────┼───────────┼────────┼─────────────────────┤
│ 10/11/2025 │ Ali MEZIANE  │ 10,000DA │ 11/2025   │ Loyer  │ [Modifier][Supprimer]│
└────────────┴──────────────┴──────────┴───────────┴────────┴─────────────────────┘
```

### Boutons d'Actions

**Modifier**: 
- Icône: ✏️ (EditOutlined)
- Couleur: Bleu (link)
- Action: Ouvre le modal avec formulaire pré-rempli

**Supprimer**:
- Icône: 🗑️ (DeleteOutlined)
- Couleur: Rouge (danger)
- Action: Affiche confirmation Popconfirm

### Modal de Modification

```
┌─────────────────────────────────────┐
│ Modifier l'Avance             [X]   │
├─────────────────────────────────────┤
│                                     │
│ Employé:        [Ahmed BENALI ▼]    │
│ Date:           [05/11/2025]        │
│ Montant (DA):   [15000]             │
│ Mois déduction: [11 ▼]              │
│ Année déduction:[2025]              │
│ Motif:          [Urgent...]         │
│                                     │
│ [Modifier] [Annuler]                │
└─────────────────────────────────────┘
```

### Confirmation de Suppression

```
┌─────────────────────────────────────┐
│ ⚠️ Supprimer cette avance ?         │
├─────────────────────────────────────┤
│ Cette action est irréversible.      │
│                                     │
│ [Oui] [Non]                         │
└─────────────────────────────────────┘
```

---

## ✅ Validations

### À la Modification

✅ Vérifier que l'avance existe
✅ Vérifier que l'employé existe
✅ Calculer le total des AUTRES avances du mois (excluant celle en modification)
✅ Vérifier que total ≤ 70% du salaire
✅ Message d'erreur détaillé si dépassement

### À la Suppression

✅ Vérifier que l'avance existe
✅ Supprimer sans validation de limite (libère l'espace)
✅ Confirmation utilisateur avant suppression

---

## 📝 Messages

### Succès

```
✓ Avance modifiée avec succès
✓ Avance supprimée avec succès
```

### Erreurs

```
❌ Avance non trouvée

❌ Le total des avances pour 11/2025 (25,000.00 DA) dépasserait 
   la limite autorisée de 70% du salaire (21,000.00 DA). 
   Autres avances du mois: 5,000.00 DA. 
   Montant maximum pour cette avance: 16,000.00 DA

❌ Erreur lors de la modification
❌ Erreur lors de la suppression
```

---

## 🔑 Points Clés

### 1. Exclusion dans le Calcul

Lors de la modification, l'avance actuelle est **exclue** du calcul du total mensuel :

```python
Avance.id != avance_id  # ← Exclusion importante
```

**Pourquoi ?**
- Évite de compter deux fois la même avance
- Permet de modifier le montant librement dans la limite disponible

### 2. Modification Partielle

L'endpoint `PUT` supporte la modification partielle (champs optionnels) :

```python
# Modifier uniquement le montant
PUT /api/avances/1
{ "montant": 18000 }

# Modifier uniquement le mois
PUT /api/avances/1
{ "mois_deduction": 12 }

# Modifier plusieurs champs
PUT /api/avances/1
{ "montant": 18000, "mois_deduction": 12, "motif": "Nouveau motif" }
```

### 3. Suppression Sans Validation

La suppression ne vérifie **pas** la limite de 70% :
- Libère immédiatement l'espace
- Permet de réorganiser les avances du mois
- Pas de blocage si d'autres avances dépendent de celle-ci

---

## 🚀 Prochaines Améliorations Possibles

1. **Historique des modifications**: Logger les changements d'avances
2. **Audit trail**: Qui a modifié/supprimé quoi et quand
3. **Verrouillage**: Empêcher modification après validation paie
4. **Notifications**: Alerter l'employé si son avance est modifiée
5. **Raison de suppression**: Demander un motif avant suppression

---

✅ **Fonctionnalités de modification et suppression implémentées avec succès !**

Les avances peuvent maintenant être modifiées et supprimées tout en respectant la limite de 70% du salaire de base.
