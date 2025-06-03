import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MATTERMOST_URL = os.getenv('MATTERMOST_URL')
    MATTERMOST_PORT = int(os.getenv('MATTERMOST_PORT', 443))
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    BOT_TEAM = os.getenv('BOT_TEAM')
    BOT_USERNAME = os.getenv('BOT_USERNAME')
    
    @classmethod
    def validate(cls):
        required = [
            cls.MATTERMOST_URL,
            cls.BOT_TOKEN,
            cls.BOT_TEAM,
            cls.BOT_USERNAME
        ]
        if not all(required):
            raise ValueError("Missing required Mattermost configuration")
