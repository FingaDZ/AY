# Règles Métier - Calcul Pointages

## Vue d'Ensemble

Ce document définit les règles métier pour le calcul automatique des pointages journaliers à partir des logs d'entrée/sortie.

## Constantes Business

| Constante | Valeur | Description | Référence |
|-----------|--------|-------------|-----------|
| `MIN_WORK_HOURS` | 4h | Minimum pour valider une journée travaillée | Règle B |
| `STANDARD_DAY_HOURS` | 8h | Journée standard (inclus pause déjeuner) | Règle D |
| `LUNCH_BREAK_HOURS` | 1h | Pause déjeuner (chomée et payée) | Règle C |
| `EFFECTIVE_WORK_HOURS` | 7h | Heures effectives (8h - 1h pause) | Calculé |
| `MAX_DAILY_HOURS` | 12h | Maximum enregistrable par jour | Règle I |
| `MAX_MONTHLY_HOURS` | 208h | Maximum heures par mois | Règle E |
| `WORK_DAYS_PER_MONTH` | 30 jours | Jours par mois (inclus vendredis) | Règle F |
| `NORMAL_MONTHLY_HOURS` | 173.33h | Heures normales par mois | Règle G |
| `MAX_OVERTIME_MONTHLY` | 34.67h | Heures supplémentaires max/mois | Règle H |

## Règles de Calcul

### Règle A : 1 Entrée + 1 Sortie par Jour

**Principe** : Chaque journée doit avoir exactement 1 entrée et 1 sortie.

**Implémentation** :
- Si plusieurs entrées : Prendre la **première**
- Si plusieurs sorties : Prendre la **dernière**
- Si entrée manquante : **Estimer à 08:00** + WARNING
- Si sortie manquante : **Estimer à 17:00** + WARNING

**Exemple** :
```
Logs: 08:15 ENTRY, 12:00 EXIT, 13:00 ENTRY, 17:30 EXIT
→ Résultat: Entrée 08:15, Sortie 17:30
```

### Règle B : Minimum 4 Heures

**Principe** : Une journée n'est validée que si >= 4h de travail.

**Implémentation** :
- Si durée < 4h → `day_value = 0` (Absent) + WARNING
- Si durée >= 4h → `day_value = 1` (Travaillé)

**Exemple** :
```
Entrée 09:00, Sortie 12:00 → 3h → Absent (WARNING)
Entrée 09:00, Sortie 13:30 → 4.5h → Travaillé (OK)
```

### Règle C : Pause Déjeuner Incluse

**Principe** : 1h de pause déjeuner est incluse dans les 8h standard et est chomée et payée.

**Implémentation** :
- La pause est **automatiquement déduite** du calcul des heures sup
- Heures effectives = Heures standard - 1h pause = 7h

**Note** : L'utilisateur n'a pas besoin de pointer la pause.

### Règle D : Journée Standard = 8 Heures

**Principe** : Une journée de travail standard = 8h (inclus 1h pause).

**Implémentation** :
- Utilisé comme référence pour le calcul
- Durée affichée = durée brute (entrée → sortie)

### Règles E, F, G, H : Limites Mensuelles

**Principe** : Limites pour validation mensuelle (non implémenté dans calcul journalier).

**Utilisation Future** :
- Validation mensuelle des totaux
- Alertes si dépassement
- Rapports mensuels

### Règle I : Maximum 12 Heures par Jour

**Principe** : Impossible d'enregistrer plus de 12h par jour.

**Implémentation** :
- Si durée > 12h → `day_value = 0` + ERROR
- Considéré comme erreur de saisie

**Exemple** :
```
Entrée 06:00, Sortie 19:00 → 13h → ERROR (durée excessive)
```

### Règle J : Heures Supplémentaires par Jour

**Principe** : Les heures sup sont calculées **par journée**, pas par mois.

**Formule** :
```
heures_sup = max(0, durée_travail - 7h)
```

**Implémentation** :
- Heures sup = au-delà de 7h effectives
- Calculées pour chaque jour individuellement
- Affichées dans colonne "H. Sup"

**Exemples** :
```
Durée 6h → 0h sup
Durée 7h → 0h sup
Durée 8h → 1h sup
Durée 9h → 2h sup
Durée 10h → 3h sup
```

## Cas Spéciaux

### Vendredi (Jour Chomé et Payé)

**Détection** : `date.weekday() == 4`

**Traitement** :
- Marqué avec WARNING "Vendredi - Jour chomé et payé"
- Calcul normal appliqué
- Affiché en orange dans UI

### Logs Incomplets

**Scénario 1 : Entrée manquante**
```
Logs: 17:00 EXIT
→ Estimation: 08:00 ENTRY
→ Durée: 9h
→ WARNING: "Entrée estimée à 08:00"
```

**Scénario 2 : Sortie manquante**
```
Logs: 08:30 ENTRY
→ Estimation: 17:00 EXIT
→ Durée: 8.5h
→ WARNING: "Sortie estimée à 17:00"
```

**Scénario 3 : Aucun log**
```
Logs: (vide)
→ Résultat: ERROR
→ day_value = 0
```

### Conflits avec Pointage Existant

**Détection** : Vérification dans table `pointages` si jour déjà rempli.

**Traitement** :
- WARNING "Conflit: Pointage déjà existant"
- Utilisateur doit décider : garder existant ou écraser

## Statuts

### OK (Vert)
- Entrée ET sortie présentes
- Durée >= 4h et <= 12h
- Pas de conflit
- Employé matché
- Pas d'estimation

### WARNING (Orange)
- Log estimé (entrée ou sortie manquante)
- Heures supplémentaires détectées
- Vendredi travaillé
- Conflit avec pointage existant
- Durée proche des limites

### ERROR (Rouge)
- Employé non trouvé
- Durée < 4h (journée invalide)
- Durée > 12h (erreur saisie)
- Sortie avant entrée
- Aucun log disponible

## Workflow de Validation

```
1. Parse logs Excel
2. Group by (employee_id, date)
3. Pour chaque jour:
   a. Extract entry + exit
   b. Estimate si manquant
   c. Calculate durée
   d. Validate limites (4h-12h)
   e. Calculate heures sup
   f. Detect special days
   g. Check conflicts
   h. Determine status
4. Display preview
5. User review & select
6. Confirm → Insert to DB
```

## Exemples Complets

### Exemple 1 : Journée Normale
```
Date: 2025-11-28 (Jeudi)
Entrée: 08:30
Sortie: 17:00
Durée: 8.5h
Heures sup: 1.5h (8.5 - 7)
Statut: WARNING (heures sup)
Pointage: 1 (Travaillé)
```

### Exemple 2 : Journée Courte
```
Date: 2025-11-29 (Vendredi)
Entrée: 10:00
Sortie: 13:00
Durée: 3h
Heures sup: 0h
Statut: WARNING (< 4h + Vendredi)
Pointage: 0 (Absent)
```

### Exemple 3 : Journée Estimée
```
Date: 2025-11-27 (Mercredi)
Entrée: (manquante) → 08:00 estimée
Sortie: 16:30
Durée: 8.5h
Heures sup: 1.5h
Statut: WARNING (entrée estimée + heures sup)
Pointage: 1 (Travaillé)
```

### Exemple 4 : Erreur
```
Date: 2025-11-26 (Mardi)
Entrée: 07:00
Sortie: 20:00
Durée: 13h
Heures sup: N/A
Statut: ERROR (> 12h max)
Pointage: 0 (Non enregistrable)
```

---

**Version** : 2.2.0  
**Date** : 29 novembre 2025  
**Auteur** : AIRBAND
