import pandas as pd
from .base import BaseConnector

class ExcelConnector(BaseConnector):
    """Connecteur pour fichiers Excel."""

    def read(self, file_path: str, sheet_name: str = 0, **kwargs) -> pd.DataFrame:
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
            self.validate(df)
            return df
        except Exception as e:
            raise RuntimeError(f"Erreur de lecture Excel : {e}")

    def write(self, data: pd.DataFrame, file_path: str, sheet_name: str = 'Sheet1', **kwargs):
        try:
            data.to_excel(file_path, sheet_name=sheet_name, index=False, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Erreur d'écriture Excel : {e}")