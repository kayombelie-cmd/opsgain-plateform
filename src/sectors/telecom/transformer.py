import pandas as pd

def transform(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Attend un DataFrame avec au moins les colonnes :
    - ticket_id : identifiant unique
    - date_ouverture : datetime
    - date_resolution : datetime
    - site_id : identifiant du site (antenne)
    - type_panne : catégorie de panne
    - equipement : type d'équipement
    - technicien : équipe ou technicien
    - resolution_a_distance : booléen (True si résolu à distance)
    """
    df = raw_df.copy()
    # Conversion des dates
    df['date_ouverture'] = pd.to_datetime(df['date_ouverture'])
    df['date_resolution'] = pd.to_datetime(df['date_resolution'])
    # Calcul de la durée d'intervention en minutes
    df['duree_minutes'] = (df['date_resolution'] - df['date_ouverture']).dt.total_seconds() / 60
    # Nettoyage : supprimer les durées négatives ou nulles
    df = df[df['duree_minutes'] > 0]
    # Ajouter colonne SLA respecté (par exemple SLA = 4h = 240 min)
    df['sla_respecte'] = df['duree_minutes'] <= 240
    # Colonne intervention terrain
    df['intervention_terrain'] = ~df['resolution_a_distance']
    return df