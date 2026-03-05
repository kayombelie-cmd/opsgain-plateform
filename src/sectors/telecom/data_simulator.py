import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(days: int = 30, start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
    """
    Génère des données simulées.
    Si start_date et end_date sont fournies, génère sur cette plage.
    Sinon, génère sur 'days' jours à partir d'aujourd'hui.
    """
    np.random.seed(42)

    if start_date is not None and end_date is not None:
        # Générer pour chaque jour entre start_date et end_date inclus
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    rows = []
    ticket_counter = 1
    for date in date_range:
        nb_tickets = np.random.randint(20, 50)
        for _ in range(nb_tickets):
            sla_respecte = np.random.choice([True, False], p=[0.85, 0.15])
            duree_minutes = np.random.randint(10, 120)
            urgence = np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])
            type_ticket = np.random.choice(['incident', 'requête', 'maintenance'], p=[0.5, 0.3, 0.2])
            resolution_a_distance = np.random.choice([True, False], p=[0.4, 0.6])
            intervention_terrain = not resolution_a_distance
            satisfaction_client = np.random.randint(1, 6)
            temps_resolution = duree_minutes
            priorite = urgence
            categorie = type_ticket
            technicien = np.random.choice(['Alice', 'Bob', 'Charlie', 'Diana'])
            equipement = np.random.choice(['Routeur A', 'Switch B', 'Antenne C', 'Fibre D'])

            rows.append({
                'ticket_id': ticket_counter,
                'date_ouverture': date,
                'date': date,
                'equipement': equipement,
                'type_ticket': type_ticket,
                'urgence': urgence,
                'priorite': priorite,
                'categorie': categorie,
                'duree_minutes': duree_minutes,
                'temps_resolution': temps_resolution,
                'sla_respecte': sla_respecte,
                'resolution_a_distance': resolution_a_distance,
                'intervention_terrain': intervention_terrain,
                'satisfaction_client': satisfaction_client,
                'technicien': technicien
            })
            ticket_counter += 1

    return pd.DataFrame(rows)