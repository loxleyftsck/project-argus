"""Generate synthetic stock data for development and testing.

Since yfinance has limitations with Indonesian Stock Exchange data,
this script creates realistic synthetic data for algorithm development.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)


def generate_normal_trading_days(ticker, start_date, end_date, base_price=10000, volatility=0.02):
    """Generate normal trading data without anomalies.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        base_price: Starting price
        volatility: Daily price volatility (default 2%)
    
    Returns:
        DataFrame with OHLCV data
    """
    dates = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days only
    n_days = len(dates)
    
    # Generate prices with random walk
    returns = np.random.normal(0, volatility, n_days)
    prices = base_price * np.exp(np.cumsum(returns))
    
    # Generate OHLCV
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        # Intraday range (High/Low around close)
        daily_range = close * np.random.uniform(0.01, 0.03)
        high = close + np.random.uniform(0, daily_range)
        low = close - np.random.uniform(0, daily_range)
        open_price = np.random.uniform(low, high)
        
        # Volume (with some variation)
        base_volume = 1000000
        volume = int(base_volume * np.random.lognormal(0, 0.5))
        
        data.append({
            'Date': date,
            'Ticker': ticker,
            'Open': round(open_price, 2),
            'High': round(high, 2),
            'Low': round(low, 2),
            'Close': round(close, 2),
            'Volume': volume
        })
    
    return pd.DataFrame(data)


def inject_pump_and_dump(df, anomaly_date):
    """Inject pump and dump pattern at specific date.
    
    Args:
        df: DataFrame with stock data
        anomaly_date: Date to inject anomaly (YYYY-MM-DD)
    
    Returns:
        Modified DataFrame
    """
    df = df.copy()
    anomaly_date = pd.to_datetime(anomaly_date)
    
    # Find index of anomaly date
    idx = df[df['Date'] == anomaly_date].index
    if len(idx) == 0:
        return df
    
    idx = idx[0]
    
    # Pump phase (3 days before)
    for i in range(max(0, idx-3), idx):
        df.loc[i, 'Volume'] = df.loc[i, 'Volume'] * np.random.uniform(5, 8)  # 5-8x volume
        df.loc[i, 'Close'] = df.loc[i, 'Close'] * np.random.uniform(1.05, 1.15)  # 5-15% price increase
        df.loc[i, 'High'] = df.loc[i, 'Close'] * 1.02
        df.loc[i, 'Low'] = df.loc[i, 'Open'] * 0.98
    
    # Peak day
    df.loc[idx, 'Volume'] = df.loc[idx, 'Volume'] * 10  # 10x volume
    df.loc[idx, 'Close'] = df.loc[idx-1, 'Close'] * 1.20  # 20% spike
    df.loc[idx, 'High'] = df.loc[idx, 'Close'] * 1.05
    
    # Dump phase (3 days after)
    for i in range(idx+1, min(len(df), idx+4)):
        df.loc[i, 'Close'] = df.loc[i-1, 'Close'] * np.random.uniform(0.85, 0.95)  # 5-15% drop
        df.loc[i, 'Volume'] = df.loc[i, 'Volume'] * np.random.uniform(3, 5)  # High volume dump
        df.loc[i, 'Low'] = df.loc[i, 'Close'] * 0.95
        df.loc[i, 'High'] = df.loc[i, 'Open']
    
    return df


def generate_sample_dataset():
    """Generate complete sample dataset with normal and anomalous patterns."""
    
    # Date range: Last 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # Generate data for multiple stocks
    stocks = [
        {'ticker': 'BBCA.JK', 'name': 'Bank Central Asia', 'base_price': 9500, 'anomaly': '2024-11-15'},
        {'ticker': 'GOTO.JK', 'name': 'GoTo Gojek', 'base_price': 52, 'anomaly': '2024-10-20'},
        {'ticker': 'BUMI.JK', 'name': 'Bumi Resources', 'base_price': 120, 'anomaly': '2024-09-10'},
    ]
    
    all_data = []
    
    for stock in stocks:
        print(f"Generating data for {stock['ticker']}...")
        
        # Generate normal trading
        df = generate_normal_trading_days(
            stock['ticker'],
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            base_price=stock['base_price']
        )
        
        # Inject anomaly
        df = inject_pump_and_dump(df, stock['anomaly'])
        
        all_data.append(df)
    
    # Combine all stocks
    combined_df = pd.concat(all_data, ignore_index=True)
    
    return combined_df


def main():
    """Generate and save sample dataset."""
    print("=" * 80)
    print("GENERATING SYNTHETIC SAMPLE DATASET")
    print("=" * 80)
    print("\nPurpose: Development and testing while yfinance has limitations")
    print("Features: Normal trading + Pump & Dump anomalies injected\n")
    
    # Generate data
    df = generate_sample_dataset()
    
    # Create output directory
    output_dir = Path("data/raw/synthetic")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save combined dataset
    output_file = output_dir / "sample_stocks_with_anomalies.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ Dataset generated successfully!")
    print(f"   Location: {output_file}")
    print(f"   Total records: {len(df):,}")
    print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"   Stocks: {df['Ticker'].unique().tolist()}")
    
    # Save individual stock files
    for ticker in df['Ticker'].unique():
        stock_df = df[df['Ticker'] == ticker]
        stock_file = output_dir / f"{ticker.replace('.JK', '')}_synthetic.csv"
        stock_df.to_csv(stock_file, index=False)
        print(f"   Saved: {stock_file.name} ({len(stock_df)} records)")
    
    # Generate summary statistics
    print("\n" + "=" * 80)
    print("DATASET SUMMARY")
    print("=" * 80)
    
    for ticker in df['Ticker'].unique():
        stock_df = df[df['Ticker'] == ticker]
        print(f"\n{ticker}:")
        print(f"  Records: {len(stock_df)}")
        print(f"  Price range: ${stock_df['Close'].min():.2f} - ${stock_df['Close'].max():.2f}")
        print(f"  Avg volume: {stock_df['Volume'].mean():,.0f}")
        print(f"  Max volume: {stock_df['Volume'].max():,.0f}")
        
        # Find anomaly peaks
        volume_zscore = (stock_df['Volume'] - stock_df['Volume'].mean()) / stock_df['Volume'].std()
        anomalies = stock_df[volume_zscore > 3]
        if not anomalies.empty:
            print(f"  Anomaly dates: {anomalies['Date'].dt.strftime('%Y-%m-%d').tolist()}")
    
    print("\n" + "=" * 80)
    print("✅ Ready for Week 1 Development!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Use this synthetic data for feature engineering")
    print("2. Test statistical detectors (Z-score, volatility, correlation)")
    print("3. Validate detection on injected anomalies")
    print("4. Later: Replace with real data from CSV or alternative API")


if __name__ == "__main__":
    main()
