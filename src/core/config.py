from dotenv import load_dotenv
import os
from loguru import logger

class Config:
    KEY_ALIAS: str = None
    KEY_PASSWORD: str = None
    
    P12_PATH: str = None
    PROFILE_PATH: str = None
    CERT_PATH: str = None
    
    DEBUG: bool = False

def load_config():
    logger.debug("Loading configuration from environment")
    load_dotenv()
    
    # Load credentials
    Config.KEY_ALIAS = os.getenv('KEY_ALIAS')
    Config.KEY_PASSWORD = os.getenv('KEY_PASSWORD')
    
    # Load paths
    Config.P12_PATH = os.getenv('P12_PATH')
    Config.PROFILE_PATH = os.getenv('PROFILE_PATH')
    Config.CERT_PATH = os.getenv('CERT_PATH')
    
    # Load debug setting
    Config.DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.debug("Configuration loaded successfully")