def calculate_gains(data, params):
    """
    Calcule les gains financiers pour le secteur Retail.
    
    Args:
        data: DataFrame des transactions.
        params: Dictionnaire de paramètres (cout_rupture, productivite_ref, etc.)
    
    Returns:
        dict: Gains calculés (period_gains, daily_gains, breakdown)
    """
    gains = {}
    
    # 1. Gain lié aux ruptures de stock
    if 'rupture_stock' in data.columns:
        nb_ruptures = data['rupture_stock'].sum()
        cout_rupture = params.get('cout_rupture', 100)  # coût moyen d'une rupture
        gains['rupture_gain'] = nb_ruptures * cout_rupture
    else:
        gains['rupture_gain'] = 0.0
    
    # 2. Gain lié à la productivité des employés
    if ('chiffre_affaires' in data.columns and 'nb_employes_presents' in data.columns 
            and data['nb_employes_presents'].sum() > 0):
        ca_total = data['chiffre_affaires'].sum()
        nb_employes = data['nb_employes_presents'].sum()
        productivite_actuelle = ca_total / nb_employes
        
        productivite_ref = params.get('productivite_ref', 800)  # CA/employé de référence
        gain_productivite = (productivite_actuelle - productivite_ref) * nb_employes
        gains['productivite_gain'] = max(0, gain_productivite)  # seulement si positif
    else:
        gains['productivite_gain'] = 0.0
    
    # Gains totaux sur la période
    gains['period_gains'] = gains['rupture_gain'] + gains['productivite_gain']
    
    # Calcul du nombre de jours (basé sur les dates)
    date_col = next((col for col in ['date_transaction', 'date'] if col in data.columns), None)
    if date_col:
        start = data[date_col].min()
        end = data[date_col].max()
        nb_jours = (end - start).days + 1
    else:
        nb_jours = 1
    
    gains['daily_gains'] = gains['period_gains'] / nb_jours if nb_jours > 0 else 0
    
    # Détail pour le graphique
    gains['breakdown'] = {
        'réduction_ruptures': gains['rupture_gain'],
        'productivité_employés': gains['productivite_gain']
    }
    
    return gains