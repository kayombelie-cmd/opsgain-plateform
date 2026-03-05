import pandas as pd

def transform(raw_df):
    """
    Colonnes :
    - date_cours
    - matiere
    - enseignant
    - classe
    - duree_minutes
    - nb_eleves_presents
    - nb_eleves_inscrits
    - note_moyenne (optionnel)
    """
    df = raw_df.copy()
    df['date_cours'] = pd.to_datetime(df['date_cours'])
    df['taux_presence'] = df['nb_eleves_presents'] / df['nb_eleves_inscrits'] * 100
    df['heures'] = df['duree_minutes'] / 60
    return df