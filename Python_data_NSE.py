import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import requests
from io import StringIO

# Step 1: Fetch all NSE symbols from official CSV
def get_nse_symbols():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = StringIO(response.text)
        df = pd.read_csv(data)
        return df['SYMBOL'].dropna().tolist()
    except Exception as e:
        print(f"Failed to fetch symbols: {e}")
        return []

# Step 2: Download historical stock data for last 2 years
def download_stock_data(symbols):
    start_date = datetime.now() - timedelta(days=730)
    end_date = datetime.now()
    os.makedirs("nse_data", exist_ok=True)

    for symbol in symbols:
        ticker = symbol + ".NS"
        try:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if not data.empty:
                data['Symbol'] = symbol
                data.to_csv(f"nse_data/{symbol}.csv", index=True)
                print(f"✅ {symbol} saved.")
            else:
                print(f"❌ No data for {symbol}")
        except Exception as e:
            print(f"⚠️ Error fetching {symbol}: {e}")
        time.sleep(0.5)  # rate limit


    return all_data

# Step 3: Save to single CSV
def save_to_csv(all_data):
    if all_data:
        df_all = pd.concat(all_data)
        os.makedirs("nse_data", exist_ok=True)
        df_all.to_csv("nse_data/combined_nse_data.csv", index=False)
        print("📁 All data saved to 'nse_data/combined_nse_data.csv'")
    else:
        print("🚫 No data to save.")

# Run the script
symbols = get_nse_symbols()
if symbols:
    print(f"Found {len(symbols)} symbols.")
    all_data = download_stock_data(symbols)
    save_to_csv(all_data)
else:
    print("⚠️ Could not retrieve any NSE stock symbols.")
