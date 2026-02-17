"""
Configuration centrale de l'application OpsGain.
Toutes les constantes et paramètres globaux sont définis ici.
"""
import streamlit as st
import os
from pathlib import Path
from datetime import datetime

# Chemins
BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "data" / "logs"

# Création des répertoires
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
(LOGS_DIR / "access").mkdir(parents=True, exist_ok=True)

# Configuration des données
PUBLIC_DATA_HASH = "portsec_2026_v1"
DATA_SEED = 42
DEFAULT_PASSWORD = "FROMelie-1756"

# Périodes par défaut
PERIODS = {
    "7 derniers jours": 7,
    "30 derniers jours": 30,
    "90 derniers jours": 90,
    "Personnalisée": None
}

# Paramètres financiers par défaut
FINANCIAL_PARAMS = {
    "monthly_fixed": 8000,
    "commission_rate": 0.12,
    "hourly_cost": 25,
    "error_cost": 150,
    "baseline_duration": 58,
    "baseline_error_rate": 0.032,
    "working_days": 22,
    "fuel_saving_per_truck": 1.5,
    "maintenance_alert_cost": 500
}

# Configuration de la carte
MAP_CONFIG = {
    "center": [-11.664, 27.482],
    "zoom": 15,
    "zones": {
        "QUAI_1": {"lat": -11.664, "lon": 27.482, "color": "blue", "icon": "ship"},
        "QUAI_2_ROUTIER": {"lat": -11.663, "lon": 27.483, "color": "green", "icon": "truck"},
        "ZONE_STOCKAGE": {"lat": -11.665, "lon": 27.481, "color": "orange", "icon": "boxes"},
        "CONTROLE_DOUANE": {"lat": -11.662, "lon": 27.484, "color": "red", "icon": "shield-alt"},
        "MAINTENANCE": {"lat": -11.666, "lon": 27.485, "color": "gray", "icon": "tools"}
    }
}

# Couleurs de l'interface
COLORS = {
    "primary": "#1E3A8A",
    "secondary": "#10B981",
    "danger": "#EF4444",
    "warning": "#F59E0B",
    "info": "#3B82F6",
    "light": "#F8FAFC",
    "dark": "#1F2937"
}

# Version
APP_VERSION = "3.0.0"
APP_NAME = "OPSGAIN PLATEFORM/PORT INTELLIGENT"
APP_DESCRIPTION = "La plateforme qui transforme vos données opérationnelles en gains financiers vérifiables en temps réel"
USE_REAL_DATA = False  # ou True si vous utilisez des données réelles

# URLs
DEFAULT_BASE_URL = "https://opsgain-plateform-kyrqqc6ibx2um8cbnqo5bg.streamlit.app"
