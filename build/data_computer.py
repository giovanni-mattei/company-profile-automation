import os
import requests
import re
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from dotenv import load_dotenv
from io import BytesIO
from .utils import format_number, format_currency, format_percentage, safe_divide, growth_rate, get_metric

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

def analyze_company(company_data):
    return {
        "company_info": get_company_info(company_data),
        "company_summary": get_company_summary(company_data),
        "price_metrics": get_price_metrics(company_data),
        "price_chart": get_price_chart(company_data),
        "financial_highlights": get_financial_highlights(company_data),
        "financial_facts": get_financial_facts(company_data),
        "news": get_news(company_data),
    }

def call_mistral(messages, model="mistral-tiny", temperature=0.1, max_tokens=100):
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {str(e)}"


def get_company_info(company_data):
    info = company_data["info"]
    return {
        "company_name": info.get("displayName", "N/A"),
        "company_ticker": info.get("symbol", "N/A"),
        "company_sector": info.get("sector", "N/A"),
        "company_industry": info.get("industry", "N/A"),
        "market_cap": format_number(info.get("marketCap", 0)),
        "share_price": format_currency(info.get("currentPrice", 0)),
        "share_earnings": format_currency(info.get("trailingEps", 0)),
        "analyst_rating": info.get("averageAnalystRating", "N/A"),
        "beta": info.get("beta", "N/A"),
        "ltm_revenue": format_number(info.get("totalRevenue", "N/A")),
        "revenue_growth": format_percentage(info.get("revenueGrowth", 0)),
        "ltm_ebitda": format_number(info.get("ebitda", 0)),
        "ebitda_margin": format_percentage(info.get("ebitdaMargins", 0)),
    }


def get_company_summary(company_data):
    info = company_data["info"]
    company_name = info.get("displayName", "N/A")
    description = info.get("longBusinessSummary", "N/A")
    prompt = f"Act as an equity research analyst. Provide ONLY a strictly 50-words or fewer summary of the business of {company_name}. Do not include any headers, titles, prefixes, or the word 'Summary'. Description: {description}"
    response = call_mistral([{"role": "user", "content": prompt}], max_tokens=200)
    return re.sub(r'[*_~`\[\]]', '', response)    


def get_price_metrics(company_data):
    data = company_data["history"]
    info = company_data["info"]
    return {
        "p_current": data["Close"].iloc[-1],
        "p_mean": data["Close"].mean(),
        "p_max": data["Close"].max(),
        "p_min": data["Close"].min(),
        "p_75q": data["Close"].quantile(0.75),
        "p_50q": data["Close"].quantile(0.5),
        "p_25q": data["Close"].quantile(0.25),
        "p_std": data["Close"].std(),
        "p_analyst": info.get("targetMeanPrice", 0)
    }


def get_price_chart(company_data):
    data = company_data["history"]
    info = company_data["info"]
    symbol = info.get("symbol", "unknown")
    p_mean = data["Close"].mean()
    p_analyst = info.get("targetMeanPrice", 0)

    plt.figure(figsize=(11.84, 6.40))
    sns.lineplot(data["Close"], linewidth=3, color="#44546A")
    plt.rcParams['font.family'] = ['Arial', 'sans-serif']
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_color('#44546A')
    plt.gca().spines['bottom'].set_color('#44546A')
    plt.tick_params(axis='both', labelsize=16, colors='#44546A')
    plt.gca().set(xlabel=None, ylabel=None)
    plt.tick_params(axis='both', labelsize=16)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())

    x_min, x_max = plt.gca().get_xlim()
    plt.hlines(y=p_mean, xmin=x_min + 0.025*(x_max - x_min), xmax=x_max - 0.025*(x_max - x_min),
               color="#ED7D31", linestyle='-', linewidth=2, label="Mean price")
    plt.hlines(y=p_analyst, xmin=x_min + 0.025*(x_max - x_min), xmax=x_max - 0.025*(x_max - x_min),
               color="#70AD47", linestyle='-', linewidth=2, label="Analyst expectation")

    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    return buffer

def get_financial_highlights(company_data):
    financials = company_data["financials"]
    cashflow = company_data["cashflow"]
    balance_sheet = company_data["balance_sheet"]

    years = [str(year.year) for year in financials.columns[:3]]

    revenue = get_metric('Total Revenue', financials)
    gross_profit = get_metric('Gross Profit', financials)
    operating_income = get_metric('Operating Income', financials)
    net_income = get_metric('Net Income', financials)
    capex = get_metric('Investing Cash Flow', cashflow)
    free_cash_flow = get_metric('Free Cash Flow', cashflow)
    op_cash_flow = get_metric('Operating Cash Flow', cashflow)
    total_debt = get_metric('Total Debt', balance_sheet)
    equity = get_metric('Stockholders Equity', balance_sheet)
    invested_capital = [d + e for d, e in zip(total_debt, equity)]

    revenue_growth = growth_rate(revenue[0], revenue[-1])
    gross_margin = safe_divide(gross_profit[0], abs(revenue[0]))
    operating_margin = safe_divide(operating_income[0], abs(revenue[0]))
    net_margin = safe_divide(net_income[0], abs(revenue[0]))
    capex_pct = safe_divide(abs(capex[0]), abs(revenue[0]))
    fcf_growth = growth_rate(free_cash_flow[0], free_cash_flow[-1])
    op_cash_pct = safe_divide(op_cash_flow[0], abs(revenue[0]))
    roic = safe_divide(net_income[0], abs(invested_capital[0]))
    debt_to_cap = safe_divide(total_debt[0], abs(invested_capital[0]))

    financial_data = {
        "Revenue": [format_number(v) for v in revenue],
        "Gross Profit": [format_number(v) for v in gross_profit],
        "Operating Profit": [format_number(v) for v in operating_income],
        "Net Income": [format_number(v) for v in net_income],
        "CapEx": [format_number(v) for v in capex],
        "Free Cash Flow": [format_number(v) for v in free_cash_flow],
        "Op. Cash Flow": [format_number(v) for v in op_cash_flow],
        "Debt": [format_number(v) for v in total_debt],
        "Equity": [format_number(v) for v in equity],
        "Invested Capital": [format_number(v) for v in invested_capital]
    }

    detail = {
        "Revenue": {**dict(zip(years, financial_data["Revenue"])), "Avg growth": format_percentage(revenue_growth)},
        "Gross Profit": {**dict(zip(years, financial_data["Gross Profit"])), "Avg margin": format_percentage(gross_margin)},
        "Operating Profit": {**dict(zip(years, financial_data["Operating Profit"])), "Avg margin": format_percentage(operating_margin)},
        "Net Income": {**dict(zip(years, financial_data["Net Income"])), "Avg margin": format_percentage(net_margin)},
        "CapEx": {**dict(zip(years, financial_data["CapEx"])), "% of revenue": format_percentage(capex_pct)},
        "Free Cash Flow": {**dict(zip(years, financial_data["Free Cash Flow"])), "% growth": format_percentage(fcf_growth)},
        "Op. Cash Flow": {**dict(zip(years, financial_data["Op. Cash Flow"])), "% of revenue": format_percentage(op_cash_pct)},
        "Debt": dict(zip(years, financial_data["Debt"])),
        "Equity": dict(zip(years, financial_data["Equity"])),
        "Invested Capital": {
            **dict(zip(years, financial_data["Invested Capital"])),
            "Avg return": format_percentage(roic),
            "Avg debt to capital ratio": format_percentage(debt_to_cap)
        }
    }
    return detail


def get_financial_facts(company_data):
    detail = get_financial_highlights(company_data)
    prompt = f"Act as an equity research analyst. Based on the following data, provide only a Python list of 3 key facts about the company, each exactly 20 words long. Financial Details: {detail}. Return only a valid Python list like: ['fact 1', 'fact 2', 'fact 3']"
    response = call_mistral([{"role": "user", "content": prompt}], max_tokens=500)
    cleaned_response = response.strip()
    for prefix in ['```python', '```']:
        if cleaned_response.startswith(prefix):
            cleaned_response = cleaned_response[len(prefix):].strip()
    if cleaned_response.endswith('```'):
        cleaned_response = cleaned_response[:-3].strip()
    return eval(cleaned_response)

    
def get_news(company_data):
    info = company_data["info"]
    company_name = info.get("displayName", "N/A")
    news_items = [f"{item['content']['title']}. {item['content'].get('summary', '')}" for item in company_data["news"]]

    prompt = f"Act as an equity research analyst. Organize these news items relative to {company_name} into 3 main topics. For each topic, provide a title and a 40-word business-relevant summary. Return ONLY a Python list of 3 dictionaries, each with 'title' and 'summary' keys.\n\nNews:\n{chr(10).join(news_items)}"

    response = call_mistral([{"role": "user", "content": prompt}], max_tokens=1000)

    cleaned_response = response.strip()
    for prefix in ['```python', '```']:
        if cleaned_response.startswith(prefix):
            cleaned_response = cleaned_response[len(prefix):].strip()
    if cleaned_response.endswith('```'):
        cleaned_response = cleaned_response[:-3].strip()

    return eval(cleaned_response)