import pandas as pd

def transform(raw_df):
    """
    Colonnes :
    - date_transaction
    - magasin
    - rayon
    - produit
    - quantite
    - prix_unitaire
    - nb_employes_presents
    - duree_ouverture_heures
    - rupture_stock (bool)
    """
    df = raw_df.copy()
    df['date_transaction'] = pd.to_datetime(df['date_transaction'], dayfirst=True)
    df['chiffre_affaires'] = df['quantite'] * df['prix_unitaire']
    return df