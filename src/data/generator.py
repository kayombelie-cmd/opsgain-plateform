"""
Générateur de données déterministes.
"""
import hashlib
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from ..config import DATA_SEED, PUBLIC_DATA_HASH
from .models import PeriodData


class DataGenerator:
    """Générateur de données synchronisées."""
    
    def __init__(self, data_hash: str = PUBLIC_DATA_HASH):
        self.data_hash = data_hash
        self._set_seeds()
    
    def _set_seeds(self):
        """Configure les seeds pour la reproductibilité."""
        random.seed(DATA_SEED)
        np.random.seed(DATA_SEED)
    
    def _generate_seed(self, base_name: str, period_str: str) -> int:
        """Génère un seed déterministe."""
        seed_string = f"{self.data_hash}_{period_str}_{base_name}"
        return int(hashlib.md5(seed_string.encode()).hexdigest(), 16) % (10**8)
    
    def create_period_data(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        use_current_time: bool = True
    ) -> PeriodData:
        """Crée un ensemble complet de données pour une période."""
        # Création des seeds
        period_str = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        
        daily_seed = self._generate_seed("daily", period_str)
        engins_seed = self._generate_seed("engins", period_str)
        hourly_seed = self._generate_seed("hourly", period_str)
        recent_seed = self._generate_seed("recent", period_str)
        
        # Dates
        dates = pd.date_range(start_date, end_date, freq='D')
        
        # Référence pour les opérations récentes
        if use_current_time:
            reference_date = datetime.now()
        else:
            reference_date = end_date.replace(hour=12, minute=0, second=0, microsecond=0)
        
        # Initialisation des générateurs aléatoires
        rng_daily = random.Random(daily_seed)
        rng_engins = random.Random(engins_seed)
        rng_hourly = random.Random(hourly_seed)
        rng_recent = random.Random(recent_seed)
        
        # 1. Données journalières
        daily_data = pd.DataFrame({
            'date': dates,
            'nb_operations': [rng_daily.randint(128, 500) for _ in dates],
            'duree_moyenne': [40 + rng_daily.uniform(-8, 12) for _ in dates],
            'urgences': [rng_daily.randint(2, 15) for _ in dates],
            'erreurs': [rng_daily.randint(2, 10) for _ in dates]
        })
        
        # 2. Données des engins
        engins = ['TRACTEUR_01', 'TRACTEUR_02', 'TRACTEUR_03', 
                 'CHARIOT_01', 'CHARIOT_02', 'GRUE_01']
        
        engins_data = pd.DataFrame({
            'engin': engins,
            'total_operations': [rng_engins.randint(200, 1000) for _ in engins],
            'erreurs': [rng_engins.randint(5, 20) for _ in engins],
            'duree_moyenne': [rng_engins.uniform(35, 60) for _ in engins]
        })
        
        # 3. Données horaires
        hours = list(range(6, 22))
        hourly_data = pd.DataFrame({
            'heure': hours,
            'nb_operations': [rng_hourly.randint(10, 50) for _ in hours]
        })
        
        # 4. Opérations récentes
        recent_ops_list = []
        for i in range(20):
            minutes_offset = 5 + (i * 6)
            timestamp = reference_date - timedelta(minutes=minutes_offset)
            
            recent_ops_list.append({
                'timestamp': timestamp.replace(second=0, microsecond=0),
                'type_operation': ['CHARGEMENT', 'DÉCHARGEMENT', 'VÉRIFICATION'][i % 3],
                'zone': ['QUAI_1', 'QUAI_2_ROUTIER', 'ZONE_STOCKAGE', 'CONTROLE_DOUANE'][i % 4],
                'engin': engins[i % len(engins)],
                'duree_minutes': 15 + (i * 2.3) % 45,
                'urgence': 1 if i % 7 == 0 else 0,
                'erreur': 1 if i % 10 == 0 else 0
            })
        
        recent_ops = pd.DataFrame(recent_ops_list)
        
        return PeriodData(
            daily_data=daily_data,
            engins_data=engins_data,
            hourly_data=hourly_data,
            recent_ops=recent_ops,
            start_date=start_date,
            end_date=end_date,
            period_name=f"{start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"
        )