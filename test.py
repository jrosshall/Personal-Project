import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Download historical stock data for Apple
ticker = 'AAPL'
data = yf.download(ticker, start='2023-01-01', end='2024-01-01')

# Display the first few rows
print("Stock Data:")
print(data.head())

# Plot closing price
plt.figure(figsize=(10, 5))
plt.plot(data['Close'], label='Close Price')
plt.title(f'{ticker} Stock Price (2023)')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
