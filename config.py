import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twitter API credentials
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# TD Ameritrade API credentials
TDA_CLIENT_ID = os.getenv('TDA_CLIENT_ID')
TDA_REDIRECT_URI = os.getenv('TDA_REDIRECT_URI')
TDA_TOKEN_PATH = os.getenv('TDA_TOKEN_PATH')

# Trading settings
MAX_POSITION_SIZE = 1  # Maximum number of contracts per trade
ACCOUNT_ID = os.getenv('TDA_ACCOUNT_ID')  # Your TD Ameritrade account ID

# Twitter settings
TARGET_USER_IDS = []  # Add target Twitter user IDs here 