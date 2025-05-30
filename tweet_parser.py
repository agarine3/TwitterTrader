import re
from datetime import datetime

class TweetParser:
    @staticmethod
    def parse_option_signal(tweet_text):
        """
        Parse a tweet for stock option signals.
        Expected format: $SYMBOL MM/DD STRIKEc/p @ PRICE
        Example: $SPY 6/6 595c @ 3.98
        """
        # Regular expression to match option signals
        pattern = r'\$(\w+)\s+(\d+)/(\d+)\s+(\d+)([cp])\s+@\s+(\d+\.?\d*)'
        match = re.search(pattern, tweet_text)
        
        if not match:
            return None
            
        symbol, month, day, strike, option_type, price = match.groups()
        
        # Convert to current year
        current_year = datetime.now().year
        expiration_date = datetime(current_year, int(month), int(day))
        
        return {
            'symbol': symbol,
            'expiration_date': expiration_date,
            'strike_price': float(strike),
            'option_type': 'call' if option_type == 'c' else 'put',
            'target_price': float(price)
        }
    
    @staticmethod
    def is_valid_signal(signal):
        """
        Validate if the parsed signal is valid for trading
        """
        if not signal:
            return False
            
        # Check if expiration date is in the future
        if signal['expiration_date'] <= datetime.now():
            return False
            
        # Add more validation rules as needed
        return True 