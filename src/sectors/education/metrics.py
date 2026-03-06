def calculate_metrics(data):
    metrics = {}
    metrics['total_cours'] = len(data)
    metrics['heures_totales'] = data['heures'].sum()
    metrics['taux_presence_moyen'] = data['taux_presence'].mean()
    metrics['nb_enseignants'] = data['enseignant'].nunique()
    metrics['nb_classes'] = data['classe'].nunique()
    if 'note_moyenne' in data.columns:
        metrics['note_moyenne_generale'] = data['note_moyenne'].mean()
    metrics['nb_jours'] = data['date_cours'].dt.date.nunique()
    return metrics