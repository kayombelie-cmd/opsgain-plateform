import pandas as pd

def calculate_gains(data: pd.DataFrame, params: dict) -> dict:
    """
    params doit contenir :
    - hourly_technician_cost: coût horaire d'un technicien (par défaut 50)
    - revenue_loss_per_hour: manque à gagner par heure d'indisponibilité (par défaut 1000)
    - travel_cost_per_intervention: coût de déplacement moyen (par défaut 100)
    - baseline_mttr: MTTR de référence pour calculer le gain (par défaut 300 min)
    """
    hourly_cost = params.get('hourly_technician_cost', 50)
    revenue_loss = params.get('revenue_loss_per_hour', 1000)
    travel_cost = params.get('travel_cost_per_intervention', 100)
    baseline_mttr = params.get('baseline_mttr', 300)  # minutes

    total_tickets = len(data)
    current_mttr = data['duree_minutes'].mean()
    time_saved_minutes = max(0, baseline_mttr - current_mttr) * total_tickets
    time_saved_hours = time_saved_minutes / 60

    # Gain lié à la réduction du temps d'intervention (main d'œuvre)
    gain_labor = time_saved_hours * hourly_cost

    # Gain lié au rétablissement plus rapide du service (revenu évité)
    gain_revenue = time_saved_hours * revenue_loss

    # Gain lié à l'augmentation de la résolution à distance (économie de déplacements)
    current_remote_rate = data['resolution_a_distance'].mean()
    baseline_remote_rate = params.get('baseline_remote_rate', 0.3)  # 30% historiquement
    additional_remote = max(0, current_remote_rate - baseline_remote_rate) * total_tickets
    gain_travel = additional_remote * travel_cost

    total_gain_period = gain_labor + gain_revenue + gain_travel
    daily_gain = total_gain_period / data['date_ouverture'].dt.date.nunique()

    return {
        'period_gains': total_gain_period,
        'daily_gains': daily_gain,
        'breakdown': {
            'gain_labor': gain_labor,
            'gain_revenue': gain_revenue,
            'gain_travel': gain_travel
        }
    }