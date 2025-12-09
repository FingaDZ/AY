# 📋 Architecture - Module Traitement Salaires v3.0

**Date**: 9 Décembre 2025  
**Version**: 3.0.0  
**Auteur**: Refonte complète

---

## 🎯 Objectifs

Créer un module **fiable, transparent et maintenable** pour le calcul automatique des salaires mensuels, en remplacement des modules `Edition Salaires` et `Salaires (Ancien)`.

### Principes de conception

✅ **Traçabilité**: Chaque calcul est documenté et vérifiable  
✅ **Robustesse**: Gestion d'erreurs avec fallback et alertes  
✅ **Conformité**: Respect du droit du travail algérien  
✅ **Performance**: Calcul de 50+ employés en < 5 secondes  
✅ **Extensibilité**: Ajout facile de nouvelles primes/déductions

---

## 📊 Schéma de Données

### Tables utilisées

```
employes (source)
  ├─ id, nom, prenom, salaire_base
  ├─ date_recrutement (→ ancienneté → IEP)
  ├─ situation_familiale, femme_au_foyer (→ prime_femme_foyer)
  ├─ prime_nuit_agent_securite (→ prime_nuit)
  └─ poste_travail (→ prime_chauffeur si chauffeur)

pointages (heures travaillées)
  ├─ employe_id, annee, mois
  ├─ jour_01..jour_31 (enum: P, A, C, M, F, R)
  ├─ heures_supplementaires (décimal)
  └─ jours_travailles, jours_ouvrables, jours_conges

missions (primes déplacement)
  ├─ chauffeur_id, client_id, date_mission
  ├─ distance_km, tarif_km
  └─ montant (distance × tarif)

avances (déductions)
  ├─ employe_id, montant, annee_deduction, mois_deduction
  └─ deduit (boolean)

credits (mensualités)
  ├─ employe_id, montant_mensuel, statut
  └─ nombre_mois, mois_restants

parametres_salaire (configuration)
  ├─ indemnite_nuisance, ifsp, iep, prime_encouragement
  ├─ prime_chauffeur, panier, prime_transport
  ├─ prime_nuit_agent_securite, prime_femme_foyer
  ├─ taux_secu_sociale (9%), jours_ouvrables (26)
  ├─ activer_heures_supp (boolean)
  └─ irg_proratise (boolean) → Active/désactive proratisation IRG

irg_bareme (barème fiscal)
  ├─ salaire (colonne MONTANT du fichier Excel)
  ├─ montant_irg (colonne IRG du fichier Excel)
  ├─ actif (boolean)
  └─ date_creation

  Note: Table de correspondance directe (pas de tranches/taux)
        Fichier source: backend/data/irg.xlsx
        Format: 2 colonnes (Salaire, IRG)
        Milliers de lignes avec pas de 10 DA
```

---

## 🔄 Processus de Calcul

### Étape 1: Récupération des données
```python
employe = db.query(Employe).get(employe_id)
pointage = db.query(Pointage).filter(
    Pointage.employe_id == employe_id,
    Pointage.annee == annee,
    Pointage.mois == mois
).first()
params = db.query(ParametresSalaire).first()
```

### Étape 2: Calcul salaire de base proratisé
```python
salaire_base_proratis = (employe.salaire_base / jours_ouvrables) * jours_travailles

# Si congés payés dans le mois
if pointage.jours_conges > 0:
    salaire_base_proratis = employe.salaire_base  # Pas de proratisation
```

### Étape 3: Heures supplémentaires
```python
if params.activer_heures_supp and pointage.heures_supplementaires > 0:
    taux_horaire = employe.salaire_base / (jours_ouvrables * 8)
    heures_supp_montant = pointage.heures_supplementaires * taux_horaire * 1.5
else:
    heures_supp_montant = 0
```

### Étape 4: Primes COTISABLES
```python
# Montants fixes depuis parametres_salaire
indemnite_nuisance = params.indemnite_nuisance  # 1000 DA
ifsp = params.ifsp  # 500 DA
iep = params.iep if anciennete >= 1 else 0  # 300 DA
prime_encouragement = params.prime_encouragement if anciennete >= 1 else 0  # 500 DA

# Primes conditionnelles
prime_chauffeur = params.prime_chauffeur if employe.poste_travail == "Chauffeur" else 0  # 800 DA
prime_nuit = params.prime_nuit_agent_securite if employe.prime_nuit_agent_securite else 0  # 600 DA

# Prime déplacement (missions)
prime_deplacement = sum(mission.montant for mission in missions_du_mois)

# Primes variables (saisies manuellement)
prime_objectif = 0  # Saisie utilisateur
prime_variable = 0  # Saisie utilisateur
```

### Étape 5: Salaire cotisable
```python
salaire_cotisable = (
    salaire_base_proratis
    + heures_supp_montant
    + indemnite_nuisance
    + ifsp
    + iep
    + prime_encouragement
    + prime_chauffeur
    + prime_nuit
    + prime_deplacement
    + prime_objectif
    + prime_variable
)
```

### Étape 6: Retenue Sécurité Sociale
```python
retenue_ss = salaire_cotisable * (params.taux_secu_sociale / 100)  # 9%
```

### Étape 7: Primes NON COTISABLES
```python
panier = params.panier  # 300 DA
prime_transport = params.prime_transport  # 500 DA
```

### Étape 8: Salaire imposable
```python
salaire_imposable = salaire_cotisable - retenue_ss + panier + prime_transport
```

### Étape 9: IRG (Impôt sur le Revenu Global) avec Proratisation

**IMPORTANT**: Le barème irg.xlsx contient les montants IRG pour **1 mois complet (30 jours)**. Si l'employé a travaillé moins, l'IRG doit être ajusté proportionnellement.

#### Logique de calcul IRG proratisé

```python
def calculer_irg_proratise(salaire_imposable, jours_travailles):
    """
    Calcul IRG avec proratisation selon jours travaillés
    
    Étapes:
    1. Extrapoler le salaire imposable à 30 jours
    2. Chercher l'IRG correspondant dans le barème (irg.xlsx)
    3. Proratiser l'IRG selon jours réellement travaillés
    
    Exemple concret:
    - Employé: 20 jours travaillés
    - Salaire imposable réel: 25,000 DA
    - Salaire extrapolé 30j: (25,000 / 20) × 30 = 37,500 DA
    - IRG barème pour 37,500 DA: 2,465 DA
    - IRG proratisé: (2,465 / 30) × 20 = 1,643 DA
    """
    
    if jours_travailles == 0:
        return 0
    
    # Paramètre irg_proratise (dans parametres_salaire)
    if not params.irg_proratise:
        # Mode simple: IRG direct sur salaire réel (pas de proratisation)
        irg_calculator = get_irg_calculator(db)
        return irg_calculator.calculer_irg(salaire_imposable)
    
    # Mode proratisé (recommandé):
    
    # 1. Extrapoler à 30 jours
    salaire_30j = (salaire_imposable / jours_travailles) * 30
    
    # 2. Chercher IRG pour salaire extrapolé dans irg.xlsx
    irg_calculator = get_irg_calculator(db)
    irg_30j = irg_calculator.calculer_irg(salaire_30j)
    
    # 3. Proratiser IRG selon jours réels
    irg_final = (irg_30j / 30) * jours_travailles
    
    # Arrondir à l'entier (IRG sans décimales)
    return int(round(irg_final))
```

#### Structure irg.xlsx

```
Colonne A (Salaire) | Colonne B (IRG)
--------------------|----------------
10000               | 0
10010               | 0
...                 | ...
30000               | 0
30010               | 10
30020               | 20
...                 | ...
37500               | 2465
...                 | ...
50000               | 5230
```

**Note**: Le fichier contient des milliers de lignes avec un pas de 10 DA pour une précision maximale. La recherche se fait par correspondance (trouver la ligne où salaire ≤ salaire_imposable).

### Étape 10: Déductions (avances + crédits)
```python
# Avances du mois
avances_mois = db.query(Avance).filter(
    Avance.employe_id == employe_id,
    Avance.annee_deduction == annee,
    Avance.mois_deduction == mois,
    Avance.deduit == False
).all()
total_avances = sum(a.montant for a in avances_mois)

# Crédits en cours
credits_actifs = db.query(Credit).filter(
    Credit.employe_id == employe_id,
    Credit.statut == StatutCredit.EN_COURS
).all()
total_credits = sum(c.montant_mensuel for c in credits_actifs)

total_deductions = total_avances + total_credits
```

### Étape 11: Vérification suffisance salaire
```python
salaire_avant_deductions = salaire_imposable - irg
avances_reportees = 0
credits_reportes = 0
alerte = None

if salaire_avant_deductions < total_deductions:
    # Salaire insuffisant → report au mois suivant
    deduction_possible = salaire_avant_deductions * 0.30  # Max 30% du salaire
    
    if total_avances > 0:
        if total_avances <= deduction_possible:
            # Déduire toutes les avances
            avances_deduites = total_avances
            deduction_possible -= total_avances
        else:
            # Déduire partiellement + reporter
            avances_deduites = deduction_possible
            avances_reportees = total_avances - deduction_possible
            deduction_possible = 0
            alerte = "AVANCES_REPORTEES"
    
    if total_credits > 0 and deduction_possible > 0:
        if total_credits <= deduction_possible:
            credits_deduits = total_credits
        else:
            credits_deduits = deduction_possible
            credits_reportes = total_credits - deduction_possible
            alerte = "CREDITS_REPORTES" if not alerte else "AVANCES_ET_CREDITS_REPORTES"
    
    total_deductions = avances_deduites + credits_deduits
    
    # Enregistrer les reports dans table report_avance_credit
    if avances_reportees > 0 or credits_reportes > 0:
        create_report_record(employe_id, annee, mois, avances_reportees, credits_reportes)
```

### Étape 12: Prime femme foyer
```python
prime_femme_foyer = params.prime_femme_foyer if employe.femme_au_foyer else 0  # 1000 DA
```

### Étape 13: Salaire net final
```python
salaire_net = salaire_imposable - irg - total_deductions + prime_femme_foyer
```

---

## 📄 Structure de Réponse API

```json
{
  "employe_id": 29,
  "employe_nom": "SAIFI",
  "employe_prenom": "SALAH EDDINE",
  "annee": 2025,
  "mois": 12,
  
  "salaire_base": "30000.00",
  "salaire_base_proratis": "31000.00",
  "jours_travailles": 31,
  "jours_conges": 0,
  "jours_ouvrables_travailles": 27,
  "heures_supplementaires": "6750.64",
  
  "primes_cotisables": {
    "indemnite_nuisance": "1000.00",
    "ifsp": "500.00",
    "iep": "300.00",
    "prime_encouragement": "500.00",
    "prime_chauffeur": "0",
    "prime_nuit_agent_securite": "0",
    "prime_deplacement": "0",
    "prime_objectif": "0",
    "prime_variable": "0"
  },
  
  "salaire_cotisable": "40050.64",
  "retenue_securite_sociale": "3604.56",
  
  "primes_non_cotisables": {
    "panier": "300.00",
    "prime_transport": "500.00"
  },
  
  "salaire_imposable": "37246.08",
  "irg": "2465.20",
  
  "deductions": {
    "total_avances": "0",
    "retenue_credit": "0",
    "avances_reportees": "0",
    "credits_reportes": "0"
  },
  
  "prime_femme_foyer": "1000.00",
  "salaire_net": "35780.88",
  
  "alerte": null,
  "statut": "OK",
  "erreur": null,
  
  "details_calcul": {
    "anciennete_annees": 5,
    "nombre_missions_mois": 2,
    "nombre_avances_mois": 0,
    "nombre_credits_actifs": 0
  }
}
```

---

## 🎨 Interface Utilisateur

### Page: Traitement Salaires

#### Section 1: Sélection période
```
┌─────────────────────────────────────────────┐
│ Traitement des Salaires                     │
├─────────────────────────────────────────────┤
│ Année: [2025 ▼]  Mois: [Décembre ▼]       │
│ [🔄 Calculer tous les salaires]             │
└─────────────────────────────────────────────┘
```

#### Section 2: Liste des employés
```
┌──────────────────────────────────────────────────────────────────┐
│ Nom          │ Salaire Base │ Salaire Net │ Statut  │ Actions  │
├──────────────┼──────────────┼─────────────┼─────────┼──────────┤
│ SAIFI Salah  │ 30,000.00 DA │ 35,780.88 DA│ ✓ OK    │ 👁 📄 💾 │
│ ZERROUG Abd. │ 35,000.00 DA │ 24,903.03 DA│ ⚠ Crédit│ 👁 📄 💾 │
│ BERKANE Hoc. │ 23,000.00 DA │ 30,230.36 DA│ ✓ OK    │ 👁 📄 💾 │
└──────────────┴──────────────┴─────────────┴─────────┴──────────┘

Légende:
👁 Détails calcul | 📄 Bulletin PDF | 💾 Valider & Enregistrer
```

#### Section 3: Modal détails calcul
```
┌────────────────────────────────────────────────────────────┐
│ Détails Calcul - SAIFI Salah Eddine                       │
├────────────────────────────────────────────────────────────┤
│ SALAIRE DE BASE                                            │
│ • Salaire mensuel: 30,000.00 DA                           │
│ • Jours travaillés: 31 / 26 jours ouvrables               │
│ • Salaire proratisé: 31,000.00 DA                         │
│                                                            │
│ HEURES SUPPLÉMENTAIRES                                     │
│ • Heures: 34.67h × 144.23 DA/h × 150% = 6,750.64 DA      │
│                                                            │
│ PRIMES COTISABLES                                          │
│ • Indemnité Nuisance: 1,000.00 DA                         │
│ • IFSP: 500.00 DA                                          │
│ • IEP (5 ans ancienneté): 300.00 DA                       │
│ • Prime Encouragement (> 1 an): 500.00 DA                │
│ TOTAL COTISABLE: 40,050.64 DA                             │
│                                                            │
│ RETENUE SÉCURITÉ SOCIALE                                   │
│ • 9% × 40,050.64 DA = 3,604.56 DA                         │
│                                                            │
│ PRIMES NON COTISABLES                                      │
│ • Panier: 300.00 DA                                        │
│ • Transport: 500.00 DA                                     │
│                                                            │
│ SALAIRE IMPOSABLE: 37,246.08 DA                           │
│                                                            │
│ IRG (Impôt sur Revenu Global) - PRORATISÉ                │
│ • Jours travaillés: 20 jours (sur 30)                    │
│ • Salaire extrapolé 30j: (37,246 / 20) × 30 = 55,869 DA │
│ • IRG barème 30j: 55,869 → 7,698 DA                      │
│ • IRG proratisé: (7,698 / 30) × 20 = 5,132 DA           │
│ TOTAL IRG: 5,132 DA                                       │
│                                                            │
│ Note: Si irg_proratise=False, IRG direct = 2,465 DA      │
│                                                            │
│ DÉDUCTIONS                                                 │
│ • Avances mois en cours: 0 DA                             │
│ • Crédit mensualité: 0 DA                                 │
│                                                            │
│ PRIME FEMME FOYER: 1,000.00 DA                            │
│                                                            │
│ ══════════════════════════════════════════════════════     │
│ SALAIRE NET À PAYER: 35,780.88 DA                         │
│ ══════════════════════════════════════════════════════     │
│                                                            │
│ [📄 Générer Bulletin PDF] [💾 Valider Salaire]            │
└────────────────────────────────────────────────────────────┘
```

---

## 🔐 Sécurité & Permissions

### Rôles utilisateurs

```python
class UserRole(enum.Enum):
    ADMIN = "admin"          # Tous droits
    COMPTABLE = "comptable"  # Lecture + édition salaires
    VIEWER = "viewer"        # Lecture seule

# Permissions
"/api/traitement-salaires/preview"  → ADMIN, COMPTABLE, VIEWER
"/api/traitement-salaires/valider"  → ADMIN, COMPTABLE
"/api/traitement-salaires/bulletin" → ADMIN, COMPTABLE, VIEWER
"/api/traitement-salaires/export"   → ADMIN, COMPTABLE
```

---

## 📋 Génération Bulletin de Paie PDF

### Template ReportLab

```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

def generer_bulletin_paie(salaire_data, employe_data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # En-tête entreprise
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, 28*cm, "AY HR MANAGEMENT")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, 27.5*cm, "Adresse entreprise")
    c.drawString(2*cm, 27*cm, "NIF: xxxxxxxxxx")
    
    # Titre
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(10.5*cm, 25*cm, f"BULLETIN DE PAIE - {mois_texte} {annee}")
    
    # Informations employé
    c.setFont("Helvetica", 10)
    y = 23*cm
    c.drawString(2*cm, y, f"Nom: {employe.nom} {employe.prenom}")
    y -= 0.5*cm
    c.drawString(2*cm, y, f"N° SS: {employe.numero_secu_sociale}")
    y -= 0.5*cm
    c.drawString(2*cm, y, f"Poste: {employe.poste_travail}")
    
    # Tableau détails salaire
    # ... (voir implémentation complète)
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
```

---

## 🧪 Tests & Validation

### Scénarios de test

1. **Employé temps plein (26 jours)**
   - Vérifier: salaire_base_proratis == salaire_base

2. **Employé avec absences**
   - Vérifier: proratisation correcte

3. **Employé avec congés payés**
   - Vérifier: pas de proratisation

4. **Employé avec heures supplémentaires**
   - Vérifier: taux 150%

5. **Employé chauffeur avec missions**
   - Vérifier: prime_deplacement = sum(missions)

6. **Employé avec avance > salaire**
   - Vérifier: report au mois suivant + alerte

7. **Employé avec crédit actif**
   - Vérifier: déduction mensualité

8. **Calcul IRG avec proratisation**
   - Scénario: Employé 20 jours, salaire imposable 25,000 DA
   - Extrapoler: (25,000 / 20) × 30 = 37,500 DA
   - IRG barème 30j: 2,465 DA
   - IRG proratisé: (2,465 / 30) × 20 = 1,643 DA
   - Vérifier: irg_proratise = True dans parametres_salaire

---

## 📈 Performance

### Objectifs

- Calcul 1 employé: < 100ms
- Calcul 50 employés: < 5s
- Génération PDF: < 2s

### Optimisations

```python
# Précharger données communes
params = db.query(ParametresSalaire).first()
baremes_irg = db.query(IRGBareme).filter(IRGBareme.actif == True).order_by(IRGBareme.ordre).all()

# Batch queries
employes = db.query(Employe).filter(Employe.actif == True).all()
pointages = db.query(Pointage).filter(
    Pointage.annee == annee,
    Pointage.mois == mois
).all()
pointages_map = {p.employe_id: p for p in pointages}

# Calcul parallèle (optionnel)
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(calculer_salaire, e.id) for e in employes]
    results = [f.result() for f in futures]
```

---

## 🚀 Migration depuis ancien système

### Étapes

1. ✅ Désactiver anciens menus (Edition Salaires, Salaires Ancien)
2. ⚙️ Créer nouveau backend API `/api/traitement-salaires`
3. 🎨 Créer interface frontend `/salaires/traitement`
4. 📄 Intégrer génération PDF bulletins
5. 🧪 Tests sur données réelles (Décembre 2025)
6. 🔄 Migration données historiques (optionnel)
7. 🗑️ Supprimer ancien code après validation

---

## 📚 Documentation API

### Endpoints

```
GET  /api/traitement-salaires/preview
     ?annee=2025&mois=12
     → Calcule tous les salaires (brouillon)

POST /api/traitement-salaires/valider
     Body: { employe_id: 29, annee: 2025, mois: 12 }
     → Valide et enregistre en DB

GET  /api/traitement-salaires/bulletin/{salaire_id}
     → Télécharge bulletin PDF

POST /api/traitement-salaires/valider-tous
     Body: { annee: 2025, mois: 12 }
     → Valide tous les salaires du mois

GET  /api/traitement-salaires/export
     ?annee=2025&mois=12&format=excel
     → Export Excel G29
```

---

## ✅ Checklist de livraison

- [x] Architecture documentée
- [ ] Backend API implémentée
- [ ] Frontend interface créée
- [ ] Génération PDF bulletins
- [ ] Tests sur 46 employés
- [ ] Documentation utilisateur
- [ ] Migration GitHub
- [ ] Formation utilisateurs

---

**Fin du document d'architecture**
