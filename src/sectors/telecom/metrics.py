import pandas as pd

def calculate_metrics(data: pd.DataFrame) -> dict:
    metrics = {}
    metrics['total_tickets'] = len(data)
    # Optionnel : vous pouvez conserver 'tickets_resolus' si nécessaire, mais utilisez la bonne colonne
    # metrics['tickets_resolus'] = data['sla_respecte'].sum()  # à décommenter si souhaité
    metrics['mttr_moyen'] = data['duree_minutes'].mean()
    metrics['taux_resolution_distance'] = data['resolution_a_distance'].mean() * 100
    metrics['taux_respect_sla'] = data['sla_respecte'].mean() * 100
    metrics['nb_interventions_terrain'] = data['intervention_terrain'].sum()
    metrics['cout_moyen_intervention'] = 150
    panne_par_equip = data.groupby('equipement')['ticket_id'].count().to_dict()
    metrics['pannes_par_equipement'] = panne_par_equip
    metrics['nb_jours'] = data['date_ouverture'].dt.date.nunique()
    return metrics