def calculate_metrics(data):
    metrics = {}
    metrics['total_livraisons'] = len(data)
    metrics['taux_retard'] = data['retard'].mean() * 100
    metrics['distance_totale'] = data['distance_km'].sum()
    metrics['carburant_total'] = data['carburant_litres'].sum()
    metrics['conso_moyenne'] = data['consommation_100km'].mean()
    metrics['duree_moyenne'] = data['duree_heures'].mean()
    return metrics