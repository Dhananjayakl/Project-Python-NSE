import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Set your data directory
data_dir = r"C:\Users\dhana\Desktop\python_stock_test\Project-Python-NSE\output"

def update_stock_xlsx(file_path):
    try:
        # Read existing Excel file
        df_existing = pd.read_excel(file_path)
        df_existing['Date'] = pd.to_datetime(df_existing['Date'], format="%Y-%m-%d")

        latest_date = df_existing['Date'].max().date()

        # Get symbol from filename
        filename = os.path.basename(file_path)
        symbol = os.path.splitext(filename)[0]
        ticker = symbol + ".NS"

        # Date range for new data
        start_date = latest_date + timedelta(days=1)
        end_date = datetime.today().date()

        if start_date > end_date:
            print(f"{symbol} is already up-to-date.")
            return

        # Download new data
        df_new = yf.download(ticker, start=start_date, end=end_date)
        if df_new.empty:
            print(f"No new data for {symbol}.")
            return

        # Format new data
        df_new.reset_index(inplace=True)
        df_new['Date'] = df_new['Date'].dt.strftime('%d-%m-%Y')
        df_new['Symbol'] = symbol
        df_new = df_new.rename(columns={
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low',
            'Close': 'Close',
            'Volume': 'Volume'
        })

        # Arrange columns
        df_new = df_new[['Date', 'Close', 'High', 'Low', 'Open', 'Volume', 'Symbol']]

        # Append and save
        df_updated = pd.concat([df_existing, df_new], ignore_index=True)
        df_updated.to_excel(file_path, index=False)
        print(f"Updated {symbol} with {len(df_new)} new rows.")

    except Exception as e:
        print(f"Error updating {file_path}: {e}")

def update_all_stocks():
    print("Checking for .xlsx files to update...")
    for filename in os.listdir(data_dir):
        if filename.endswith('.xlsx'):
            full_path = os.path.join(data_dir, filename)
            update_stock_xlsx(full_path)

if __name__ == "__main__":
    update_all_stocks()
