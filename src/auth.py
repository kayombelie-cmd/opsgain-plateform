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
        # CSS (identique à avant, mais sans set_page_config)
        st.markdown("""
        <style>
            /* styles inchangés */
        </style>
        """, unsafe_allow_html=True)

        # Contenu principal avec i18n
        st.markdown('<div class="login-main">', unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; font-size: 3.5rem; color: #3B82F6;'>🔐</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 class='login-title'>{i18n.get('auth.title')}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p class='login-slogan'>{i18n.get('auth.slogan')}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='login-description'><strong>{i18n.get('auth.description')}</strong></p>", unsafe_allow_html=True)
        st.markdown(f"<p class='login-caption'>📊 {i18n.get('app.subtitle', 'Dashboard opérationnel synchronisé')} • 🚀 {APP_VERSION} • 📅 Données 2026</p>", unsafe_allow_html=True)
        st.markdown('<hr class="login-divider">', unsafe_allow_html=True)

        password = st.text_input(
            i18n.get('auth.password_label'),
            type="password",
            help=i18n.get('auth.password_help', default="Entrez le mot de passe fourni par votre administrateur OpsGain"),
            key="password_input"
        )

        if st.button(i18n.get('auth.button_access'), type="primary", use_container_width=True):
            if password == DEFAULT_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error(i18n.get('auth.wrong_password'))

        st.markdown('<hr class="login-divider">', unsafe_allow_html=True)
        st.markdown(f"<p class='login-footer'>© 2026 OpsGain Technologies • Tous droits réservés</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='login-security'>{i18n.get('app.footer', '🔐 Accès sécurisé • 🔄 Données synchronisées • 📈 ROI vérifiable')}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)