"""
Utilitaires pour le calcul kilométrique multi-clients
"""
from typing import List, Dict
from decimal import Decimal


def calculer_km_multi_clients(
    clients_distances: List[Dict],
    km_supplementaire_par_client: int = 10
) -> Dict:
    """
    Calcule le kilométrage total pour une mission multi-clients
    
    Logique (Option 1 du cahier des charges):
    - Dernier client: utiliser sa distance réelle
    - Clients précédents: ajouter km_supplementaire_par_client pour chaque client
    
    Formule: km_total = dernier_client_km + (nb_clients - 1) × km_supplementaire
    
    Args:
        clients_distances: Liste de dicts avec 'client_id', 'client_nom', 'distance_km'
        km_supplementaire_par_client: Km supplémentaires par client additionnel (défaut: 10)
    
    Returns:
        Dict avec:
            - km_total: Kilométrage total calculé
            - dernier_client_km: Distance du dernier client
            - km_supplementaires: Km ajoutés pour les autres clients
            - nb_clients: Nombre de clients
            - details: Liste détaillée pour chaque client
    
    Exemple:
        >>> clients = [
        ...     {'client_id': 1, 'client_nom': 'Client A', 'distance_km': 50},
        ...     {'client_id': 2, 'client_nom': 'Client B', 'distance_km': 30},
        ...     {'client_id': 3, 'client_nom': 'Client C', 'distance_km': 20}
        ... ]
        >>> result = calculer_km_multi_clients(clients, km_supplementaire=10)
        >>> result['km_total']
        40  # 20 (dernier) + (3-1)×10 = 40
    """
    
    if not clients_distances:
        return {
            'km_total': 0,
            'dernier_client_km': 0,
            'km_supplementaires': 0,
            'nb_clients': 0,
            'details': []
        }
    
    nb_clients = len(clients_distances)
    
    # Si un seul client, utiliser sa distance directement
    if nb_clients == 1:
        client = clients_distances[0]
        km = float(client.get('distance_km', 0))
        return {
            'km_total': km,
            'dernier_client_km': km,
            'km_supplementaires': 0,
            'nb_clients': 1,
            'details': [{
                'client_id': client['client_id'],
                'client_nom': client.get('client_nom', 'N/A'),
                'distance_km': km,
                'est_dernier': True,
                'km_pris_en_compte': km
            }]
        }
    
    # Multi-clients: dernier client + km supplémentaires
    dernier_client = clients_distances[-1]
    dernier_client_km = float(dernier_client.get('distance_km', 0))
    
    km_supplementaires = (nb_clients - 1) * km_supplementaire_par_client
    km_total = dernier_client_km + km_supplementaires
    
    # Détails pour chaque client
    details = []
    for i, client in enumerate(clients_distances):
        est_dernier = (i == nb_clients - 1)
        distance_km = float(client.get('distance_km', 0))
        
        if est_dernier:
            km_pris_en_compte = distance_km
        else:
            km_pris_en_compte = km_supplementaire_par_client
        
        details.append({
            'client_id': client['client_id'],
            'client_nom': client.get('client_nom', 'N/A'),
            'distance_km': distance_km,
            'est_dernier': est_dernier,
            'km_pris_en_compte': km_pris_en_compte
        })
    
    return {
        'km_total': km_total,
        'dernier_client_km': dernier_client_km,
        'km_supplementaires': km_supplementaires,
        'nb_clients': nb_clients,
        'details': details
    }


def formatter_recap_km(calcul_result: Dict) -> str:
    """
    Formate un récapitulatif lisible du calcul kilométrique
    
    Args:
        calcul_result: Résultat de calculer_km_multi_clients()
    
    Returns:
        Chaîne formatée pour affichage
    """
    nb = calcul_result['nb_clients']
    
    if nb == 0:
        return "Aucun client"
    
    if nb == 1:
        return f"1 client: {calcul_result['km_total']:.1f} km"
    
    recap = f"{nb} clients:\n"
    for detail in calcul_result['details']:
        symbole = "→" if detail['est_dernier'] else "+"
        recap += f"  {symbole} {detail['client_nom']}: {detail['distance_km']:.1f} km "
        recap += f"(pris en compte: {detail['km_pris_en_compte']:.1f} km)\n"
    
    recap += f"\nTotal: {calcul_result['dernier_client_km']:.1f} (dernier) "
    recap += f"+ {calcul_result['km_supplementaires']:.0f} (supplémentaires) "
    recap += f"= {calcul_result['km_total']:.1f} km"
    
    return recap
