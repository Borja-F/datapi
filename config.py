import os

class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'postgresql://fl0user:VASF0wG7HoPe@ep-winter-credit-54118564.eu-central-1.aws.neon.tech:5432/Apikey?sslmode=require'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY_LENGTH = 32  # Set the desired length for API keys
