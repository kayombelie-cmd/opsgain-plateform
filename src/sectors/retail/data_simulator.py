import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(days=30):
    np.random.seed(44)
    end = datetime.now()
    start = end - timedelta(days=days)
    magasins = ['Mag A', 'Mag B', 'Mag C']
    rayons = ['Alimentation', 'Électroménager', 'Textile', 'Hygiène']
    produits = [f'Produit-{i}' for i in range(1, 21)]
    data = []
    for day in range(days):
        date = start + timedelta(days=day)
        nb_trans = np.random.poisson(lam=200)
        for _ in range(nb_trans):
            rupture = np.random.rand() < 0.05  # 5% de ruptures
            qte = np.random.randint(1, 5) if not rupture else 0
            prix = np.random.uniform(5, 200)
            ca = qte * prix
            employes = np.random.randint(5, 20)
            data.append({
                'date_transaction': date + timedelta(hours=np.random.uniform(8, 20)),
                'magasin': np.random.choice(magasins),
                'rayon': np.random.choice(rayons),
                'produit': np.random.choice(produits),
                'quantite': qte,
                'prix_unitaire': prix,
                'nb_employes_presents': employes,
                'duree_ouverture_heures': 12,
                'rupture_stock': rupture
            })
    return pd.DataFrame(data)