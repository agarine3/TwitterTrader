from tda import auth, client
import config
import json
from datetime import datetime

class Trader:
    def __init__(self):
        self.client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize TD Ameritrade client"""
        try:
            self.client = auth.client_from_token_file(
                config.TDA_TOKEN_PATH,
                config.TDA_CLIENT_ID
            )
        except Exception as e:
            print(f"Error initializing TD Ameritrade client: {e}")
            raise
    
    def execute_option_trade(self, signal):
        """
        Execute an option trade based on the signal
        """
        try:
            # Format the option symbol
            expiration_date = signal['expiration_date'].strftime('%y%m%d')
            option_type = 'C' if signal['option_type'] == 'call' else 'P'
            option_symbol = f"{signal['symbol']}_{expiration_date}{option_type}{int(signal['strike_price'])}"
            
            # Create the order
            order = {
                "orderType": "LIMIT",
                "session": "NORMAL",
                "duration": "DAY",
                "orderStrategyType": "SINGLE",
                "price": signal['target_price'],
                "orderLegCollection": [{
                    "instruction": "BUY_TO_OPEN",
                    "quantity": config.MAX_POSITION_SIZE,
                    "instrument": {
                        "symbol": option_symbol,
                        "assetType": "OPTION"
                    }
                }]
            }
            
            # Place the order
            response = self.client.place_order(config.ACCOUNT_ID, order)
            
            if response.status_code == 201:
                print(f"Successfully placed order for {option_symbol}")
                return True
            else:
                print(f"Failed to place order: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error executing trade: {e}")
            return False 