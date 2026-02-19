"""
Gestionnaire de traduction multilingue robuste.
Ne plante jamais, même si les fichiers JSON sont manquants.
"""
import json
from pathlib import Path

class I18n:
    def __init__(self, locale_dir="locales"):
        self.locale_dir = Path(locale_dir)
        self.translations = {}
        self.current_lang = "fr"
        # Traductions minimales de secours (français)
        self.fallback_fr = {
            "auth": {
                "title": "OPSGAIN PLATFORM",
                "slogan": "💎 Vos Opérations • Nos Gains",
                "description": "La plateforme qui transforme vos données opérationnelles<br>en gains financiers vérifiables en temps réel.",
                "password_label": "Mot de passe d'accès :",
                "button_access": "🚀 ACCÉDER AU DASHBOARD",
                "wrong_password": "❌ Mot de passe incorrect"
            },
            "app": {
                "title": "OPSGAIN PLATFORM / PORT SEC INTELLIGENT",
                "subtitle": "Dashboard opérationnel synchronisé",
                "footer": "OPSGAIN PLATFORM v3.0 - Données synchronisées"
            },
            "sidebar": {
                "title": "OPSGAIN PLATFORM / PORT SEC INTELLIGENT",
                "demo_button": "🚀 Lancer la démonstration complète",
                "period_analysis": "📅 PÉRIODE D'ANALYSE",
                "select_period": "Sélectionner la période",
                "filters": "🔧 FILTRES",
                "language": "🌍 LANGUE",
                "financial_params": "💰 PARAMÈTRES FINANCIERS",
                "data_sync": "🔗 PARTAGE DE DONNÉES SYNCHRONISÉES",
                "info": "📊 INFORMATIONS",
                "version": "**OpsGain Plateform Version:** {version}",
                "status": "**Statut:** Données synchronisées",
                "data_hash": "**Hash des données:** `{hash}`",
                "developer": "**Développeur:** ELIE KAYOMB MBUMB",
                "access_status": "**Accès sécurisé:** ✅ Authentifié"
            },
            "dashboard": {
                "operational_summary": "📊 SYNTHÈSE OPÉRATIONNELLE",
                "total_operations": "📦 Opérations Total",
                "avg_duration": "⏱️ Durée Moyenne",
                "error_rate": "❌ Taux d'Erreur",
                "total_gains": "💰 Gains Totaux Période"
            },
            "periods": {
                "last_7_days": "7 derniers jours",
                "last_30_days": "30 derniers jours",
                "last_90_days": "90 derniers jours",
                "custom": "Personnalisée"
            },
            "common": {
                "per_day": "/jour",
                "minutes": "min",
                "errors": "erreurs",
                "operations": "opérations"
            }
        }

    def load_language(self, lang_code):
        """Charge un fichier JSON. En cas d'échec, dictionnaire vide."""
        file_path = self.locale_dir / f"{lang_code}.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.translations[lang_code] = json.load(f)
        except Exception:
            # Fichier manquant ou invalide → dictionnaire vide
            self.translations[lang_code] = {}
            # Optionnel : log dans la console
            print(f"[i18n] Attention : fichier {lang_code}.json introuvable ou invalide. Utilisation du fallback français.")

    def set_language(self, lang_code):
        """Change la langue active."""
        if lang_code not in self.translations:
            self.load_language(lang_code)
        self.current_lang = lang_code

    def get(self, key, default=None, **kwargs):
        """
        Récupère une traduction.
        Parcourt d'abord la langue courante, puis le fallback français.
        Si rien trouvé, retourne `default` ou la clé.
        """
        try:
            keys = key.split('.')
            # 1. Chercher dans la langue courante
            val = self.translations.get(self.current_lang, {})
            for k in keys:
                val = val.get(k, {})
                if val == {}:
                    break
            if val != {}:
                if kwargs and isinstance(val, str):
                    return val.format(**kwargs)
                return val

            # 2. Fallback en français
            val = self.fallback_fr
            for k in keys:
                val = val.get(k, {})
                if val == {}:
                    return default if default is not None else key
            if kwargs and isinstance(val, str):
                return val.format(**kwargs)
            return val
        except Exception:
            return default if default is not None else key

# Instance globale (charge les deux langues, mais les fichiers peuvent manquer)
i18n = I18n()
i18n.load_language("fr")
i18n.load_language("en")