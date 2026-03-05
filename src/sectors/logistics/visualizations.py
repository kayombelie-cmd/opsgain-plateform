import plotly.express as px

def get_visualizations(data):
    figs = []
    # Taux de retard par jour
    daily_retard = data.groupby(data['date_depart'].dt.date)['retard'].mean().reset_index()
    daily_retard.columns = ['date', 'taux_retard']
    figs.append(px.line(daily_retard, x='date', y='taux_retard', title='Taux de retard quotidien'))

    # Consommation par véhicule
    conso_vehicule = data.groupby('vehicule')['consommation_100km'].mean().reset_index()
    figs.append(px.bar(conso_vehicule, x='vehicule', y='consommation_100km', title='Consommation moyenne par véhicule'))

    # Répartition des statuts
    statuts = data['statut'].value_counts()
    figs.append(px.pie(values=statuts.values, names=statuts.index, title='Statut des livraisons'))
    return figs