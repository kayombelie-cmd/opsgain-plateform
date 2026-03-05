import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(days: int = 30) -> pd.DataFrame:
    np.random.seed(42)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    sites = [f'Site-{i}' for i in range(1, 21)]
    equipements = ['Routeur', 'Antenne', 'Onduleur', 'Climatisation', 'Groupe électrogène']
    types_panne = ['Panne réseau', 'Coupure électrique', 'Surchauffe', 'Défaut matériel', 'Configuration']
    techniciens = ['Équipe A', 'Équipe B', 'Équipe C']

    data = []
    for day in range(days):
        date = start_date + timedelta(days=day)
        nb_tickets = np.random.poisson(lam=15)  # 15 tickets par jour en moyenne
        for _ in range(nb_tickets):
            ouverture = date + timedelta(hours=np.random.uniform(0, 24))
            duree = np.random.gamma(shape=2, scale=60)  # durée moyenne ~120 min, écart-type élevé
            resolution = ouverture + timedelta(minutes=duree)
            remote = np.random.rand() < 0.4  # 40% de chances d'être résolu à distance
            data.append({
                'ticket_id': f'TICK-{day}-{_}',
                'date_ouverture': ouverture,
                'date_resolution': resolution,
                'site_id': np.random.choice(sites),
                'type_panne': np.random.choice(types_panne),
                'equipement': np.random.choice(equipements),
                'technicien': np.random.choice(techniciens),
                'resolution_a_distance': remote
            })
    df = pd.DataFrame(data)
    return df