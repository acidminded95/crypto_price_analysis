import pandas as pd
import sqlite3
from typing import Tuple, Dict, Any, Optional
from config import DB_PATH, MOVING_AVERAGE_WINDOW

class DataProcessor:
    def __init__(self, db_path=None):
        """Initialize the data processor"""
        self.db_path = db_path if db_path is not None else DB_PATH

    def calculate_moving_average(self, df: pd.DataFrame) -> pd.Series:
        """Calculate moving average for price data"""
        return df['price'].rolling(window=MOVING_AVERAGE_WINDOW).mean()

    def get_price_analysis(self, coin_id: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Get price analysis for a specific coin
        
        Args:
            coin_id: The ID of the coin to analyze
            
        Returns:
            Tuple containing:
            - DataFrame with price data and moving average
            - Dictionary with analysis statistics
            
        Raises:
            ValueError: If no data is found for the given coin_id
        """
        # Connect to the database
        conn = sqlite3.connect(self.db_path)
        
        # Read the data into a pandas DataFrame
        query = "SELECT * FROM crypto_prices WHERE coin_id = ?"
        df = pd.read_sql_query(query, conn, params=(coin_id,))
        conn.close()
        
        if df.empty:
            raise ValueError(f"No data found for coin ID: {coin_id}")
        
        # Convert date string to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Sort by date
        df = df.sort_values('date')
        
        # Calculate moving average
        df['moving_average'] = self.calculate_moving_average(df)
        
        # Calculate price change percentage
        first_price = df['price'].iloc[0]
        last_price = df['price'].iloc[-1]
        price_change_pct = ((last_price - first_price) / first_price) * 100
        
        # Calculate basic statistics
        analysis = {
            'mean_price': df['price'].mean(),
            'std_price': df['price'].std(),
            'min_price': df['price'].min(),
            'max_price': df['price'].max(),
            'price_change_pct': price_change_pct,
            'moving_average': df['moving_average'].tolist()
        }
        
        return df, analysis

    def get_all_coins_data(self) -> pd.DataFrame:
        """Get price data for all coins in the database
        
        Returns:
            DataFrame containing price data for all coins
        """
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM crypto_prices", conn)
        conn.close()
        
        if df.empty:
            raise ValueError("No data found in the database")
            
        # Convert date string to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Sort by date and coin_id
        df = df.sort_values(['date', 'coin_id'])
        
        return df

    def get_coin_comparison(self, coin_ids: list[str]) -> Dict[str, Any]:
        """Compare multiple coins based on their price performance
        
        Args:
            coin_ids: List of coin IDs to compare
            
        Returns:
            Dictionary containing comparison metrics
        """
        all_data = self.get_all_coins_data()
        
        # Filter data for requested coins
        coin_data = all_data[all_data['coin_id'].isin(coin_ids)]
        
        if coin_data.empty:
            raise ValueError(f"No data found for any of the coins: {coin_ids}")
        
        # Calculate metrics for each coin
        comparison = {}
        for coin_id in coin_ids:
            coin_df = coin_data[coin_data['coin_id'] == coin_id]
            first_price = coin_df['price'].iloc[0]
            last_price = coin_df['price'].iloc[-1]
            price_change = ((last_price - first_price) / first_price) * 100
            
            comparison[coin_id] = {
                'price_change_pct': price_change,
                'mean_price': coin_df['price'].mean(),
                'volatility': coin_df['price'].std(),
                'max_price': coin_df['price'].max(),
                'min_price': coin_df['price'].min()
            }
        
        return comparison 