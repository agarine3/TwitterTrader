from ib_insync import *
from dotenv import load_dotenv
import os
import sys

def test_ib_connection():
    # Load environment variables
    load_dotenv()
    
    # Get IB connection details from environment
    host = os.getenv('IB_HOST', '127.0.0.1')
    port = int(os.getenv('IB_PORT', '7497'))  # Using 7497 for paper trading
    client_id = int(os.getenv('IB_CLIENT_ID', '1'))
    
    print(f"Connecting to IB Paper Trading at {host}:{port} (Client ID: {client_id})...")
    
    try:
        # Create IB connection
        ib = IB()
        ib.connect(host, port, clientId=client_id)
        
        # Test connection by getting account info
        account = ib.managedAccounts()[0]
        print(f"\nSuccessfully connected to paper trading account: {account}")
        
        # Get account summary
        account_summary = ib.accountSummary()
        print("\nAccount Summary:")
        for summary in account_summary:
            print(f"{summary.tag}: {summary.value}")
        
        # Test market data connection with a simple stock
        print("\nTesting market data connection with AAPL...")
        contract = Stock('AAPL', 'SMART', 'USD')
        ib.qualifyContracts(contract)
        ticker = ib.reqMktData(contract)
        ib.sleep(2)  # Wait for data
        
        if ticker.last:
            print(f"AAPL last price: ${ticker.last}")
        else:
            print("Could not get AAPL price data")
        
        # Test options data
        print("\nTesting options data with AAPL...")
        chains = ib.reqSecDefOptParams('AAPL', '', 'STK', 0)
        if chains:
            print("Successfully retrieved options chain")
            # Get the first available expiration
            expirations = chains[0].expirations
            if expirations:
                print(f"Available expirations: {expirations[:5]}...")  # Show first 5 expirations
        else:
            print("Could not get options chain")
        
        # Clean up
        ib.disconnect()
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"\nError connecting to IB: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure TWS or IB Gateway is running in PAPER TRADING mode")
        print("2. Verify the port number is 7497 for paper trading")
        print("3. Check if API connections are enabled in TWS/Gateway")
        print("4. Ensure '127.0.0.1' is in the trusted IP addresses")
        sys.exit(1)

if __name__ == "__main__":
    test_ib_connection() 