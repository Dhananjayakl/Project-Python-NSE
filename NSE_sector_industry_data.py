import pandas as pd
import requests
import time
import yfinance as yf
from io import StringIO

# Step 1: Download NSE stock list
def fetch_nse_stock_list():
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
        print(f"❌ Failed to fetch symbols: {e}")
        return []

# Step 2: Get sector and industry from yfinance
def get_sector_industry(symbols):
    info_list = []
    failed_list = []

    for symbol in symbols:
        ticker = symbol + ".NS"
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            sector = info.get("sector", "N/A")
            industry = info.get("industry", "N/A")

            if sector == "N/A" and industry == "N/A":
                raise ValueError("Sector/Industry not available")

            info_list.append({
                "Symbol": symbol,
                "Sector": sector,
                "Industry": industry
            })
            print(f"✅ {symbol} → Sector: {sector}, Industry: {industry}")
        except Exception as e:
            print(f"⚠️ Failed to get info for {symbol}: {e}")
            failed_list.append(symbol)

        time.sleep(0.1)  # Delay to avoid rate limits

    # Save failed symbols
    if failed_list:
        pd.DataFrame({"Symbol": failed_list}).to_csv("failed_symbols.csv", index=False)
        print(f"⚠️ {len(failed_list)} symbols failed. Saved to 'failed_symbols.csv'")

    return pd.DataFrame(info_list)

# Step 3: Run the pipeline
symbols = fetch_nse_stock_list()
if symbols:
    df_info = get_sector_industry(symbols)
    df_info.to_csv("nse_stock_sector_industry.csv", index=False)
    print("📁 Saved sector/industry info to 'nse_stock_sector_industry.csv'")
else:
    print("❌ No symbols to process.")
