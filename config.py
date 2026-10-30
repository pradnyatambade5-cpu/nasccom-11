import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-finance-bot-2026-key-@991')
    
    # Serverless / Vercel detection: Vercel filesystem is read-only except /tmp
    IS_VERCEL = bool(os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME'))
    
    _default_db = (Path('/tmp') / 'finance.db') if IS_VERCEL else (BASE_DIR / 'instance' / 'finance.db')
    
    # Database URL configuration
    _db_url = os.getenv('DATABASE_URL', f"sqlite:///{_default_db}")
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
        
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
