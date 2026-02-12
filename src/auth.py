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
        """Affiche la page de login."""
        st.set_page_config(page_title="OpsGain - Authentification", layout="centered")
        
        # CSS COMPLET AVEC RÉINITIALISATION
        st.markdown("""
        <style>
            /* RÉINITIALISATION DES STYLES STREAMLIT */
            div[data-testid="stVerticalBlock"] {
                align-items: center !important;
            }
            
            div[data-testid="stVerticalBlockBorderWrapper"] {
                max-width: 450px !important;
                margin: 0 auto !important;
            }
            
            /* CONTENEUR PRINCIPAL */
            .login-main {
                width: 100% !important;
                max-width: 450px !important;
                margin: 0 auto !important;
                padding: 30px 20px !important;
                text-align: center !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
            }
            
            /* ÉMOJI */
            .login-emoji {
                font-size: 3.5rem !important;
                margin-bottom: 10px !important;
                text-align: center !important;
            }
            
            /* TITRES */
            .login-title {
                color: #1E3A8A !important;
                font-size: 2.2rem !important;
                font-weight: 800 !important;
                margin: 0 0 5px 0 !important;
                text-align: center !important;
                width: 100% !important;
            }
            
            .login-slogan {
                color: #10B981 !important;
                font-size: 1.1rem !important;
                font-weight: 600 !important;
                margin: 0 0 10px 0 !important;
                text-align: center !important;
                width: 100% !important;
            }
            
            /* DESCRIPTION */
            .login-description {
                color: #475569 !important;
                font-size: 0.95rem !important;
                line-height: 1.5 !important;
                margin: 0 auto 25px auto !important;
                text-align: center !important;
                width: 100% !important;
                max-width: 380px !important;
                padding: 0 10px !important;
            }
            
            /* CAPTION */
            .login-caption {
                color: #6B7280 !important;
                font-size: 0.8rem !important;
                margin: 0 auto 20px auto !important;
                text-align: center !important;
                width: 100% !important;
            }
            
            /* DIVISEUR */
            .login-divider {
                width: 100% !important;
                margin: 20px 0 !important;
                border-color: #E5E7EB !important;
            }
            
            /* CHAMP MOT DE PASSE */
            div[data-testid="stTextInput"] {
                width: 100% !important;
                max-width: 350px !important;
                margin: 0 auto 20px auto !important;
            }
            
            /* BOUTON */
            div[data-testid="stButton"] {
                width: 100% !important;
                max-width: 350px !important;
                margin: 0 auto !important;
            }
            
            button[kind="primary"] {
                width: 100% !important;
            }
            
            /* FOOTER */
            .login-footer {
                color: #6B7280 !important;
                font-size: 0.85rem !important;
                margin: 20px 0 0 0 !important;
                text-align: center !important;
                width: 100% !important;
            }
            
            /* BADGE SÉCURITÉ */
            .login-security {
                color: #9CA3AF !important;
                font-size: 0.75rem !important;
                margin: 15px 0 0 0 !important;
                text-align: center !important;
                width: 100% !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # CONTENEUR PRINCIPAL
        st.markdown('<div class="login-main">', unsafe_allow_html=True)
        
        # Logo/emoji
        st.markdown('<div class="login-emoji">🔐</div>', unsafe_allow_html=True)
        
        # Titre principal
        st.markdown(f"<h2 class='title-blue'>{i18n.get('auth.title')}</h2>", unsafe_allow_html=True)
        
        # Slogan
        st.markdown(f"<p class='slogan-green'>{i18n.get('auth.slogan')}</p>", unsafe_allow_html=True)
        
        # Description
        st.markdown(f"""
<p class='description'>
<strong>{i18n.get('auth.description')}</strong>
</p>
""", unsafe_allow_html=True)
        
        # Version info
        st.markdown('<p class="login-caption">📊 Dashboard opérationnel synchronisé • 🚀 3.0.0 • 📅 Données 2026</p>', unsafe_allow_html=True)
        
        # Divider
        st.markdown('<hr class="login-divider">', unsafe_allow_html=True)
        
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
        
        # Divider
        st.markdown('<hr class="login-divider">', unsafe_allow_html=True)
        
        # Footer
        st.markdown('<p class="login-footer">© 2026 OpsGain Technologies • Tous droits réservés</p>', unsafe_allow_html=True)
        
        # Badge sécurité
        st.markdown('<p class="login-security">🔐 Accès sécurisé • 🔄 Données synchronisées • 📈 ROI vérifiable</p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)