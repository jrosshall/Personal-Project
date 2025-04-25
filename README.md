# Investment Goal Planner

A Python application that helps users determine how much they need to invest to reach their financial goals. The application analyzes historical market data and provides personalized investment recommendations.

## Features

- Calculate required periodic investments (weekly, monthly, yearly)
- Analyze historical performance of major market indices
- Provide visual comparisons of different market indices
- Recommend the best-suited market index based on your goals
- Display key market metrics and educational content

## Requirements

- Python 3.7+
- Required packages are listed in `requirements.txt`

## Installation

1. Clone this repository:
```bash
git clone <your-repository-url>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

You can run the application in two ways:

1. Web Interface (recommended):
```bash
streamlit run Personal_proj.py
```

2. Command Line Interface:
```bash
python Personal_proj.py
```

## Data Sources

The application uses historical market data from:
- S&P 500 (SPY)
- Nasdaq (QQQ)
- Dow Jones (DIA)
- Russell 2000 (IWM)

Data is fetched using the yfinance library.
