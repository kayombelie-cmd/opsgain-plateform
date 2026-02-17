import pandas as pd
from pathlib import Path
from datetime import datetime
from ..utils.logger import setup_logger
from .models import PeriodData

logger = setup_logger(__name__)

class FileDataRepository:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def get_period_data(self, start_date: datetime, end_date: datetime) -> PeriodData:
        # Nettoyer les dates (enlever fuseau horaire)
        start_date = start_date.replace(tzinfo=None)
        end_date = end_date.replace(tzinfo=None)

        try:
            # Chemins des fichiers
            daily_path = self.data_dir / 'daily_operations.csv'
            engins_path = self.data_dir / 'equipment_performance.csv'
            recent_path = self.data_dir / 'recent_operations.csv'

            # Vérifier existence
            for path in [daily_path, engins_path, recent_path]:
                if not path.exists():
                    raise FileNotFoundError(f"Fichier manquant : {path}")

            # Chargement avec conversion explicite des dates
            daily = pd.read_csv(daily_path)
            engins = pd.read_csv(engins_path)
            recent = pd.read_csv(recent_path)

            # Convertir les colonnes de dates
            daily['date'] = pd.to_datetime(daily['date'], format='%Y-%m-%d', errors='coerce')
            recent['timestamp'] = pd.to_datetime(recent['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

            # Supprimer les lignes avec dates invalides
            daily = daily.dropna(subset=['date'])
            recent = recent.dropna(subset=['timestamp'])

            # Filtrer sur la période
            daily = daily[(daily['date'] >= start_date) & (daily['date'] <= end_date)]
            recent = recent[(recent['timestamp'] >= start_date) & (recent['timestamp'] <= end_date)]

            # Créer hourly_data à partir de recent (si possible)
            if not recent.empty:
                recent['heure'] = recent['timestamp'].dt.hour
                hourly = recent.groupby('heure').size().reset_index(name='nb_operations')
            else:
                hourly = pd.DataFrame({'heure': range(24), 'nb_operations': 0})

            period_name = f"{start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"

            return PeriodData(
                daily_data=daily,
                engins_data=engins,
                hourly_data=hourly,
                recent_ops=recent,
                start_date=start_date,
                end_date=end_date,
                period_name=period_name
            )

        except Exception as e:
            logger.error(f"Erreur lors du chargement des données réelles: {e}")
            raise  # Propage l'erreur pour qu'elle apparaisse dans les logs