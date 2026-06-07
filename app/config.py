import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'torino-2026-dev-key'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../instance/app.db'))}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../static/tiles'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024