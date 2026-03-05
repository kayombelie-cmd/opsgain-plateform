import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(days=30):
    np.random.seed(43)
    end = datetime.now()
    start = end - timedelta(days=days)
    vehicules = ['VH-001', 'VH-002', 'VH-003', 'VH-004']
    chauffeurs = ['Jean', 'Pierre', 'Marie', 'Paul']
    data = []
    for day in range(days):
        date = start + timedelta(days=day)
        nb_livraisons = np.random.poisson(lam=20)
        for i in range(nb_livraisons):
            depart = date + timedelta(hours=np.random.uniform(6, 18))
            distance = np.random.uniform(50, 500)
            vitesse = np.random.normal(60, 10)  # km/h
            duree_heures = distance / vitesse
            arrivee = depart + timedelta(hours=duree_heures)
            retard = np.random.rand() < 0.1  # 10% de retard
            conso = np.random.normal(30, 5)  # L/100km
            carburant = (distance / 100) * conso
            data.append({
                'livraison_id': f'LIV-{day}-{i}',
                'date_depart': depart,
                'date_arrivee': arrivee,
                'distance_km': distance,
                'chauffeur': np.random.choice(chauffeurs),
                'vehicule': np.random.choice(vehicules),
                'carburant_litres': carburant,
                'statut': 'retard' if retard else 'à temps',
                'client': f'Client-{np.random.randint(1,50)}'
            })
    return pd.DataFrame(data)