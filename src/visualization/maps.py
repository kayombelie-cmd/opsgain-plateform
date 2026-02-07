"""
Générateur de cartes interactives.
"""
import folium
from folium import plugins

from ..config import MAP_CONFIG


class MapGenerator:
    """Générateur de cartes interactives."""
    
    @staticmethod
    def create_realtime_map() -> folium.Map:
        """Crée une carte interactive du port."""
        m = folium.Map(
            location=MAP_CONFIG['center'],
            zoom_start=MAP_CONFIG['zoom'],
            control_scale=True,
            tiles='CartoDB positron'  # Style clair
        )
        
        # Ajout des zones
        for zone_name, zone_info in MAP_CONFIG['zones'].items():
            folium.Marker(
                location=[zone_info['lat'], zone_info['lon']],
                popup=f'''
                <div style="font-family: Arial, sans-serif;">
                    <h4 style="color: {zone_info['color']}; margin-bottom: 5px;">{zone_name}</h4>
                    <p><strong>Statut:</strong> Normal</p>
                    <p><strong>Activité:</strong> Élevée</p>
                    <p><strong>Dernière mise à jour:</strong> Juste maintenant</p>
                </div>
                ''',
                tooltip=zone_name,
                icon=folium.Icon(
                    color=zone_info['color'], 
                    icon=zone_info['icon'], 
                    prefix='fa'
                )
            ).add_to(m)
        
        # Périmètre du port
        port_perimeter = [
            [-11.666, 27.480],
            [-11.661, 27.480],
            [-11.661, 27.486],
            [-11.666, 27.486],
            [-11.666, 27.480]  # Fermer le polygone
        ]
        
        folium.Polygon(
            locations=port_perimeter,
            color=MAP_CONFIG['zones']['QUAI_1']['color'],
            fill=True,
            fill_color=MAP_CONFIG['zones']['QUAI_1']['color'],
            fill_opacity=0.1,
            weight=3,
            popup='<b>Périmètre du Port Sec</b><br>Zone sécurisée'
        ).add_to(m)
        
        # Ajout de contrôles
        folium.LayerControl().add_to(m)
        plugins.Fullscreen().add_to(m)
        plugins.MousePosition().add_to(m)
        
        return m