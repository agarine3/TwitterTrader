import tweepy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_user_tweets(username, count=5):
    """Fetch recent tweets from a specific user"""
    # Initialize the client with just the bearer token
    client = tweepy.Client(bearer_token=os.getenv('TWITTER_BEARER_TOKEN'))
    
    try:
        # Get user ID from username
        user = client.get_user(username=username)
        if not user.data:
            print(f"Could not find user: {username}")
            return
        
        user_id = user.data.id
        
        # Get recent tweets
        tweets = client.get_users_tweets(
            user_id,
            max_results=max(5, count),  # Twitter API requires at least 5
            tweet_fields=['created_at', 'text']
        )
        
        if not tweets.data:
            print(f"No tweets found for user: {username}")
            return
            
        print(f"\nLatest {len(tweets.data)} tweets from @{username}:")
        for tweet in tweets.data[:count]:
            print(f"Time: {tweet.created_at}")
            print(f"Tweet: {tweet.text}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error fetching tweets: {e}")

if __name__ == "__main__":
    # Test with user
    username = os.getenv('TWITTER_USER')
    get_user_tweets(username, count=3) 