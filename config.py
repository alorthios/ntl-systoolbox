"""
NTL-SysToolbox - Configuration
Centralized configuration for all modules
"""

# MySQL Configuration (Module 2)
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': '',
    'port': 3306
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
