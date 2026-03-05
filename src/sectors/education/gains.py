def calculate_gains(data, params):
    # params: cout_enseignant_horaire, subvention_par_eleve, objectif_presence
    cout_ens = params.get('cout_enseignant_horaire', 30)
    subvention = params.get('subvention_par_eleve', 5)  # par élève présent
    objectif_presence = params.get('objectif_presence', 85)  # %

    # Gain lié à l'amélioration de la présence
    current_presence = data['taux_presence'].mean()
    if current_presence > objectif_presence:
        gain_presence = (current_presence - objectif_presence) / 100 * data['nb_eleves_inscrits'].sum() * subvention * (data['date_cours'].nunique())
    else:
        gain_presence = 0

    # Gain lié à l'optimisation des heures (réduction des heures creuses, etc.)
    # Ici on compare le ratio élèves/enseignant
    total_eleves_presents = data['nb_eleves_presents'].sum()
    total_heures = data['heures'].sum()
    ratio_actuel = total_eleves_presents / total_heures if total_heures > 0 else 0
    ratio_cible = params.get('ratio_eleves_par_heure_cible', 20)
    if ratio_actuel < ratio_cible:
        heures_optimisees = total_heures - (total_eleves_presents / ratio_cible)
        gain_optimisation = heures_optimisees * cout_ens
    else:
        gain_optimisation = 0

    total_gain = gain_presence + gain_optimisation
    daily_gain = total_gain / data['date_cours'].nunique()
    return {
        'period_gains': total_gain,
        'daily_gains': daily_gain,
        'breakdown': {
            'gain_presence': gain_presence,
            'gain_optimisation': gain_optimisation
        }
    }