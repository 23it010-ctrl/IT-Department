import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-123'
    
    # Check if running on Vercel
    IS_VERCEL = os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_URL') is not None
    
    # Base directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # SQLite & Upload Configuration
    if IS_VERCEL:
        SQLITE_DB = '/tmp/database.db'
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        SQLITE_DB = os.path.join(BASE_DIR, 'database.db')
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    
    # Create upload folder if not exists (local only, Vercel done in app.py)
    if not IS_VERCEL and not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7

