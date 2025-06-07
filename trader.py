from ib_insync import *
from datetime import datetime, timedelta
import time
import logging
from config import IB_HOST, IB_PORT, IB_CLIENT_ID

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)

class Trader:
    def __init__(self):
        self.ib = IB()
        self.positions = {}  # Track positions and their details
        self.profit_targets = {
            'target1': 0.15,  # 15% profit
            'target2': 0.30,  # 30% profit
            'target3': 0.50   # 50% profit
        }
        self.average_down_threshold = -0.40  # 40% down triggers averaging down
        self.position_sizes = {
            'initial': 1,     # Start with 1 contract
            'average': 1      # Add 1 contract at a time
        }
        self.max_contracts = 3  # Maximum number of contracts
        self.max_wait_time = 30  # Maximum wait time in minutes
        self.price_margin = 0.02  # Maximum price deviation in dollars
        self.trailing_stop_percentage = 0.10  # 10% trailing stop

    def initialize_client(self):
        """Initialize connection to Interactive Brokers"""
        try:
            self.ib.connect(IB_HOST, IB_PORT, clientId=IB_CLIENT_ID)
            logging.info("Successfully connected to Interactive Brokers")
        except Exception as e:
            logging.error(f"Failed to connect to Interactive Brokers: {str(e)}")
            raise

    def get_option_quote(self, symbol, expiry, strike, option_type):
        """Get current quote for an option"""
        try:
            # Create option contract
            contract = Option(symbol, expiry, strike, option_type, 'SMART', '100')
            self.ib.qualifyContracts(contract)
            
            # Request market data
            ticker = self.ib.reqMktData(contract)
            self.ib.sleep(2)  # Wait for data
            
            if ticker.last:
                return ticker.last
            return None
        except Exception as e:
            logging.error(f"Error getting option quote: {str(e)}")
            return None

    def calculate_position_size(self, current_price, is_average_down=False):
        """Calculate position size based on current price and whether it's an average down"""
        base_size = self.position_sizes['average'] if is_average_down else self.position_sizes['initial']
        return base_size

    def place_limit_order(self, contract, quantity, limit_price, action='BUY'):
        """Place a limit order"""
        try:
            order = LimitOrder(action, quantity, limit_price)
            trade = self.ib.placeOrder(contract, order)
            self.ib.sleep(1)  # Wait for order to be placed
            
            if trade.orderStatus.status == 'Filled':
                logging.info(f"Order filled: {action} {quantity} {contract.symbol} at {limit_price}")
                return True
            else:
                logging.warning(f"Order not filled: {trade.orderStatus.status}")
                return False
        except Exception as e:
            logging.error(f"Error placing order: {str(e)}")
            return False

    def place_trailing_stop(self, contract, quantity, trailing_percent):
        """Place a trailing stop order"""
        try:
            # Get current price
            current_price = self.get_option_quote(
                contract.symbol,
                contract.lastTradeDateOrContractMonth,
                contract.strike,
                contract.right
            )
            
            if current_price:
                # Calculate trailing stop price
                stop_price = current_price * (1 - trailing_percent)
                
                # Create trailing stop order
                order = StopOrder('SELL', quantity, stop_price)
                trade = self.ib.placeOrder(contract, order)
                self.ib.sleep(1)
                
                if trade.orderStatus.status == 'Submitted':
                    logging.info(f"Placed trailing stop order at {stop_price}")
                    return True
                else:
                    logging.warning(f"Failed to place trailing stop: {trade.orderStatus.status}")
                    return False
        except Exception as e:
            logging.error(f"Error placing trailing stop: {str(e)}")
            return False

    def setup_profit_targets(self, contract, entry_price, quantity):
        """Set up limit sell orders at different profit targets"""
        # For multiple contracts, we'll sell at different targets
        if quantity >= 3:
            # Sell 1 contract at each target
            for target_name, target_percentage in self.profit_targets.items():
                target_price = entry_price * (1 + target_percentage)
                self.place_limit_order(contract, 1, target_price, 'SELL')
                logging.info(f"Placed {target_name} limit sell order at {target_price}")
        elif quantity == 2:
            # Sell 1 contract at 30% and keep 1 for trailing stop
            target_price = entry_price * (1 + self.profit_targets['target2'])
            self.place_limit_order(contract, 1, target_price, 'SELL')
            logging.info(f"Placed target2 limit sell order at {target_price}")
        else:
            # For 1 contract, use trailing stop
            self.place_trailing_stop(contract, 1, self.trailing_stop_percentage)

    def check_and_average_down(self, contract, position):
        """Check if position needs averaging down and execute if necessary"""
        if position['quantity'] >= self.max_contracts:
            logging.info("Maximum contracts reached, no more averaging down")
            return

        current_price = self.get_option_quote(
            contract.symbol,
            contract.lastTradeDateOrContractMonth,
            contract.strike,
            contract.right
        )
        
        if current_price:
            price_change = (current_price - position['entry_price']) / position['entry_price']
            
            if price_change <= self.average_down_threshold:
                # Calculate new average price and position size
                new_quantity = self.calculate_position_size(current_price, is_average_down=True)
                new_average_price = (position['entry_price'] * position['quantity'] + 
                                   current_price * new_quantity) / (position['quantity'] + new_quantity)
                
                # Place average down order
                if self.place_limit_order(contract, new_quantity, current_price, 'BUY'):
                    # Update position tracking
                    position['quantity'] += new_quantity
                    position['entry_price'] = new_average_price
                    position['averaged_down'] = True
                    
                    # Set up new profit targets based on new average price
                    self.setup_profit_targets(contract, new_average_price, position['quantity'])
                    logging.info(f"Averaged down position: new quantity={position['quantity']}, "
                               f"new average price={new_average_price}")

    def execute_option_trade(self, signal):
        """Execute an option trade based on the signal"""
        try:
            # Format option symbol
            option_symbol = f"{signal['symbol']}{signal['expiry']}{signal['strike']}{signal['option_type']}"
            
            # Create option contract
            contract = Option(
                signal['symbol'],
                signal['expiry'],
                signal['strike'],
                signal['option_type'],
                'SMART',
                '100'
            )
            self.ib.qualifyContracts(contract)
            
            # Get target price from signal
            target_price = signal['target_price']
            start_time = datetime.now()
            
            # Try to execute trade within 30 minutes
            while (datetime.now() - start_time).total_seconds() < (self.max_wait_time * 60):
                current_price = self.get_option_quote(
                    signal['symbol'],
                    signal['expiry'],
                    signal['strike'],
                    signal['option_type']
                )
                
                if current_price:
                    # Check if price is within margin (1-2 cents higher max)
                    if current_price <= target_price + self.price_margin:
                        # Calculate position size (1 contract initially)
                        quantity = self.calculate_position_size(current_price)
                        
                        # Place initial order
                        if self.place_limit_order(contract, quantity, current_price, 'BUY'):
                            # Track position
                            self.positions[option_symbol] = {
                                'contract': contract,
                                'quantity': quantity,
                                'entry_price': current_price,
                                'averaged_down': False,
                                'entry_time': datetime.now()
                            }
                            
                            # Set up profit targets
                            self.setup_profit_targets(contract, current_price, quantity)
                            
                            # Start monitoring for average down opportunity
                            self.check_and_average_down(contract, self.positions[option_symbol])
                            
                            logging.info(f"Successfully executed trade: {option_symbol} at {current_price}")
                            return
                
                # Wait 1 minute before next attempt
                time.sleep(60)
            
            logging.warning(f"Trade not executed within {self.max_wait_time} minutes: {option_symbol}")
                
        except Exception as e:
            logging.error(f"Error executing trade: {str(e)}")

    def cleanup(self):
        """Clean up resources"""
        if self.ib.isConnected():
            self.ib.disconnect()
            logging.info("Disconnected from Interactive Brokers") 