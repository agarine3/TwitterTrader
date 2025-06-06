# TwitterTrader

A Twitter-based stock trading bot that monitors specific users for stock option signals and executes trades automatically.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your credentials (use `.env.example` as a template):
```
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
TDA_CLIENT_ID=your_tda_client_id
TDA_REDIRECT_URI=your_tda_redirect_uri
TDA_TOKEN_PATH=path_to_token_file
```

3. Run the bot:
```bash
python3 main.py
```

## Features
- Real-time Twitter stream monitoring
- Automatic stock option signal detection
- Trade execution through TD Ameritrade API
- Configurable target Twitter accounts
- Price validation and trade execution

## Note
This bot is for educational purposes only. Always test thoroughly with paper trading before using real money.
