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
    
    def get(self, key, default=None):
        """Récupère une traduction par clé."""
        try:
            # Navigation dans la structure JSON : "app.title"
            keys = key.split('.')
            value = self.translations[self.current_lang]
            
            for k in keys:
                value = value[k]
            
            return value
        except (KeyError, TypeError):
            return default if default else key
    
    def t(self, key, default=None):
        """Alias pour get()."""
        return self.get(key, default)


# Instance globale
i18n = I18n()
i18n.load_language("fr")
i18n.load_language("en")