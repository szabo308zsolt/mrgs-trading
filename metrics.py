import pandas as pd

def calculate_macd(df, fast=12, slow=26, signal=9):
    """Calculate MACD and Signal line."""
    exp1 = df['close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def calculate_vwap(df):
    """Calculate VWAP for a given DataFrame with columns: high, low, close, volume"""
    price = (df['high'] + df['low'] + df['close']) / 3
    vwap = (price * df['volume']).cumsum() / df['volume'].cumsum()
    return vwap
