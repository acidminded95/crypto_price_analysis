# Cryptocurrency Price Analysis Tool

This project provides an automated solution for analyzing cryptocurrency price behavior using the CoinGecko API, pandas for data processing, and Streamlit for visualization.

## Features

- Automated data collection from CoinGecko API
- Support for multiple cryptocurrencies
- SQLite database storage for historical data
- 5-day moving average calculation
- Interactive visualization using Streamlit
- Price comparison across different cryptocurrencies
- Comprehensive price analysis and insights
- Unit tests for data processing and collection functions

## Prerequisites

- Python 3.8+
- CoinGecko API key (free plan available at https://www.coingecko.com/api/pricing)
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your CoinGecko API key:
   - Create a `.env` file in the project root
   - Add your API key:
     ```
     COINGECKO_API_KEY=your_api_key_here
     ```
   - Make sure to replace `your_api_key_here` with your actual CoinGecko API key

## Usage

1. Run the data collection and processing:
   ```bash
   python src/main.py
   ```
   This will collect data for Bitcoin by default. You can modify the list of coins in `src/main.py`.

2. Launch the Streamlit dashboard:
   ```bash
   streamlit run src/app.py
   ```

## Project Structure

```
.
├── README.md
├── requirements.txt
├── .env
└── src/
    ├── main.py           # Main script for data collection and processing
    ├── app.py           # Streamlit dashboard application
    ├── data_collector.py # CoinGecko API interaction and data collection
    ├── data_processor.py # Data analysis and processing functions
    └── config.py        # Configuration settings
```

## Data Collection

The application collects cryptocurrency price data for Q1 2025 from the CoinGecko API and stores it in a SQLite database. A valid CoinGecko API key is required for data collection.

## Data Processing

- Uses pandas for efficient data processing
- Calculates 5-day moving average
- Handles data cleaning and transformation
- Supports multiple cryptocurrencies

## Visualization

The Streamlit dashboard provides:
- Interactive price charts with moving averages
- Price comparison across different cryptocurrencies
- Key metrics and statistics:
  - Mean price
  - Standard deviation
  - Minimum and maximum prices
  - Price change percentage
- Market insights and analysis
- Raw data exploration

## Features

1. Multi-Coin Support:
   - Compare multiple cryptocurrencies
   - Individual analysis for each coin
   - Combined performance metrics

2. Data Analysis:
   - Price trends and patterns
   - Volatility analysis
   - Moving average calculations
   - Performance comparisons

3. User Interface:
   - Interactive charts
   - Customizable coin selection
   - Expandable data views
   - Real-time insights

## Assumptions

1. CoinGecko API availability and rate limits
2. Valid CoinGecko API key with appropriate access level
3. Sufficient local storage for SQLite database
4. Internet connectivity for API calls
5. Data quality from the API


## License

This project is licensed under the MIT License - see the LICENSE file for details. 
