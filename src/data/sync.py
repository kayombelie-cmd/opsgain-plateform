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
            # Récupération des paramètres d'URL - NOUVELLE API STREAMLIT
            query_params = st.query_params
            
            # Si aucun paramètre, retourner None
            if not query_params:
                return None
            
            # Convertir en dict simple
            params = {}
            for key in query_params:
                value = query_params[key]
                if isinstance(value, list) and len(value) > 0:
                    params[key] = value[0]
                elif value:
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
            
            # Générer les données synchronisées
            return self.generator.create_period_data(
                start_date, end_date, use_current_time=False
            )
            
        except Exception as e:
            st.error(f"Erreur lors du chargement des paramètres URL: {e}")
            return None