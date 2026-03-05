import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(days: int = 30, start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
    """
    Génère des données simulées pour le secteur Éducation.
    Si start_date et end_date sont fournies, génère sur cette plage.
    Sinon, génère sur 'days' jours à partir d'aujourd'hui.
    """
    np.random.seed(45)

    if start_date is not None and end_date is not None:
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    matieres = ['Mathématiques', 'Français', 'Histoire', 'Sciences', 'Anglais']
    enseignants = [f'Prof {m}' for m in matieres]
    classes = ['6ème A', '6ème B', '5ème A', '5ème B', '4ème', '3ème']

    data = []
    for date in date_range:
        for matiere in matieres:
            for classe in classes[:2]:  # seulement quelques classes par jour
                duree = np.random.choice([45, 60, 90])
                presents = np.random.randint(20, 35)
                inscrits = 35
                note = np.random.normal(12, 3) if np.random.rand() > 0.3 else None
                data.append({
                    'date_cours': date + timedelta(hours=np.random.uniform(8, 16)),
                    'matiere': matiere,
                    'enseignant': f'Prof {matiere}',
                    'classe': classe,
                    'duree_minutes': duree,
                    'nb_eleves_presents': presents,
                    'nb_eleves_inscrits': inscrits,
                    'note_moyenne': note
                })
    return pd.DataFrame(data)