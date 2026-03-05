from .telecom import TelecomSector
from .logistics import LogisticsSector
from .retail import RetailSector
from .education import EducationSector

class SectorFactory:
    @staticmethod
    def get_sector(sector_name: str):
        sector_name = sector_name.lower()
        if sector_name == 'telecom':
            return TelecomSector()
        elif sector_name == 'logistics':
            return LogisticsSector()
        elif sector_name == 'retail':
            return RetailSector()
        elif sector_name == 'education':
            return EducationSector()
        else:
            raise ValueError(f"Secteur inconnu : {sector_name}")