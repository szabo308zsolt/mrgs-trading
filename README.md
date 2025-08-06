# S&P 500 Stock Dashboard

This is a Streamlit application that allows you to visualize and analyze stock data for S&P 500 companies. The application provides interactive charts, raw data, and basic statistics for any selected stock.

## Features

- Real-time S&P 500 stock data using Yahoo Finance API
- Interactive candlestick charts using Plotly
- Date range selection
- Raw data display
- Basic statistics
- Dark theme for better visualization

## Installation

1. Clone this repository
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:
```bash
streamlit run sp500_dashboard.py
```

The application will open in your default web browser. You can:
1. Select a date range using the date pickers in the sidebar
2. Choose a stock from the S&P 500 list
3. View the interactive chart, raw data, and statistics

## Project Structure

- `sp500_dashboard.py` - Main Streamlit app
- `metrics.py` - Calculation functions for indicators
- `data/` - Folder for storing downloaded or cached stock data

## Dependencies

- streamlit
- pandas
- yfinance
- plotly
- requests
- beautifulsoup4 

## TODO

- Add ability to save file that it's downloaded to a csv file. 
- Add ability to read from the csv file when it's available, and only download new data incrementally
- Add ability to download all data from the past at once, keeping the downloads incremental
- Add ability to display a metric next to the daily data
- Add ability to