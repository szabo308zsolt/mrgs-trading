import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
from yahooquery import Ticker  # <-- Use yahooquery

def get_sp500_symbols():
    """Get the list of S&P 500 symbols from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'wikitable'})
    symbols = []
    for row in table.findAll('tr')[1:]:
        symbol = row.findAll('td')[0].text.strip()
        symbols.append(symbol)
    return symbols

def download_stock_data(symbol, start_date, end_date):
    """Download stock data for a given symbol and date range using yahooquery."""
    try:
        ticker = Ticker(symbol)
        # yahooquery expects dates as strings in 'YYYY-MM-DD' format
        df = ticker.history(start=str(start_date), end=str(end_date))
        if df.empty:
            return None
        # If multiple symbols, df is multi-indexed; select only the symbol
        if isinstance(df.index, pd.MultiIndex):
            df = df.xs(symbol)
        df.index = pd.to_datetime(df.index)
        return df
    except Exception as e:
        st.error(f"Error downloading data for {symbol}: {str(e)}")
        return None

def plot_stock_data(df, symbol):
    """Create an interactive plot using Plotly."""
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='OHLC'
    ))
    
    fig.update_layout(
        title=f'{symbol} Stock Price',
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        template='plotly_dark'
    )
    
    return fig

# Set page config
st.set_page_config(page_title="S&P 500 Stock Dashboard", layout="wide")

# Title
st.title("S&P 500 Stock Dashboard")

# Sidebar
st.sidebar.header("Settings")

# Date range selection
end_date = date.today()
start_date = end_date - timedelta(days=365)
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start Date", start_date)
with col2:
    end_date = st.date_input("End Date", end_date)

# Get S&P 500 symbols
symbols = get_sp500_symbols()

# Symbol selection
selected_symbol = st.sidebar.selectbox("Select Stock", symbols)

# Download and display data
if selected_symbol:
    st.subheader(f"Stock Data for {selected_symbol}")
    
    # Download data
    df = download_stock_data(selected_symbol, start_date, end_date)
    
    if df is not None and not df.empty:
        # Display the plot
        fig = plot_stock_data(df, selected_symbol)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display raw data
        st.subheader("Raw Data")
        st.dataframe(df)
        
        # Display statistics
        st.subheader("Statistics")
        stats = df['close'].describe()
        st.write(stats)
    else:
        st.error("No data available for the selected period.")