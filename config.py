import os

class Config:
    # Vercel will provide DATABASE_URL. Locally, it will use your Aiven cloud DB.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        "mysql+pymysql://avnadmin:AVNS__MrHlHumj797xzKdlpK@mysql-2e3285f6-bhuvibarla-9349.i.aivencloud.com:17494/defaultdb"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'