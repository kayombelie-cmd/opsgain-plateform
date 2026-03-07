import plotly.express as px
def get_visualizations(data):
    """
    Génère les graphiques pour le secteur Retail.
    
    Args:
        data: DataFrame des transactions.
    
    Returns:
        list: Liste de figures Plotly.
    """
    import plotly.express as px
    import plotly.graph_objects as go
    
    figures = []
    
    # Graphique 1 : Ventes par jour (si date disponible)
    date_col = next((col for col in ['date_transaction', 'date'] if col in data.columns), None)
    if date_col and 'chiffre_affaires' in data.columns:
        ventes_par_jour = data.groupby(date_col)['chiffre_affaires'].sum().reset_index()
        fig1 = px.line(ventes_par_jour, x=date_col, y='chiffre_affaires', 
                       title="Chiffre d'affaires par jour")
        figures.append(fig1)
    
    # Graphique 2 : Répartition des ventes par catégorie (si 'categorie' existe)
    if 'categorie' in data.columns and 'chiffre_affaires' in data.columns:
        ventes_cat = data.groupby('categorie')['chiffre_affaires'].sum().reset_index()
        fig2 = px.pie(ventes_cat, values='chiffre_affaires', names='categorie', 
                      title="Répartition du CA par catégorie")
        figures.append(fig2)
    
    # Graphique 3 : Ruptures de stock (si la colonne existe)
    if 'rupture_stock' in data.columns:
        # Évolution du taux de rupture par jour
        if date_col:
            taux_rupture_jour = data.groupby(date_col)['rupture_stock'].mean().reset_index()
            fig3 = px.line(taux_rupture_jour, x=date_col, y='rupture_stock', 
                           title="Taux de rupture par jour")
            figures.append(fig3)
        
        # Ruptures par rayon (si 'rayon' existe)
        if 'rayon' in data.columns:
            ruptures_rayon = data[data['rupture_stock'] == True].groupby('rayon').size().reset_index(name='nb')
            if not ruptures_rayon.empty:
                fig4 = px.bar(ruptures_rayon, x='rayon', y='nb', 
                              title="Nombre de ruptures par rayon")
                figures.append(fig4)
    else:
        # Graphique informatif si rupture_stock est absent
        fig_info = go.Figure()
        fig_info.add_annotation(
            text="Données de rupture de stock non disponibles",
            showarrow=False,
            font=dict(size=14)
        )
        fig_info.update_layout(title="Ruptures de stock")
        figures.append(fig_info)
    
    # Si aucun graphique n'a été généré, ajouter un placeholder
    if not figures:
        fig_empty = go.Figure()
        fig_empty.add_annotation(text="Aucun graphique disponible pour ces données", showarrow=False)
        figures.append(fig_empty)
    
    return figures
