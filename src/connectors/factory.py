from .excel import ExcelConnector
from .csv import CSVConnector
from .api import APIConnector

class ConnectorFactory:
    @staticmethod
    def get_connector(connector_type: str, **kwargs):
        connector_type = connector_type.lower()
        if connector_type == 'excel':
            return ExcelConnector()
        elif connector_type == 'csv':
            return CSVConnector()
        elif connector_type == 'api':
            return APIConnector()
        else:
            raise ValueError(f"Type de connecteur inconnu : {connector_type}")