# Quick Start Guide 🚀

## Pick Your Data Path & START Week 1

Choose ONE option below and execute. All paths work!

---

## 🎯 Option A: Synthetic Data (START NOW!)

**Time:** 0 seconds  
**Best For:** Immediate development start

```bash
# Verify data exists
python -c "import pandas as pd; df = pd.read_csv('data/raw/synthetic/sample_stocks_with_anomalies.csv'); print(f'✅ {len(df)} records ready! Stocks: {df.Ticker.unique()}')"

# Start Week 1 development
# You're ready to code statistical detectors!
```

---

## 📥 Option B: Manual Download (5 Minutes)

**Time:** 5 minutes  
**Best For:** Real data, portfolio proof

### Steps

1. Open: <https://finance.yahoo.com/quote/BBCA.JK/history>
2. Time Period → **6M**
3. Click **Download** button
4. Save to: `data/raw/manual/BBCA.csv`
5. Repeat: GOTO.JK, BUMI.JK
6. Run loader:

```bash
python src/scripts/load_manual_csv.py
```

---

## 🔑 Option C: Alpha Vantage API (5 Min Setup)

**Time:** 5 minutes signup  
**Best For:** Automated updates

### Steps

1. Get FREE API key: <https://www.alphavantage.co/support/#api-key>
2. Test it:

```python
import requests
import pandas as pd
from io import StringIO

url = "https://www.alphavantage.co/query"
params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': 'BBCA.JK',
    'apikey': 'YOUR_KEY_HERE',  # Replace!
    'outputsize': 'full',
    'datatype': 'csv'
}

response = requests.get(url, params=params)
df = pd.read_csv(StringIO(response.text))
print(f"✅ Downloaded {len(df)} records!")
df.to_csv('data/raw/manual/BBCA_alphavantage.csv', index=False)
```

---

## ✅ After Getting Data

Whichever option you chose, verify it worked:

```bash
# Check data directory
ls data/raw/manual/        # For Options B & C
ls data/raw/synthetic/     # For Option A

# Load and inspect
python -c "import pandas as pd; df = pd.read_csv('YOUR_DATA_FILE.csv'); print(df.head()); print(f'\\n{len(df)} records, {len(df.Ticker.unique())} stocks')"
```

---

## 🎯 Next: Week 1 Development

Now start implementing:

1. Feature engineering (Z-score, volatility)
2. Statistical detectors
3. MLflow logging
4. Test on anomalies

See: `implementation_plan.md` Week 1 section

---

**Status:** ✅ Data Ready → START CODING! 💪
