"""
Point d'entrée principal de l'application OpsGain Platform.
"""
import streamlit as st
import time
from datetime import datetime, timedelta
from streamlit_folium import st_folium
from src.utils.i18n import i18n

# Import des modules refactorés
from src.auth import Authentication
from src.config import APP_NAME, APP_VERSION, PUBLIC_DATA_HASH, PERIODS, COLORS, USE_REAL_DATA
from src.utils.logger import setup_logger
from src.data.sync import DataSynchronizer
from src.finance.calculator import FinancialCalculator
from src.visualization.components import UIComponents
from src.visualization.charts import ChartGenerator
from src.visualization.maps import MapGenerator
from src.utils.exports import generate_excel_report  # Nouvel import

# Configuration
logger = setup_logger(__name__)


def main():
    """Fonction principale de l'application."""
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🚛",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    if 'language' not in st.session_state:
        st.session_state.language = 'fr'
    i18n.set_language(st.session_state.language)

    Authentication.check_auth()

    st.markdown(UIComponents.style_css(), unsafe_allow_html=True)

    # Initialisation des services avec le mode de données (réelles ou simulées)
    data_sync = DataSynchronizer(use_real_data=USE_REAL_DATA)
    finance_calc = FinancialCalculator(st.session_state)
    chart_gen = ChartGenerator()
    map_gen = MapGenerator()

    render_sidebar(data_sync)

    with st.spinner("Chargement des données synchronisées..."):
        period_data = data_sync.load_period_data()

    financial_metrics = finance_calc.calculate(period_data)

    render_header(period_data.period_name)
    render_operational_summary(period_data, financial_metrics)
    render_performance_analysis(period_data, chart_gen)
    render_equipment_performance(period_data, chart_gen)
    render_realtime_map(map_gen)
    render_alerts_and_activity(period_data)
    render_recommendations(period_data)
    render_financial_module(financial_metrics, period_data)
    render_footer(financial_metrics, period_data.period_name)


def render_sidebar(data_sync):
    with st.sidebar:
        st.markdown(f"### 🎯 **{APP_NAME}**")
        st.markdown("---")

        if st.button("🚀 **Lancer la démonstration complète**", type="primary"):
            st.session_state.demo_launched = True
            st.rerun()

        st.markdown("---")
        st.markdown("### 📅 **PÉRIODE D'ANALYSE**")

        default_end = datetime.now()
        default_start = default_end - timedelta(days=30)

        period_option = st.selectbox(
            "Sélectionner la période",
            options=list(PERIODS.keys())
        )

        handle_period_selection(period_option, default_start, default_end)
        render_filters()

        st.markdown("---")
        st.markdown("### 🌍 **LANGUE**")

        language = st.selectbox(
            "Sélectionner la langue",
            options=["fr", "en"],
            format_func=lambda x: "🇫🇷 Français" if x == "fr" else "🇬🇧 English",
            key="language_select"
        )

        if language != st.session_state.language:
            st.session_state.language = language
            i18n.set_language(language)
            st.rerun()

        render_financial_params()
        render_sync_section(data_sync)
        render_info_section()


def handle_period_selection(period_option, default_start, default_end):
    if period_option == "Personnalisée":
        col1, col2 = st.columns(2)
        with col1:
            start_date_input = st.date_input("Date début", value=default_start)
        with col2:
            end_date_input = st.date_input("Date fin", value=default_end)

        st.session_state.start_date = datetime.combine(start_date_input, datetime.min.time())
        st.session_state.end_date = datetime.combine(end_date_input, datetime.max.time())
        st.session_state.selected_period = f"{start_date_input.strftime('%d/%m/%Y')} au {end_date_input.strftime('%d/%m/%Y')}"
    else:
        days = PERIODS[period_option]
        start_date = default_end - timedelta(days=days)
        st.session_state.start_date = start_date
        st.session_state.end_date = default_end
        st.session_state.selected_period = f"{start_date.strftime('%d/%m/%Y')} au {default_end.strftime('%d/%m/%Y')}"


def render_filters():
    st.markdown("---")
    st.markdown("### 🔧 **FILTRES**")

    st.checkbox("Afficher les erreurs", value=True, key="show_errors")
    st.checkbox("Afficher les alertes", value=True, key="show_alerts")
    auto_refresh = st.checkbox("🔄 Actualisation automatique", value=False, key="auto_refresh")

    if auto_refresh:
        refresh_rate = st.slider("Intervalle (secondes)", 5, 60, 30, key="refresh_rate")
        st.info(f"Prochain rafraîchissement dans {refresh_rate}s")
        st.session_state.auto_refresh = True
        st.session_state.refresh_rate = refresh_rate


def render_financial_params():
    st.markdown("---")
    st.markdown("### 💰 **PARAMÈTRES FINANCIERS**")

    init_financial_params()

    col1, col2 = st.columns(2)
    with col1:
        monthly_fixed = st.number_input(
            "Fixé mensuel ($)",
            min_value=0,
            max_value=20000,
            value=st.session_state.monthly_fixed,
            step=500,
            key="monthly_fixed_input"
        )
        st.session_state.monthly_fixed = monthly_fixed

    with col2:
        commission_input = st.number_input(
            "Commission (%)",
            min_value=0.0,
            max_value=50.0,
            value=st.session_state.commission_rate * 100,
            step=0.5,
            key="commission_rate_input"
        )
        st.session_state.commission_rate = commission_input / 100

    col3, col4 = st.columns(2)
    with col3:
        hourly_cost = st.number_input(
            "Coût horaire moyen ($/h)",
            min_value=10,
            max_value=100,
            value=st.session_state.hourly_cost,
            step=5,
            key="hourly_cost_input"
        )
        st.session_state.hourly_cost = hourly_cost

    with col4:
        error_cost = st.number_input(
            "Coût erreur moyen ($)",
            min_value=50,
            max_value=500,
            value=st.session_state.error_cost,
            step=50,
            key="error_cost_input"
        )
        st.session_state.error_cost = error_cost

    st.markdown("#### 📈 **Valeurs de Référence**")
    col5, col6 = st.columns(2)
    with col5:
        baseline_duration = st.number_input(
            "Durée référence (min)",
            min_value=30,
            max_value=120,
            value=st.session_state.baseline_duration,
            step=1,
            key="baseline_duration_input"
        )
        st.session_state.baseline_duration = baseline_duration

    with col6:
        baseline_error_input = st.number_input(
            "Taux erreur référence (%)",
            min_value=1.0,
            max_value=10.0,
            value=st.session_state.baseline_error_rate * 100,
            step=0.1,
            key="baseline_error_input"
        )
        st.session_state.baseline_error_rate = baseline_error_input / 100

    working_days = st.slider(
        "Jours ouvrables/mois",
        20, 26,
        st.session_state.working_days,
        key="working_days_input"
    )
    st.session_state.working_days = working_days


def init_financial_params():
    from src.config import FINANCIAL_PARAMS

    defaults = FINANCIAL_PARAMS.copy()

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sync_section(data_sync):
    st.markdown("---")
    st.markdown("### 🔗 **PARTAGE DE DONNÉES SYNCHRONISÉES**")

    st.info(f"""
    **Hash des données :** `{PUBLIC_DATA_HASH}`

    **Pour partager les mêmes données :**
    1. Configurez la période ci-dessus
    2. Générez le lien de partage
    3. Envoyez-le à vos collaborateurs
    """)

    if st.button("🔗 Générer lien de partage", type="secondary"):
        selected_period = st.session_state.get('selected_period', '30 derniers jours')
        start_date = st.session_state.get('start_date', datetime.now() - timedelta(days=30))
        end_date = st.session_state.get('end_date', datetime.now())

        share_url, link_id = data_sync.generate_shareable_link(
            selected_period, start_date, end_date
        )

        st.success(f"✅ Lien généré ! ID de suivi: {link_id}")
        st.code(share_url, language="text")

        st.markdown(f"""
        <a href="{share_url}" target="_blank">
            <button style="
                background: {COLORS['secondary']}; 
                color: white; 
                border: none; 
                padding: 10px 20px; 
                border-radius: 5px; 
                cursor: pointer; 
                width: 100%; 
                margin-top: 10px;
                font-weight: 600;
            ">
                🌐 Ouvrir dans un nouvel onglet
            </button>
        </a>
        """, unsafe_allow_html=True)


def render_info_section():
    st.markdown("---")
    st.markdown("#### 📊 **INFORMATIONS**")
    st.markdown(f"**OpsGain Plateform Version:** {APP_VERSION}")
    st.markdown("**Statut:** Données synchronisées")
    st.markdown(f"**Hash des données:** `{PUBLIC_DATA_HASH}`")
    st.markdown("**Développeur:** ELIE KAYOMB MBUMB")
    st.markdown("**Accès sécurisé:** ✅ Authentifié")


def render_header(period_name):
    col1, col2 = st.columns([1, 5])

    with col1:
        try:
            st.image("assets/logo.png", width=80)
        except:
            from PIL import Image, ImageDraw
            import io

            img = Image.new('RGB', (80, 80), color=COLORS['primary'])
            d = ImageDraw.Draw(img)
            d.text((20, 35), "PSI", fill=(255, 255, 255))

            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            st.image(buf, width=80)

    with col2:
        st.markdown(f'<h1 class="main-title">{i18n.get("app.title", APP_NAME)}</h1>', unsafe_allow_html=True)
        st.markdown(f"**Dashboard opérationnel synchronisé | Période: {period_name} | Données Simulées 2026**")
        st.markdown("**Vos Operations Nos Gains. | La plateforme qui transforme vos données opérationnelles en gains financiers vérifiables en temps réel.**")

    UIComponents.render_sync_badge()
    st.markdown("---")

    if st.session_state.get('demo_launched', False):
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i in range(101):
            progress_bar.progress(i)
            status_text.text(f"Analyse des données en cours... {i}%")
            time.sleep(0.02)

        progress_bar.empty()
        status_text.empty()
        st.balloons()
        st.success("✅ **Démonstration terminée** - Données analysées avec succès")
        st.session_state.demo_launched = False


def render_operational_summary(period_data, financial_metrics):
    st.markdown(f'<h2 class="section-title">{i18n.get("dashboard.operational_summary", "📊 SYNTHÈSE OPÉRATIONNELLE")}</h2>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_ops = period_data.daily_data['nb_operations'].sum()
        avg_daily_ops = total_ops / len(period_data.daily_data) if len(period_data.daily_data) > 0 else 0
        st.metric(
            label="📦 Opérations Total",
            value=f"{total_ops:,}",
            delta=f"{avg_daily_ops:,.0f}/jour",
            help=f"Total sur {len(period_data.daily_data)} jours"
        )

    with col2:
        avg_duration = period_data.daily_data['duree_moyenne'].mean()
        prev_duration = avg_duration * 1.05
        delta_pct = ((prev_duration - avg_duration) / prev_duration * 100) if prev_duration > 0 else 0
        st.metric(
            label="⏱️ Durée Moyenne",
            value=f"{avg_duration:.1f} min",
            delta=f"-{delta_pct:.1f}%" if delta_pct > 0 else None,
            help="Moyenne pondérée par le nombre d'opérations"
        )

    with col3:
        total_errors = period_data.daily_data['erreurs'].sum()
        total_ops = period_data.daily_data['nb_operations'].sum()
        error_rate = (total_errors / total_ops * 100) if total_ops > 0 else 0
        st.metric(
            label="❌ Taux d'Erreur",
            value=f"{error_rate:.1f}%",
            delta=f"{total_errors} erreurs",
            delta_color="normal" if error_rate < 2.5 else "inverse",
            help=f"Total de {total_errors} erreurs sur la période"
        )

    with col4:
        st.metric(
            label="💰 Gains Totaux Période",
            value=f"${financial_metrics.period_gains:,.0f}",
            delta=f"${financial_metrics.daily_gains:,.0f}/jour",
            help=f"Gains estimés sur {len(period_data.daily_data)} jours"
        )

    st.markdown("---")


def render_performance_analysis(period_data, chart_gen):
    st.markdown('<h2 class="section-title">📈 ANALYSE DES PERFORMANCES</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Activité Journalière")
        if not period_data.daily_data.empty:
            fig1 = chart_gen.create_daily_activity_chart(
                period_data.daily_data,
                period_data.period_name
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            UIComponents.render_alert("Aucune donnée disponible", "warning")

    with col2:
        st.markdown("#### 🕒 Distribution Horaire")
        if not period_data.hourly_data.empty:
            fig2 = chart_gen.create_hourly_distribution_chart(period_data.hourly_data)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            UIComponents.render_alert("Aucune donnée horaire disponible", "warning")


def render_equipment_performance(period_data, chart_gen):
    st.markdown('<h2 class="section-title">🏗️ PERFORMANCE DES ÉQUIPEMENTS</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        if not period_data.engins_data.empty:
            fig3 = chart_gen.create_engins_performance_chart(period_data.engins_data)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            UIComponents.render_alert("Aucune donnée d'équipement disponible", "warning")

    with col2:
        st.markdown("#### ⚠️ Engins à Surveiller")
        if not period_data.engins_data.empty:
            period_data.engins_data['taux_erreur'] = (
                period_data.engins_data['erreurs'] /
                period_data.engins_data['total_operations'] * 100
            )
            problem_engins = period_data.engins_data[period_data.engins_data['taux_erreur'] > 1.5]

            if not problem_engins.empty:
                for _, engin in problem_engins.iterrows():
                    error_class = "badge-danger" if engin['taux_erreur'] > 3 else "badge-warning"
                    st.markdown(f"""
                    <div class="metric-card">
                        <strong>{engin['engin']}</strong><br>
                        <span class="{error_class}">{engin['erreurs']} erreurs ({engin['taux_erreur']:.1f}%)</span><br>
                        <small>{engin['total_operations']} opérations</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                UIComponents.render_alert("✅ Tous les engins fonctionnent normalement", "success")
        else:
            UIComponents.render_alert("Aucun engin problématique détecté", "info")


def render_realtime_map(map_gen):
    st.markdown('<h2 class="section-title">🗺️ CARTE TEMPS-RÉEL DU PORT</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        port_map = map_gen.create_realtime_map()
        st_folium(port_map, width=800, height=500)

    with col2:
        st.markdown("#### 🔍 FILTRES")

        selected_engins = st.multiselect(
            "Types d'engins",
            ["Tracteur", "Chariot", "Grue", "Camion"],
            default=["Tracteur", "Chariot"],
            key="map_engins_filter"
        )

        st.slider("Rafraîchissement (secondes)", 5, 60, 30, key="map_refresh_rate")
        st.checkbox("Afficher les trajets", value=True, key="show_routes")
        st.checkbox("Afficher les zones congestion", value=True, key="show_congestion")
        st.checkbox("Afficher les alertes sur carte", value=True, key="show_alerts_on_map")

        st.markdown("---")
        st.markdown("#### 🎯 LÉGENDE")
        st.markdown("🔵 **Quai Principal**")
        st.markdown("🟢 **Quai Routier**")
        st.markdown("🟠 **Zone Stockage**")
        st.markdown("🔴 **Contrôle Douane**")
        st.markdown("⚫ **Maintenance**")


def render_alerts_and_activity(period_data):
    st.markdown('<h2 class="section-title">🚨 ALERTES ET ACTIVITÉ EN TEMPS RÉEL</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ⚠️ ALERTES ACTIVES")

        alerts = []

        if not period_data.daily_data.empty and len(period_data.daily_data) > 1:
            latest_day = period_data.daily_data.iloc[-1]
            avg_operations = period_data.daily_data['nb_operations'].mean()

            if latest_day['nb_operations'] > avg_operations * 1.3:
                alerts.append("📈 **Volume anormalement élevé** - Augmentation de +30%")

            if latest_day['erreurs'] > 0 and (latest_day['erreurs'] / latest_day['nb_operations']) > 0.03:
                alerts.append("❌ **Taux d'erreur critique** - Supérieur à 3%")

        if not period_data.engins_data.empty:
            period_data.engins_data['taux_erreur'] = (
                period_data.engins_data['erreurs'] /
                period_data.engins_data['total_operations'] * 100
            )
            engins_problematiques = period_data.engins_data[period_data.engins_data['taux_erreur'] > 2.0]

            for _, engin in engins_problematiques.iterrows():
                alerts.append(f"⚠️ **Maintenance préventive requise** - {engin['engin']} (taux erreur: {engin['taux_erreur']:.1f}%)")

        if alerts:
            for alert in alerts:
                if "❌" in alert or "⚠️" in alert:
                    UIComponents.render_alert(alert, "danger")
                else:
                    UIComponents.render_alert(alert, "warning")
        else:
            UIComponents.render_alert("✅ Aucune alerte active", "success")

    with col2:
        st.markdown("#### 📝 DERNIÈRES OPÉRATIONS")

        if not period_data.recent_ops.empty:
            recent_ops_display = period_data.recent_ops.head(10).copy()

            for _, row in recent_ops_display.iterrows():
                timestamp_str = row['timestamp'].strftime('%H:%M') if hasattr(row['timestamp'], 'strftime') else str(row['timestamp'])

                icon = ""
                if row.get('urgence', 0):
                    icon += "⚠️ "
                if row.get('erreur', 0):
                    icon += "❌ "

                st.markdown(f"""
                **{timestamp_str}** - {icon}{row['type_operation']}  
                *{row['zone']}* | {row['engin']} | {row['duree_minutes']:.0f} min
                """)
        else:
            UIComponents.render_alert("Aucune opération récente", "info")


def render_recommendations(period_data):
    st.markdown('<h2 class="section-title">💡 RECOMMANDATIONS INTELLIGENTES</h2>', unsafe_allow_html=True)

    recommendations = []

    if not period_data.recent_ops.empty and 'urgence' in period_data.recent_ops.columns:
        zone_urgences = period_data.recent_ops.groupby('zone')['urgence'].sum()
        if len(zone_urgences) > 0 and zone_urgences.max() > 0:
            zone_probleme = zone_urgences.idxmax()
            nb_urgences = int(zone_urgences.max())
            recommendations.append(f"**Optimiser {zone_probleme}** : {nb_urgences} urgences détectées")

    if not period_data.engins_data.empty:
        period_data.engins_data['taux_erreur'] = (
            period_data.engins_data['erreurs'] /
            period_data.engins_data['total_operations'] * 100
        )
        if not period_data.engins_data.empty:
            engin_probleme = period_data.engins_data.loc[period_data.engins_data['taux_erreur'].idxmax()]
            if engin_probleme['taux_erreur'] > 2.0:
                recommendations.append(f"**Maintenance {engin_probleme['engin']}** : Taux erreur: {engin_probleme['taux_erreur']:.1f}%")

    if not period_data.hourly_data.empty:
        heure_pic = period_data.hourly_data.loc[period_data.hourly_data['nb_operations'].idxmax(), 'heure']
        ops_pic = period_data.hourly_data['nb_operations'].max()
        heure_creux = period_data.hourly_data.loc[period_data.hourly_data['nb_operations'].idxmin(), 'heure']
        ops_creux = period_data.hourly_data['nb_operations'].min()

        if ops_pic > ops_creux * 1.5:
            recommendations.append(f"**Équilibrage charge** : Déplacer des opérations de {heure_pic}h vers {heure_creux}h")

    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
    else:
        UIComponents.render_alert("Analyse en cours... sélectionnez une période pour les recommandations.", "info")


def render_financial_module(financial_metrics, period_data):
    st.markdown('<h2 class="section-title">💰 MODULE FINANCIER</h2>', unsafe_allow_html=True)

    period_summary = financial_metrics.period_summary
    st.markdown(f"#### 📅 **ANALYSE FINANCIÈRE POUR : {period_data.period_name.upper()}**")

    UIComponents.render_period_summary(period_summary)

    st.markdown(f"""
    <div style="background: {COLORS['info']}; color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
        🔒 **Données synchronisées** : Tous les utilisateurs voient exactement les mêmes chiffres
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📊 GAINS FINANCIERS BASÉS SUR LA PÉRIODE")

    fin_row1_col1, fin_row1_col2, fin_row1_col3, fin_row1_col4 = st.columns(4)

    with fin_row1_col1:
        st.markdown(f"""
        <div class="commission-card">
            <h3 style="color: white; margin: 0; font-size: 2rem;">${financial_metrics.daily_gains:,.0f}</h3>
            <p style="margin: 0; opacity: 0.9;">Gains journaliers</p>
            <small>Basé sur {period_summary['total_days']} jours</small>
        </div>
        """, unsafe_allow_html=True)

    with fin_row1_col2:
        st.markdown(f"""
        <div class="gain-card">
            <h3 style="color: white; margin: 0; font-size: 2rem;">${financial_metrics.monthly_projection:,.0f}</h3>
            <p style="margin: 0; opacity: 0.9;">Projection mensuelle</p>
            <small>Sur {st.session_state.working_days} jours ouvrables</small>
        </div>
        """, unsafe_allow_html=True)

    with fin_row1_col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['primary']} 0%, #1E40AF 100%); 
                    color: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
            <h3 style="color: white; margin: 0; font-size: 2rem;">${financial_metrics.your_commission_today:,.0f}</h3>
            <p style="margin: 0; opacity: 0.9;">Commission journalière</p>
            <small>Fixe + {st.session_state.commission_rate*100}% des gains</small>
        </div>
        """, unsafe_allow_html=True)

    with fin_row1_col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); 
                    color: white; padding: 25px; border-radius: 15px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.15);">
            <h3 style="color: white; margin: 0; font-size: 2rem;">${financial_metrics.your_commission_monthly:,.0f}</h3>
            <p style="opacity: 0.9; font-size: 1rem;">🎯 Votre revenu mensuel</p>
            <small>Basé sur la performance de {period_data.period_name}</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col_graphique, col_resume = st.columns([3, 2])

    with col_graphique:
        st.markdown("#### 📈 RÉPARTITION DES GAINS (MOYENNE JOURNALIÈRE)")
        chart_gen = ChartGenerator()
        fig_fin = chart_gen.create_financial_pie_chart(financial_metrics.breakdown)
        st.plotly_chart(fig_fin, use_container_width=True)

    with col_resume:
        st.markdown("#### 📝 RÉCAPITULATIF CONTRAT")

        st.markdown('''
        <div style="
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        ">
        ''', unsafe_allow_html=True)

        st.markdown(f"""
        <div style="line-height: 2.2;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #E5E7EB; padding: 8px 0;">
                <span style="font-weight: 600; color: #4B5563;">Fixé mensuel</span>
                <span style="font-weight: 700; color: #1E3A8A;">${st.session_state.monthly_fixed:,.0f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #E5E7EB; padding: 8px 0;">
                <span style="font-weight: 600; color: #4B5563;">Taux commission</span>
                <span style="font-weight: 700; color: #10B981;">{st.session_state.commission_rate*100}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #E5E7EB; padding: 8px 0;">
                <span style="font-weight: 600; color: #4B5563;">Jours ouvrables</span>
                <span style="font-weight: 700; color: #F59E0B;">{st.session_state.working_days} jours</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #E5E7EB; padding: 8px 0;">
                <span style="font-weight: 600; color: #4B5563;">Coût horaire</span>
                <span style="font-weight: 700; color: #8B5CF6;">${st.session_state.hourly_cost}/h</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                <span style="font-weight: 600; color: #4B5563;">Coût erreur</span>
                <span style="font-weight: 700; color: #EF4444;">${st.session_state.error_cost}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("#### 🔒 VÉRIFICATION & ACTIONS")
        st.info(f"""
        **Période analysée :** {period_data.period_name}
        **Hash de calcul :** `{financial_metrics.transaction_hash}`
        **Hash des données :** `{PUBLIC_DATA_HASH}`
        """)

        # Nouvelle section EXPORT
        st.markdown("#### 📥 EXPORT")
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            if st.button("📊 Exporter Excel", type="secondary"):
                excel_data = generate_excel_report(period_data, financial_metrics)
                st.download_button(
                    label="Télécharger le rapport Excel",
                    data=excel_data,
                    file_name=f"rapport_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        with col_exp2:
            if st.button("🔄 Actualiser", type="primary"):
                st.rerun()

    st.markdown("---")

    st.markdown("#### 📋 DÉTAILS DES CALCULS - ANALYSE FINANCIÈRE")

    with st.expander("🔍 Afficher les calculs détaillés", expanded=True):
        st.markdown(f"""
        ### 📅 PÉRIODE ANALYSÉE
        **Du :** {period_summary['start_date']}
        **Au :** {period_summary['end_date']}
        **Nombre de jours :** {period_summary['total_days']} jours
        **Hash des données :** `{PUBLIC_DATA_HASH}`
        """)
        st.divider()

        st.markdown("### 1. GAIN TEMPS (Réduction de durée des opérations)")

        baseline_duration = st.session_state.baseline_duration
        avg_duration = period_summary['avg_duration']
        hourly_cost = st.session_state.hourly_cost
        total_ops = period_summary['total_operations']

        time_saved_minutes = max(0, baseline_duration - avg_duration)
        time_saved_hours = time_saved_minutes / 60
        gain_per_op = time_saved_hours * hourly_cost
        total_time_gain = gain_per_op * total_ops

        st.markdown(f"""
        **Paramètres :**
        - Durée de référence : {baseline_duration} minutes
        - Durée moyenne période : {avg_duration:.1f} minutes
        - Coût horaire moyen : ${hourly_cost}/heure
        - Total opérations période : {total_ops:,} opérations

        **Calcul :**
        - Économie par opération : {time_saved_minutes:.1f} minutes = {time_saved_hours:.3f} heures
        - Gain par opération : {time_saved_hours:.3f} h × ${hourly_cost}/h = **${gain_per_op:.2f}**
        - Gain total temps : {total_ops:,} opérations × ${gain_per_op:.2f} = **${financial_metrics.breakdown.get('time_gain_period', 0):,.2f}**
        - Gain journalier moyen : **${financial_metrics.breakdown.get('time_gain', 0):,.2f}/jour**
        """)
        st.divider()

        st.markdown("### 2. GAIN ERREURS (Réduction des erreurs)")

        baseline_error_rate = st.session_state.baseline_error_rate * 100
        current_error_rate = period_summary['error_rate']
        error_cost = st.session_state.error_cost

        errors_avoided = max(0, (baseline_error_rate - current_error_rate) / 100 * total_ops)
        total_error_gain = errors_avoided * error_cost

        st.markdown(f"""
        **Paramètres :**
        - Taux erreur référence : {baseline_error_rate:.1f}%
        - Taux erreur période : {current_error_rate:.1f}%
        - Coût par erreur : ${error_cost}
        - Total opérations période : {total_ops:,} opérations

        **Calcul :**
        - Erreurs évitées : ({baseline_error_rate:.1f}% - {current_error_rate:.1f}%) × {total_ops:,} = **{errors_avoided:.1f}** erreurs
        - Gain total erreurs : {errors_avoided:.1f} erreurs × ${error_cost} = **${financial_metrics.breakdown.get('error_gain_period', 0):,.2f}**
        - Gain journalier moyen : **${financial_metrics.breakdown.get('error_gain', 0):,.2f}/jour**
        """)
        st.divider()

        st.markdown("### 3. GAIN MAINTENANCE (Prévention des pannes)")

        maintenance_cost = 500
        maintenance_gain_period = financial_metrics.breakdown.get('maintenance_gain_period', 0)
        maintenance_alerts = int(maintenance_gain_period / maintenance_cost) if maintenance_cost > 0 else 0

        st.markdown(f"""
        **Paramètres :**
        - Alertes maintenance détectées : {maintenance_alerts} alertes
        - Coût évité par alerte : ${maintenance_cost}
        - Gain total maintenance période : ${maintenance_gain_period:,.2f}

        **Calcul :**
        - Gain total maintenance : {maintenance_alerts} alertes × ${maintenance_cost}/alerte = **${maintenance_gain_period:,.2f}**
        - Gain journalier moyen : **${financial_metrics.breakdown.get('maintenance_gain', 0):,.2f}/jour**
        """)
        st.divider()

        st.markdown("### 4. GAIN CARBURANT (Optimisation des trajets)")

        trucks_per_day = min(500, period_summary['avg_daily_operations'] * 0.3)
        fuel_saving = 1.5

        daily_fuel_gain = trucks_per_day * fuel_saving
        total_fuel_gain = daily_fuel_gain * period_summary['total_days']

        st.markdown(f"""
        **Paramètres :**
        - Camions par jour : {trucks_per_day:.0f} camions
        - Économie par camion : ${fuel_saving}$/jour
        - Nombre de jours : {period_summary['total_days']} jours

        **Calcul :**
        - Gain carburant journalier : {trucks_per_day:.0f} × ${fuel_saving} = ${daily_fuel_gain:.2f}$/jour
        - Gain total carburant : ${daily_fuel_gain:.2f}/jour × {period_summary['total_days']} jours = ${financial_metrics.breakdown.get('fuel_gain_period', 0):,.2f}$
        """)
        st.divider()

        st.markdown("### 📊 SYNTHÈSE FINANCIÈRE")
        st.markdown(f"""
        **Gains totaux sur la période :**
        - Gain temps : ${financial_metrics.breakdown.get('time_gain_period', 0):,.2f}$
        - Gain erreurs : ${financial_metrics.breakdown.get('error_gain_period', 0):,.2f}$
        - Gain maintenance : ${financial_metrics.breakdown.get('maintenance_gain_period', 0):,.2f}$
        - Gain carburant : ${financial_metrics.breakdown.get('fuel_gain_period', 0):,.2f}$

        **Total gains période :** **${financial_metrics.period_gains:,.2f}**

        **Moyennes journalières :**
        - Gain temps : ${financial_metrics.breakdown.get('time_gain', 0):,.2f}$/jour
        - Gain erreurs : ${financial_metrics.breakdown.get('error_gain', 0):,.2f}$/jour
        - Gain maintenance : ${financial_metrics.breakdown.get('maintenance_gain', 0):,.2f}$/jour
        - Gain carburant : ${financial_metrics.breakdown.get('fuel_gain', 0):,.2f}$/jour

        **Total gains journaliers :${financial_metrics.daily_gains:,.2f}$/jour

        **Projection mensuelle ({st.session_state.working_days} jours) :
        - ${financial_metrics.daily_gains:,.2f}$/jour × {st.session_state.working_days} jours = ${financial_metrics.monthly_projection:,.2f}$

        **Votre commission :**
        - Fixe mensuel : ${st.session_state.monthly_fixed:,.2f}$
        - Variable ({st.session_state.commission_rate*100}%) : ${financial_metrics.monthly_projection * st.session_state.commission_rate:,.2f}$
        - Commission totale : ${financial_metrics.your_commission_monthly:,.2f}$
        """)


def render_footer(financial_metrics, period_name):
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #6B7280; padding: 20px; font-size: 0.9rem;">
        <strong>OPSGAIN PLATFORM {APP_VERSION}</strong> - Données synchronisées pour tous les utilisateurs<br>
        <strong>La plateforme qui transforme vos données opérationnelles en gains financiers vérifiables en temps réel</strong><br>
        <strong>Période analysée</strong> : {period_name} 
        <strong>Hash des données</strong> : {PUBLIC_DATA_HASH} | Hash de vérification: {financial_metrics.transaction_hash}<br>
        <small>Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()