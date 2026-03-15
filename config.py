import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-123'
    
    # Check if running on Vercel
    IS_VERCEL = os.environ.get('VERCEL') == '1'
    
    # SQLite Configuration
    if IS_VERCEL:
        SQLITE_DB = '/tmp/database.db'
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        SQLITE_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
