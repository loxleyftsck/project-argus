"""CSV Loader - Load manually downloaded stock data

This script loads CSV files from data/raw/manual/ directory,
validates format, and prepares for analysis.

Supports CSV from:
- Yahoo Finance
- Stooq.com
- IDX website
- Investing.com
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import setup_logger
from src.utils.validators import DataQualityChecker

logger = setup_logger(__name__)


def detect_csv_format(df):
    """Detect which source the CSV came from.
    
    Returns:
        str: 'yahoo', 'stooq', 'idx', or 'unknown'
    """
    columns_lower = [c.lower() for c in df.columns]
    
    # Yahoo Finance: Date, Open, High, Low, Close, Adj Close, Volume
    if 'adj close' in columns_lower or 'adj_close' in columns_lower:
        return 'yahoo'
    
    # Stooq: Date, Open, High, Low, Close, Volume
    if 'date' in columns_lower and 'open' in columns_lower and len(df.columns) == 6:
        return 'stooq'
    
    # IDX: Various formats, usually has Kode/Code column
    if 'kode' in columns_lower or 'code' in columns_lower:
        return 'idx'
    
    return 'unknown'


def normalize_csv(file_path):
    """Load and normalize CSV to standard format.
    
    Args:
        file_path: Path to CSV file
    
    Returns:
        DataFrame with columns: Date, Open, High, Low, Close, Volume, Ticker
    """
    try:
        # Try different encodings
        for encoding in ['utf-8', 'latin1', 'iso-8859-1']:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except:
                continue
        
        if df is None:
            logger.error(f"Failed to read {file_path}")
            return None
        
        # Detect format
        source = detect_csv_format(df)
        logger.info(f"  Detected format: {source}")
        
        # Normalize column names
        df.columns = [c.strip().title().replace(' ', '_') for c in df.columns]
        
        # Standard columns
        required = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        
        # Map variations
        column_map = {
            'Tanggal': 'Date',
            'Tgl': 'Date',
            'Pembukaan': 'Open',
            'Tertinggi': 'High',
            'Terendah': 'Low',
            'Penutupan': 'Close',
            'Vol': 'Volume',
            'Adj_Close': 'Adj_Close'  # Keep but optional
        }
        
        df.rename(columns=column_map, inplace=True)
        
        # Convert Date to datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Extract ticker from filename if not in data
        if 'Ticker' not in df.columns:
            ticker = file_path.stem.split('_')[0].upper()
            if not ticker.endswith('.JK'):
                ticker = f"{ticker}.JK"
            df['Ticker'] = ticker
        
        # Keep only required + optional columns
        keep_cols = [c for c in required + ['Ticker', 'Adj_Close'] if c in df.columns]
        df = df[keep_cols]
        
        # Drop rows with missing critical data
        df.dropna(subset=['Date', 'Close'], inplace=True)
        
        # Sort by date
        df = df.sort_values('Date').reset_index(drop=True)
        
        logger.info(f"  Loaded {len(df)} records")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return None


def load_manual_csvs():
    """Load all CSV files from data/raw/manual directory."""
    
    logger.info("=" * 80)
    logger.info("LOADING MANUALLY DOWNLOADED CSV FILES")
    logger.info("=" * 80)
    
    manual_dir = Path("data/raw/manual")
    
    if not manual_dir.exists():
        manual_dir.mkdir(parents=True, exist_ok=True)
        logger.warning(f"\n❌ No manual CSV files found in: {manual_dir}")
        logger.info("\n📋 Please download CSV files and save to this directory")
        logger.info("   See: data/raw/MANUAL_DOWNLOAD_GUIDE.txt for instructions")
        return None
    
    # Find all CSV files
    csv_files = list(manual_dir.glob("*.csv"))
    
    if not csv_files:
        logger.warning(f"\n❌ No CSV files found in: {manual_dir}")
        logger.info("\n📋 Download stocks from Yahoo Finance:")
        logger.info("   1. https://finance.yahoo.com/quote/BBCA.JK/history")
        logger.info("   2. Click 'Download' → Save to data/raw/manual/")
        logger.info("   3. Repeat for GOTO.JK, BUMI.JK, etc.")
        return None
    
    logger.info(f"\nFound {len(csv_files)} CSV file(s):")
    for f in csv_files:
        logger.info(f"  📄 {f.name}")
    
    # Load and combine all CSVs
    all_data = []
    successful = []
    failed = []
    
    for csv_file in csv_files:
        logger.info(f"\n{'─'*60}")
        logger.info(f"Loading: {csv_file.name}")
        
        df = normalize_csv(csv_file)
        
        if df is not None and len(df) > 0:
            all_data.append(df)
            successful.append({
                'file': csv_file.name,
                'ticker': df['Ticker'].iloc[0],
                'records': len(df),
                'date_range': f"{df['Date'].min().date()} to {df['Date'].max().date()}"
            })
        else:
            failed.append(csv_file.name)
    
    if not all_data:
        logger.error("\n❌ No valid data loaded!")
        return None
    
    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Save combined dataset
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "manual_stocks_combined.csv"
    combined_df.to_csv(output_file, index=False)
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("LOADING SUMMARY")
    logger.info("=" * 80)
    
    logger.info(f"\n✅ Successfully loaded: {len(successful)} file(s)")
    for item in successful:
        logger.info(f"   {item['ticker']}: {item['records']} records ({item['date_range']})")
    
    if failed:
        logger.info(f"\n❌ Failed to load: {len(failed)} file(s)")
        for filename in failed:
            logger.info(f"   {filename}")
    
    logger.info(f"\n📊 Combined dataset:")
    logger.info(f"   Total records: {len(combined_df):,}")
    logger.info(f"   Stocks: {combined_df['Ticker'].unique().tolist()}")
    logger.info(f"   Date range: {combined_df['Date'].min().date()} to {combined_df['Date'].max().date()}")
    logger.info(f"\n💾 Saved to: {output_file}")
    
    # Run quality checks
    logger.info("\n" + "=" * 80)
    logger.info("DATA QUALITY CHECK")
    logger.info("=" * 80)
    
    for ticker in combined_df['Ticker'].unique():
        logger.info(f"\n{ticker}:")
        stock_df = combined_df[combined_df['Ticker'] == ticker]
        
        checker = DataQualityChecker(stock_df)
        report = checker.run_all_checks()
        
        logger.info(f"  Status: {report['overall_status']}")
        logger.info(f"  Completeness: {report['completeness']['score']:.1f}%")
        logger.info(f"  Consistency: {'PASS' if report['consistency']['pass'] else 'FAIL'}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ READY FOR WEEK 1 DEVELOPMENT!")
    logger.info("=" * 80)
    
    return combined_df


if __name__ == "__main__":
    df = load_manual_csvs()
    
    if df is not None:
        print(f"\n🎉 SUCCESS! {len(df)} records loaded")
        print(f"📁 Location: data/processed/manual_stocks_combined.csv")
        sys.exit(0)
    else:
        print("\n⚠️ No data loaded - manual download needed")
        sys.exit(1)
