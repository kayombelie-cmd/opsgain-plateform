import pandas as pd
import io
from datetime import datetime

def generate_excel_report(period_data, financial_metrics):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Feuille 1 : Résumé
        summary_data = {
            'Période': [period_data.period_name],
            'Début': [period_data.start_date.strftime('%Y-%m-%d')],
            'Fin': [period_data.end_date.strftime('%Y-%m-%d')],
            'Jours': [len(period_data.daily_data)],
            'Opérations totales': [financial_metrics.period_summary['total_operations']],
            'Gains période': [financial_metrics.period_gains],
            'Commission mensuelle': [financial_metrics.your_commission_monthly]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Résumé', index=False)

        # Feuille 2 : Activité journalière
        period_data.daily_data.to_excel(writer, sheet_name='Activité journalière', index=False)

        # Feuille 3 : Performance engins
        period_data.engins_data.to_excel(writer, sheet_name='Engins', index=False)

        # Feuille 4 : Opérations récentes
        period_data.recent_ops.to_excel(writer, sheet_name='Opérations récentes', index=False)

        # Feuille 5 : Détail des gains
        gains_df = pd.DataFrame([
            {'Type': 'Temps', 'Journalier': financial_metrics.breakdown['time_gain'],
             'Période': financial_metrics.breakdown['time_gain_period']},
            {'Type': 'Erreurs', 'Journalier': financial_metrics.breakdown['error_gain'],
             'Période': financial_metrics.breakdown['error_gain_period']},
            {'Type': 'Maintenance', 'Journalier': financial_metrics.breakdown['maintenance_gain'],
             'Période': financial_metrics.breakdown['maintenance_gain_period']},
            {'Type': 'Carburant', 'Journalier': financial_metrics.breakdown['fuel_gain'],
             'Période': financial_metrics.breakdown['fuel_gain_period']},
        ])
        gains_df.to_excel(writer, sheet_name='Détail gains', index=False)

    return output.getvalue()