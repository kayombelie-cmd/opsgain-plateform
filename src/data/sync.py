"""
Gestion de la synchronisation des données et partage.
"""
import json
import urllib.parse
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from pathlib import Path

import pandas as pd
import streamlit as st

from src.connectors.factory import ConnectorFactory
from src.sectors import SectorFactory
from ..config import PUBLIC_DATA_HASH, DEFAULT_BASE_URL
from ..utils.logger import log_access
from .generator import DataGenerator
from .models import PeriodData


class DataSynchronizer:
    """
    Gère la synchronisation et le partage des données.
    
    Supporte trois modes de fonctionnement :
    - "mock" : génération de données simulées (via DataGenerator)
    - "file" : chargement depuis des fichiers locaux (ancien FileDataRepository)
    - "sector" : chargement via un couple secteur/connecteur (nouvelle architecture)
    """
    
    def __init__(
        self,
        use_real_data: bool = False,
        sector_name: Optional[str] = None,
        connector_type: Optional[str] = None,
        connector_config: Optional[dict] = None
    ):
        """
        Initialise le synchroniseur.

        Args:
            use_real_data: Si True, utilise des données réelles (fichiers ou secteur/connecteur).
                          Si False, utilise le générateur de données mockées.
            sector_name: Nom du secteur (ex: "hotel", "restaurant"). Requis si mode "sector".
            connector_type: Type de connecteur (ex: "csv", "api"). Requis si mode "sector".
            connector_config: Configuration spécifique au connecteur.
        """
        self.generator = DataGenerator()
        self.sector_name = sector_name
        self.connector_type = connector_type
        self.connector_config = connector_config or {}

        # Détermination du mode de données
        if not use_real_data:
            self.data_mode = "mock"
        elif sector_name and connector_type:
            self.data_mode = "sector"
            # Pré-instanciation du secteur et du connecteur pour un usage ultérieur
            self.sector = SectorFactory.get_sector(sector_name)
            self.connector = ConnectorFactory.get_connector(connector_type, **self.connector_config)
        else:
            self.data_mode = "file"
            from .repository import FileDataRepository
            self.data_repo = FileDataRepository(Path('data/real'))

    def load_period_data(self) -> PeriodData:
        """
        Charge les données selon le mode (URL ou sidebar).

        Returns:
            PeriodData: Données de la période.
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
            query_params = st.query_params
            if not query_params:
                return None

            # Conversion en dictionnaire simple
            params = {}
            for key in query_params:
                value = query_params[key]
                if isinstance(value, list) and len(value) > 0:
                    params[key] = value[0]
                elif value:
                    params[key] = value

            # Vérification de la synchronisation
            if params.get('sync') != 'true' or 'period' not in params:
                return None

            # Parsing des données de période
            period_data = json.loads(params['period'])
            start_date = datetime.strptime(period_data['start'], '%Y-%m-%d')
            end_date = datetime.strptime(period_data['end'], '%Y-%m-%d')
            link_id = params.get('ref', 'unknown')

            # Log d'accès
            log_access(link_id, period_data.get('name', 'Unknown'))

            # Sauvegarde en session
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date
            st.session_state.selected_period = period_data.get(
                'name',
                f"{start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"
            )

            # Chargement des données selon le mode
            if self.data_mode == "sector":
                return self._load_from_sector(start_date, end_date)
            elif self.data_mode == "file":
                return self.data_repo.get_period_data(start_date, end_date)
            else:  # mock
                return self.generator.create_period_data(
                    start_date, end_date, use_current_time=False
                )

        except Exception as e:
            # En production, on ignore silencieusement l'erreur
            return None

    def _load_from_sidebar(self) -> PeriodData:
        """Charge les données basées sur la configuration de la sidebar."""
        # Valeurs par défaut robustes
        default_end = datetime.now()
        default_start = default_end - timedelta(days=30)

        # Récupération depuis session_state avec vérifications
        start_date = default_start
        end_date = default_end

        if 'start_date' in st.session_state:
            session_start = st.session_state.start_date
            if isinstance(session_start, datetime):
                start_date = session_start
            elif isinstance(session_start, str):
                try:
                    start_date = datetime.strptime(session_start, '%Y-%m-%d')
                except ValueError:
                    start_date = default_start

        if 'end_date' in st.session_state:
            session_end = st.session_state.end_date
            if isinstance(session_end, datetime):
                end_date = session_end
            elif isinstance(session_end, str):
                try:
                    end_date = datetime.strptime(session_end, '%Y-%m-%d')
                except ValueError:
                    end_date = default_end

        # S'assurer que start_date <= end_date
        if start_date > end_date:
            start_date = end_date - timedelta(days=30)

        # Chargement selon le mode
        if self.data_mode == "sector":
            return self._load_from_sector(start_date, end_date)
        elif self.data_mode == "file":
            return self.data_repo.get_period_data(start_date, end_date)
        else:  # mock
            return self.generator.create_period_data(
                start_date, end_date, use_current_time=True
            )

    def _load_from_sector(self, start_date: datetime, end_date: datetime) -> PeriodData:
        """
        Charge les données via le secteur et le connecteur pour une période donnée.
        
        Args:
            start_date: Date de début.
            end_date: Date de fin.
        
        Returns:
            PeriodData: Données transformées pour la période.
        """
        # Construction de la source : le connecteur doit savoir interpréter ce dictionnaire
        source = {
            'start_date': start_date,
            'end_date': end_date
        }
        # Lecture brute via le connecteur
        raw_data = self.connector.read(source, **self.connector_config)
        # Transformation selon le secteur
        normalized_data = self.sector.transform(raw_data)
        # Conversion en objet PeriodData
        return self._df_to_period_data(normalized_data, start_date, end_date)

    def _df_to_period_data(self, df: pd.DataFrame, start_date: datetime, end_date: datetime) -> PeriodData:
        """
        Convertit un DataFrame (sortie du secteur) en objet PeriodData.
        Cette méthode est à adapter selon la structure réelle de PeriodData.
        Par défaut, on stocke le DataFrame dans un attribut 'data'.
        
        Args:
            df: DataFrame contenant les données transformées.
            start_date: Date de début.
            end_date: Date de fin.
        
        Returns:
            PeriodData: Instance peuplée.
        """
        # NOTE: La structure de PeriodData n'étant pas connue, nous supposons
        # qu'elle accepte au minimum start_date, end_date, et un champ 'data'.
        # Vous devrez ajuster cette méthode en fonction de la vraie définition.
        # Si PeriodData attend un DataFrame, on peut passer df directement.
        # Sinon, on le convertit en dictionnaire.
        if hasattr(PeriodData, 'data'):
            # Supposons que PeriodData a un attribut 'data' qui peut être un dict
            return PeriodData(
                start_date=start_date,
                end_date=end_date,
                data=df.to_dict(orient='records')
            )
        else:
            # Sinon, on suppose que le constructeur accepte le DataFrame
            return PeriodData(
                start_date=start_date,
                end_date=end_date,
                df=df  # ou tout autre nom d'attribut
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