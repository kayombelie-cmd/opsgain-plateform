import plotly.express as px

def get_visualizations(data):
    figs = []
    # CA par jour
    daily_ca = data.groupby(data['date_transaction'].dt.date)['chiffre_affaires'].sum().reset_index()
    daily_ca.columns = ['date', 'ca']
    figs.append(px.line(daily_ca, x='date', y='ca', title='Chiffre d\'affaires quotidien'))

    # Ruptures par rayon
    ruptures_rayon = data[data['rupture_stock']].groupby('rayon').size().reset_index(name='nb')
    figs.append(px.bar(ruptures_rayon, x='rayon', y='nb', title='Nombre de ruptures par rayon'))

    # Productivité employé
    prod = data.groupby('date_transaction')['chiffre_affaires'].sum() / data.groupby('date_transaction')['nb_employes_presents'].mean()
    prod_df = prod.reset_index()
    prod_df.columns = ['date', 'productivite']
    figs.append(px.line(prod_df, x='date', y='productivite', title='Productivité (CA / employé)'))
    return figs