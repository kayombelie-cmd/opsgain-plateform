from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, List

class BaseSector(ABC):
    """Classe de base pour un secteur d'activité."""

    @abstractmethod
    def transform(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Transforme les données brutes en DataFrame normalisé pour le secteur.
        """
        pass

    @abstractmethod
    def calculate_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule les métriques opérationnelles clés à partir des données normalisées.
        Retourne un dictionnaire de métriques (ex: total_operations, avg_duration, error_rate, etc.)
        """
        pass

    @abstractmethod
    def calculate_gains(self, data: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule les gains financiers à partir des données et des paramètres de contrat.
        Retourne un dictionnaire avec daily_gains, period_gains, breakdown, etc.
        """
        pass

    @abstractmethod
    def get_visualizations(self, data: pd.DataFrame) -> List[Any]:
        """
        Retourne une liste de figures Plotly (ou autres) à afficher dans le dashboard.
        """
        pass

    @abstractmethod
    def generate_sample_data(self, days: int = 30) -> pd.DataFrame:
        """
        Génère des données simulées pour le secteur (pour les démos).
        """
        pass