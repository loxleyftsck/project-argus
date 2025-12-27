"""Yahoo Finance Web Scraper - Last Resort for Real Data

This script uses requests + BeautifulSoup to scrape historical data
directly from Yahoo Finance website when API methods fail.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time
from bs4 import BeautifulSoup
import json

def scrape_yahoo_finance(ticker, start_date, end_date):
    """Scrape historical data from Yahoo Finance website.
    
    Args:
        ticker: Stock ticker (e.g., 'BBCA.JK')
        start_date: datetime object
        end_date: datetime object
    
    Returns:
        DataFrame with OHLCV data or None
    """
    try:
        print(f"🌐 Scraping Yahoo Finance for {ticker}...")
        
        # Convert to Unix timestamps
        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())
        
        # Yahoo Finance download URL (CSV download endpoint)
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}"
        
        params = {
            'period1': start_ts,
            'period2': end_ts,
            'interval': '1d',
            'events': 'history'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        session = requests.Session()
        response = session.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            
            if not df.empty and len(df) > 0:
                print(f"✅ Scraped {len(df)} records for {ticker}")
                df['Ticker'] = ticker
                return df
            else:
                print(f"⚠️ Got response but no data for {ticker}")
        else:
            print(f"❌ HTTP {response.status_code} for {ticker}")
            
    except Exception as e:
        print(f"❌ Scraping failed for {ticker}: {e}")
    
    return None


def main():
    """Download real data using web scraping."""
    
    print("=" * 80)
    print("YAHOO FINANCE WEB SCRAPER - GETTING REAL DATA!")
    print("=" * 80)
    
    # Target stocks
    stocks = ['BBCA.JK', 'GOTO.JK', 'BUMI.JK', 'BBRI.JK', 'TLKM.JK']
    
    # Date range: 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    print(f"\nDate range: {start_date.date()} to {end_date.date()}")
    print(f"Stocks to download: {len(stocks)}\n")
    
    # Create output directory
    output_dir = Path("data/raw/scraped")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    successful = []
    failed = []
    
    for ticker in stocks:
        print(f"\n{'─'*60}")
        df = scrape_yahoo_finance(ticker, start_date, end_date)
        
        if df is not None and len(df) > 0:
            # Save to CSV
            filename = f"{ticker.replace('.JK', '')}_scraped.csv"
            filepath = output_dir / filename
            df.to_csv(filepath, index=False)
            
            successful.append({
                'ticker': ticker,
                'records': len(df),
                'file': str(filepath)
            })
            
            print(f"💾 Saved: {filepath}")
        else:
            failed.append(ticker)
        
        # Be polite - don't hammer the server
        time.sleep(2)
    
    # Summary
    print("\n" + "=" * 80)
    print("SCRAPING SUMMARY")
    print("=" * 80)
    
    print(f"\n✅ Successful: {len(successful)}/{len(stocks)}")
    for item in successful:
        print(f"   {item['ticker']}: {item['records']} records → {item['file']}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}/{len(stocks)}")
        for ticker in failed:
            print(f"   {ticker}")
    
    # Save summary
    if successful:
        summary_file = output_dir / "scraping_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Web Scraping Summary\n")
            f.write(f"Date: {datetime.now()}\n\n")
            for item in successful:
                f.write(f"{item['ticker']}: {item['records']} records\n")
        
        print(f"\nSummary saved: {summary_file}")
        print("\n🎉 GOT REAL DATA! Ready for Week 1!")
    else:
        print("\n⚠️ All scraping attempts failed.")
        print("📋 Manual download required - see instructions below")
    
    return successful, failed


if __name__ == "__main__":
    successful, failed = main()
    
    if successful:
        exit(0)
    else:
        exit(1)
