import pandas as pd
import os
import yfinance as yf
from datetime import datetime
import time

def load_all_stock_data(folder='nse_data'):
    all_dfs = []
    for filename in os.listdir(folder):
        if filename.endswith(".csv"):
            filepath = os.path.join(folder, filename)
            try:
                # Skip first 2 rows of metadata
                df = pd.read_csv(filepath, skiprows=2)

                # Ensure required columns exist
                if 'Date' not in df.columns or 'Close' not in df.columns:
                    print(f" Skipping {filename}: Required columns missing.")
                    continue

                df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
                df['Symbol'] = filename.replace(".csv", "")
                all_dfs.append(df)
            except Exception as e:
                print(f" Failed to load {filename}: {e}")
    return all_dfs


def get_fundamentals(symbol):
    try:
        ticker = yf.Ticker(symbol + ".NS")
        info = ticker.info
        market_cap = info.get("marketCap", 0)
        pe_ratio = info.get("trailingPE", None)
        return market_cap, pe_ratio
    except Exception as e:
        print(f"Error fetching fundamentals for {symbol}: {e}")
        return 0, None

def filter_stocks(all_dfs, days_limit=365):
    result = []
    for df in all_dfs:
        try:
            df = df.sort_values('Date')
            symbol = df['Symbol'].iloc[0]
            date_range = (df['Date'].max() - df['Date'].min()).days

            if date_range <= days_limit:
                df['50DMA'] = df['Close'].rolling(window=50).mean()
                df['20DMA'] = df['Close'].rolling(window=20).mean()
                latest = df.iloc[-1]
                close = latest['Close']
                above_dma = (
                    "Both" if close > latest['50DMA'] and close > latest['20DMA']
                    else "50DMA" if close > latest['50DMA']
                    else "20DMA" if close > latest['20DMA']
                    else None
                )

                if above_dma:
                    market_cap, pe_ratio = get_fundamentals(symbol)
                    time.sleep(0.5)  # rate limiting

                    if market_cap and market_cap >= 2000 * 1e7 and pe_ratio and pe_ratio < 100:
                        result.append({
                            "Symbol": symbol,
                            "Listed_Days": date_range,
                            "Close": close,
                            "50DMA": latest['50DMA'],
                            "20DMA": latest['20DMA'],
                            "Above_Which_DMA": above_dma,
                            "Market_Cap_Cr": round(market_cap / 1e7, 2),
                            "PE_Ratio": round(pe_ratio, 2)
                        })
        except Exception as e:
            print(f" Error processing {df['Symbol'].iloc[0]}: {e}")
    
    return pd.DataFrame(result)


# Run filters
all_dataframes = load_all_stock_data()
filtered_stocks = filter_stocks(all_dataframes)

# Save results
filtered_stocks.to_csv("nse_data/recent_listed_filtered.csv", index=False)
print(" Final filtered stocks saved to 'nse_data/recent_listed_filtered.csv'")
print(filtered_stocks)
