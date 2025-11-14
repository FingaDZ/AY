from datetime import date

def calculer_anciennete_corrigee(date_recrutement, annee, mois):
    date_calcul = date(annee, mois, 1)
    
    # Si l'employé est recruté après la date de calcul, ancienneté = 0
    if date_recrutement > date_calcul:
        return 0
    
    delta = date_calcul - date_recrutement
    annees = delta.days // 365
    return max(0, annees)

print('TEST CORRECTION IEP:')
print('=' * 60)
print('')

e7_rec = date(2025, 11, 10)
e8_rec = date(2025, 11, 12)

print(f'Employé 7 recruté: {e7_rec}')
anc7_oct = calculer_anciennete_corrigee(e7_rec, 2025, 10)
anc7_nov = calculer_anciennete_corrigee(e7_rec, 2025, 11)
anc7_dec = calculer_anciennete_corrigee(e7_rec, 2025, 12)
print(f'  Ancienneté octobre 2025: {anc7_oct} ans → IEP: {25000 * anc7_oct * 0.01} DA')
print(f'  Ancienneté novembre 2025: {anc7_nov} ans → IEP: {25000 * anc7_nov * 0.01} DA')
print(f'  Ancienneté décembre 2025: {anc7_dec} ans → IEP: {25000 * anc7_dec * 0.01} DA')
print('')

print(f'Employé 8 recruté: {e8_rec}')
anc8_oct = calculer_anciennete_corrigee(e8_rec, 2025, 10)
anc8_nov = calculer_anciennete_corrigee(e8_rec, 2025, 11)
anc8_dec = calculer_anciennete_corrigee(e8_rec, 2025, 12)
print(f'  Ancienneté octobre 2025: {anc8_oct} ans → IEP: {20000 * anc8_oct * 0.01} DA')
print(f'  Ancienneté novembre 2025: {anc8_nov} ans → IEP: {20000 * anc8_nov * 0.01} DA')
print(f'  Ancienneté décembre 2025: {anc8_dec} ans → IEP: {20000 * anc8_dec * 0.01} DA')
print('')
print('=' * 60)
print('✅ CORRECTION: IEP ne peut plus être négatif')
