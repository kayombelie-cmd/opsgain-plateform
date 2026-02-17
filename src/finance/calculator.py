"""
Calculateur financier.
"""
import hashlib
from datetime import datetime
from typing import Dict
import pandas as pd

from ..config import FINANCIAL_PARAMS, PUBLIC_DATA_HASH
from ..data.models import PeriodData, FinancialMetrics


class FinancialCalculator:
    """Calcule les métriques financières."""
    
    def __init__(self, session_state):
        self.session_state = session_state
   
    def _get_param(self, key: str, default=None):
        """Récupère un paramètre financier."""
        return getattr(self.session_state, key, FINANCIAL_PARAMS.get(key, default))
    def _empty_metrics(self, period_name: str) -> FinancialMetrics:
        """Retourne des métriques vides quand aucune donnée."""
        empty_summary = {
            'selected_period': period_name,
            'start_date': '',
            'end_date': '',
            'total_days': 0,
            'total_operations': 0,
            'avg_daily_operations': 0,
            'avg_duration': 0,
            'total_errors': 0,
            'error_rate': 0,
            'period_gains': 0
        }
        return FinancialMetrics(
            daily_gains=0,
            monthly_projection=0,
            period_gains=0,
            your_commission_today=0,
            your_commission_monthly=0,
            breakdown={},
            transaction_hash='',
            period_summary=empty_summary,
            metrics={}
        )
    def calculate(self, period_data: PeriodData) -> FinancialMetrics:
        """Calcule toutes les métriques financières."""
        if period_data.is_empty():
            return self._empty_metrics(period_data.period_name)
        
        daily_data = period_data.daily_data
        
        # 1. Statistiques de base
        total_days = len(daily_data)
        total_ops = daily_data['nb_operations'].sum()
        avg_daily_ops = total_ops / total_days if total_days > 0 else 0
        
        # Durée moyenne pondérée
        if total_ops > 0:
            avg_duration = (daily_data['duree_moyenne'] * daily_data['nb_operations']).sum() / total_ops
        else:
            avg_duration = daily_data['duree_moyenne'].mean() if len(daily_data) > 0 else 0
        
        # Taux d'erreur
        total_errors = daily_data['erreurs'].sum()
        error_rate = total_errors / total_ops if total_ops > 0 else 0
        
        # 2. Calcul des gains
        baseline_duration = self._get_param('baseline_duration')
        hourly_cost = self._get_param('hourly_cost')
        baseline_error = self._get_param('baseline_error_rate')
        error_cost = self._get_param('error_cost')
        
        # Gain temps
        time_saved = max(0, baseline_duration - avg_duration)
        time_gain_total = time_saved * total_ops * (hourly_cost / 60)
        time_gain_daily = time_gain_total / total_days if total_days > 0 else 0
        
        # Gain erreurs
        errors_avoided = max(0, (baseline_error - error_rate) * total_ops)
        error_gain_total = errors_avoided * error_cost
        error_gain_daily = error_gain_total / total_days if total_days > 0 else 0
        
        # Gain maintenance
        engins_data = period_data.engins_data
        if not engins_data.empty:
            maintenance_alerts = len([e for e in engins_data['erreurs'] if e > 10])
        else:
            maintenance_alerts = 0
        
        maintenance_gain_total = maintenance_alerts * self._get_param('maintenance_alert_cost')
        maintenance_gain_daily = maintenance_gain_total / total_days if total_days > 0 else 0
        
        # Gain carburant
        trucks_per_day = min(500, avg_daily_ops * 0.3)
        fuel_gain_daily = trucks_per_day * self._get_param('fuel_saving_per_truck')
        fuel_gain_total = fuel_gain_daily * total_days
        
        # 3. Totaux
        total_daily_gains = (time_gain_daily + error_gain_daily + 
                           maintenance_gain_daily + fuel_gain_daily)
        total_period_gains = total_daily_gains * total_days
        
        # 4. Commission
        monthly_fixed = self._get_param('monthly_fixed')
        commission_rate = self._get_param('commission_rate')
        working_days = self._get_param('working_days')
        
        daily_fixed = monthly_fixed / working_days if working_days > 0 else 0
        daily_variable = total_daily_gains * commission_rate
        daily_commission = daily_fixed + daily_variable
        
        monthly_projection = total_daily_gains * working_days
        monthly_commission = monthly_fixed + (monthly_projection * commission_rate)
        
                # 5. Hash de vérification
        hash_string = f"{period_data.period_name}:{total_ops}:{total_period_gains}:{daily_commission}:{PUBLIC_DATA_HASH}"
        transaction_hash = hashlib.sha256(hash_string.encode()).hexdigest()[:16]
        
        # 6. Création des métriques détaillées pour l'affichage
        metrics = {
            'total_ops_today': round(avg_daily_ops, 2),
            'avg_duration_today': round(avg_duration, 2),
            'error_rate_today': round(error_rate * 100, 2),
            'time_saved_minutes': round(time_saved, 2),
            'errors_avoided': round(errors_avoided, 2),
            'maintenance_alerts': maintenance_alerts,
            'trucks_per_day': round(trucks_per_day, 2),
            'baseline_duration': baseline_duration,
            'hourly_cost': hourly_cost,
            'baseline_error_rate': round(baseline_error * 100, 2),
            'error_cost': error_cost,
            'monthly_fixed': monthly_fixed,
            'commission_rate': round(commission_rate * 100, 2),
            'working_days': working_days,
            'fuel_saving_per_truck': self._get_param('fuel_saving_per_truck'),
            'maintenance_alert_cost': self._get_param('maintenance_alert_cost')
        }
        
        # 7. Résumé de période et breakdown
        period_summary = {
            'selected_period': period_data.period_name,
            'start_date': period_data.start_date.strftime('%d/%m/%Y'),
            'end_date': period_data.end_date.strftime('%d/%m/%Y'),
            'total_days': total_days,
            'total_operations': int(total_ops),
            'avg_daily_operations': round(avg_daily_ops, 1),
            'avg_duration': round(avg_duration, 1),
            'total_errors': int(total_errors),
            'error_rate': round(error_rate * 100, 1),
            'period_gains': round(total_period_gains, 2)
        }
        
        breakdown = {
            'time_gain': round(time_gain_daily, 2),
            'error_gain': round(error_gain_daily, 2),
            'maintenance_gain': round(maintenance_gain_daily, 2),
            'fuel_gain': round(fuel_gain_daily, 2),
            'time_gain_period': round(time_gain_total, 2),
            'error_gain_period': round(error_gain_total, 2),
            'maintenance_gain_period': round(maintenance_gain_total, 2),
            'fuel_gain_period': round(fuel_gain_total, 2)
        }
        
        return FinancialMetrics(
            daily_gains=round(total_daily_gains, 2),
            monthly_projection=round(monthly_projection, 2),
            period_gains=round(total_period_gains, 2),
            your_commission_today=round(daily_commission, 2),
            your_commission_monthly=round(monthly_commission, 2),
            breakdown=breakdown,
            transaction_hash=f"0x{transaction_hash}",
            period_summary=period_summary,
            metrics=metrics  
        )