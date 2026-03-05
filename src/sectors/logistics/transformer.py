import pandas as pd

def transform(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Colonnes attendues :
    - livraison_id
    - date_depart
    - date_arrivee
    - distance_km
    - chauffeur
    - vehicule
    - carburant_litres
    - statut (à temps / retard)
    - client
    """
    df = raw_df.copy()
    df['date_depart'] = pd.to_datetime(df['date_depart'])
    df['date_arrivee'] = pd.to_datetime(df['date_arrivee'])
    df['duree_heures'] = (df['date_arrivee'] - df['date_depart']).dt.total_seconds() / 3600
    df['retard'] = df['statut'] == 'retard'
    df['consommation_100km'] = df['carburant_litres'] / (df['distance_km'] / 100)
    return df