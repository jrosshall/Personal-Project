import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Major market indices and their ETF tickers
INDICES = {
    "S&P 500": "SPY",    # SPDR S&P 500 ETF
    "Nasdaq": "QQQ",     # Invesco QQQ (Nasdaq-100)
    "Dow Jones": "DIA",  # SPDR Dow Jones Industrial Average ETF
    "Russell 2000": "IWM" # iShares Russell 2000 ETF
}

# Download 10 years of data for each index
start_date = datetime.now().date() - timedelta(days=365*10)
all_data = {}

print("Downloading market data...")
for index_name, ticker in INDICES.items():
    print(f"Fetching {index_name} data...")
    hist_data = yf.Ticker(ticker).history(start=start_date)
    all_data[index_name] = hist_data

# Save to CSV files
print("\nSaving data to files...")
for index_name, data in all_data.items():
    filename = f"market_data_{index_name.lower().replace(' ', '_').replace('&', 'and')}.csv"
    data.to_csv(filename)
    print(f"Saved {filename}")

print("\nDone! You can now use these CSV files with the investment planner.")
