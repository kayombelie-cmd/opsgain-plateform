"""
Modèles de données et structures.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
import pandas as pd


@dataclass
class FinancialMetrics:
    """Métriques financières calculées."""
    daily_gains: float
    monthly_projection: float
    period_gains: float
    your_commission_today: float
    your_commission_monthly: float
    breakdown: Dict[str, float]
    transaction_hash: str
    period_summary: Dict[str, any]
    metrics: Dict[str, any]
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire pour sérialisation."""
        return {
            'daily_gains': self.daily_gains,
            'monthly_projection': self.monthly_projection,
            'period_gains': self.period_gains,
            'your_commission_today': self.your_commission_today,
            'your_commission_monthly': self.your_commission_monthly,
            'breakdown': self.breakdown,
            'transaction_hash': self.transaction_hash,
            'period_summary': self.period_summary,
            'metrics': self.metrics  # ← AJOUTEZ CETTE LIGNE
        }


@dataclass
class PeriodData:
    """Données complètes pour une période."""
    daily_data: pd.DataFrame
    engins_data: pd.DataFrame
    hourly_data: pd.DataFrame
    recent_ops: pd.DataFrame
    start_date: datetime
    end_date: datetime
    period_name: str
    
    def is_empty(self) -> bool:
        """Vérifie si les données sont vides."""
        return (
            self.daily_data.empty or 
            self.engins_data.empty or 
            self.hourly_data.empty
        )