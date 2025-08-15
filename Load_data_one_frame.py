#Load All CSV Files into One DataFrame (When Needed)
import pandas as pd
import os

def load_all_stock_data(folder='nse_data'):
    all_dfs = []
    for filename in os.listdir(folder):
        if filename.endswith(".csv"):
            filepath = os.path.join(folder, filename)
            try:
                df = pd.read_csv(filepath)
                df['Symbol'] = filename.replace(".csv", "")  # if symbol column is missing
                all_dfs.append(df)
            except Exception as e:
                print(f"Failed to load {filename}: {e}")
    return pd.concat(all_dfs, ignore_index=True)

# Load everything into one DataFrame
df_all = load_all_stock_data()


#Load One File at a Time (Efficient for large datasets)
folder = 'nse_data'

for filename in os.listdir(folder):
    if filename.endswith(".csv"):
        filepath = os.path.join(folder, filename)
        df = pd.read_csv(filepath)

        # Example: Calculate 20-day MA
        df['MA20'] = df['Close'].rolling(20).mean()

        # Example: Print if last close is above MA20
        if df['Close'].iloc[-1] > df['MA20'].iloc[-1]:
            print(f"{filename.replace('.csv', '')} is above 20-day MA")

