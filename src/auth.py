"""
Gestion de l'authentification.
"""
import streamlit as st
import os
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
        try:
            st.markdown("""
            <style>
            /* Logo en haut à gauche */
            .logo-container {
                position: absolute;
                top: 20px;
                left: 20px;
                z-index: 1000;
            }
            .stApp {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                position: relative;
            }
            .block-container {
                width: 100%;
                text-align: center;
                padding: 2rem;
            }
            .stTextInput > div, .stButton > button {
                width: 100%;
                max-width: 400px;
                margin: 0 auto;
            }
            hr {
                margin: 20px auto;
            }
            </style>
            """, unsafe_allow_html=True)

            # Logo en haut à gauche (hors du bloc centré)
            st.markdown('<div class="logo-container">', unsafe_allow_html=True)
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                logo_path = os.path.join(current_dir, "..", "assets", "opsgain_logo.jpg")
                if os.path.exists(logo_path):
                    st.image(logo_path, width=100)  # Agrandi à 100px
                else:
                    st.markdown("<h1 style='color: #3B82F6; font-size: 3rem;'>🔐</h1>", unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"<p>Erreur chargement logo: {e}</p>", unsafe_allow_html=True)
                st.markdown("<h1 style='color: #3B82F6; font-size: 3rem;'>🔐</h1>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Contenu centré
            st.markdown('<div class="block-container">', unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align: center; color: #1E3A8A; font-size: 2.2rem; font-weight: 800;'>{i18n.get('auth.title')}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #10B981; font-size: 1.1rem; font-weight: 600;'>{i18n.get('auth.slogan')}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #475569; font-size: 0.95rem;'><strong>{i18n.get('auth.description')}</strong></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #6B7280; font-size: 0.8rem; margin-bottom: 20px;'>📊 {i18n.get('app.subtitle')} • 🚀 {APP_VERSION} • 📅 Données 2026</p>", unsafe_allow_html=True)

            st.divider()

            # Sélecteur de rôle
            role = st.selectbox(
                "Choisissez votre profil",
                options=["Administrateur", "Utilisateur"],
                key="role_select"
            )

            password = st.text_input(
                i18n.get('auth.password_label'),
                type="password",
                label_visibility="collapsed",
                placeholder=i18n.get('auth.password_label')
            )

            if st.button(i18n.get('auth.button_access'), type="primary", use_container_width=True):
                if password == DEFAULT_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.role = "admin" if role == "Administrateur" else "user"
                    st.rerun()
                else:
                    st.error(i18n.get('auth.wrong_password'))

            st.divider()
            st.markdown("<p style='text-align: center; color: #6B7280; font-size: 0.85rem;'>© 2026 OpsGain Technologies • Tous droits réservés</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #9CA3AF; font-size: 0.75rem; margin-top: 10px;'>{i18n.get('app.footer')}</p>", unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erreur dans la page de connexion : {e}")
            st.exception(e)