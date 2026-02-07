"""
Composants UI réutilisables.
"""
import streamlit as st
from typing import Optional

from ..config import COLORS, PUBLIC_DATA_HASH


class UIComponents:
    """Composants d'interface utilisateur."""
    
    @staticmethod
    def style_css() -> str:
        """Retourne le CSS personnalisé."""
        return f"""
        <style>
            /* Thème principal */
            .stApp {{
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            }}
            
            /* Cartes métriques */
            .metric-card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                border-left: 5px solid {COLORS['primary']};
                margin: 10px 0;
            }}
            
            .financial-card {{
                background: white;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                border-top: 4px solid {COLORS['secondary']};
                margin: 10px 0;
            }}
            
            /* Alertes */
            .alert-card {{
                background: #FEF2F2;
                border-left: 5px solid {COLORS['danger']};
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }}
            
            .success-card {{
                background: #F0FDF4;
                border-left: 5px solid {COLORS['secondary']};
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }}
            
            /* Titres */
            .main-title {{
                color: {COLORS['primary']};
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 0.5rem;
            }}
            
            .section-title {{
                color: #334155;
                font-size: 1.5rem;
                font-weight: 700;
                margin: 1.5rem 0 1rem 0;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid #e2e8f0;
            }}
            
            /* Badges */
            .badge {{
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
                display: inline-block;
            }}
            
            .badge-success {{ background: {COLORS['secondary']}; color: white; }}
            .badge-warning {{ background: {COLORS['warning']}; color: white; }}
            .badge-danger {{ background: {COLORS['danger']}; color: white; }}
            .badge-info {{ background: {COLORS['info']}; color: white; }}
            
            /* Cards spéciales financières */
            .commission-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            }}
            
            .gain-card {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            }}
            
            /* Badge de synchronisation */
            .sync-badge {{
                background: linear-gradient(135deg, {COLORS['secondary']} 0%, #059669 100%);
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                display: inline-block;
                font-weight: 600;
                margin-bottom: 10px;
            }}
            
            /* Amélioration des tables */
            .dataframe {{
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            
            /* Boutons */
            .stButton > button {{
                border-radius: 8px;
                font-weight: 600;
            }}
        </style>
        """
    
    @staticmethod
    def render_sync_badge():
        """Affiche le badge de synchronisation."""
        st.markdown(f"""
        <div class="sync-badge">
            🔄 Données synchronisées | Hash: {PUBLIC_DATA_HASH}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_period_summary(period_summary: dict):
        """Affiche le résumé de période."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Période analysée",
                f"{period_summary['total_days']} jours",
                f"{period_summary['start_date']} → {period_summary['end_date']}"
            )
        
        with col2:
            st.metric(
                "Opérations totales",
                f"{period_summary['total_operations']:,.0f}",
                f"{period_summary['avg_daily_operations']:,.0f}/jour"
            )
        
        with col3:
            st.metric(
                "Durée moyenne",
                f"{period_summary['avg_duration']:.1f} min",
                f"{period_summary['error_rate']:.1f}% erreurs"
            )
        
        with col4:
            daily_gain = period_summary['period_gains'] / period_summary['total_days'] if period_summary['total_days'] > 0 else 0
            st.metric(
                "Gains période",
                f"${period_summary['period_gains']:,.0f}",
                f"${daily_gain:,.0f}/jour"
            )
    
    @staticmethod
    def render_alert(message: str, alert_type: str = "info"):
        """Affiche une alerte stylisée."""
        if alert_type == "danger":
            st.markdown(f'<div class="alert-card">{message}</div>', unsafe_allow_html=True)
        elif alert_type == "success":
            st.markdown(f'<div class="success-card">{message}</div>', unsafe_allow_html=True)
        elif alert_type == "warning":
            st.warning(message)
        else:
            st.info(message)