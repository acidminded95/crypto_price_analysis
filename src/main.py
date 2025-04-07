import os
import logging
from data_collector import CoinGeckoCollector
from data_processor import DataProcessor
from typing import Dict, Any, Tuple
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def collect_and_analyze_coin(coin_name: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Collect and analyze data for a specific coin"""
    try:
        # Initialize collector and get coin ID
        collector = CoinGeckoCollector()
        collector.get_all_coins()
        coin_id = collector.get_coin_id(coin_name)
        
        if coin_id is None:
            raise ValueError(f"Coin '{coin_name}' not found")
            
        logger.info(f"Found {coin_name} ID: {coin_id}")
        
        # Collect and store data
        collector.collect_and_store_coin_data(coin_id)
        
        # Analyze data
        processor = DataProcessor()
        df, stats = processor.get_price_analysis(coin_id)
        
        return df, stats
        
    except Exception as e:
        logger.error(f"Error processing {coin_name}: {str(e)}")
        raise

def main():
    try:
        # List of coins to analyze
        coins = ["Bitcoin"]
        
        for coin in coins:
            logger.info(f"Processing {coin}...")
            df, stats = collect_and_analyze_coin(coin)
            
            # Log analysis results
            logger.info(f"Analysis completed successfully for {coin}")
            logger.info(f"Mean price: ${stats['mean_price']:,.2f}")
            logger.info(f"Price change: {stats['price_change_pct']:.2f}%")
            logger.info("-" * 50)
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main() 