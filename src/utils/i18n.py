"""
Gestionnaire de traduction multilingue.
"""
import json
from pathlib import Path
import streamlit as st


class I18n:
    """Gestionnaire de langues."""
    
    def __init__(self, locale_dir="locales"):
        self.locale_dir = Path(locale_dir)
        self.translations = {}
        self.current_lang = "fr"
        
    def load_language(self, lang_code):
        """Charge les traductions d'une langue."""
        file_path = self.locale_dir / f"{lang_code}.json"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.translations[lang_code] = json.load(f)
        except FileNotFoundError:
            # Charger le français par défaut
            with open(self.locale_dir / "fr.json", 'r', encoding='utf-8') as f:
                self.translations[lang_code] = json.load(f)
    
    def set_language(self, lang_code):
        """Définit la langue active."""
        if lang_code not in self.translations:
            self.load_language(lang_code)
        self.current_lang = lang_code
    
    def get(self, key, default=None, **kwargs):
        try:
            keys = key.split('.')
            value = self.translations[self.current_lang]
            for k in keys:
                value = value[k]
            if kwargs:
                value = value.format(**kwargs)
            return value
        except (KeyError, TypeError, AttributeError) as e:
            # Optionnel : logger l'erreur
            print(f"[i18n] Clé manquante : {key}")  # ou utiliser logger
            return default if default is not None else key


# Instance globale
i18n = I18n()
i18n.load_language("fr")
i18n.load_language("en")