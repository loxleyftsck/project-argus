"""Week 0 Deliverable: Data Validation Script

Test yfinance API with 10 IDX stocks and generate quality control report.
This validates data pipeline reliability before building detection engine.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
import yfinance as yf

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import setup_logger
from src.utils.validators import DataQualityChecker
from src.utils.config import RAW_DATA_DIR, YFINANCE_TIMEOUT, YFINANCE_MAX_RETRIES

logger = setup_logger(__name__)


# Test stocks: Mix of blue-chip and mid-cap Indonesian stocks
TEST_TICKERS = [
    "BBCA.JK",  # Bank Central Asia (Blue-chip)
    "BBRI.JK",  # Bank Rakyat Indonesia (Blue-chip)
    "TLKM.JK",  # Telkom Indonesia (Blue-chip)
    "GOTO.JK",  # GoTo Gojek Tokopedia (Mid-cap, manipulation case 2024)
    "BUMI.JK",  # Bumi Resources (Mid-cap, suspension case 2023)
    "BMRI.JK",  # Bank Mandiri (Blue-chip)
    "ASII.JK",  # Astra International (Blue-chip)
    "UNVR.JK",  # Unilever Indonesia (Blue-chip)
    "ICBP.JK",  # Indofood CBP (Blue-chip)
    "KLBF.JK",  # Kalbe Farma (Mid-cap)
]


def fetch_stock_data(
    ticker: str,
    start_date: str,
    end_date: str,
    max_retries: int = YFINANCE_MAX_RETRIES
) -> pd.DataFrame:
    """Fetch stock data from yfinance with retry logic.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'BBCA.JK')
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        max_retries: Maximum number of retry attempts
    
    Returns:
        DataFrame with OHLCV data
    
    Raises:
        RuntimeError: If all retry attempts fail
    """
    logger.info(f"Fetching data for {ticker} from {start_date} to {end_date}")
    
    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date, timeout=YFINANCE_TIMEOUT)
            
            if df.empty:
                logger.warning(f"No data returned for {ticker} (attempt {attempt + 1}/{max_retries})")
                continue
            
            # Reset index to make Date a column
            df.reset_index(inplace=True)
            
            # Add ticker column
            df['Ticker'] = ticker
            
            logger.info(f"Successfully fetched {len(df)} rows for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching {ticker} (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise RuntimeError(f"Failed to fetch data for {ticker} after {max_retries} attempts")
    
    raise RuntimeError(f"Failed to fetch data for {ticker}")


def validate_data_pipeline() -> Dict:
    """Main validation function: test yfinance with 10 IDX stocks.
    
    Returns:
        Validation report with statistics and QC results
    """
    logger.info("=" * 80)
    logger.info("WEEK 0: DATA VALIDATION & QC")
    logger.info("=" * 80)
    
    # Define date range: Last 3 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    logger.info(f"Date range: {start_str} to {end_str}")
    logger.info(f"Testing {len(TEST_TICKERS)} stocks: {', '.join(TEST_TICKERS)}")
    
    results = {
        'test_date': datetime.now().isoformat(),
        'date_range': {'start': start_str, 'end': end_str},
        'stocks_tested': len(TEST_TICKERS),
        'successful_fetches': 0,
        'failed_fetches': 0,
        'quality_reports': {},
        'overall_status': 'PENDING'
    }
    
    all_data: List[pd.DataFrame] = []
    
    # Fetch data for each ticker
    for ticker in TEST_TICKERS:
        try:
            df = fetch_stock_data(ticker, start_str, end_str)
            
            # Run quality check
            checker = DataQualityChecker(df)
            qc_report = checker.run_all_checks()
            
            results['quality_reports'][ticker] = qc_report
            results['successful_fetches'] += 1
            
            # Save to CSV
            output_file = RAW_DATA_DIR / f"{ticker.replace('.JK', '')}_{start_str}_{end_str}.csv"
            df.to_csv(output_file, index=False)
            logger.info(f"Saved data to {output_file}")
            
            all_data.append(df)
            
        except Exception as e:
            logger.error(f"Failed to process {ticker}: {e}")
            results['failed_fetches'] += 1
            results['quality_reports'][ticker] = {
                'overall_status': 'ERROR',
                'error': str(e)
            }
    
    # Calculate aggregate statistics
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        results['statistics'] = {
            'total_records': len(combined_df),
            'date_range_coverage': {
                'earliest': combined_df['Date'].min().strftime('%Y-%m-%d'),
                'latest': combined_df['Date'].max().strftime('%Y-%m-%d')
            },
            'avg_records_per_stock': len(combined_df) // len(TEST_TICKERS)
        }
        
        # Save combined dataset
        combined_file = RAW_DATA_DIR / f"combined_test_data_{start_str}_{end_str}.csv"
        combined_df.to_csv(combined_file, index=False)
        logger.info(f"Saved combined dataset to {combined_file}")
    
    # Determine overall status
    passed_qc = sum(
        1 for report in results['quality_reports'].values()
        if report.get('overall_status') == 'PASS'
    )
    
    results['passed_qc'] = passed_qc
    results['overall_status'] = 'PASS' if passed_qc >= 7 else 'FAIL'  # 70% success rate
    
    return results


def generate_report(results: Dict) -> None:
    """Generate and save validation report.
    
    Args:
        results: Validation results dictionary
    """
    logger.info("=" * 80)
    logger.info("VALIDATION REPORT SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Stocks tested: {results['stocks_tested']}")
    logger.info(f"Successful fetches: {results['successful_fetches']}")
    logger.info(f"Failed fetches: {results['failed_fetches']}")
    logger.info(f"Passed QC: {results['passed_qc']}")
    logger.info(f"Overall status: {results['overall_status']}")
    
    if 'statistics' in results:
        logger.info(f"Total records: {results['statistics']['total_records']}")
        logger.info(
            f"Date coverage: {results['statistics']['date_range_coverage']['earliest']} "
            f"to {results['statistics']['date_range_coverage']['latest']}"
        )
    
    # Save JSON report
    report_file = RAW_DATA_DIR / "data_validation_report.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Full report saved to {report_file}")
    logger.info("=" * 80)


def main():
    """Main execution function."""
    try:
        results = validate_data_pipeline()
        generate_report(results)
        
        # Exit code based on status
        sys.exit(0 if results['overall_status'] == 'PASS' else 1)
        
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
