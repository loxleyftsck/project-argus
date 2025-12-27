"""Selenium Web Scraper for Yahoo Finance - AUTOMATED BROWSER

This uses Selenium to automate a real Chrome browser to download
historical stock data from Yahoo Finance. Works when APIs fail!

Requires: selenium, webdriver-manager
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import time

def setup_driver():
    """Setup Chrome driver with options."""
    print("🌐 Setting up Chrome browser...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run without opening browser window
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set download directory
    download_dir = str(Path("data/raw/selenium").absolute())
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Install and setup driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("✅ Browser ready!")
    return driver, download_dir


def scrape_yahoo_selenium(ticker, download_dir, driver):
    """Scrape stock data using Selenium browser automation.
    
    Args:
        ticker: Stock ticker (e.g., 'BBCA.JK')
        download_dir: Download directory path
        driver: Selenium WebDriver instance
    
    Returns:
        DataFrame or None
    """
    try:
        print(f"\n{'='*60}")
        print(f"🔍 Scraping {ticker} with Selenium...")
        
        # Navigate to Yahoo Finance historical data page
        url = f"https://finance.yahoo.com/quote/{ticker}/history"
        driver.get(url)
        
        # Wait for page to load
        print("  ⏳ Waiting for page to load...")
        time.sleep(3)
        
        # Set time period to max (or 6 months)
        try:
            # Click time period dropdown
            time_period_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'dropdown-toggle')]"))
            )
            time_period_btn.click()
            time.sleep(1)
            
            # Select "Max" or specific period
            max_option = driver.find_element(By.XPATH, "//button[contains(text(), '6M') or contains(text(), '6 mo')]")
            max_option.click()
            time.sleep(2)
            
        except Exception as e:
            print(f"  ⚠️ Could not set time period: {e}")
        
        # Find and click Download button
        print("  📥 Clicking Download button...")
        try:
            download_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@download, '') or contains(text(), 'Download')]"))
            )
            download_btn.click()
            
            print("  ⏳ Waiting for download...")
            time.sleep(5)  # Wait for download to complete
            
            # Find downloaded file
            download_path = Path(download_dir)
            csv_files = list(download_path.glob(f"{ticker}*.csv"))
            
            if csv_files:
                latest_file = max(csv_files, key=lambda p: p.stat().st_mtime)
                print(f"  ✅ Downloaded: {latest_file.name}")
                
                # Load and return data
                df = pd.read_csv(latest_file)
                df['Ticker'] = ticker
                
                print(f"  📊 Loaded {len(df)} records")
                return df
            else:
                print(f"  ❌ Download file not found")
                return None
                
        except Exception as e:
            print(f"  ❌ Download failed: {e}")
            return None
        
    except Exception as e:
        print(f"❌ Selenium scraping failed for {ticker}: {e}")
        return None


def main():
    """Main scraping function."""
    
    print("=" * 80)
    print("SELENIUM WEB SCRAPER - AUTOMATED BROWSER DOWNLOAD!")
    print("=" * 80)
    
    stocks = ['BBCA.JK', 'GOTO.JK', 'BUMI.JK', 'BBRI.JK', 'TLKM.JK']
    
    # Setup browser
    try:
        driver, download_dir = setup_driver()
    except Exception as e:
        print(f"\n❌ Failed to setup Chrome driver: {e}")
        print("\n💡 Make sure Chrome browser is installed on your system!")
        return []
    
    successful = []
    all_data = []
    
    try:
        for ticker in stocks:
            df = scrape_yahoo_selenium(ticker, download_dir, driver)
            
            if df is not None and len(df) > 0:
                all_data.append(df)
                successful.append({
                    'ticker': ticker,
                    'records': len(df)
                })
            
            # Be polite - wait between requests
            time.sleep(3)
        
    finally:
        # Always close browser
        print("\n🔒 Closing browser...")
        driver.quit()
    
    # Summary
    print("\n" + "=" * 80)
    print("SELENIUM SCRAPING SUMMARY")
    print("=" * 80)
    
    if successful:
        print(f"\n✅ Successfully scraped: {len(successful)}/{len(stocks)} stocks")
        for item in successful:
            print(f"   {item['ticker']}: {item['records']} records")
        
        # Combine and save
        combined_df = pd.concat(all_data, ignore_index=True)
        
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "selenium_scraped_data.csv"
        combined_df.to_csv(output_file, index=False)
        
        print(f"\n💾 Combined data saved: {output_file}")
        print(f"   Total records: {len(combined_df):,}")
        print(f"   Stocks: {combined_df['Ticker'].unique().tolist()}")
        
        print("\n🎉 SUCCESS! REAL DATA ACQUIRED!")
        
        return successful
    else:
        print("\n❌ All scraping attempts failed")
        print("\n💡 Possible issues:")
        print("   1. Chrome browser not installed")
        print("   2. Internet connection problems")
        print("   3. Yahoo Finance website blocked/changed")
        print("\n📋 Try manual download instead:")
        print("   https://finance.yahoo.com/quote/BBCA.JK/history")
        
        return []


if __name__ == "__main__":
    results = main()
    
    if results:
        exit(0)
    else:
        exit(1)
