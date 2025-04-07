from datetime import datetime, timezone
import os

# API Configuration
COINGECKO_API_BASE_URL = "https://api.coingecko.com/api/v3"

# Database Configuration
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "crypto.db")

# Date Range Configuration
START_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)  # Start ofQ1 2025
END_DATE = datetime(2025, 3, 31, 23, 59, 59, tzinfo=timezone.utc)   # End of Q1 2025

# Moving Average Configuration
MOVING_AVERAGE_WINDOW = 5

# API Rate Limiting
RATE_LIMIT = 10  # requests per minute 