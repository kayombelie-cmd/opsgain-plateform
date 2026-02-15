import pytest
from datetime import datetime
import pandas as pd
from src.data.models import PeriodData
from src.finance.calculator import FinancialCalculator

@pytest.fixture
def sample_period_data():
    daily = pd.DataFrame({
        'date': pd.date_range('2026-01-01', periods=5),
        'nb_operations': [100, 110, 105, 120, 115],
        'duree_moyenne': [45, 44, 46, 43, 45],
        'erreurs': [2, 3, 1, 4, 2]
    })
    engins = pd.DataFrame({
        'engin': ['A', 'B'],
        'total_operations': [500, 450],
        'erreurs': [10, 8]
    })
    hourly = pd.DataFrame({'heure': [8,9,10], 'nb_operations': [20,30,25]})
    recent = pd.DataFrame(columns=['timestamp', 'type_operation', 'zone', 'engin', 'duree_minutes', 'urgence', 'erreur'])
    return PeriodData(daily, engins, hourly, recent, datetime(2026,1,1), datetime(2026,1,5), "Test")

def test_calculate_basic(sample_period_data):
    session_state = type('obj', (object,), {
        'baseline_duration': 50,
        'hourly_cost': 30,
        'baseline_error_rate': 0.03,
        'error_cost': 200,
        'maintenance_alert_cost': 500,
        'fuel_saving_per_truck': 1.5,
        'monthly_fixed': 5000,
        'commission_rate': 0.1,
        'working_days': 22
    })
    calc = FinancialCalculator(session_state)
    metrics = calc.calculate(sample_period_data)

    assert metrics.daily_gains > 0
    assert metrics.period_gains == metrics.daily_gains * 5
    assert 'time_gain' in metrics.breakdown
    assert metrics.transaction_hash.startswith('0x')