"""
Classe pour gérer les textes dynamiques multilingues.
"""
from .i18n import i18n


class Texts:
    """Gestionnaire de textes."""
    
    @staticmethod
    def period_options():
        """Options de période selon la langue."""
        if i18n.current_lang == 'fr':
            return ["7 derniers jours", "30 derniers jours", "90 derniers jours", "Personnalisée"]
        else:
            return ["Last 7 days", "Last 30 days", "Last 90 days", "Custom"]
    
    @staticmethod
    def get_zone_name(zone_key):
        """Noms des zones selon la langue."""
        zones_fr = {
            'QUAI_1': 'Quai Principal',
            'QUAI_2_ROUTIER': 'Quai Routier',
            'ZONE_STOCKAGE': 'Zone Stockage',
            'CONTROLE_DOUANE': 'Contrôle Douane'
        }
        zones_en = {
            'QUAI_1': 'Main Quay',
            'QUAI_2_ROUTIER': 'Road Quay',
            'ZONE_STOCKAGE': 'Storage Zone',
            'CONTROLE_DOUANE': 'Customs Control'
        }
        
        zones = zones_fr if i18n.current_lang == 'fr' else zones_en
        return zones.get(zone_key, zone_key)
    
    @staticmethod
    def get_operation_type(op_key):
        """Types d'opération selon la langue."""
        ops_fr = {
            'CHARGEMENT': 'Chargement',
            'DÉCHARGEMENT': 'Déchargement',
            'VÉRIFICATION': 'Vérification'
        }
        ops_en = {
            'CHARGEMENT': 'Loading',
            'DÉCHARGEMENT': 'Unloading',
            'VÉRIFICATION': 'Verification'
        }
        
        ops = ops_fr if i18n.current_lang == 'fr' else ops_en
        return ops.get(op_key, op_key)