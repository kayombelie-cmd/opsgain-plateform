from abc import ABC, abstractmethod
from typing import Any, Optional
import pandas as pd

class BaseConnector(ABC):
    """Interface commune pour tous les connecteurs de données."""

    @abstractmethod
    def read(self, source: Any, **kwargs) -> pd.DataFrame:
        """
        Lit les données depuis une source et retourne un DataFrame pandas.
        """
        pass

    @abstractmethod
    def write(self, data: pd.DataFrame, destination: Any, **kwargs) -> None:
        """
        Écrit des données vers une destination (optionnel).
        """
        pass

    def validate(self, data: pd.DataFrame) -> bool:
        if data.empty:
            raise ValueError("Les données sont vides.")
        return True