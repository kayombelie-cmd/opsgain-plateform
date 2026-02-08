"""
Gestion de l'authentification.
"""
import streamlit as st

from .config import DEFAULT_PASSWORD, APP_NAME, APP_VERSION
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
        """Affiche la page de login."""
        st.set_page_config(page_title="OpsGain - Authentification", layout="centered")
        
        # CSS personnalisé
        st.markdown("""
        <style>
            .title-blue {
                color: #1E3A8A;
                text-align: center;
                font-size: 2.2rem;
                font-weight: 700;
                margin-bottom: 5px;
            }
            .slogan-green {
                color: #10B981;
                text-align: center;
                font-size: 1.1rem;
                font-weight: 600;
                margin-bottom: 5px;
            }
            .description {
                color: #475569;
                text-align: center;
                font-size: 0.9rem;
                line-height: 1.4;
                margin-bottom: 25px;
                max-width: 400px;
                margin-left: auto;
                margin-right: auto;
            }
            .security-badge {
                color: #6B7280;
                text-align: center;
                font-size: 0.75rem;
                margin-top: 10px;
            }
            .login-container {
                max-width: 400px;
                margin: 0 auto;
                padding: 20px;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Conteneur principal
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Logo/emoji
        st.markdown("<h1 style='text-align: center; color: #3B82F6; font-size: 3.5rem;'>🔐</h1>", unsafe_allow_html=True)
        
        # Titre principal
        st.markdown(f"<h2 class='title-blue'>OPSGAIN PLATEFORM</h2>", unsafe_allow_html=True)
        
        # Slogan
        st.markdown("<p class='slogan-green'>💎 Vos Opérations • Nos Gains</p>", unsafe_allow_html=True)
        
        # Description
        st.markdown("""
                  <p class='description'>
                  <strong>La plateforme qui transforme vos données opérationnelles<br>
                           en gains financiers vérifiables en temps réel.</strong>
                  </p>
        """, unsafe_allow_html=True)
        
        # Version info
        st.caption(f"📊 Dashboard opérationnel synchronisé • 🚀 {APP_VERSION} • 📅 Données 2026")
        st.divider()
        
        # Champ mot de passe
        password = st.text_input(
            "**Mot de passe d'accès :**", 
            type="password",
            help="Entrez le mot de passe fourni par votre administrateur OpsGain",
            key="password_input"
        )
        
        # Bouton d'accès
        if st.button("**🚀 ACCÉDER AU DASHBOARD**", type="primary", use_container_width=True):
            if password == DEFAULT_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect")
                logger.warning(f"Tentative d'accès échouée")
        
        st.divider()
        
        # Footer
        st.markdown("<p style='text-align: center; color: #6B7280; font-size: 0.85rem;'>© 2026 OpsGain Technologies • Tous droits réservés</p>", unsafe_allow_html=True)
        
        # Badge sécurité
        st.markdown('<p class="security-badge">🔐 Accès sécurisé • 🔄 Données synchronisées • 📈 ROI vérifiable</p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)