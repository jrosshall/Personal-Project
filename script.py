import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import datetime
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression
import seaborn as sns
import matplotlib.pyplot as plt
import logging
import os
import sys
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO)

def run_streamlit():
    """Launch the Streamlit app using the current script."""
    current_script = os.path.abspath(__file__)
    streamlit_cmd = [sys.executable, '-m', 'streamlit', 'run', current_script]
    subprocess.run(streamlit_cmd)

def is_streamlit_running():
    """Check if the script is being run by Streamlit."""
    try:
        # This will raise an exception if not running in Streamlit
        st.runtime.get_instance()
        return True
    except:
        return False

# -------------------------------------------
# Utility Functions
# -------------------------------------------

def fetch_crypto_data(crypto_id, days='90'):
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart'
        params = {'vs_currency': 'usd', 'days': days}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        prices = pd.DataFrame(data['prices'], columns=['Timestamp', 'Price'])
        prices['Date'] = pd.to_datetime(prices['Timestamp'], unit='ms').dt.date
        daily_prices = prices.groupby('Date').mean().reset_index()
        return daily_prices
    except:
        return pd.DataFrame(columns=['Date', 'Price'])

def fetch_stock_data(ticker, start, end):
    try:
        stock = yf.download(ticker, start=start, end=end)
        stock = stock[['Close']].reset_index()
        stock.columns = ['Date', 'Price']
        stock['Date'] = pd.to_datetime(stock['Date']).dt.date
        return stock
    except:
        return pd.DataFrame(columns=['Date', 'Price'])

def calculate_returns(df):
    df = df.copy()
    df['Return'] = df['Price'].pct_change()
    return df

def calculate_volatility(df):
    return df['Return'].std() * (252 ** 0.5) if not df['Return'].isnull().all() else 0.0

def linear_regression_forecast(df, days=10):
    df = df.dropna()
    if len(df) < 2:
        return pd.DataFrame(columns=['Date', 'Predicted Price'])
    df['Days'] = np.arange(len(df))
    X = df[['Days']]
    y = df['Price']
    model = LinearRegression().fit(X, y)
    future_days = np.arange(len(df), len(df) + days).reshape(-1, 1)
    preds = model.predict(future_days)
    future_dates = pd.date_range(start=pd.to_datetime(df['Date'].iloc[-1]) + pd.Timedelta(days=1), periods=days)
    return pd.DataFrame({'Date': future_dates, 'Predicted Price': preds})

# -------------------------------------------
# Streamlit UI
# -------------------------------------------

logging.info('Starting Streamlit application')

try:
    st.set_page_config(layout="wide")
    logging.info('Page config set')
    
    st.title("📊 Crypto vs. Stock Market Analysis (Enhanced)")
    logging.info('Title set')

    # Sidebar Inputs
    st.sidebar.header("Input Settings")
    cryptos = st.sidebar.multiselect("Choose Cryptocurrencies", ['bitcoin', 'ethereum', 'litecoin'], default=['bitcoin'])
    stocks = st.sidebar.multiselect("Choose Stock Tickers", ['SPY', 'AAPL', 'GOOGL'], default=['SPY'])
    days = st.sidebar.slider("Days of Data", 30, 365, 90)
    start_date = datetime.date.today() - datetime.timedelta(days=days)
    end_date = datetime.date.today()
    logging.info('Sidebar inputs set up')

except Exception as e:
    st.error(f"An error occurred during app initialization: {str(e)}")
    logging.error(f"Error during initialization: {str(e)}")
    st.stop()



try:
    # Display Data and Stats
    st.subheader("📈 Price & Performance")
    logging.info('Starting data display section')

    col1, col2 = st.columns(2)
    combined_series = []

    # CRYPTO
    for crypto in cryptos:
        try:
            logging.info(f'Fetching data for {crypto}')
            df = fetch_crypto_data(crypto, str(days))
            if df.empty:
                st.warning(f"No data found for {crypto}")
                continue
            
            df = calculate_returns(df)
            combined_series.append(pd.Series(df['Return'].values, index=df['Date'], name=f'{crypto}_return'))

            with col1:
                st.plotly_chart(px.line(df, x='Date', y='Price', title=f'{crypto.capitalize()} Price'), use_container_width=True)
            with col2:
                st.metric(f"{crypto.capitalize()} Volatility", f"{calculate_volatility(df):.2%}")
                st.metric(f"{crypto.capitalize()} Return", f"{df['Return'].sum():.2%}")
                if st.checkbox(f"Show {crypto.capitalize()} Forecast"):
                    forecast_df = linear_regression_forecast(df)
                    st.plotly_chart(px.line(forecast_df, x='Date', y='Predicted Price', title=f'{crypto.capitalize()} Forecast'), use_container_width=True)
            logging.info(f'Successfully processed {crypto} data')
            
        except Exception as e:
            st.error(f"Error processing {crypto}: {str(e)}")
            logging.error(f"Error processing {crypto}: {str(e)}")
            continue

    # STOCKS
    for stock in stocks:
        try:
            logging.info(f'Fetching data for {stock}')
            df = fetch_stock_data(stock, start=start_date, end=end_date)
            if df.empty:
                st.warning(f"No data found for {stock}")
                continue
            
            df = calculate_returns(df)
            combined_series.append(pd.Series(df['Return'].values, index=df['Date'], name=f'{stock}_return'))

            with col1:
                st.plotly_chart(px.line(df, x='Date', y='Price', title=f'{stock.upper()} Price'), use_container_width=True)
            with col2:
                st.metric(f"{stock.upper()} Volatility", f"{calculate_volatility(df):.2%}")
                st.metric(f"{stock.upper()} Return", f"{df['Return'].sum():.2%}")
                if st.checkbox(f"Show {stock.upper()} Forecast"):
                    forecast_df = linear_regression_forecast(df)
                    st.plotly_chart(px.line(forecast_df, x='Date', y='Predicted Price', title=f'{stock.upper()} Forecast'), use_container_width=True)
            logging.info(f'Successfully processed {stock} data')
            
        except Exception as e:
            st.error(f"Error processing {stock}: {str(e)}")
            logging.error(f"Error processing {stock}: {str(e)}")
            continue

except Exception as e:
    st.error(f"An error occurred while displaying data: {str(e)}")
    logging.error(f"Error in data display section: {str(e)}")
    st.stop()

try:
    # -------------------------------------------
    # Correlation & Volatility Heatmap
    # -------------------------------------------
    logging.info('Starting correlation and volatility analysis')

    st.subheader("🔁 Correlation Matrix & Volatility Heatmap")

    if combined_series:
        try:
            combined_df = pd.concat(combined_series, axis=1).dropna()

            if not combined_df.empty:
                corr = combined_df.corr()
                fig_corr, ax_corr = plt.subplots()
                sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax_corr)
                st.pyplot(fig_corr)
                logging.info('Correlation heatmap generated')

                st.subheader("🔥 Rolling Volatility Heatmap")
                rolling_vol = combined_df.rolling(window=7).std() * np.sqrt(252)
                fig_vol, ax_vol = plt.subplots()
                sns.heatmap(rolling_vol.T, cmap="YlGnBu", ax=ax_vol, cbar=True)
                ax_vol.set_xlabel("Time")
                ax_vol.set_ylabel("Assets")
                st.pyplot(fig_vol)
                logging.info('Volatility heatmap generated')
            else:
                st.info("Not enough overlapping data to display correlation or volatility heatmaps.")
        except Exception as e:
            st.error(f"Error generating heatmaps: {str(e)}")
            logging.error(f"Error in heatmap generation: {str(e)}")
    else:
        st.info("No return data collected for correlation analysis.")

    st.info('💡 You can run this app either by clicking Run in your IDE or using `streamlit run script.py` in your terminal.')
    logging.info('Application completed successfully')

except Exception as e:
    st.error(f"An error occurred in the analysis section: {str(e)}")
    logging.error(f"Error in analysis section: {str(e)}")
    st.stop()

if __name__ == '__main__' and not is_streamlit_running():
    print("Starting Streamlit application...")
    run_streamlit()
