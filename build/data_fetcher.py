import yfinance as yf

def get_company_data(symbol: str):
    ticker = yf.Ticker(symbol)
    return {
        "info": ticker.info,
        "financials": ticker.financials,
        "balance_sheet": ticker.balance_sheet,
        "cashflow": ticker.cashflow,
        "history": ticker.history(period="6mo"),
        "news": ticker.news
    }