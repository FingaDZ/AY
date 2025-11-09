# Fichier IRG (Impôt sur le Revenu Global)

Ce dossier contient le fichier `irg.xlsx` qui définit le barème de l'IRG.

## Structure du fichier irg.xlsx

Le fichier Excel doit avoir la structure suivante :

| Colonne A | Colonne B |
|-----------|-----------|
| Salaire   | IRG       |
| 0         | 0         |
| 30000     | 0         |
| 35000     | 500       |
| 40000     | 1000      |
| 45000     | 1750      |
| 50000     | 2500      |
| ...       | ...       |

## Comment créer le fichier

1. Créer un fichier Excel nommé `irg.xlsx`
2. Dans la première ligne (en-tête) :
   - Cellule A1 : "Salaire"
   - Cellule B1 : "IRG"
3. À partir de la ligne 2, entrer les valeurs :
   - Colonne A : Montant du salaire imposable en DA
   - Colonne B : Montant de l'IRG correspondant en DA

## Exemple de barème

Le système effectuera une interpolation linéaire entre les valeurs.

Par exemple, si vous avez :
- 40000 DA → 1000 DA d'IRG
- 45000 DA → 1750 DA d'IRG

Pour un salaire de 42500 DA :
- IRG = 1000 + ((42500 - 40000) / (45000 - 40000)) × (1750 - 1000)
- IRG = 1000 + (2500 / 5000) × 750
- IRG = 1000 + 375 = 1375 DA

## Barème par défaut

Si le fichier n'existe pas, le système utilisera un barème par défaut basé sur la législation algérienne.
