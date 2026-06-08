import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'torino-2026-super-secret-key-change-this'

    # Use SQLite for now (reliable on Render)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../instance/app.db'))}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../static/tiles'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024