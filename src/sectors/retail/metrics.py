def calculate_metrics(data):
    metrics = {}
    metrics['total_transactions'] = len(data)
    metrics['ca_total'] = data['chiffre_affaires'].sum()
    metrics['ca_moyen_par_transaction'] = data['chiffre_affaires'].mean()
    metrics['taux_rupture'] = data['rupture_stock'].mean() * 100
    metrics['productivite_employe'] = data['chiffre_affaires'].sum() / data['nb_employes_presents'].sum()
    return metrics