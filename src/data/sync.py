"""
Gestion de la synchronisation des données et partage.
"""
import json
import urllib.parse
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from pathlib import Path  # Ajout pour le chemin du repository

import streamlit as st

from ..config import PUBLIC_DATA_HASH, DEFAULT_BASE_URL
from ..utils.logger import log_access
from .generator import DataGenerator
from .models import PeriodData


class DataSynchronizer:
    """Gère la synchronisation et le partage des données."""
    
    def __init__(self, use_real_data: bool = False):
        """
        Initialise le synchroniseur.
        
        Args:
            use_real_data: Si True, utilise les données réelles depuis le repository.
                          Sinon, utilise le générateur de données mockées.
        """
        self.generator = DataGenerator()  # toujours disponible pour le mode mock
        if use_real_data:
            from .repository import FileDataRepository
            self.data_repo = FileDataRepository(Path('data/real'))
        else:
            self.data_repo = None
    
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
            link_id = params.get('ref', 'unknown')
            
            # Log de l'accès
            log_access(link_id, period_data.get('name', 'Unknown'))
            
            # Sauvegarder dans session_state
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date
            st.session_state.selected_period = period_data.get('name', 
                f"{start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}")
            
            # Générer les données synchronisées (réelles ou mock selon le mode)
            if self.data_repo:
                return self.data_repo.get_period_data(start_date, end_date)
            else:
                return self.generator.create_period_data(
                    start_date, end_date, use_current_time=False
                )
            
        except Exception as e:
            # Ne pas afficher l'erreur en production
            return None
    
    def _load_from_sidebar(self) -> PeriodData:
        """Charge les données basées sur la configuration de la sidebar."""
        # Valeurs par défaut robustes
        default_end = datetime.now()
        default_start = default_end - timedelta(days=30)
        
        # Récupérer les valeurs avec vérification de type
        start_date = default_start
        end_date = default_end
        
        # Vérifier si start_date existe et est du bon type
        if 'start_date' in st.session_state:
            session_start = st.session_state.start_date
            if isinstance(session_start, datetime):
                start_date = session_start
            elif isinstance(session_start, str):
                try:
                    start_date = datetime.strptime(session_start, '%Y-%m-%d')
                except:
                    start_date = default_start
        
        # Vérifier si end_date existe et est du bon type
        if 'end_date' in st.session_state:
            session_end = st.session_state.end_date
            if isinstance(session_end, datetime):
                end_date = session_end
            elif isinstance(session_end, str):
                try:
                    end_date = datetime.strptime(session_end, '%Y-%m-%d')
                except:
                    end_date = default_end
        
        # S'assurer que start_date <= end_date
        if start_date > end_date:
            start_date = end_date - timedelta(days=30)
        
        # Générer les données (réelles ou mock selon le mode)
        if self.data_repo:
            return self.data_repo.get_period_data(start_date, end_date)
        else:
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