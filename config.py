import os
from urllib.parse import quote_plus

class Config:
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:your_password@localhost/your_database"

    SECRET_KEY = os.urandom(24)
    password = quote_plus("Bhuvi@123")  # Encodes special characters
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:{password}@localhost/college_connect"

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    
