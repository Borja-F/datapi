from app import db_api
from config import Config

class APIKey(db_api.Model):
    id = db_api.Column(db_api.Integer, primary_key=True)
    key = db_api.Column(db_api.String(Config.API_KEY_LENGTH), unique=True, nullable=False)

    def __init__(self, key):
        self.key = key
