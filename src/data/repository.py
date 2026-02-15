import pandas as pd
from pathlib import Path
from datetime import datetime
from .models import PeriodData

class FileDataRepository:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def get_period_data(self, start_date: datetime, end_date: datetime) -> PeriodData:
        # Charger les fichiers CSV
        daily = pd.read_csv(self.data_dir / 'daily_operations.csv', parse_dates=['date'])
        engins = pd.read_csv(self.data_dir / 'equipment_performance.csv')
        recent = pd.read_csv(self.data_dir / 'recent_operations.csv', parse_dates=['timestamp'])

        # Filtrer sur la période demandée
        daily = daily[(daily['date'] >= start_date) & (daily['date'] <= end_date)]
        recent = recent[(recent['timestamp'] >= start_date) & (recent['timestamp'] <= end_date)]

        # Générer hourly_data à partir de daily ou créer un placeholder
        # Pour simplifier, on peut créer un DataFrame hourly vide ou le déduire
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