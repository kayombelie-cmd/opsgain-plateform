def calculate_metrics(data):
    metrics = {}
    
    # Nombre de transactions
    metrics['total_transactions'] = len(data)
    
    # Chiffre d'affaires total (utilise 'chiffre_affaires' ou 'montant_total')
    ca_col = 'chiffre_affaires' if 'chiffre_affaires' in data.columns else 'montant_total'
    if ca_col in data.columns:
        metrics['ca_total'] = data[ca_col].sum()
        metrics['ca_moyen_par_transaction'] = data[ca_col].mean()
    else:
        metrics['ca_total'] = 0.0
        metrics['ca_moyen_par_transaction'] = 0.0
    
    # Taux de rupture (optionnel)
    if 'rupture_stock' in data.columns:
        metrics['taux_rupture'] = data['rupture_stock'].mean() * 100
    else:
        metrics['taux_rupture'] = 0.0
    
    # Productivité employé (optionnel)
    if 'nb_employes_presents' in data.columns and ca_col in data.columns and data['nb_employes_presents'].sum() > 0:
        metrics['productivite_employe'] = data[ca_col].sum() / data['nb_employes_presents'].sum()
    else:
        metrics['productivite_employe'] = 0.0
    
     # Nombre de jours de la période
    date_col = next((col for col in ['date_transaction', 'date'] if col in data.columns), None)
    if date_col:
        start_date = data[date_col].min()
        end_date = data[date_col].max()
        metrics['nb_jours'] = (end_date - start_date).days + 1
    else:
        metrics['nb_jours'] = 1
    
    return metrics