"""
Gestion de la synchronisation des données et partage.
"""
import json
import urllib.parse
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
import streamlit as st

from ..config import PUBLIC_DATA_HASH, DEFAULT_BASE_URL
from ..utils.logger import log_access
from .generator import DataGenerator
from .models import PeriodData


class DataSynchronizer:
    """Gère la synchronisation et le partage des données."""
    
    def __init__(self):
        self.generator = DataGenerator()
    
    def load_period_data(self) -> PeriodData:
        """
        Charge les données selon le mode (URL ou sidebar).
        
        Returns:
            PeriodData: Données de la période
        """
        # Essayer de charger depuis l'URL
        url_data = self._load_from_url()
        if url_data:
            return url_data
        
        # Sinon charger depuis la sidebar
        return self._load_from_sidebar()
    
    def _load_from_url(self) -> Optional[PeriodData]:
        """Charge les données depuis les paramètres d'URL."""
        try:
            # Récupération des paramètres d'URL
            query_params = st.experimental_get_query_params()
            
            # Convertir en dict simple
            params = {}
            for key, value in query_params.items():
                if isinstance(value, list) and len(value) > 0:
                    params[key] = value[0]
                else:
                    params[key] = value
            
            # Vérifier si c'est un lien synchronisé
            if params.get('sync') != 'true':
                return None
            
            if 'period' not in params:
                return None
            
            # Parser les données de période
            period_data = json.loads(params['period'])
            start_date = datetime.strptime(period_data['start'], '%Y-%m-%d')
            end_date = datetime.strptime(period_data['end'], '%Y-%m-%d')
            data_hash = params.get('data_hash', PUBLIC_DATA_HASH)
            link_id = params.get('ref', 'unknown')
            
            # Log de l'accès
            log_access(link_id, period_data.get('name', 'Unknown'))
            
            # Sauvegarder dans session_state
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date
            st.session_state.selected_period = period_data.get('name', 
                f"{start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}")
            
            # Générer les données
            return self.generator.create_period_data(
                start_date, end_date, use_current_time=False
            )
            
        except Exception as e:
            st.error(f"Erreur lors du chargement des paramètres URL: {e}")
            return None
    
    def _load_from_sidebar(self) -> PeriodData:
        """Charge les données basées sur la configuration de la sidebar."""
        default_end = datetime.now()
        
        # Récupérer la période sélectionnée
        selected_period = st.session_state.get('selected_period', '30 derniers jours')
        start_date = st.session_state.get('start_date', default_end - timedelta(days=30))
        end_date = st.session_state.get('end_date', default_end)
        
        # Générer les données
        return self.generator.create_period_data(
            start_date, end_date, use_current_time=True
        )
    
    def generate_shareable_link(
        self, 
        period_name: str, 
        start_date: datetime, 
        end_date: datetime,
        base_url: str = DEFAULT_BASE_URL
    ) -> Tuple[str, str]:
        """Génère un lien de partage synchronisé."""
        link_id = str(uuid.uuid4())[:8]
        
        period_data = {
            'name': period_name,
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
        
        params = {
            'sync': 'true',
            'period': json.dumps(period_data),
            'data_hash': PUBLIC_DATA_HASH,
            'ref': link_id,
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
        }
        
        params_str = urllib.parse.urlencode(params)
        return f"{base_url}/?{params_str}", link_id