import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

# User input for crypto and stock
crypto_symbol = input("Enter crypto symbol (e.g., BTC-USD): ")
stock_symbol = input("Enter stock symbol (e.g., SPY): ")

# Set timeframe
start_date = '2020-01-01'
end_date = datetime.datetime.today().strftime('%Y-%m-%d')

# Download data
crypto = yf.download(crypto_symbol, start=start_date, end=end_date)
stock = yf.download(stock_symbol, start=start_date, end=end_date)

# Rename columns to distinguish
crypto = crypto[['Close']].rename(columns={'Close': 'Crypto_Close'})
stock = stock[['Close']].rename(columns={'Close': 'Stock_Close'})

# Merge data
df = pd.merge(crypto, stock, left_index=True, right_index=True, how='inner')

# Calculate daily returns
df['Crypto_Return'] = df['Crypto_Close'].pct_change()
df['Stock_Return'] = df['Stock_Close'].pct_change()

# Drop NaN rows
df.dropna(inplace=True)

# Calculate correlation
correlation = df['Crypto_Return'].corr(df['Stock_Return'])

# Print correlation
print(f"\nCorrelation between {crypto_symbol} and {stock_symbol} daily returns: {correlation:.4f}")

# Plot normalized prices
df['Crypto_Normalized'] = df['Crypto_Close'] / df['Crypto_Close'].iloc[0]
df['Stock_Normalized'] = df['Stock_Close'] / df['Stock_Close'].iloc[0]

plt.figure(figsize=(12,6))
plt.plot(df.index, df['Crypto_Normalized'], label=crypto_symbol)
plt.plot(df.index, df['Stock_Normalized'], label=stock_symbol)
plt.title(f"{crypto_symbol} vs {stock_symbol} Performance Since {start_date}")
plt.xlabel("Date")
plt.ylabel("Normalized Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot return correlation scatter
plt.figure(figsize=(8,6))
sns.scatterplot(x='Stock_Return', y='Crypto_Return', data=df, alpha=0.5)
plt.title(f"Daily Return Correlation: {crypto_symbol} vs {stock_symbol}")
plt.xlabel(f"{stock_symbol} Daily Return")
plt.ylabel(f"{crypto_symbol} Daily Return")
plt.grid(True)
plt.tight_layout()
plt.show()

# Optional: Rolling correlation
df['Rolling_Correlation'] = df['Crypto_Return'].rolling(window=30).corr(df['Stock_Return'])

plt.figure(figsize=(12,6))
plt.plot(df.index, df['Rolling_Correlation'], label='30-Day Rolling Correlation', color='purple')
plt.title(f"30-Day Rolling Correlation: {crypto_symbol} vs {stock_symbol}")
plt.xlabel("Date")
plt.ylabel("Correlation")
plt.axhline(0, color='gray', linestyle='--')
plt.grid(True)
plt.tight_layout()
plt.legend()
plt.show()
