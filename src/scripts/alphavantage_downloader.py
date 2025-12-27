"""Alpha Vantage Real Data Download Script

Free Tier Limits:
- 5 API calls per minute
- 500 API calls per day
- Good for 50-100 stocks with historical data

Get free API key: https://www.alphavantage.co/support/#api-key
"""

import requests
import pandas as pd
from io import StringIO
from pathlib import Path
from datetime import datetime
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

# 🔑 PASTE YOUR API KEY HERE (get it from https://www.alphavantage.co/support/#api-key)
ALPHA_VANTAGE_API_KEY = "0CCNG2M0YJV5QWAV"  # Alpha Vantage Free Tier API Key

# Stocks to download
STOCKS = [
    'BBCA.JK',  # Bank Central Asia
    'GOTO.JK',  # GoTo
    'BUMI.JK',  # Bumi Resources
    'BBRI.JK',  # Bank Rakyat Indonesia
    'TLKM.JK',  # Telkom
]

# Output directory
OUTPUT_DIR = Path("data/raw/alphavantage")

# ============================================================================
# FUNCTIONS
# ============================================================================

def download_stock_data(ticker, api_key):
    """Download historical data from Alpha Vantage.
    
    Args:
        ticker: Stock ticker (e.g., 'BBCA.JK')
        api_key: Alpha Vantage API key
    
    Returns:
        DataFrame or None
    """
    print(f"\n{'─'*60}")
    print(f"📥 Downloading {ticker}...")
    
    try:
        url = "https://www.alphavantage.co/query"
        
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': ticker,
            'apikey': api_key,
            'outputsize': 'compact',  # Free tier: last 100 days (full = premium only)
            'datatype': 'csv'
        }
        
        response = requests.get(url, params=params, timeout=20)
        
        if response.status_code == 200:
            # Check if we got CSV data (not an error message)
            if 'timestamp' in response.text.lower() or 'date' in response.text.lower():
                df = pd.read_csv(StringIO(response.text))
                
                # Rename timestamp column to Date if needed
                if 'timestamp' in df.columns:
                    df.rename(columns={'timestamp': 'Date'}, inplace=True)
                
                # Add ticker column
                df['Ticker'] = ticker
                
                # Convert Date to datetime
                df['Date'] = pd.to_datetime(df['Date'])
                
                # Sort by date
                df = df.sort_values('Date').reset_index(drop=True)
                
                print(f"  ✅ SUCCESS: {len(df)} records")
                print(f"  📅 Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
                
                return df
            else:
                # Check for error messages
                if 'error' in response.text.lower() or 'invalid' in response.text.lower():
                    print(f"  ❌ API Error: {response.text[:200]}")
                    
                    # Common error messages
                    if 'api key' in response.text.lower():
                        print(f"  ⚠️ HINT: Check your API key is correct!")
                    elif 'premium' in response.text.lower():
                        print(f"  ⚠️ HINT: This ticker might require premium tier")
                    elif 'limit' in response.text.lower():
                        print(f"  ⚠️ HINT: Rate limit reached - wait 1 minute")
                else:
                    print(f"  ⚠️ Unexpected response format")
                    print(f"  Response preview: {response.text[:300]}")
                
                return None
        else:
            print(f"  ❌ HTTP Error {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ❌ Download failed: {e}")
        return None


def main():
    """Main download function."""
    
    print("=" * 80)
    print("ALPHA VANTAGE REAL DATA DOWNLOAD")
    print("=" * 80)
    
    # Check API key
    if ALPHA_VANTAGE_API_KEY == "YOUR_API_KEY_HERE":
        print("\n❌ ERROR: API key not set!")
        print("\n📋 To fix:")
        print("1. Get free API key: https://www.alphavantage.co/support/#api-key")
        print("2. Open: src/scripts/alphavantage_downloader.py")
        print("3. Replace 'YOUR_API_KEY_HERE' with your actual key")
        print("4. Run this script again")
        return
    
    print(f"\n✅ API Key set: {ALPHA_VANTAGE_API_KEY[:8]}...")
    print(f"📊 Stocks to download: {len(STOCKS)}")
    print(f"⏱️ Rate limit: 5 calls/min (will wait between requests)")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    successful = []
    failed = []
    all_data = []
    
    for i, ticker in enumerate(STOCKS):
        # Download
        df = download_stock_data(ticker, ALPHA_VANTAGE_API_KEY)
        
        if df is not None and len(df) > 0:
            # Save individual file
            filename = f"{ticker.replace('.JK', '')}_alphavantage.csv"
            filepath = OUTPUT_DIR / filename
            df.to_csv(filepath, index=False)
            
            print(f"  💾 Saved: {filepath}")
            
            successful.append({
                'ticker': ticker,
                'records': len(df),
                'file': str(filepath)
            })
            
            all_data.append(df)
        else:
            failed.append(ticker)
        
        # Rate limiting: Wait 12 seconds between requests (5 calls/min = 1 call per 12 sec)
        if i < len(STOCKS) - 1:  # Don't wait after last stock
            wait_time = 13  # 13 seconds to be safe
            print(f"  ⏳ Waiting {wait_time}s (rate limit)...")
            time.sleep(wait_time)
    
    # Summary
    print("\n" + "=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)
    
    if successful:
        print(f"\n✅ Successfully downloaded: {len(successful)}/{len(STOCKS)} stocks")
        for item in successful:
            print(f"   {item['ticker']}: {item['records']:,} records")
        
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_file = OUTPUT_DIR / "all_stocks_combined.csv"
        combined_df.to_csv(combined_file, index=False)
        
        print(f"\n📊 Combined dataset:")
        print(f"   Total records: {len(combined_df):,}")
        print(f"   Stocks: {combined_df['Ticker'].nunique()}")
        print(f"   Date range: {combined_df['Date'].min().date()} to {combined_df['Date'].max().date()}")
        print(f"\n💾 Saved to: {combined_file}")
        
        print("\n🎉 SUCCESS! REAL DATA DOWNLOADED!")
        print("✅ Ready for Week 1 development!")
        
    else:
        print("\n❌ No stocks downloaded successfully")
    
    if failed:
        print(f"\n⚠️ Failed stocks: {failed}")
        print("\n💡 Troubleshooting:")
        print("   - Check API key is correct")
        print("   - Verify internet connection")
        print("   - Wait if rate limited (500 calls/day)")
        print("   - Some IDX stocks might not be available")


if __name__ == "__main__":
    main()
