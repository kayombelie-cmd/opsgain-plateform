import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(days: int = 30, start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
    np.random.seed(43)
    if start_date is not None and end_date is not None:
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    vehicules = ['VH-001', 'VH-002', 'VH-003', 'VH-004']
    chauffeurs = ['Jean', 'Pierre', 'Marie', 'Paul']
    data = []
    livraison_id = 1
    for date in date_range:
        nb_livraisons = np.random.poisson(lam=20)
        for i in range(nb_livraisons):
            depart = date + timedelta(hours=np.random.uniform(6, 18))
            distance = np.random.uniform(50, 500)
            vitesse = np.random.normal(60, 10)
            duree_heures = distance / vitesse
            arrivee = depart + timedelta(hours=duree_heures)
            retard = np.random.rand() < 0.1
            conso = np.random.normal(30, 5)
            carburant = (distance / 100) * conso
            data.append({
                'livraison_id': f'LIV-{livraison_id}',
                'date_depart': depart,
                'date_arrivee': arrivee,
                'distance_km': distance,
                'chauffeur': np.random.choice(chauffeurs),
                'vehicule': np.random.choice(vehicules),
                'carburant_litres': carburant,
                'statut': 'retard' if retard else 'à temps',
                'client': f'Client-{np.random.randint(1,50)}'
            })
            livraison_id += 1
    return pd.DataFrame(data)