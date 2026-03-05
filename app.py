"""
Point d'entrée principal de l'application OpsGain Platform.
"""
import streamlit as st

# ⚠️ set_page_config en PREMIER
st.set_page_config(
    page_title="OpsGain Platform / Port Intelligent",
    page_icon="assets/opsgain_logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Imports standards ---
import time
from datetime import datetime, timedelta
from streamlit_folium import st_folium

# --- Imports de vos modules ---
from src.utils.i18n import i18n
from src.auth import Authentication
from src.config import APP_NAME, APP_VERSION, PUBLIC_DATA_HASH, PERIODS, COLORS, FINANCIAL_PARAMS, USE_REAL_DATA
from src.utils.logger import setup_logger
from src.data.sync import DataSynchronizer
from src.finance.calculator import FinancialCalculator
from src.visualization.components import UIComponents
from src.visualization.charts import ChartGenerator
from src.visualization.maps import MapGenerator

# ⚠️ Import conditionnel de l'export Excel (s'il n'existe pas, on le met à None)
try:
    from src.utils.exports import generate_excel_report
except ImportError:
    generate_excel_report = None
    print("⚠️ Module src.utils.exports non trouvé – fonction d'export désactivée.")

# 🔧 NOUVEAU : Importer SectorFactory
from src.sectors import SectorFactory

# Configuration du logger
logger = setup_logger(__name__)


def main():
    try:
        # Langue
        if 'language' not in st.session_state:
            st.session_state.language = 'fr'
        i18n.set_language(st.session_state.language)

        # Authentification
        Authentication.check_auth()
         # Initialiser le rôle si absent (par sécurité)
        if 'role' not in st.session_state:
            st.session_state.role = 'user'   # rôle par défaut
        # CSS
        st.markdown(UIComponents.style_css(), unsafe_allow_html=True)

        # Initialisation des services
        data_sync = DataSynchronizer(use_real_data=USE_REAL_DATA)
        finance_calc = FinancialCalculator(st.session_state)
        chart_gen = ChartGenerator()
        map_gen = MapGenerator()

        # Sidebar
        render_sidebar(data_sync)

                # --- NOUVEAU : Affichage basé sur les données du secteur ---
        if st.session_state.get('data_loaded', False):
            data = st.session_state.data
            sector = SectorFactory.get_sector(st.session_state.sector)

            # Calcul des métriques
            metrics = sector.calculate_metrics(data)
            # Paramètres de gains (à adapter selon vos besoins)
            gain_params = {
                'hourly_technician_cost': st.session_state.get('hourly_cost', 50),
                # Ajoutez d'autres paramètres si nécessaire
            }
            gains = sector.calculate_gains(data, gain_params)

            # Affichage des KPI
            render_sector_metrics(metrics, sector_name=st.session_state.sector)

            # Visualisations
            figs = sector.get_visualizations(data)
            for fig in figs:
                st.plotly_chart(fig, use_container_width=True)

            # Affichage des gains
            st.markdown(f"## Gains financiers estimés")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gains totaux période", f"${gains['period_gains']:,.0f}")
            with col2:
                st.metric("Gains journaliers moyens", f"${gains['daily_gains']:,.0f}")
            with col3:
                # Exemple de commission (10% des gains journaliers)
                st.metric("Votre commission (exemple)", f"${gains['daily_gains'] * 0.1:,.0f}")

            # Détail des gains
            with st.expander("Détail des gains"):
                for key, value in gains['breakdown'].items():
                    st.write(f"{key}: ${value:,.2f}")
        else:
            st.info("Veuillez charger des données via la sidebar.")
        # --- FIN DU NOUVEAU CODE ---
    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
        st.exception(e)


# ------------------------------------------------------------------------------
# Fonctions de rendu (sidebar, header, etc.)
# ------------------------------------------------------------------------------

def render_sidebar(data_sync):
    with st.sidebar:
        st.markdown(f"### 🎯 **{i18n.get('sidebar.title')}**")
        st.markdown("---")
        
        if st.button(i18n.get('sidebar.demo_button'), type="primary", use_container_width=True):
            st.session_state.demo_launched = True
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"### {i18n.get('sidebar.period_analysis')}")
        
        default_end = datetime.now()
        default_start = default_end - timedelta(days=30)
        
        # Liste des options de période traduites
        period_options = [
            i18n.get('periods.last_7_days'),
            i18n.get('periods.last_30_days'),
            i18n.get('periods.last_90_days'),
            i18n.get('periods.custom')
        ]
        
        # Sélecteur de période
        selected_period_text = st.selectbox(
            i18n.get('sidebar.select_period'),
            options=period_options,
            key="period_select"
        )
        
        # Mapper le texte sélectionné à une clé interne
        if selected_period_text == i18n.get('periods.last_7_days'):
            period_key = "7d"
        elif selected_period_text == i18n.get('periods.last_30_days'):
            period_key = "30d"
        elif selected_period_text == i18n.get('periods.last_90_days'):
            period_key = "90d"
        else:
            period_key = "custom"
        
        # Appeler la fonction de gestion des dates avec la clé
        handle_period_selection(period_key, default_start, default_end)

                # --- NOUVEAU : Sélection du secteur et mode de données ---
        st.markdown("---")
        st.markdown("### 🏭 Secteur d'activité")
        sector_options = {
            'telecom': '📡 Télécommunications',
            'logistics': '🚚 Logistique',
            'retail': '🛒 Grande Distribution',
            'education': '🎓 Éducation'
        }
        selected_sector_key = st.selectbox(
            "Choisissez le secteur",
            options=list(sector_options.keys()),
            format_func=lambda x: sector_options[x],
            key='sector_select'
        )
        if selected_sector_key != st.session_state.get('sector'):
            st.session_state.sector = selected_sector_key
            st.rerun()

        # Choix du mode de données (simulées ou réel)
        data_mode = st.radio("Mode de données", ["Simulées", "Réelles"], key='data_mode')

        if data_mode == "Réelles":
            source_type = st.selectbox("Type de source", ["Excel", "CSV", "API"], key='source_type')
            if source_type == "Excel":
                uploaded_file = st.file_uploader("Choisissez un fichier Excel", type=['xlsx', 'xls'], key='excel_file')
                if uploaded_file:
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                        tmp.write(uploaded_file.getvalue())
                        st.session_state.data_source = tmp.name
                        st.session_state.connector_type = 'excel'
                        st.session_state.connector_config = {}
            elif source_type == "CSV":
                uploaded_file = st.file_uploader("Choisissez un fichier CSV", type=['csv'], key='csv_file')
                if uploaded_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
                        tmp.write(uploaded_file.getvalue())
                        st.session_state.data_source = tmp.name
                        st.session_state.connector_type = 'csv'
                        st.session_state.connector_config = {}
            elif source_type == "API":
                url = st.text_input("URL de l'API")
                method = st.selectbox("Méthode", ["GET", "POST"])
                if url:
                    st.session_state.data_source = url
                    st.session_state.connector_type = 'api'
                    st.session_state.connector_config = {'method': method}
        else:
            st.info("Données simulées générées automatiquement.")
            days_sim = st.slider("Nombre de jours de simulation", 7, 90, 30)
            st.session_state.sim_days = days_sim

        # Bouton de chargement
        if st.button("Charger les données", type="primary"):
            with st.spinner("Chargement en cours..."):
                sector_name = st.session_state.sector
                if data_mode == "Simulées":
                    sector = SectorFactory.get_sector(sector_name)
                    data = sector.generate_sample_data(st.session_state.get('sim_days', 30))
                    st.session_state.data = data
                    st.session_state.data_loaded = True
                else:
                    if 'data_source' not in st.session_state:
                        st.error("Veuillez sélectionner une source de données.")
                    else:
                        sync = DataSynchronizer(
                            sector_name=sector_name,
                            connector_type=st.session_state.connector_type,
                            connector_config=st.session_state.connector_config
                        )
                        data = sync.load_data(st.session_state.data_source)
                        st.session_state.data = data
                        st.session_state.data_loaded = True
                st.rerun()
        # --- FIN DU NOUVEAU CODE ---
        
        # Filtres
        render_filters()
        
        # Sélecteur de langue
        st.markdown("---")
        st.markdown(f"### {i18n.get('sidebar.language')}")
        language = st.selectbox(
            "",
            options=["fr", "en"],
            format_func=lambda x: "🇫🇷 Français" if x == "fr" else "🇬🇧 English",
            key="language_select",
            label_visibility="collapsed"
        )
        if language != st.session_state.language:
            st.session_state.language = language
            i18n.set_language(language)
            st.rerun()
        
        # Paramètres financiers – réservés aux admins
        if st.session_state.get('role') == 'admin':
            render_financial_params()
        else:
            st.markdown("---")
            st.info("Les paramètres financiers sont réservés à l'administrateur.")

        render_sync_section(data_sync)
        render_info_section()


def handle_period_selection(period_key, default_start, default_end):
    if period_key == "custom":
        col1, col2 = st.columns(2)
        with col1:
            start_date_input = st.date_input("Date début", value=default_start)
        with col2:
            end_date_input = st.date_input("Date fin", value=default_end)
        st.session_state.start_date = datetime.combine(start_date_input, datetime.min.time())
        st.session_state.end_date = datetime.combine(end_date_input, datetime.max.time())
        st.session_state.selected_period = f"{start_date_input.strftime('%d/%m/%Y')} au {end_date_input.strftime('%d/%m/%Y')}"
    else:
        days_map = {"7d": 7, "30d": 30, "90d": 90}
        days = days_map.get(period_key, 30)
        start_date = default_end - timedelta(days=days)
        st.session_state.start_date = start_date
        st.session_state.end_date = default_end
        period_name_key = f"periods.last_{days}_days"
        st.session_state.selected_period = i18n.get(period_name_key, f"{days} derniers jours")


def render_filters():
    st.markdown("---")
    st.markdown(f"### {i18n.get('sidebar.filters')}")
    
    st.checkbox(i18n.get('sidebar.show_errors'), value=True, key="show_errors")
    st.checkbox(i18n.get('sidebar.show_alerts'), value=True, key="show_alerts")
    auto_refresh = st.checkbox(i18n.get('sidebar.auto_refresh'), value=False, key="auto_refresh")
    
    if auto_refresh:
        refresh_rate = st.slider(i18n.get('sidebar.refresh_interval'), 5, 60, 30, key="refresh_rate")
        st.info(i18n.get('sidebar.next_refresh', seconds=refresh_rate))
        st.session_state.auto_refresh = True
        st.session_state.refresh_rate = refresh_rate


def render_financial_params():
    st.markdown("---")
    st.markdown(f"### {i18n.get('sidebar.financial_params')}")
    
    init_financial_params()
    
    col1, col2 = st.columns(2)
    with col1:
        monthly_fixed = st.number_input(
            i18n.get('sidebar.monthly_fixed'),
            min_value=0, max_value=20000,
            value=st.session_state.monthly_fixed,
            step=500, key="monthly_fixed_input"
        )
        st.session_state.monthly_fixed = monthly_fixed
    with col2:
        commission_input = st.number_input(
            i18n.get('sidebar.commission_rate'),
            min_value=0.0, max_value=50.0,
            value=st.session_state.commission_rate * 100,
            step=0.5, key="commission_rate_input"
        )
        st.session_state.commission_rate = commission_input / 100

    col3, col4 = st.columns(2)
    with col3:
        hourly_cost = st.number_input(
            i18n.get('sidebar.hourly_cost'),
            min_value=10,
            max_value=100,
            value=st.session_state.hourly_cost,
            step=5,
            key="hourly_cost_input"
        )
        st.session_state.hourly_cost = hourly_cost

    with col4:
        error_cost = st.number_input(
            i18n.get('sidebar.error_cost'),
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
            i18n.get('sidebar.baseline_duration'),
            min_value=30,
            max_value=120,
            value=st.session_state.baseline_duration,
            step=1,
            key="baseline_duration_input"
        )
        st.session_state.baseline_duration = baseline_duration

    with col6:
        baseline_error_input = st.number_input(
            i18n.get('sidebar.baseline_error'),
            min_value=1.0,
            max_value=10.0,
            value=st.session_state.baseline_error_rate * 100,
            step=0.1,
            key="baseline_error_input"
        )
        st.session_state.baseline_error_rate = baseline_error_input / 100

    working_days = st.slider(
        i18n.get('sidebar.working_days'),
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
    # Ne rien afficher si l'utilisateur n'est pas authentifié
    if not st.session_state.get('authenticated', False):
        return

    st.markdown("---")
    st.markdown(f"### {i18n.get('sidebar.data_sync')}")
    
    default_sync_info = f"**Hash des données :** `{PUBLIC_DATA_HASH}`\n\n**Pour partager les mêmes données :**\n1. Configurez la période ci-dessus\n2. Générez le lien de partage\n3. Envoyez-le à vos collaborateurs"
    sync_info_text = i18n.get('sidebar.sync_info', default=default_sync_info)
    if '{hash}' in sync_info_text:
        sync_info_text = sync_info_text.format(hash=PUBLIC_DATA_HASH)
    st.info(sync_info_text)
    
    if st.button(i18n.get('sidebar.generate_link'), use_container_width=True, type="secondary"):
        selected_period = st.session_state.get('selected_period', i18n.get('periods.last_30_days'))
        start_date = st.session_state.get('start_date', datetime.now() - timedelta(days=30))
        end_date = st.session_state.get('end_date', datetime.now())
        
        share_url, link_id = data_sync.generate_shareable_link(selected_period, start_date, end_date)
        
        st.success(i18n.get('sidebar.link_success', id=link_id))
        st.code(share_url, language="text")
        
        st.markdown(f"""
        <a href="{share_url}" target="_blank">
            <button style="background: {COLORS['secondary']}; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; width: 100%; margin-top: 10px; font-weight: 600;">
                {i18n.get('sidebar.open_link')}
            </button>
        </a>
        """, unsafe_allow_html=True)


def render_info_section():
    st.markdown("---")
    st.markdown(f"#### {i18n.get('sidebar.info')}")
    st.markdown(i18n.get('sidebar.version', version=APP_VERSION))
    st.markdown(i18n.get('sidebar.status'))
    st.markdown(i18n.get('sidebar.data_hash', hash=PUBLIC_DATA_HASH))
    st.markdown(i18n.get('sidebar.developer'))
    st.markdown(i18n.get('sidebar.access_status'))
    mode = "📡 **Données réelles**" if USE_REAL_DATA else "🧪 **Données simulées**"
    st.markdown(mode)


def render_header(period_name):
    col1, col2 = st.columns([1, 5])
    with col1:
        try:
            st.image("assets/opsgain_logo.jpg", width=150)
        except Exception:
            from PIL import Image, ImageDraw
            import io
            img = Image.new('RGB', (90, 90), color=COLORS['primary'])
            d = ImageDraw.Draw(img)
            d.text((20, 35), "OG", fill=(255, 255, 255))
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            st.image(buf, width=150)

    with col2:
        st.markdown(f'<h1 class="main-title">{i18n.get("app.title", APP_NAME)}</h1>', unsafe_allow_html=True)
        st.markdown(f"{i18n.get('header.subtitle')} | {i18n.get('common.period')}: {period_name} | {i18n.get('header.simulated_data')}")
        st.markdown(f"{i18n.get('header.slogan')}")

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
    st.markdown(f'<h2 class="section-title">{i18n.get("dashboard.operational_summary")}</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_ops = period_data.daily_data['nb_operations'].sum()
        avg_daily_ops = total_ops / len(period_data.daily_data) if len(period_data.daily_data) > 0 else 0
        st.metric(
            label=i18n.get('dashboard.total_operations'),
            value=f"{total_ops:,}",
            delta=f"{avg_daily_ops:,.0f}{i18n.get('common.per_day')}",
            help=f"Total sur {len(period_data.daily_data)} jours"
        )
    with col2:
        avg_duration = period_data.daily_data['duree_moyenne'].mean()
        prev_duration = avg_duration * 1.05
        delta_pct = ((prev_duration - avg_duration) / prev_duration * 100) if prev_duration > 0 else 0
        st.metric(
            label=i18n.get('dashboard.avg_duration'),
            value=f"{avg_duration:.1f} {i18n.get('common.minutes')}",
            delta=f"-{delta_pct:.1f}%" if delta_pct > 0 else None,
            help="Moyenne pondérée par le nombre d'opérations"
        )
    with col3:
        total_errors = period_data.daily_data['erreurs'].sum()
        total_ops = period_data.daily_data['nb_operations'].sum()
        error_rate = (total_errors / total_ops * 100) if total_ops > 0 else 0
        st.metric(
            label=i18n.get('dashboard.error_rate'),
            value=f"{error_rate:.1f}%",
            delta=f"{total_errors} {i18n.get('common.errors')}",
            delta_color="normal" if error_rate < 2.5 else "inverse",
            help=f"Total de {total_errors} erreurs sur la période"
        )
    with col4:
        st.metric(
            label=i18n.get('dashboard.total_gains'),
            value=f"${financial_metrics.period_gains:,.0f}",
            delta=f"${financial_metrics.daily_gains:,.0f}{i18n.get('common.per_day')}",
            help=f"Gains estimés sur {len(period_data.daily_data)} jours"
        )
    st.markdown("---")


def render_performance_analysis(period_data, chart_gen):
    st.markdown(f'<h2 class="section-title">{i18n.get("dashboard.performance_analysis")}</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### {i18n.get('dashboard.daily_activity')}")
        if not period_data.daily_data.empty:
            fig1 = chart_gen.create_daily_activity_chart(period_data.daily_data, period_data.period_name)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            UIComponents.render_alert(i18n.get('dashboard.no_data'), "warning")
    with col2:
        st.markdown(f"#### {i18n.get('dashboard.hourly_distribution')}")
        if not period_data.hourly_data.empty:
            fig2 = chart_gen.create_hourly_distribution_chart(period_data.hourly_data)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            UIComponents.render_alert(i18n.get('dashboard.no_hourly_data'), "warning")


def render_equipment_performance(period_data, chart_gen):
    st.markdown(f'<h2 class="section-title">{i18n.get("dashboard.equipment_performance")}</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if not period_data.engins_data.empty:
            fig3 = chart_gen.create_engins_performance_chart(period_data.engins_data)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            UIComponents.render_alert(i18n.get('dashboard.no_data'), "warning")
    with col2:
        st.markdown(f"#### {i18n.get('dashboard.equipment_to_monitor')}")
        if not period_data.engins_data.empty:
            period_data.engins_data['taux_erreur'] = (period_data.engins_data['erreurs'] / period_data.engins_data['total_operations'] * 100)
            problem_engins = period_data.engins_data[period_data.engins_data['taux_erreur'] > 1.5]
            if not problem_engins.empty:
                for _, engin in problem_engins.iterrows():
                    error_class = "badge-danger" if engin['taux_erreur'] > 3 else "badge-warning"
                    st.markdown(f"""
                    <div class="metric-card">
                        <strong>{engin['engin']}</strong><br>
                        <span class="{error_class}">{engin['erreurs']} {i18n.get('common.errors')} ({engin['taux_erreur']:.1f}%)</span><br>
                        <small>{engin['total_operations']} {i18n.get('common.operations')}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                UIComponents.render_alert(i18n.get('dashboard.all_equipment_ok'), "success")
        else:
            UIComponents.render_alert(i18n.get('dashboard.no_problem_equipment'), "info")


def render_realtime_map(map_gen):
    st.markdown(f'<h2 class="section-title">{i18n.get("dashboard.realtime_map")}</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        port_map = map_gen.create_realtime_map()
        st_folium(port_map, width=800, height=500)
    with col2:
        st.markdown(f"#### {i18n.get('dashboard.map_filters')}")
        st.multiselect(
            i18n.get('dashboard.equipment_types'),
            [i18n.get('equipment_types.tractor'), i18n.get('equipment_types.forklift'), i18n.get('equipment_types.crane'), i18n.get('equipment_types.truck')],
            default=[i18n.get('equipment_types.tractor'), i18n.get('equipment_types.forklift')],
            key="map_engins_filter"
        )
        st.slider(i18n.get('dashboard.refresh_map'), 5, 60, 30, key="map_refresh_rate")
        st.checkbox(i18n.get('dashboard.show_routes'), value=True, key="show_routes")
        st.checkbox(i18n.get('dashboard.show_congestion'), value=True, key="show_congestion")
        st.checkbox(i18n.get('dashboard.show_alerts_on_map'), value=True, key="show_alerts_on_map")
        
        st.markdown("---")
        st.markdown(f"#### {i18n.get('dashboard.legend')}")
        st.markdown(i18n.get('dashboard.legend_main_quay'))
        st.markdown(i18n.get('dashboard.legend_road_quay'))
        st.markdown(i18n.get('dashboard.legend_storage'))
        st.markdown(i18n.get('dashboard.legend_customs'))
        st.markdown(i18n.get('dashboard.legend_maintenance'))


def render_alerts_and_activity(period_data):
    st.markdown(f'<h2 class="section-title">{i18n.get("dashboard.alerts")}</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### {i18n.get('dashboard.active_alerts')}")
        alerts = []
        if not period_data.daily_data.empty and len(period_data.daily_data) > 1:
            latest_day = period_data.daily_data.iloc[-1]
            avg_operations = period_data.daily_data['nb_operations'].mean()
            if latest_day['nb_operations'] > avg_operations * 1.3:
                alerts.append(i18n.get('alerts.high_volume'))
            if latest_day['erreurs'] > 0 and (latest_day['erreurs'] / latest_day['nb_operations']) > 0.03:
                alerts.append(i18n.get('alerts.critical_error_rate'))
        if not period_data.engins_data.empty:
            period_data.engins_data['taux_erreur'] = (period_data.engins_data['erreurs'] / period_data.engins_data['total_operations'] * 100)
            engins_problematiques = period_data.engins_data[period_data.engins_data['taux_erreur'] > 2.0]
            for _, engin in engins_problematiques.iterrows():
                alerts.append(i18n.get('alerts.maintenance_needed', equip=engin['engin'], rate=engin['taux_erreur']))
        if alerts:
            for alert in alerts:
                if "❌" in alert or "⚠️" in alert:
                    UIComponents.render_alert(alert, "danger")
                else:
                    UIComponents.render_alert(alert, "warning")
        else:
            UIComponents.render_alert(i18n.get('dashboard.no_alerts'), "success")
    
    with col2:
        st.markdown(f"#### {i18n.get('dashboard.recent_ops')}")
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
                *{row['zone']}* | {row['engin']} | {row['duree_minutes']:.0f} {i18n.get('common.minutes')}
                """)
        else:
            UIComponents.render_alert(i18n.get('dashboard.no_recent_ops'), "info")


def render_recommendations(period_data):
    st.markdown(f'<h2 class="section-title">{i18n.get("dashboard.recommendations")}</h2>', unsafe_allow_html=True)
    
    recommendations = []
    if not period_data.recent_ops.empty and 'urgence' in period_data.recent_ops.columns:
        zone_urgences = period_data.recent_ops.groupby('zone')['urgence'].sum()
        if len(zone_urgences) > 0 and zone_urgences.max() > 0:
            zone_probleme = zone_urgences.idxmax()
            nb_urgences = int(zone_urgences.max())
            recommendations.append(i18n.get('recommendations.optimize_zone', zone=zone_probleme, urgences=nb_urgences))
    if not period_data.engins_data.empty:
        period_data.engins_data['taux_erreur'] = (period_data.engins_data['erreurs'] / period_data.engins_data['total_operations'] * 100)
        if not period_data.engins_data.empty:
            engin_probleme = period_data.engins_data.loc[period_data.engins_data['taux_erreur'].idxmax()]
            if engin_probleme['taux_erreur'] > 2.0:
                recommendations.append(i18n.get('recommendations.maintenance', equip=engin_probleme['engin'], rate=engin_probleme['taux_erreur']))
    if not period_data.hourly_data.empty:
        heure_pic = period_data.hourly_data.loc[period_data.hourly_data['nb_operations'].idxmax(), 'heure']
        ops_pic = period_data.hourly_data['nb_operations'].max()
        heure_creux = period_data.hourly_data.loc[period_data.hourly_data['nb_operations'].idxmin(), 'heure']
        ops_creux = period_data.hourly_data['nb_operations'].min()
        if ops_pic > ops_creux * 1.5:
            recommendations.append(i18n.get('recommendations.load_balancing', peak=heure_pic, offpeak=heure_creux))
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
    else:
        UIComponents.render_alert(i18n.get('dashboard.analyzing'), "info")


def render_financial_module(financial_metrics, period_data):
    st.markdown(f'<h2 class="section-title">{i18n.get("financial.title")}</h2>', unsafe_allow_html=True)

    period_summary = financial_metrics.period_summary
    st.markdown(f"#### {i18n.get('financial.analysis_for', period=period_data.period_name.upper())}")
    UIComponents.render_period_summary(period_summary)

    st.markdown(f"""
    <div style="background: {COLORS['info']}; color: white; padding: 10px 15px; border-radius: 10px; margin: 10px 0;">
        {i18n.get('financial.sync_badge')}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"#### {i18n.get('financial.gains_title')}")

    fin_row1_col1, fin_row1_col2, fin_row1_col3, fin_row1_col4 = st.columns(4)

    with fin_row1_col1:
        st.markdown(f"""
        <div class="commission-card">
            <h3 style="color: white; margin: 0; font-size: 2rem;">${financial_metrics.daily_gains:,.0f}</h3>
            <p style="margin: 0; opacity: 0.9;">{i18n.get('financial.daily_gains')}</p>
            <small>{i18n.get('financial.based_on', days=period_summary['total_days'])}</small>
        </div>
        """, unsafe_allow_html=True)

    with fin_row1_col2:
        st.markdown(f"""
        <div class="gain-card">
            <h3 style="color: white; margin: 0; font-size: 2rem;">${financial_metrics.monthly_projection:,.0f}</h3>
            <p style="margin: 0; opacity: 0.9;">{i18n.get('financial.monthly_projection')}</p>
            <small>{i18n.get('financial.based_on', days=st.session_state.working_days)}</small>
        </div>
        """, unsafe_allow_html=True)

    with fin_row1_col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['primary']} 0%, #1E40AF 100%); 
                    color: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
            <h3 style="color: white; margin: 0; font-size: 2rem;">${financial_metrics.your_commission_today:,.0f}</h3>
            <p style="margin: 0; opacity: 0.9;">{i18n.get('financial.daily_commission')}</p>
            <small>{i18n.get('financial.fixed_plus', rate=st.session_state.commission_rate*100)}</small>
        </div>
        """, unsafe_allow_html=True)

    with fin_row1_col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); 
                    color: white; padding: 25px; border-radius: 15px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.15);">
            <h3 style="color: white; margin: 0; font-size: 2rem;">${financial_metrics.your_commission_monthly:,.0f}</h3>
            <p style="opacity: 0.9; font-size: 1rem;">{i18n.get('financial.monthly_income')}</p>
            <small>{i18n.get('financial.based_on_performance', period=period_data.period_name)}</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col_graphique, col_resume = st.columns([3, 2])

    with col_graphique:
        st.markdown(f"{i18n.get('financial.pie_chart_title')}")
        chart_gen = ChartGenerator()
        fig_fin = chart_gen.create_financial_pie_chart(financial_metrics.breakdown)
        st.plotly_chart(fig_fin, use_container_width=True)

    with col_resume:
        st.markdown(f" {i18n.get('financial.contract_summary')}")

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
                <span style="font-weight: 600; color: #4B5563;">{i18n.get('financial.monthly_fixed')}</span>
                <span style="font-weight: 700; color: #1E3A8A;">${st.session_state.monthly_fixed:,.0f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #E5E7EB; padding: 8px 0;">
                <span style="font-weight: 600; color: #4B5563;">{i18n.get('financial.commission_rate')}</span>
                <span style="font-weight: 700; color: #10B981;">{st.session_state.commission_rate*100}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #E5E7EB; padding: 8px 0;">
                <span style="font-weight: 600; color: #4B5563;">{i18n.get('financial.working_days')}</span>
                <span style="font-weight: 700; color: #F59E0B;">{st.session_state.working_days} {i18n.get('common.days')}</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #E5E7EB; padding: 8px 0;">
                <span style="font-weight: 600; color: #4B5563;">{i18n.get('financial.hourly_cost')}</span>
                <span style="font-weight: 700; color: #8B5CF6;">${st.session_state.hourly_cost}/h</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                <span style="font-weight: 600; color: #4B5563;">{i18n.get('financial.error_cost')}</span>
                <span style="font-weight: 700; color: #EF4444;">${st.session_state.error_cost}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"#### {i18n.get('financial.verification')}")
        st.info(f"""
        {i18n.get('financial.period_analyzed')}  
        {i18n.get('financial.from', date=period_summary['start_date'])}  
        {i18n.get('financial.to', date=period_summary['end_date'])}  
        {i18n.get('financial.days_count', days=period_summary['total_days'])}  
        {i18n.get('financial.data_hash', hash=PUBLIC_DATA_HASH)}
        """)

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button(i18n.get('financial.export_report'), type="secondary", use_container_width=True):
                if generate_excel_report is not None:
                    excel_data = generate_excel_report(period_data, financial_metrics)
                    st.download_button(
                        label="📥 Télécharger le rapport",
                        data=excel_data,
                        file_name=f"rapport_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_excel"
                    )
                
                    

        with col_btn2:
            if st.button(i18n.get('financial.refresh'), type="primary", use_container_width=True):
                st.rerun()

    st.markdown("---")

    st.markdown(f" {i18n.get('financial.details_expander')}")

    with st.expander(i18n.get('financial.show_details'), expanded=True):
        st.markdown(f" {i18n.get('financial.period_analyzed')}")
        st.markdown(f"{i18n.get('financial.from', date=period_summary['start_date'])}")
        st.markdown(f"{i18n.get('financial.to', date=period_summary['end_date'])}")
        st.markdown(f"{i18n.get('financial.days_count', days=period_summary['total_days'])}")
        st.markdown(f"{i18n.get('financial.data_hash', hash=PUBLIC_DATA_HASH)}")
        st.divider()

        st.markdown(f" {i18n.get('financial.gain_time')}")

        baseline_duration = st.session_state.baseline_duration
        avg_duration = period_summary['avg_duration']
        hourly_cost = st.session_state.hourly_cost
        total_ops = period_summary['total_operations']

        time_saved_minutes = max(0, baseline_duration - avg_duration)
        time_saved_hours = time_saved_minutes / 60
        gain_per_op = time_saved_hours * hourly_cost
        total_time_gain = gain_per_op * total_ops

        st.markdown(f"""
        {i18n.get('financial.params')}
        - {i18n.get('financial.baseline_duration')}: {baseline_duration} {i18n.get('common.minutes')}
        - {i18n.get('financial.avg_duration')}: {avg_duration:.1f} {i18n.get('common.minutes')}
        - {i18n.get('financial.hourly_cost')}: ${hourly_cost}$/h
        - {i18n.get('financial.total_operations')}: {total_ops:,} {i18n.get('common.operations')}

        {i18n.get('financial.calculation')}
        - {i18n.get('financial.savings_per_op')}: {time_saved_minutes:.1f} {i18n.get('common.minutes')} = {time_saved_hours:.3f} {i18n.get('common.hours')}
        - {i18n.get('financial.gain_per_op')}: {time_saved_hours:.3f} h × ${hourly_cost}$/h = ${gain_per_op:.2f}$
        - {i18n.get('financial.total_gain')}: {total_ops:,} {i18n.get('common.operations')} × ${gain_per_op:.2f} = ${financial_metrics.breakdown.get('time_gain_period', 0):,.2f}$
        - {i18n.get('financial.daily_avg')}: ${financial_metrics.breakdown.get('time_gain', 0):,.2f}{i18n.get('common.per_day')}$
        """)
        st.divider()

        st.markdown(f" {i18n.get('financial.gain_errors')}")

        baseline_error_rate = st.session_state.baseline_error_rate * 100
        current_error_rate = period_summary['error_rate']
        error_cost = st.session_state.error_cost

        errors_avoided = max(0, (baseline_error_rate - current_error_rate) / 100 * total_ops)
        total_error_gain = errors_avoided * error_cost

        st.markdown(f"""
        {i18n.get('financial.params')}
        - {i18n.get('financial.baseline_error_rate')}: {baseline_error_rate:.1f}%
        - {i18n.get('financial.current_error_rate')}: {current_error_rate:.1f}%
        - {i18n.get('financial.error_cost')}: ${error_cost}$
        - {i18n.get('financial.total_operations')}: {total_ops:,} {i18n.get('common.operations')}

        {i18n.get('financial.calculation')}
        - {i18n.get('financial.errors_avoided')}: ({baseline_error_rate:.1f}% - {current_error_rate:.1f}%) × {total_ops:,} = {errors_avoided:.1f} {i18n.get('common.errors')}
        - {i18n.get('financial.total_gain')}: {errors_avoided:.1f} {i18n.get('common.errors')} × ${error_cost} = ${financial_metrics.breakdown.get('error_gain_period', 0):,.2f}$
        - {i18n.get('financial.daily_avg')}: ${financial_metrics.breakdown.get('error_gain', 0):,.2f}{i18n.get('common.per_day')}$
        """)
        st.divider()

        st.markdown(f"{i18n.get('financial.gain_maintenance')}")

        maintenance_alerts = financial_metrics.metrics.get('maintenance_alerts', 0)
        maintenance_cost = 500
        maintenance_gain_period = financial_metrics.breakdown.get('maintenance_gain_period', 0)

        st.markdown(f"""
        {i18n.get('financial.params')}
        - {i18n.get('financial.maintenance_alerts')}: {maintenance_alerts} {i18n.get('common.alerts')}
        - {i18n.get('financial.maintenance_cost_per_alert')}: ${maintenance_cost}$
        - {i18n.get('financial.maintenance_gain_total')}: ${maintenance_gain_period:,.2f}$

        {i18n.get('financial.calculation')}
        - {i18n.get('financial.total_gain')}: {maintenance_alerts} × ${maintenance_cost} = ${maintenance_gain_period:,.2f}$
        - {i18n.get('financial.daily_avg')}: ${financial_metrics.breakdown.get('maintenance_gain', 0):,.2f}{i18n.get('common.per_day')}$
        """)
        st.divider()

        st.markdown(f" {i18n.get('financial.gain_fuel')}")

        trucks_per_day = min(500, period_summary['avg_daily_operations'] * 0.3)
        fuel_saving = 1.5

        daily_fuel_gain = trucks_per_day * fuel_saving
        total_fuel_gain = daily_fuel_gain * period_summary['total_days']

        st.markdown(f"""
        {i18n.get('financial.params')}
        - {i18n.get('financial.trucks_per_day')}: {trucks_per_day:.0f} ${i18n.get('common.trucks')}$
        - {i18n.get('financial.fuel_saving_per_truck')}: ${fuel_saving}{i18n.get('common.per_day')}
        - {i18n.get('financial.days_analyzed')}: {period_summary['total_days']} {i18n.get('common.days')}

        {i18n.get('financial.calculation')}
        - {i18n.get('financial.daily_fuel_gain')}: {trucks_per_day:.0f} × ${fuel_saving} = ${daily_fuel_gain:.2f}{i18n.get('common.per_day')}$
        - {i18n.get('financial.total_fuel_gain')}: ${daily_fuel_gain:.2f}{i18n.get('common.per_day')} × {period_summary['total_days']} {i18n.get('common.days')} = ${financial_metrics.breakdown.get('fuel_gain_period', 0):,.2f}$
        """)
        st.divider()
               # Synthèse financière
        st.markdown("---")
        st.markdown(f" {i18n.get('financial.summary', '📊 SYNTHÈSE FINANCIÈRE')}")

        # Gains totaux sur la période
        st.markdown(f"{i18n.get('financial.total_gains_period', 'Gains totaux sur la période :')}")
        st.markdown(f"- {i18n.get('financial.gain_time', '1. GAIN TEMPS')}: ${financial_metrics.breakdown.get('time_gain_period', 0):,.2f}")
        st.markdown(f"- {i18n.get('financial.gain_errors', '2. GAIN ERREURS')}: ${financial_metrics.breakdown.get('error_gain_period', 0):,.2f}")
        st.markdown(f"- {i18n.get('financial.gain_maintenance', '3. GAIN MAINTENANCE')}: ${financial_metrics.breakdown.get('maintenance_gain_period', 0):,.2f}")
        st.markdown(f"- {i18n.get('financial.gain_fuel', '4. GAIN CARBURANT')}: ${financial_metrics.breakdown.get('fuel_gain_period', 0):,.2f}")

        st.markdown(f"{i18n.get('financial.total_period_gains', 'Total des gains sur la période')}:${financial_metrics.period_gains:,.2f}")

        # Moyennes journalières
        st.markdown(f"{i18n.get('financial.daily_averages', 'Moyennes journalières :')}")
        st.markdown(f"- {i18n.get('financial.gain_time', '1. GAIN TEMPS')}: ${financial_metrics.breakdown.get('time_gain', 0):,.2f}{i18n.get('common.per_day', '/jour')}")
        st.markdown(f"- {i18n.get('financial.gain_errors', '2. GAIN ERREURS')}: ${financial_metrics.breakdown.get('error_gain', 0):,.2f}{i18n.get('common.per_day', '/jour')}")
        st.markdown(f"- {i18n.get('financial.gain_maintenance', '3. GAIN MAINTENANCE')}: ${financial_metrics.breakdown.get('maintenance_gain', 0):,.2f}{i18n.get('common.per_day', '/jour')}")
        st.markdown(f"- {i18n.get('financial.gain_fuel', '4. GAIN CARBURANT')}: ${financial_metrics.breakdown.get('fuel_gain', 0):,.2f}{i18n.get('common.per_day', '/jour')}")

        st.markdown(f"{i18n.get('financial.total_daily_gains', 'Total des gains journaliers')}: ${financial_metrics.daily_gains:,.2f}{i18n.get('common.per_day', '/jour')}")

        st.markdown(f"{i18n.get('financial.monthly_projection_detail', days=st.session_state.working_days)}")
        st.markdown(f"- ${financial_metrics.daily_gains:,.2f}{i18n.get('common.per_day', '/jour')} × {st.session_state.working_days} {i18n.get('common.days', 'jours')} = ${financial_metrics.monthly_projection:,.2f}")

        st.markdown(f"{i18n.get('financial.your_commission_detail', 'Votre commission :')}")
        st.markdown(f"- {i18n.get('financial.fixed_monthly', 'Fixe mensuel')}: ${st.session_state.monthly_fixed:,.2f}")
        st.markdown(f"- {i18n.get('financial.variable', rate=st.session_state.commission_rate*100)}: ${financial_metrics.monthly_projection * st.session_state.commission_rate:,.2f}")
        st.markdown(f"- {i18n.get('financial.total_commission', 'Commission totale')}: ${financial_metrics.your_commission_monthly:,.2f}")


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
def render_sector_metrics(metrics, sector_name):
    st.markdown(f" Métriques opérationnelles - {sector_name.capitalize()}")
    cols = st.columns(len(metrics))
    for i, (key, value) in enumerate(metrics.items()):
        with cols[i % len(cols)]:
            if isinstance(value, float):
                st.metric(key.replace('_', ' ').title(), f"{value:.2f}")
            else:
                st.metric(key.replace('_', ' ').title(), value)

if __name__ == "__main__":
    main()