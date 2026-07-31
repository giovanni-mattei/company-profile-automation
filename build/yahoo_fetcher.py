import yfinance as yf
import pandas as pd

def get_company_data(symbol: str):
    if not symbol or not isinstance(symbol, str):
        return {"error": "Invalid symbol. Must be a non-empty string."}

    try:
        ticker = yf.Ticker(symbol)

        financials = ticker.financials if not ticker.financials.empty else pd.DataFrame()
        balance_sheet = ticker.balance_sheet if not ticker.balance_sheet.empty else pd.DataFrame()
        cashflow = ticker.cashflow if not ticker.cashflow.empty else pd.DataFrame()
        history = ticker.history(period="6mo") if not ticker.history(period="6mo").empty else pd.DataFrame()

        return {
            "info": ticker.info or {},
            "financials": financials,
            "balance_sheet": balance_sheet,
            "cashflow": cashflow,
            "history": history,
            "news": ticker.news or []
        }
    except Exception as e:
        return {"error": f"Failed to fetch data for {symbol}: {str(e)}"}