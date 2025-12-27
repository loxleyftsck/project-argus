"""Real Data Acquisition - Multiple Source Fallback Strategy

Tries multiple methods to get REAL Indonesian stock data:
1. investpy (investing.com data)
2. Yahoo Finance direct download
3. Manual CSV from IDX website guidance

NO SYNTHETIC DATA - REAL ONLY!
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import requests
from io import StringIO

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def try_investpy(ticker, start_date, end_date):
    """Try getting data from investing.com via investpy library.
    
    Args:
        ticker: Stock ticker (without .JK suffix)
        start_date: Start date (DD/MM/YYYY)
        end_date: End date (DD/MM/YYYY)
    
    Returns:
        DataFrame or None
    """
    try:
        import investpy
        
        logger.info(f"Trying investpy for {ticker}...")
        
        # investpy uses different format
        df = investpy.get_stock_historical_data(
            stock=ticker,
            country='indonesia',
            from_date=start_date,
            to_date=end_date
        )
        
        if not df.empty:
            logger.info(f"✅ investpy SUCCESS: {len(df)} records for {ticker}")
            
            # Rename columns to match our format
            df.reset_index(inplace=True)
            df.rename(columns={'Date': 'Date'}, inplace=True)
            df['Ticker'] = f"{ticker}.JK"
            
            return df
        
    except Exception as e:
        logger.warning(f"investpy failed for {ticker}: {e}")
    
    return None


def try_yahoo_download_direct(ticker, start_date, end_date):
    """Try direct download from Yahoo Finance website (not API).
    
    Args:
        ticker: Stock ticker (e.g., BBCA.JK)
        start_date: datetime object
        end_date: datetime object
    
    Returns:
        DataFrame or None
    """
    try:
        logger.info(f"Trying Yahoo Finance direct download for {ticker}...")
        
        # Convert dates to Unix timestamps
        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())
        
        # Yahoo Finance download URL
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}"
        params = {
            'period1': start_ts,
            'period2': end_ts,
            'interval': '1d',
            'events': 'history',
            'includeAdjustedClose': 'true'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            
            if not df.empty and 'Date' in df.columns:
                logger.info(f"✅ Yahoo direct download SUCCESS: {len(df)} records for {ticker}")
                
                df['Ticker'] = ticker
                df['Date'] = pd.to_datetime(df['Date'])
                
                return df
        
        logger.warning(f"Yahoo download failed: HTTP {response.status_code}")
        
    except Exception as e:
        logger.warning(f"Yahoo direct download failed for {ticker}: {e}")
    
    return None


def try_idx_website_scraping(ticker):
    """Guide user to manually download from IDX website.
    
    Args:
        ticker: Stock ticker
    
    Returns:
        Instructions string
    """
    instructions = f"""
    
    ════════════════════════════════════════════════════════════════════
    MANUAL DOWNLOAD INSTRUCTIONS FOR {ticker}
    ════════════════════════════════════════════════════════════════════
    
    Since automated methods failed, here's how to get REAL data manually:
    
    📍 IDX Official Website (Most Reliable):
    
    1. Go to: https://www.idx.co.id/en/market-data/trading-data/stock/
    
    2. Search for stock code: {ticker.replace('.JK', '')}
    
    3. Click on "Historical Data" or "Trading Data"
    
    4. Select date range: Last 6 months or 1 year
    
    5. Download CSV
    
    6. Save to: data/raw/manual/{ticker.replace('.JK', '')}_real.csv
    
    ─────────────────────────────────────────────────────────────────────
    
    📍 Alternative: Yahoo Finance Website (Manual)
    
    1. Go to: https://finance.yahoo.com/quote/{ticker}/history
    
    2. Set "Time Period" to desired range
    
    3. Click "Download" button
    
    4. Save CSV to: data/raw/manual/{ticker.replace('.JK', '')}_yahoo.csv
    
    ─────────────────────────────────────────────────────────────────────
    
    📍 Alternative: Investing.com Website
    
    1. Go to: https://www.investing.com/
    
    2. Search: "{ticker.replace('.JK', '')} Indonesia"
    
    3. Navigate to "Historical Data" tab
    
    4. Download CSV
    
    5. Save to: data/raw/manual/{ticker.replace('.JK', '')}_investing.csv
    
    ════════════════════════════════════════════════════════════════════
    """
    
    return instructions


def acquire_real_data():
    """Main function to acquire REAL stock data using multiple methods."""
    
    logger.info("=" * 80)
    logger.info("REAL DATA ACQUISITION - NO SYNTHETIC!")
    logger.info("=" * 80)
    
    # Target stocks
    stocks = [
        'BBCA',  # Bank Central Asia
        'GOTO',  # GoTo
        'BUMI',  # Bumi Resources
        'BBRI',  # Bank Rakyat Indonesia
        'TLKM',  # Telkom
    ]
    
    # Date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # 6 months
    
    start_str_investpy = start_date.strftime('%d/%m/%Y')
    end_str_investpy = end_date.strftime('%d/%m/%Y')
    
    results = {
        'successful': [],
        'failed': [],
        'manual_instructions': []
    }
    
    # Create output directory
    output_dir = Path("data/raw/real")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    manual_dir = Path("data/raw/manual")
    manual_dir.mkdir(parents=True, exist_ok=True)
    
    for stock in stocks:
        ticker = f"{stock}.JK"
        logger.info(f"\n{'='*60}")
        logger.info(f"Attempting to acquire: {ticker}")
        logger.info(f"{'='*60}")
        
        data = None
        method = None
        
        # Method 1: investpy
        data = try_investpy(stock, start_str_investpy, end_str_investpy)
        if data is not None:
            method = "investpy"
        
        # Method 2: Yahoo direct download
        if data is None:
            data = try_yahoo_download_direct(ticker, start_date, end_date)
            if data is not None:
                method = "yahoo_direct"
        
        # Save if successful
        if data is not None:
            output_file = output_dir / f"{stock}_real.csv"
            data.to_csv(output_file, index=False)
            
            results['successful'].append({
                'ticker': ticker,
                'method': method,
                'records': len(data),
                'file': str(output_file)
            })
            
            logger.info(f"✅ SUCCESS via {method}: {len(data)} records")
            logger.info(f"   Saved to: {output_file}")
        else:
            results['failed'].append(ticker)
            instructions = try_idx_website_scraping(ticker)
            results['manual_instructions'].append(instructions)
            
            logger.warning(f"❌ All automated methods FAILED for {ticker}")
            logger.info(instructions)
    
    # Summary report
    logger.info("\n" + "=" * 80)
    logger.info("ACQUISITION SUMMARY")
    logger.info("=" * 80)
    
    logger.info(f"\n✅ Successful: {len(results['successful'])}/{len(stocks)}")
    for item in results['successful']:
        logger.info(f"   {item['ticker']}: {item['records']} records via {item['method']}")
    
    logger.info(f"\n❌ Failed (need manual download): {len(results['failed'])}/{len(stocks)}")
    for ticker in results['failed']:
        logger.info(f"   {ticker}")
    
    if results['failed']:
        logger.info("\n" + "⚠" * 40)
        logger.info("MANUAL DOWNLOAD REQUIRED FOR FAILED STOCKS")
        logger.info("⚠" * 40)
        logger.info("\nInstructions have been printed above.")
        logger.info("Please download CSV files and save to: data/raw/manual/")
    
    # Save summary
    summary_file = output_dir / "acquisition_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(f"Real Data Acquisition Summary\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"\nSuccessful: {len(results['successful'])}/{len(stocks)}\n")
        for item in results['successful']:
            f.write(f"  {item['ticker']}: {item['method']}\n")
        
        f.write(f"\nFailed: {len(results['failed'])}\n")
        for ticker in results['failed']:
            f.write(f"  {ticker}\n")
    
    logger.info(f"\nSummary saved to: {summary_file}")
    
    return results


if __name__ == "__main__":
    results = acquire_real_data()
    
    # Exit code based on success
    if len(results['successful']) > 0:
        print(f"\n🎉 SUCCESS! Got REAL data for {len(results['successful'])} stocks!")
        sys.exit(0)
    else:
        print("\n⚠️ No automated success. Manual download required.")
        sys.exit(1)
