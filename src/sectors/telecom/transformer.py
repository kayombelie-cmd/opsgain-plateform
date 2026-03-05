import pandas as pd

def transform(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme les données brutes du secteur télécom.
    Attend soit :
        - 'duree_minutes' directement,
        - ou 'date_ouverture' et 'date_resolution' pour calculer la durée.
    """
    df = raw_df.copy()
    
    # Conversion des dates si présentes
    if 'date_ouverture' in df.columns:
        df['date_ouverture'] = pd.to_datetime(df['date_ouverture'])
    if 'date_resolution' in df.columns:
        df['date_resolution'] = pd.to_datetime(df['date_resolution'])
    
    # Calcul de duree_minutes si elle manque
    if 'duree_minutes' not in df.columns:
        if 'date_ouverture' in df.columns and 'date_resolution' in df.columns:
            df['duree_minutes'] = (df['date_resolution'] - df['date_ouverture']).dt.total_seconds() / 60
        else:
            raise ValueError("Impossible de calculer la durée : ni 'duree_minutes' ni les dates nécessaires ne sont fournies.")
    
    # Nettoyage : supprimer les durées négatives ou nulles
    df = df[df['duree_minutes'] > 0].copy()
    
    # Ajout des colonnes dérivées
    df['sla_respecte'] = df['duree_minutes'] <= 240  # SLA = 4h
    
    if 'resolution_a_distance' in df.columns:
        df['intervention_terrain'] = ~df['resolution_a_distance']
    else:
        # Si la colonne n'existe pas, on la crée avec une valeur par défaut (False)
        df['resolution_a_distance'] = False
        df['intervention_terrain'] = True
    
    return df