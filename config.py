import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {'csv'}
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour session timeout 