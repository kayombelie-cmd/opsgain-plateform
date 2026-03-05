from typing import Any
import requests
import pandas as pd
from .base import BaseConnector

class APIConnector(BaseConnector):
    """Connecteur pour API REST."""

    def read(self, url: str, method: str = 'GET', params: dict = None, headers: dict = None, json_path: str = None, **kwargs) -> pd.DataFrame:
        try:
            response = requests.request(method, url, params=params, headers=headers, **kwargs)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and json_path:
                for key in json_path.split('.'):
                    data = data[key]
                df = pd.DataFrame(data)
            else:
                raise ValueError("Format de réponse API non supporté.")
            self.validate(df)
            return df
        except Exception as e:
            raise RuntimeError(f"Erreur d'appel API : {e}")

    def write(self, data: pd.DataFrame, destination: Any, **kwargs):
        raise NotImplementedError("L'écriture via API n'est pas implémentée.")