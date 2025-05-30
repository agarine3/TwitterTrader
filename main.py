import tweepy
import config
from tweet_parser import TweetParser
from trader import Trader
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TwitterStreamListener(tweepy.StreamingClient):
    def __init__(self, bearer_token, tweet_parser, trader):
        super().__init__(bearer_token)
        self.tweet_parser = tweet_parser
        self.trader = trader
    
    def on_tweet(self, tweet):
        try:
            logger.info(f"Received tweet: {tweet.text}")
            
            # Parse the tweet for option signals
            signal = self.tweet_parser.parse_option_signal(tweet.text)
            
            if signal and self.tweet_parser.is_valid_signal(signal):
                logger.info(f"Valid signal detected: {signal}")
                
                # Execute the trade
                if self.trader.execute_option_trade(signal):
                    logger.info("Trade executed successfully")
                else:
                    logger.error("Failed to execute trade")
            else:
                logger.debug("No valid signal found in tweet")
                
        except Exception as e:
            logger.error(f"Error processing tweet: {e}")

def main():
    # Initialize components
    tweet_parser = TweetParser()
    trader = Trader()
    
    # Initialize Twitter stream
    stream = TwitterStreamListener(
        bearer_token=config.TWITTER_BEARER_TOKEN,
        tweet_parser=tweet_parser,
        trader=trader
    )
    
    # Add rules to filter tweets
    for user_id in config.TARGET_USER_IDS:
        stream.add_rules(tweepy.StreamRule(f"from:{user_id}"))
    
    # Start streaming
    logger.info("Starting Twitter stream...")
    stream.filter(tweet_fields=['text'])
    
if __name__ == "__main__":
    main() 