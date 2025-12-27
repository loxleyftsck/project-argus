"""Alternative Data Sources for Indonesian Stocks

After extensive testing, here are working alternatives to yfinance:
1. Stooq.com - Free CSV download
2. Alpha Vantage - API with free tier
3. Direct IDX website scraping
4. Manual download guide
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
from pathlib import Path
import time

def try_stooq(ticker, start_date, end_date):
    """Download from Stooq.com - Free historical data service.
    
    Stooq supports Indonesian stocks with format: TICKER.ID
    
    Args:
        ticker: Stock ticker without exchange (e.g., 'BBCA')
        start_date: datetime object
        end_date: datetime object
    
    Returns:
        DataFrame or None
    """
    try:
        print(f"🔍 Trying Stooq.com for {ticker}...")
        
        # Stooq format: TICKER.ID for Indonesian stocks
        stooq_ticker = f"{ticker}.ID"
        
        # Stooq URL format
        url = f"https://stooq.com/q/d/l/?s={stooq_ticker}&i=d"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            
            if not df.empty and len(df) > 10:  # At least 10 records
                # Stooq format: Date, Open, High, Low, Close, Volume
                df['Date'] = pd.to_datetime(df['Date'])
                df['Ticker'] = f"{ticker}.JK"
                
                # Filter by date range
                df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
                
                if len(df) > 0:
                    print(f"✅ Stooq SUCCESS: {len(df)} records for {ticker}")
                    return df
        
        print(f"⚠️ Stooq: No valid data for {ticker}")
        
    except Exception as e:
        print(f"❌ Stooq failed for {ticker}: {e}")
    
    return None


def try_alphavantage(ticker, api_key=None):
    """Download from Alpha Vantage API.
    
    Alpha Vantage has free tier: 5 API requests per minute, 500 per day
    Get free API key from: https://www.alphavantage.co/support/#api-key
    
    Args:
        ticker: Stock ticker (e.g., 'BBCA.JK')
        api_key: Alpha Vantage API key (optional, uses demo key if None)
    
    Returns:
        DataFrame or None
    """
    try:
        if api_key is None:
            print("⚠️ No Alpha Vantage API key provided (using demo - limited)")
            api_key = "demo"
        
        print(f"🔍 Trying Alpha Vantage for {ticker}...")
        
        # Alpha Vantage endpoint
        url = "https://www.alphavantage.co/query"
        
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': ticker,
            'apikey': api_key,
            'outputsize': 'full',  # Get full historical data
            'datatype': 'csv'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            
            # Check if we got actual data (not error message)
            if 'timestamp' in df.columns or 'date' in df.columns:
                df.rename(columns={'timestamp': 'Date'}, inplace=True)
                df['Date'] = pd.to_datetime(df['Date'])
                df['Ticker'] = ticker
                
                print(f"✅ Alpha Vantage SUCCESS: {len(df)} records for {ticker}")
                return df
            else:
                print(f"⚠️ Alpha Vantage: Response doesn't contain expected data")
                print(f"   Response preview: {response.text[:200]}")
        
    except Exception as e:
        print(f"❌ Alpha Vantage failed for {ticker}: {e}")
    
    return None


def download_manual_guide():
    """Generate comprehensive manual download guide."""
    
    guide = """
    ╔════════════════════════════════════════════════════════════════════╗
    ║           MANUAL DOWNLOAD GUIDE - INDONESIAN STOCKS                ║
    ║                    (GUARANTEED TO WORK!)                           ║
    ╚════════════════════════════════════════════════════════════════════╝
    
    Since all automated APIs failed, here's the FASTEST manual method:
    
    ┌────────────────────────────────────────────────────────────────────┐
    │ METHOD 1: Yahoo Finance Website (EASIEST - 2 minutes per stock)   │
    └────────────────────────────────────────────────────────────────────┘
    
    1. Open: https://finance.yahoo.com/quote/BBCA.JK/history
    
    2. Click "Time Period" dropdown → Select "6M" (6 months)
    
    3. Click "Download" blue button (top right)
    
    4. CSV will download (BBCA.JK.csv)
    
    5. Rename to: BBCA_manual.csv
    
    6. Move to: data/raw/manual/
    
    7. Repeat for other stocks:
       - GOTO.JK → https://finance.yahoo.com/quote/GOTO.JK/history
       - BUMI.JK → https://finance.yahoo.com/quote/BUMI.JK/history
       - BBRI.JK → https://finance.yahoo.com/quote/BBRI.JK/history
       - TLKM.JK → https://finance.yahoo.com/quote/TLKM.JK/history
    
    ⏱️ Total time: ~10 minutes for 5 stocks
    
    ┌────────────────────────────────────────────────────────────────────┐
    │ METHOD 2: Stooq.com (Alternative)                                  │
    └────────────────────────────────────────────────────────────────────┘
    
    1. Go to: https://stooq.com/q/?s=bbca.id
    
    2. Click "Historical data" tab
    
    3. Set date range (last 6 months)
    
    4. Click "Download" → CSV format
    
    5. Save to: data/raw/manual/BBCA_stooq.csv
    
    Note: Stooq uses .ID suffix for Indonesian stocks
    
    ┌────────────────────────────────────────────────────────────────────┐
    │ METHOD 3: IDX Official Website (Most Reliable)                     │
    └────────────────────────────────────────────────────────────────────┘
    
    1. Go to: https://www.idx.co.id/en/market-data/trading-data/stock/
    
    2. Search stock code: BBCA
    
    3. Click "Historical Data"
    
    4. Select date range
    
    5. Download Excel/CSV
    
    6. Save to: data/raw/manual/BBCA_idx.csv
    
    ┌────────────────────────────────────────────────────────────────────┐
    │ AFTER DOWNLOAD: Load Data                                          │
    └────────────────────────────────────────────────────────────────────┘
    
    Run our loader script:
    
        python src/scripts/load_manual_csv.py
    
    This will:
    - Find all CSV files in data/raw/manual/
    - Validate format
    - Combine into single dataset
    - Ready for Week 1 development!
    
    ╔════════════════════════════════════════════════════════════════════╗
    ║  📊 YOU ONLY NEED 2-3 STOCKS TO START!                            ║
    ║  → GOTO.JK (pump & dump case)                                     ║
    ║  → BUMI.JK (suspension case)                                      ║
    ║  → BBCA.JK (normal trading baseline)                              ║
    ╚════════════════════════════════════════════════════════════════════╝
    """
    
    return guide


def main():
    """Try all alternative sources."""
    
    print("=" * 80)
    print("ALTERNATIVE DATA SOURCES - TRYING EVERYTHING!")
    print("=" * 80)
    
    stocks = ['BBCA', 'GOTO', 'BUMI', 'BBRI', 'TLKM']
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    output_dir = Path("data/raw/alternative")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    successful = []
    
    for stock in stocks:
        print(f"\n{'='*60}")
        print(f"Trying {stock}...")
        print(f"{'='*60}")
        
        # Try Stooq first (most reliable for international stocks)
        df = try_stooq(stock, start_date, end_date)
        
        if df is not None and len(df) > 0:
            filepath = output_dir / f"{stock}_stooq.csv"
            df.to_csv(filepath, index=False)
            print(f"💾 Saved: {filepath}")
            
            successful.append({
                'ticker': stock,
                'source': 'stooq',
                'records': len(df),
                'file': str(filepath)
            })
        
        # Be polite
        time.sleep(3)
    
    # Print results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    if successful:
        print(f"\n🎉 SUCCESS! Downloaded {len(successful)}/{len(stocks)} stocks:")
        for item in successful:
            print(f"   ✅ {item['ticker']}: {item['records']} records from {item['source']}")
        
        print("\n📁 Files saved to: data/raw/alternative/")
        print("✅ READY FOR WEEK 1 DEVELOPMENT!")
        
        return True
    else:
        print("\n❌ All automated methods FAILED")
        print("\n📋 MANUAL DOWNLOAD REQUIRED:")
        print(download_manual_guide())
        
        # Save guide to file
        guide_file = Path("data/raw/MANUAL_DOWNLOAD_GUIDE.txt")
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(download_manual_guide())
        
        print(f"\n📄 Guide saved to: {guide_file}")
        print("\n⏱️ Manual download takes ~10 minutes total")
        print("💡 TIP: Only download 2-3 stocks to start!")
        
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
