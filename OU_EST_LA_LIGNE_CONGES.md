## OÙ LA LIGNE DOIT APPARAÎTRE

### Dans le bulletin PDF, section "DÉTAIL DU SALAIRE"

La ligne **"Jours de congé pris ce mois"** doit apparaître:

**POSITION**: Juste après "Salaire de base (contrat)", AVANT "Heures supplémentaires"

**STRUCTURE**:
```
DÉSIGNATION                    | BASE | TAUX     | GAIN  | RETENUE
----------------------------------------------------------- --------
Salaire de base (contrat)     | XXX  | 26/26 j  | XXX   |
→ Jours de congé pris ce mois | ← ICI | 1.0 j    | Payé  |         ← CETTE LIGNE
Heures supplémentaires         |      |          | XXX   |
```

### POURQUOI C'EST MAINTENANT RÉSOLU

1. **Code ajouté dans `/opt/ay-hr/backend/services/salaire_calculator.py`** (ligne 66-77):
   ```python
   # ⭐ Récupérer congés depuis table conges
   from models import Conge
   conge_record = self.db.query(Conge).filter(
       Conge.employe_id == employe_id,
       Conge.annee == annee,
       Conge.mois == mois
   ).first()
   jours_conges = float(conge_record.jours_conges_pris or 0) if conge_record else 0
   ```

2. **Champ ajouté au dictionnaire retourné** (ligne 187):
   ```python
   "jours_conges": jours_conges,  # ⭐ AJOUTÉ
   ```

3. **Ligne déjà présente dans PDF** (`/opt/ay-hr/backend/services/pdf_generator.py` ligne 900-904):
   ```python
   ['Jours de congé pris ce mois',
    '',
    f"{salaire_data.get('jours_conges', 0):.1f} j",
    'Payé',
    ''],
   ```

### TEST IMMÉDIAT

**Utilisez l'interface web**:
1. Allez dans **Salaires** → **Générer Bulletins**
2. Sélectionnez **Décembre 2025**
3. Générez le bulletin pour **SAIFI Salah Eddine** (qui a 1 jour de congé)
4. Ouvrez le PDF

**RÉSULTAT ATTENDU**:  
Vous devriez voir la ligne:
```
Jours de congé pris ce mois    |      | 1.0 j    | Payé  |
```

### POURQUOI ÇA A PRIS DU TEMPS

❌ **Erreur initiale**: Modification de `salary_processor.py` (fichier legacy non utilisé)  
✅ **Correction**: Modification de `salaire_calculator.py` (fichier réellement utilisé par l'API)

**Commit final**: `df72401` + backend redémarré à **18:38:11 UTC**  
**Statut**: ✅ **OPÉRATIONNEL MAINTENANT**
