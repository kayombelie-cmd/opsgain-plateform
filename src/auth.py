"""
Gestion de l'authentification.
"""
import streamlit as st

from .config import DEFAULT_PASSWORD, APP_NAME, APP_VERSION
from src.utils.i18n import i18n
from .utils.logger import setup_logger

logger = setup_logger(__name__)


class Authentication:
    """Gestionnaire d'authentification."""
    
    @staticmethod
    def check_auth():
        """Vérifie si l'utilisateur est authentifié."""
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        
        if not st.session_state.authenticated:
            Authentication.render_login_page()
            st.stop()
        else:
            logger.info("Utilisateur authentifié")
    
    @staticmethod
    def render_login_page():
     st.set_page_config(page_title="OpsGain - Authentification", layout="centered")
    
    # CSS minimal et efficace
    st.markdown("""
    <style>
        /* Force le centrage de tout le contenu */
        .stApp > header, .stApp > section {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
        .main > div {
            max-width: 500px !important;
            margin: 0 auto !important;
            text-align: center !important;
        }
        h1, h2, p, .stTextInput, .stButton {
            text-align: center !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }
        .stTextInput > div, .stButton > button {
            width: 100% !important;
            max-width: 350px !important;
            margin: 0 auto !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenu centré
    st.markdown("<h1 style='text-align: center; font-size: 3.5rem; color: #3B82F6;'>🔐</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #1E3A8A; font-size: 2.2rem; font-weight: 800;'>OPSGAIN PLATFORM</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #10B981; font-size: 1.1rem; font-weight: 600;'>💎 Vos Opérations • Nos Gains</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #475569; font-size: 0.95rem; max-width: 400px; margin: 0 auto 25px auto;'><strong>La plateforme qui transforme vos données opérationnelles<br>en gains financiers vérifiables en temps réel.</strong></p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6B7280; font-size: 0.8rem; margin-bottom: 20px;'>📊 Dashboard opérationnel synchronisé • 🚀 3.0.0 • 📅 Données 2026</p>", unsafe_allow_html=True)
    
    st.divider()
    
    password = st.text_input("**Mot de passe d'accès :**", type="password", label_visibility="collapsed", placeholder="Mot de passe")
    
    if st.button("**🚀 ACCÉDER AU DASHBOARD**", type="primary", use_container_width=True):
        if password == DEFAULT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect")
    
    st.divider()
    st.markdown("<p style='text-align: center; color: #6B7280; font-size: 0.85rem;'>© 2026 OpsGain Technologies • Tous droits réservés</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.75rem; margin-top: 10px;'>🔐 Accès sécurisé • 🔄 Données synchronisées • 📈 ROI vérifiable</p>", unsafe_allow_html=True)