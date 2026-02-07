"""
Configuration centralisée du logging.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
import csv
import socket

from ..config import LOGS_DIR


def setup_logger(name: str = __name__, log_file: str = "app.log") -> logging.Logger:
    """
    Configure et retourne un logger.
    
    Args:
        name: Nom du logger
        log_file: Nom du fichier de log
    
    Returns:
        logging.Logger: Instance configurée
    """
    logger = logging.getLogger(name)
    
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler fichier
    log_path = LOGS_DIR / log_file
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Ajout des handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_client_ip() -> str:
    """Récupère l'adresse IP du client."""
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip
    except:
        return "IP non disponible"


def log_access(link_id: str, period: str) -> None:
    """
    Log les accès via liens partagés.
    
    Args:
        link_id: ID unique du lien
        period: Période sélectionnée
    """
    access_logger = setup_logger("access", "access.log")
    ip = get_client_ip()
    
    access_logger.info(f"LINK_ACCESS - ID: {link_id} - IP: {ip} - Period: {period}")
    
    # Sauvegarde CSV pour analyse
    access_file = LOGS_DIR / "access" / "access_log.csv"
    
    with open(access_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'link_id', 'ip', 'period'])
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow({
            'timestamp': datetime.now().isoformat(),
            'link_id': link_id,
            'ip': ip,
            'period': period
        })