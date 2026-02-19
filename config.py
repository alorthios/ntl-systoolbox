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

# Application Settings
APP_NAME = "NTL-SysToolbox"
APP_VERSION = "2.0.0"
DEBUG = False
