import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(days=30):
    np.random.seed(45)
    end = datetime.now()
    start = end - timedelta(days=days)
    matieres = ['Mathématiques', 'Français', 'Histoire', 'Sciences', 'Anglais']
    enseignants = [f'Prof {m}' for m in matieres]
    classes = ['6ème A', '6ème B', '5ème A', '5ème B', '4ème', '3ème']
    data = []
    for day in range(days):
        date = start + timedelta(days=day)
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