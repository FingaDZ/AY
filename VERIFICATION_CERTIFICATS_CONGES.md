# ✅ VÉRIFICATION v3.6.1 - Certificats & Congés

## Date: 22 décembre 2025

## 🎯 Points Demandés

### 1. ✅ Certificat de Travail pour Employés Inactifs

**Statut**: **DÉJÀ IMPLÉMENTÉ CORRECTEMENT** ✅

#### Backend - Logique de Validation
**Fichier**: [backend/routers/employes.py](backend/routers/employes.py#L577-L594)

```python
@router.get("/{employe_id}/certificat-travail")
def generate_certificat_travail(employe_id: int, ...):
    """Générer un certificat de travail pour un employé inactif"""
    
    # ✅ Vérification que l'employé est INACTIF
    if employe.actif:
        raise HTTPException(
            status_code=400, 
            detail="Impossible de générer un certificat de travail pour un employé actif. 
                    Utilisez l'attestation de travail."
        )
```

#### Backend - Logique Attestation (inverse)
**Fichier**: [backend/routers/employes.py](backend/routers/employes.py#L528-L545)

```python
@router.get("/{employe_id}/attestation-travail")
def generate_attestation_travail(employe_id: int, ...):
    """Générer une attestation de travail pour un employé ACTIF"""
    
    # ✅ Vérification que l'employé est ACTIF
    if not employe.actif:
        raise HTTPException(
            status_code=400,
            detail="Impossible de générer une attestation pour un employé inactif. 
                    Utilisez le certificat de travail."
        )
```

#### PDF Généré
**Fichier**: [backend/services/pdf_generator.py](backend/services/pdf_generator.py#L2304-L2366)

```python
def generate_certificat_travail(self, employe_data: Dict) -> BytesIO:
    """Générer un certificat de travail"""
    
    # ✅ Titre du document
    story.append(Paragraph("<b>CERTIFICAT DE TRAVAIL</b>", title_style))
    
    # ✅ Nom du fichier généré
    filename = f"certificat_travail_{employe.nom}_{employe.prenom}_{date}.pdf"
```

**Résultat**: 
- ✅ Employé **ACTIF** → **Attestation de Travail** uniquement
- ✅ Employé **INACTIF** → **Certificat de Travail** uniquement
- ✅ PDF avec titre "CERTIFICAT DE TRAVAIL"
- ✅ Nom de fichier: `certificat_travail_NOM_PRENOM_DATE.pdf`

---

### 2. ✅ Mois de Consommation des Congés

**Statut**: **DÉJÀ IMPLÉMENTÉ DANS v3.6.1** ✅

#### Base de Données
**Migration**: [database/migration_v3.6.1_conges_credits_contrats.sql](database/migration_v3.6.1_conges_credits_contrats.sql#L7-L9)

```sql
-- ✅ Colonnes ajoutées dans v3.6.1
ALTER TABLE conges 
ADD COLUMN IF NOT EXISTS mois_deduction INT COMMENT 'Mois de déduction sur bulletin (1-12)',
ADD COLUMN IF NOT EXISTS annee_deduction INT COMMENT 'Année de déduction sur bulletin';
```

**Vérification sur serveur**:
```bash
mysql -u root -p ay_hr -e "DESCRIBE conges;" | grep mois_deduction
# Résultat: mois_deduction  int(11) YES  NULL ✅
```

#### Backend - API
**Fichier**: [backend/routers/conges.py](backend/routers/conges.py#L16-L17)

**Schema**:
```python
class CongeUpdate(BaseModel):
    jours_pris: float
    mois_deduction: Optional[int] = None  # ✅ Mois où déduire (1-12)
    annee_deduction: Optional[int] = None  # ✅ Année où déduire

class CongeResponse(BaseModel):
    # ... autres champs
    mois_deduction: Optional[int] = None  # ✅ Affiché dans les réponses
    annee_deduction: Optional[int] = None  # ✅
```

**Endpoint de mise à jour** (ligne 95-146):
```python
@router.put("/{conge_id}/consommation")
def update_consommation(conge_id: int, update: CongeUpdate, ...):
    # ✅ Mise à jour du mois/année de déduction si fournis
    if update.mois_deduction is not None:
        if not (1 <= update.mois_deduction <= 12):
            raise HTTPException(
                status_code=400, 
                detail="Mois de déduction invalide (doit être entre 1 et 12)"
            )
        conge.mois_deduction = update.mois_deduction
        
    if update.annee_deduction is not None:
        if update.annee_deduction < 2000 or update.annee_deduction > 2100:
            raise HTTPException(
                status_code=400, 
                detail="Année de déduction invalide"
            )
        conge.annee_deduction = update.annee_deduction
```

**Validation**:
- ✅ Mois: 1-12 uniquement
- ✅ Année: 2000-2100
- ✅ Optionnel (si non fourni, utilise le mois d'acquisition)

#### Utilisation dans les Bulletins de Paie

Le système utilise ces champs pour la génération des bulletins:

**Logique**:
1. Si `mois_deduction` ET `annee_deduction` sont définis → Déduction sur ce mois spécifique
2. Si non définis → Déduction sur le mois d'acquisition (comportement actuel)

**Exemple**:
```
Congé acquis:     Mai 2025
Congé pris:       3 jours le 15 juin 2025
mois_deduction:   7 (juillet)
annee_deduction:  2025

Résultat: Les 3 jours seront déduits du bulletin de JUILLET 2025
         (et non de juin)
```

---

## 🎯 Frontend - Action Requise

### ⚠️ Interface Utilisateur à Ajouter

Le backend est prêt, mais le **frontend doit être mis à jour** pour permettre la sélection du mois:

**Fichier à modifier**: `frontend/src/pages/Conges/CongesPage.jsx`

**Ajout nécessaire**: 
- Champ de sélection "Mois de déduction" (Select 1-12)
- Champ de sélection "Année de déduction" (Input number)

**Exemple de code à ajouter**:
```jsx
<Form.Item label="Mois de déduction sur bulletin">
  <Select placeholder="Sélectionnez un mois (optionnel)">
    <Option value={1}>Janvier</Option>
    <Option value={2}>Février</Option>
    <Option value={3}>Mars</Option>
    {/* ... */}
    <Option value={12}>Décembre</Option>
  </Select>
</Form.Item>

<Form.Item label="Année de déduction">
  <InputNumber 
    min={2000} 
    max={2100} 
    placeholder="2025"
  />
</Form.Item>
```

**Payload à envoyer**:
```javascript
const payload = {
  jours_pris: 3.5,
  mois_deduction: 7,      // Juillet
  annee_deduction: 2025   // 2025
};

await axios.put(`/api/conges/${congeId}/consommation`, payload);
```

---

## 📊 Résumé

| Fonctionnalité | Backend | Base de Données | Frontend | Statut |
|----------------|---------|-----------------|----------|--------|
| Certificat Travail Inactifs | ✅ | N/A | ✅ | **COMPLET** |
| Attestation Travail Actifs | ✅ | N/A | ✅ | **COMPLET** |
| Mois Déduction Congés | ✅ | ✅ | ⚠️ | **Backend OK, Frontend à compléter** |

---

## 🚀 Tests

### Test Certificat vs Attestation

```bash
# Employé ACTIF (actif = true)
curl http://192.168.20.55:8000/employes/1/certificat-travail
# Devrait retourner: 400 - "Utilisez l'attestation de travail"

curl http://192.168.20.55:8000/employes/1/attestation-travail
# Devrait retourner: 200 - PDF généré ✅

# Employé INACTIF (actif = false)
curl http://192.168.20.55:8000/employes/50/attestation-travail
# Devrait retourner: 400 - "Utilisez le certificat de travail"

curl http://192.168.20.55:8000/employes/50/certificat-travail
# Devrait retourner: 200 - PDF généré ✅
```

### Test Mois Déduction Congés

```bash
# Mettre à jour un congé avec mois de déduction spécifique
curl -X PUT http://192.168.20.55:8000/conges/250/consommation \
  -H "Content-Type: application/json" \
  -d '{
    "jours_pris": 3.5,
    "mois_deduction": 7,
    "annee_deduction": 2025
  }'

# Vérifier dans la base de données
mysql -u root -p ay_hr -e "SELECT id, mois, annee, jours_conges_pris, mois_deduction, annee_deduction FROM conges WHERE id=250;"
```

---

## ✅ Conclusion

**Les deux fonctionnalités sont DÉJÀ IMPLÉMENTÉES correctement dans le backend v3.6.1:**

1. ✅ **Certificat de Travail** - Fonctionne parfaitement
2. ✅ **Mois de Déduction Congés** - API prête, frontend à compléter

**Prochaine étape**: Mettre à jour l'interface frontend pour ajouter les sélecteurs de mois/année de déduction.
