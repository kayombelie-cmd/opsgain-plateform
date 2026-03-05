import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def get_visualizations(data: pd.DataFrame) -> list:
    figs = []

    # Évolution du MTTR par jour
    daily_mttr = data.groupby(data['date_ouverture'].dt.date)['duree_minutes'].mean().reset_index()
    daily_mttr.columns = ['date', 'mttr']
    fig1 = px.line(daily_mttr, x='date', y='mttr', title='MTTR quotidien (minutes)')
    figs.append(fig1)

    # Répartition des pannes par type d'équipement
    panne_counts = data['equipement'].value_counts().reset_index()
    panne_counts.columns = ['equipement', 'nombre']
    fig2 = px.bar(panne_counts, x='equipement', y='nombre', title='Nombre de pannes par équipement')
    figs.append(fig2)

    # Taux de résolution à distance vs terrain
    remote_rate = data['resolution_a_distance'].mean() * 100
    field_rate = 100 - remote_rate
    fig3 = go.Figure(data=[go.Pie(labels=['À distance', 'Terrain'], values=[remote_rate, field_rate])])
    fig3.update_layout(title='Résolution des incidents')
    figs.append(fig3)

    return figs