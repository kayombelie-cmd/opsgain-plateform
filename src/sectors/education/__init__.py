from .transformer import transform
from .metrics import calculate_metrics
from .gains import calculate_gains
from .visualizations import get_visualizations
from .data_simulator import generate_sample_data
from ..base_sector import BaseSector

class EducationSector(BaseSector):
    def transform(self, raw_data):
        return transform(raw_data)

    def calculate_metrics(self, data):
        return calculate_metrics(data)

    def calculate_gains(self, data, params):
        return calculate_gains(data, params)

    def get_visualizations(self, data):
        return get_visualizations(data)

    def generate_sample_data(self, days=30):
        return generate_sample_data(days)