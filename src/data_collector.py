import requests
import sqlite3
from datetime import datetime, timezone
import time
from typing import List, Dict, Any
import logging
import os
from dotenv import load_dotenv
from config import (
    COINGECKO_API_BASE_URL,
    DB_PATH,
    START_DATE,
    END_DATE,
    RATE_LIMIT
)

# Load environment variables using absolute path
project_root = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoinGeckoCollector:
    def __init__(self):
        self.base_url = COINGECKO_API_BASE_URL
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 60 / RATE_LIMIT
        self.all_coins = []
        self.DB_PATH = DB_PATH
        
        # Get API key from environment variables
        self.api_key = os.getenv('COINGECKO_API_KEY')
        if not self.api_key:
            raise ValueError(f"COINGECKO_API_KEY not found in environment variables. Checked .env file at: {env_path}")
        
        # Add API key to session headers for free tier
        self.session.headers.update({
            'x-cg-demo-api-key': self.api_key
        })
        
        # Create database if it doesn't exist
        self.create_database()

    def rate_limit(self, delay=None):
        """Implement rate limiting for API requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        wait_time = delay if delay is not None else self.min_request_interval
        if time_since_last_request < wait_time:
            time.sleep(wait_time - time_since_last_request)
        self.last_request_time = time.time()

    def get_all_coins(self) -> List[Dict[str, Any]]:
        """Retrieve list of all cryptocurrencies"""
        self.rate_limit()
        endpoint = f"{self.base_url}/coins/list"
        response = self.session.get(endpoint)
        response.raise_for_status()
        self.all_coins = response.json()
        return self.all_coins

    def get_coin_id(self, coin_name: str) -> str:
        """Get coin ID by name"""
        # First get all coins if we haven't already
        if not self.all_coins:
            self.get_all_coins()
            
        for coin in self.all_coins:
            if coin['name'].lower() == coin_name.lower():
                return coin['id']
        return None

    def get_historical_data(self, coin_id: str) -> List[Dict[str, Any]]:
        """Get historical price data for a specific coin"""
        self.rate_limit()
        endpoint = f"{self.base_url}/coins/{coin_id}/market_chart/range"
        
        # Calculate timestamps using midnight UTC from config dates
        from_timestamp = int(START_DATE.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc).timestamp())
        to_timestamp = int(END_DATE.replace(hour=23, minute=59, second=59, microsecond=0, tzinfo=timezone.utc).timestamp())
        
        params = {
            'vs_currency': 'usd',
            'from': from_timestamp,
            'to': to_timestamp
        }
        
        try:
            response = self.session.get(endpoint, params=params)
            
            if response.status_code != 200:
                logger.error(f"Error response: {response.text}")
                response.raise_for_status()
                
            data = response.json()
            logger.info(f"Response data keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
            
            # Transform the data to match our database schema
            transformed_data = []
            for i in range(len(data['prices'])):
                timestamp, price = data['prices'][i]
                _, market_cap = data['market_caps'][i]
                _, volume = data['total_volumes'][i]
                
                # Convert timestamp to date string
                date = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d')
                
                transformed_data.append({
                    'date': date,
                    'market_data': {
                        'current_price': {
                            'usd': price
                        },
                        'market_cap': {
                            'usd': market_cap
                        },
                        'total_volume': {
                            'usd': volume
                        }
                    }
                })
            
            # Sort data by date
            transformed_data.sort(key=lambda x: x['date'])
            
            logger.info(f"Retrieved {len(transformed_data)} data points for {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")
            return transformed_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Error response: {e.response.text}")
            raise

    def create_database(self):
        """Create the database and tables if they don't exist"""
        # Create directory if needed
        if self.DB_PATH:
            db_dir = os.path.dirname(self.DB_PATH)
            if db_dir:  # Only create directory if there's a path and path doesn't already exist
                os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        
        try:
            # Create crypto_prices table with composite primary key
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crypto_prices (
                    date TEXT NOT NULL,
                    coin_id TEXT NOT NULL,
                    price REAL NOT NULL,
                    market_cap REAL NOT NULL,
                    volume REAL NOT NULL,
                    PRIMARY KEY (date, coin_id)
                )
            """)
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def save_to_database(self, data: List[Dict[str, Any]], coin_id: str):
        """Save historical data to SQLite database"""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        
        try:
            for entry in data:
                date = entry['date']
                price = entry['market_data']['current_price']['usd']
                market_cap = entry['market_data']['market_cap']['usd']
                volume = entry['market_data']['total_volume']['usd']
                
                # Use INSERT OR REPLACE to update existing records
                cursor.execute("""
                    INSERT OR REPLACE INTO crypto_prices 
                    (date, coin_id, price, market_cap, volume)
                    VALUES (?, ?, ?, ?, ?)
                """, (date, coin_id, price, market_cap, volume))
            
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def collect_coin_data(self, coin_id: str) -> List[Dict[str, Any]]:
        """Collect historical data for a specific coin"""
        try:
            logger.info(f"Starting data collection process for coin ID: {coin_id}")
            
            # Get historical data
            historical_data = self.get_historical_data(coin_id)
            logger.info(f"Retrieved {len(historical_data)} data points")
            
            return historical_data

        except Exception as e:
            logger.error(f"Error during data collection: {str(e)}")
            raise

    def store_coin_data(self, data: List[Dict[str, Any]], coin_id: str):
        """Store historical data for a specific coin"""
        try:
            # Save to database
            self.save_to_database(data, coin_id)
            logger.info(f"Data successfully saved to database for coin ID: {coin_id}")
        except Exception as e:
            logger.error(f"Error during data storage: {str(e)}")
            raise

    def collect_and_store_coin_data(self, coin_id: str):
        """Collect and store historical data for a specific coin"""
        try:
            data = self.collect_coin_data(coin_id)
            self.store_coin_data(data, coin_id)
        except Exception as e:
            logger.error(f"Error during data collection and storage: {str(e)}")
            raise 