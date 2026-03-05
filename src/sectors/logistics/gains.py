def calculate_gains(data, params):
    # params: fuel_cost_per_liter, driver_hourly_cost, baseline_retard_rate
    fuel_cost = params.get('fuel_cost_per_liter', 1.5)
    driver_cost = params.get('driver_hourly_cost', 20)
    baseline_retard = params.get('baseline_retard_rate', 0.15)

    current_retard_rate = data['retard'].mean()
    reduction_retard = max(0, baseline_retard - current_retard_rate) * len(data)
    # Estimation du coût d'un retard (pénalités, perte de confiance)
    cout_retard_unitaire = params.get('cout_retard_unitaire', 200)
    gain_retard = reduction_retard * cout_retard_unitaire

    # Gain carburant via optimisation de consommation
    conso_moyenne = data['consommation_100km'].mean()
    baseline_conso = params.get('baseline_conso', 35)  # L/100km
    reduction_conso = max(0, baseline_conso - conso_moyenne) * (data['distance_km'].sum() / 100)
    gain_carburant = reduction_conso * fuel_cost

    total_gain = gain_retard + gain_carburant
    daily_gain = total_gain / data['date_depart'].dt.date.nunique()

    return {
        'period_gains': total_gain,
        'daily_gains': daily_gain,
        'breakdown': {
            'gain_retard': gain_retard,
            'gain_carburant': gain_carburant
        }
    }