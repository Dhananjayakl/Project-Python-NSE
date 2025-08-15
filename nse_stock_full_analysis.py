import pandas as pd
import requests
import time
import yfinance as yf
from io import StringIO

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

def calculate_growth(series):
    qoq = yoy = "N/A"
    if len(series) >= 2:
        try:
            qoq = round(((series[0] - series[1]) / abs(series[1])) * 100, 2)
        except ZeroDivisionError:
            qoq = "N/A"
    if len(series) >= 5:
        try:
            yoy = round(((series[0] - series[4]) / abs(series[4])) * 100, 2)
        except ZeroDivisionError:
            yoy = "N/A"
    return qoq, yoy

def get_stock_data(symbols):
    info_list = []
    failed_list = []

    for symbol in symbols:
        ticker = symbol + ".NS"
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Metadata
            company_name = info.get("longName", "N/A")
            sector = info.get("sector", "N/A")
            industry = info.get("industry", "N/A")
            website = info.get("website", "N/A")
            market_cap = info.get("marketCap", "N/A")
            trailing_pe = info.get("trailingPE", "N/A")
            forward_pe = info.get("forwardPE", "N/A")
            trailing_eps = info.get("trailingEps", "N/A")
            float_shares = info.get("floatShares", "N/A")
            high_52w = info.get("fiftyTwoWeekHigh", "N/A")
            low_52w = info.get("fiftyTwoWeekLow", "N/A")
            volume = info.get("volume", "N/A")
            avg_volume = info.get("averageVolume", "N/A")
            dividend_yield = info.get("dividendYield", "N/A")
            return_on_equity = info.get("returnOnEquity", "N/A")
            pb_ratio = info.get("priceToBook", "N/A")
            beta = info.get("beta", "N/A")

            # Quarterly Earnings (EPS)
            income_stmt = stock.quarterly_income_stmt
            eps_series = []
            if income_stmt is not None and not income_stmt.empty:
                if 'Net Income' in income_stmt.index and 'Basic Average Shares' in income_stmt.index:
                    net_income = income_stmt.loc['Net Income'].tolist()
                    shares = income_stmt.loc['Basic Average Shares'].tolist()
                    eps_series = [round(n / s, 2) if s != 0 else 0 for n, s in zip(net_income, shares)]
            eps_qoq, eps_yoy = calculate_growth(eps_series)

            # Quarterly Financials (Revenue)
            financials = stock.quarterly_financials
            revenue_series = []
            if financials is not None and not financials.empty and 'Total Revenue' in financials.index:
                revenue_series = financials.loc['Total Revenue'].tolist()[:5]
            sales_qoq, sales_yoy = calculate_growth(revenue_series)

            # Append all data
            info_list.append({
                "Symbol": symbol,
                "Company Name": company_name,
                "Sector": sector,
                "Industry": industry,
                "Website": website,
                "Market Cap": market_cap,
                "Trailing PE": trailing_pe,
                "Forward PE": forward_pe,
                "Trailing EPS": trailing_eps,
                "Float Shares": float_shares,
                "52W High": high_52w,
                "52W Low": low_52w,
                "Volume": volume,
                "Average Volume": avg_volume,
                "Dividend Yield": dividend_yield,
                "Return on Equity": return_on_equity,
                "Price to Book Ratio": pb_ratio,
                "Beta": beta,
                "EPS Last 5 Qtrs": eps_series,
                "EPS QoQ %": eps_qoq,
                "EPS YoY %": eps_yoy,
                "Revenue Last 5 Qtrs": revenue_series,
                "Sales QoQ %": sales_qoq,
                "Sales YoY %": sales_yoy
            })

            print(f"✅ {symbol}: EPS QoQ={eps_qoq}%, YoY={eps_yoy}% | Sales QoQ={sales_qoq}%, YoY={sales_yoy}%")

        except Exception as e:
            print(f"⚠️ Failed to fetch info for {symbol}: {e}")
            failed_list.append(symbol)

        time.sleep(0.5)  # Avoid hitting rate limits

    # Save failed symbols for later retry
    if failed_list:
        pd.DataFrame({"Symbol": failed_list}).to_csv("failed_symbols.csv", index=False)
        print(f"⚠️ {len(failed_list)} symbols failed. Saved to 'failed_symbols.csv'")

    # Return the final DataFrame containing all stock data
    return pd.DataFrame(info_list)

# Run everything
symbols = fetch_nse_stock_list()
if symbols:
    df = get_stock_data(symbols)
    df.to_csv("nse_full_stock_data.csv", index=False)
    print("📁 Full data saved to 'nse_full_stock_data.csv'")
else:
    print("❌ No symbols to process.")
