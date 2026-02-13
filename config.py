"""
NTL-SysToolbox - Configuration
Centralized configuration for all modules
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MySQL Configuration (Module 2)
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', ''),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

# Servers to Monitor (Module 1)
SERVERS = {
    'local': {
        'name': 'Local Machine',
        'type': 'local',
        'os': 'auto'  # auto-detect or 'windows'/'linux'
    }
}

# Application Settings
APP_NAME = "NTL-SysToolbox"
APP_VERSION = "1.0.0"
DEBUG = False
