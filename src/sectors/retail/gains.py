def calculate_gains(data, params):
    # params: marge_moyenne, cout_employe_horaire, penalite_rupture
    marge = params.get('marge_moyenne', 0.3)
    cout_employe = params.get('cout_employe_horaire', 15)
    penalite_rupture = params.get('penalite_rupture', 100)

    # Gain par augmentation du CA (via optimisation des horaires ou réduction des ruptures)
    # On simplifie : gain lié à la réduction des ruptures de stock
    nb_ruptures = data['rupture_stock'].sum()
    gain_rupture = nb_ruptures * penalite_rupture

    # Gain lié à l'optimisation des effectifs (on pourrait comparer au ratio CA/employé)
    # Ici on utilise un ratio cible
    ratio_cible = params.get('ratio_ca_employe_cible', 500)
    current_ratio = data['chiffre_affaires'].sum() / data['nb_employes_presents'].sum()
    if current_ratio < ratio_cible:
        # Perte potentielle
        perte = (ratio_cible - current_ratio) * data['nb_employes_presents'].sum()
        gain_employe = perte * 0.5  # on récupère 50% du gap
    else:
        gain_employe = 0

    total_gain = gain_rupture + gain_employe
    daily_gain = total_gain / data['date_transaction'].dt.date.nunique()
    return {
        'period_gains': total_gain,
        'daily_gains': daily_gain,
        'breakdown': {
            'gain_rupture': gain_rupture,
            'gain_employe': gain_employe
        }
    }