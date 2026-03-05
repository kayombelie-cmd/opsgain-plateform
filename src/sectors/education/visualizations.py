import plotly.express as px

def get_visualizations(data):
    figs = []
    # Taux de présence par jour
    daily_pres = data.groupby(data['date_cours'].dt.date)['taux_presence'].mean().reset_index()
    daily_pres.columns = ['date', 'taux_presence']
    figs.append(px.line(daily_pres, x='date', y='taux_presence', title='Taux de présence quotidien'))

    # Heures par matière
    heures_matiere = data.groupby('matiere')['heures'].sum().reset_index()
    figs.append(px.bar(heures_matiere, x='matiere', y='heures', title='Heures de cours par matière'))

    # Distribution des notes (si disponibles)
    if 'note_moyenne' in data.columns:
        figs.append(px.histogram(data, x='note_moyenne', nbins=20, title='Distribution des notes moyennes'))
    return figs