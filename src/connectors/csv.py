import pandas as pd
from .base import BaseConnector

class CSVConnector(BaseConnector):
    """Connecteur pour fichiers CSV."""

    def read(self, file_path: str, encoding: str = 'utf-8', sep: str = ',', **kwargs) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path, encoding=encoding, sep=sep, **kwargs)
            self.validate(df)
            return df
        except Exception as e:
            raise RuntimeError(f"Erreur de lecture CSV : {e}")

    def write(self, data: pd.DataFrame, file_path: str, encoding: str = 'utf-8', sep: str = ',', **kwargs):
        try:
            data.to_csv(file_path, encoding=encoding, sep=sep, index=False, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Erreur d'écriture CSV : {e}")