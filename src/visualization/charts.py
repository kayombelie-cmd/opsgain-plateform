"""
Générateur de graphiques Plotly.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from ..config import COLORS


class ChartGenerator:
    """Générateur de graphiques."""
    
    @staticmethod
    def create_daily_activity_chart(daily_data: pd.DataFrame, period_name: str) -> go.Figure:
        """Crée un graphique d'activité journalière."""
        fig = go.Figure()
        
        # Barres pour les opérations
        fig.add_trace(go.Bar(
            x=daily_data['date'],
            y=daily_data['nb_operations'],
            name='Opérations',
            marker_color=COLORS['info'],
            opacity=0.8
        ))
        
        # Ligne pour la durée moyenne
        if 'duree_moyenne' in daily_data.columns:
            fig.add_trace(go.Scatter(
                x=daily_data['date'],
                y=daily_data['duree_moyenne'],
                name='Durée moyenne (min)',
                yaxis='y2',
                line=dict(color=COLORS['danger'], width=3),
                mode='lines+markers'
            ))
            
            fig.update_layout(
                yaxis2=dict(
                    title='Durée (minutes)',
                    overlaying='y',
                    side='right',
                    showgrid=False,
                    title_font=dict(color=COLORS['danger']),
                    tickfont=dict(color=COLORS['danger'])
                )
            )
        
        fig.update_layout(
            title=dict(
                text=f"Activité Journalière - {period_name}",
                font=dict(size=16, color=COLORS['dark'])
            ),
            xaxis_title="Date",
            yaxis_title="Nombre d'opérations",
            height=400,
            hovermode='x unified',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    
    @staticmethod
    def create_hourly_distribution_chart(hourly_data: pd.DataFrame) -> go.Figure:
        """Crée un graphique de distribution horaire."""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=hourly_data['heure'],
            y=hourly_data['nb_operations'],
            marker_color=COLORS['secondary'],
            name='Opérations',
            opacity=0.8
        ))
        
        fig.update_layout(
            title=dict(
                text="Distribution Horaire des Opérations",
                font=dict(size=16, color=COLORS['dark'])
            ),
            xaxis_title="Heure de la journée",
            yaxis_title="Nombre d'opérations",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                tickmode='linear',
                tick0=6,
                dtick=2
            )
        )
        
        return fig
    
    @staticmethod
    def create_engins_performance_chart(engins_data: pd.DataFrame, top_n: int = 10) -> go.Figure:
        """Crée un graphique de performance des engins."""
        top_engins = engins_data.nlargest(top_n, 'total_operations')
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=top_engins['engin'],
            x=top_engins['total_operations'],
            orientation='h',
            marker_color=COLORS['primary'],
            name='Opérations',
            opacity=0.8
        ))
        
        fig.update_layout(
            title=dict(
                text=f"Top {top_n} Engins par Volume",
                font=dict(size=16, color=COLORS['dark'])
            ),
            xaxis_title="Nombre d'opérations",
            yaxis_title="Engin",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig
    
    @staticmethod
    def create_financial_pie_chart(breakdown: dict) -> go.Figure:
        """Crée un camembert pour la répartition des gains."""
        categories = ['Gain Temps', 'Gain Erreurs', 'Gain Maintenance', 'Gain Carburant']
        values = [
            breakdown.get('time_gain', 0),
            breakdown.get('error_gain', 0),
            breakdown.get('maintenance_gain', 0),
            breakdown.get('fuel_gain', 0)
        ]
        
        # Filtrer les catégories avec des valeurs positives
        filtered_data = [(cat, val) for cat, val in zip(categories, values) if val > 0]
        
        if not filtered_data:
            # Créer un graphique vide
            fig = go.Figure()
            fig.update_layout(
                title="Aucun gain à afficher",
                height=300
            )
            return fig
        
        cats, vals = zip(*filtered_data)
        
        fig = px.pie(
            names=cats,
            values=vals,
            color_discrete_sequence=[
                COLORS['secondary'],
                COLORS['info'],
                COLORS['warning'],
                COLORS['danger']
            ],
            hole=0.3
        )
        
        fig.update_layout(
            title=dict(
                text="Répartition des Gains Journaliers",
                font=dict(size=14, color=COLORS['dark'])
            ),
            height=300,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        
        return fig