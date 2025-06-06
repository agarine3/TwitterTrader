import requests
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv('IO_KEY')

# Polling interval in seconds
polling_interval_seconds = 60

def get_recent_tweets(username):
    """Get recent tweets from a user"""
    
    # Calculate time for last 10 minutes
    now = datetime.now()
    buffer_seconds = polling_interval_seconds * 0.5
    total_lookback_seconds = polling_interval_seconds + buffer_seconds
    
    time_ago = now - timedelta(seconds=total_lookback_seconds)
    since_time = int(time_ago.timestamp())
    
    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    headers = {"X-API-Key": API_KEY}
    params = {
        "query": f"from:{username} since_time:{since_time}",
        "queryType": "Latest"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        tweets = data.get('tweets', [])
        return tweets
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def monitor_user(username):
    """Simple monitoring loop"""
    print(f"Monitoring @{username}...")
    
    while True:
        tweets = get_recent_tweets(username)
        
        if tweets:
            print(f"\nFound {len(tweets)} recent tweets:")
            for tweet in tweets:
                print(f"- {tweet.get('text', '')}")
        else:
            print("No new tweets")
        
        # Wait before checking again
        time.sleep(polling_interval_seconds)

if __name__ == "__main__":
    # Replace with the username you want to monitor
    username = os.getenv('TWITTER_USER')
    
    monitor_user(username)