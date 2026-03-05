import pandas as pd

def calculate_metrics(data: pd.DataFrame) -> dict:
    metrics = {}
    metrics['total_tickets'] = len(data)
    metrics['tickets_resolus'] = data['sla_respecte'].sum()  # ou tout simplement len(data)
    metrics['mttr_moyen'] = data['duree_minutes'].mean()  # Mean Time To Repair en minutes
    metrics['taux_resolution_distance'] = data['resolution_a_distance'].mean() * 100
    metrics['taux_respect_sla'] = data['sla_respecte'].mean() * 100
    metrics['nb_interventions_terrain'] = data['intervention_terrain'].sum()
    metrics['cout_moyen_intervention'] = 150  # à ajuster selon paramètres réels
    # Pannes par type d'équipement
    panne_par_equip = data.groupby('equipement')['ticket_id'].count().to_dict()
    metrics['pannes_par_equipement'] = panne_par_equip
    return metrics