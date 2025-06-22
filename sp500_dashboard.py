import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
from yahooquery import Ticker  # <-- Use yahooquery
from metrics import calculate_macd, calculate_vwap  # <-- Import from metrics.py

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

def plot_stock_data(df, symbol, indicators=None, voo_df=None, macd_tuple=None, vwap=None):
    """Create an interactive plot using Plotly, with optional indicators."""
    from plotly.subplots import make_subplots
    has_macd = indicators and "MACD" in indicators and macd_tuple is not None
    rows = 2 if has_macd else 1
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        row_heights=[0.7, 0.3] if has_macd else [1.0],
                        vertical_spacing=0.05 if has_macd else 0.0)
    # Main candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name=f'{symbol} OHLC'
    ), row=1, col=1)
    # VWAP overlay
    if indicators and "VWAP" in indicators and vwap is not None:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=vwap,
            mode='lines',
            name='VWAP',
            line=dict(color='orange', width=2)
        ), row=1, col=1)
    # MACD subplot
    if has_macd:
        macd, signal_line = macd_tuple
        fig.add_trace(go.Scatter(
            x=df.index,
            y=macd,
            mode='lines',
            name='MACD',
            line=dict(color='cyan')
        ), row=2, col=1)
        fig.add_trace(go.Scatter(
            x=df.index,
            y=signal_line,
            mode='lines',
            name='Signal',
            line=dict(color='magenta')
        ), row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_layout(
        title=f'{symbol} Stock Price',
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        template='plotly_dark',
        height=700 if has_macd else 500
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

# Indicator selection (below stock selector)
indicator_options = ["MACD", "VWAP"] 
selected_indicators = st.sidebar.multiselect(
    "Show Trading Indicators", indicator_options, default=[]
)

# Download and display data
if selected_symbol:
    st.subheader(f"Stock Data for {selected_symbol}")
    
    # Download data
    df = download_stock_data(selected_symbol, start_date, end_date)
    
    # Calculate VWAP if needed
    vwap = None
    if "VWAP" in selected_indicators and df is not None and not df.empty:
        vwap = calculate_vwap(df)
    
    # Calculate MACD if needed
    macd_tuple = None
    if "MACD" in selected_indicators and df is not None and not df.empty:
        macd_tuple = calculate_macd(df)
    
    if df is not None and not df.empty:
        # Display the plot
        fig = plot_stock_data(df, selected_symbol, indicators=selected_indicators, voo_df=None, macd_tuple=macd_tuple, vwap=vwap)
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