import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

try:
    import streamlit as st
    USING_STREAMLIT = True
    # Set page configuration
    st.set_page_config(page_title="Investment Goal Planner", layout="wide")
except:
    USING_STREAMLIT = False

# Major market indices and their tickers
INDICES = {
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Dow Jones": "^DJI",
    "Russell 2000": "^RUT"
}

def get_historical_data(ticker, start_date):
    """Fetch historical data for a given ticker"""
    stock = yf.Ticker(ticker)
    hist = stock.history(start=start_date)
    return hist

def calculate_metrics(hist_data):
    """Calculate key investment metrics"""
    annual_returns = hist_data['Close'].resample('Y').last().pct_change()
    metrics = {
        'avg_annual_return': annual_returns.mean(),
        'volatility': annual_returns.std(),
        'max_drawdown': (hist_data['Close'].min() - hist_data['Close'].max()) / hist_data['Close'].max(),
        'current_price': hist_data['Close'][-1]
    }
    return metrics

def calculate_investment_needs(goal_amount, years, annual_return):
    """Calculate required periodic investments"""
    r = annual_return
    n_years = years
    
    # Calculate yearly investment needed
    yearly = goal_amount / ((1 + r) ** n_years - 1) * r
    monthly = yearly / 12
    weekly = yearly / 52
    
    return {
        'yearly': yearly,
        'monthly': monthly,
        'weekly': weekly
    }

def run_streamlit_app():
    # Main app
    st.title("🎯 Investment Goal Planner")

    # User inputs
    col1, col2 = st.columns(2)

    with col1:
        goal_amount = st.number_input("Enter your savings goal ($)", min_value=1000, value=100000)
        goal_date = st.date_input("Target date to reach goal", 
                                min_value=datetime.now().date() + timedelta(days=365),
                                value=datetime.now().date() + timedelta(days=365*5))

    # Calculate time frame
    years_to_goal = (goal_date - datetime.now().date()).days / 365.25

    # Fetch and analyze historical data
    index_metrics = {}
    for index_name, ticker in INDICES.items():
        hist_data = get_historical_data(ticker, start_date=datetime.now().date() - timedelta(days=365*10))
        index_metrics[index_name] = calculate_metrics(hist_data)

    # Find best suited index based on goal timeframe and amount
    def get_index_score(metrics, years):
        return (
            metrics['avg_annual_return'] * 0.4 +
            (1 / abs(metrics['volatility'])) * 0.3 +
            (1 / abs(metrics['max_drawdown'])) * 0.3
        ) * (1 if years > 10 else 0.8)  # Penalty for shorter timeframes

    index_scores = {name: get_index_score(metrics, years_to_goal) 
                    for name, metrics in index_metrics.items()}

    recommended_index = max(index_scores, key=index_scores.get)

    # Display recommendations
    st.header("📊 Investment Recommendations")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Recommended Index")
        st.write(f"Based on your goals and timeframe, we recommend investing in the **{recommended_index}**")
        
        metrics = index_metrics[recommended_index]
        investment_needs = calculate_investment_needs(
            goal_amount, 
            years_to_goal, 
            metrics['avg_annual_return']
        )
        
        st.subheader("Required Investment Amounts")
        st.write(f"To reach your goal of **${goal_amount:,.2f}** by **{goal_date}**, you should invest:")
        st.write(f"🔹 ${investment_needs['yearly']:,.2f} yearly")
        st.write(f"🔹 ${investment_needs['monthly']:,.2f} monthly")
        st.write(f"🔹 ${investment_needs['weekly']:,.2f} weekly")

    with col2:
        st.subheader("Key Metrics")
        st.write(f"Average Annual Return: {metrics['avg_annual_return']*100:.1f}%")
        st.write(f"Volatility: {metrics['volatility']*100:.1f}%")
        st.write(f"Maximum Drawdown: {metrics['max_drawdown']*100:.1f}%")

    # Visualizations
    st.header("📈 Historical Performance")

    # Plot historical data for all indices
    fig = go.Figure()

    for index_name, ticker in INDICES.items():
        hist_data = get_historical_data(ticker, start_date=datetime.now().date() - timedelta(days=365*10))
        normalized_price = hist_data['Close'] / hist_data['Close'].iloc[0] * 100
        fig.add_trace(go.Scatter(
            x=hist_data.index,
            y=normalized_price,
            name=index_name,
            mode='lines'
        ))

    fig.update_layout(
        title='10-Year Performance Comparison (Normalized)',
        xaxis_title='Date',
        yaxis_title='Normalized Price (Base=100)',
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    # Educational section
    st.header("📚 Understanding the Metrics")

    with st.expander("What do these metrics mean?"):
        st.write("""
        - **Average Annual Return**: The mean yearly return of the index over the analyzed period.
        - **Volatility**: A measure of the price variation, indicating the investment's risk level.
        - **Maximum Drawdown**: The largest peak-to-trough decline, showing the worst-case historical scenario.
        
        Our recommendation algorithm considers these factors along with your time horizon to suggest the most suitable index.
        Remember that past performance doesn't guarantee future results.
        """)

    with st.expander("Investment Strategy Tips"):
        st.write("""
        1. **Consistency is Key**: Regular periodic investments (dollar-cost averaging) can help reduce the impact of market volatility.
        2. **Long-term Perspective**: The longer your investment horizon, the better chance you have of reaching your goals despite market fluctuations.
        3. **Risk Management**: Consider your personal risk tolerance when deciding on investment amounts and frequency.
        4. **Regular Review**: Periodically review and adjust your investment strategy as needed.
        """)

def run_cli_app():
    print("\n🎯 Investment Goal Planner\n")
    
    # Get user inputs
    goal_amount = float(input("Enter your savings goal ($): "))
    while True:
        try:
            target_date_str = input("Enter target date (YYYY-MM-DD): ")
            goal_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
            if goal_date <= datetime.now().date() + timedelta(days=365):
                print("Please enter a date at least 1 year in the future.")
                continue
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD format.")
    
    # Calculate time frame
    years_to_goal = (goal_date - datetime.now().date()).days / 365.25
    
    print("\nAnalyzing market data...")
    
    # Fetch and analyze historical data
    index_metrics = {}
    for index_name, ticker in INDICES.items():
        hist_data = get_historical_data(ticker, start_date=datetime.now().date() - timedelta(days=365*10))
        index_metrics[index_name] = calculate_metrics(hist_data)
    
    # Find best suited index
    def get_index_score(metrics, years):
        return (
            metrics['avg_annual_return'] * 0.4 +
            (1 / abs(metrics['volatility'])) * 0.3 +
            (1 / abs(metrics['max_drawdown'])) * 0.3
        ) * (1 if years > 10 else 0.8)
    
    index_scores = {name: get_index_score(metrics, years_to_goal) 
                    for name, metrics in index_metrics.items()}
    
    recommended_index = max(index_scores, key=index_scores.get)
    metrics = index_metrics[recommended_index]
    
    # Calculate investment needs
    investment_needs = calculate_investment_needs(
        goal_amount,
        years_to_goal,
        metrics['avg_annual_return']
    )
    
    # Display results
    print("\n📊 Investment Recommendations\n")
    print(f"Based on your goals and timeframe, we recommend investing in the {recommended_index}")
    print(f"\nTo reach your goal of ${goal_amount:,.2f} by {goal_date}, you should invest:")
    print(f"🔹 ${investment_needs['yearly']:,.2f} yearly")
    print(f"🔹 ${investment_needs['monthly']:,.2f} monthly")
    print(f"🔹 ${investment_needs['weekly']:,.2f} weekly")
    
    print("\nKey Metrics:")
    print(f"Average Annual Return: {metrics['avg_annual_return']*100:.1f}%")
    print(f"Volatility: {metrics['volatility']*100:.1f}%")
    print(f"Maximum Drawdown: {metrics['max_drawdown']*100:.1f}%")
    
    print("\nNote: For interactive visualizations and more detailed analysis,")
    print("run this program with 'streamlit run Personal_proj.py'")

if __name__ == "__main__":
    if USING_STREAMLIT:
        run_streamlit_app()
    else:
        run_cli_app()
