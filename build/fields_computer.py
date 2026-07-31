import os
import re
import ast
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from io import BytesIO
from .mistral_handler import call_mistral
from .utils import format_number, format_currency, format_percentage, safe_divide, growth_rate

# Slide 1
def get_company_info(company_data):
    info = company_data.get("info", {})
    if not info:
        return {"error": "Company info not available."}

    return {
        "company_name":     info.get("displayName", "N/A"),
        "company_ticker":   info.get("symbol", "N/A"),
        "company_sector":   info.get("sector", "N/A"),
        "company_industry": info.get("industry", "N/A"),
        "market_cap":       format_number(info.get("marketCap", 0)),
        "share_price":      format_currency(info.get("currentPrice", 0)),
        "share_earnings":   format_currency(info.get("trailingEps", 0)),
        "analyst_rating":   info.get("averageAnalystRating", "N/A"),
        "beta":             info.get("beta", "N/A"),
        "ltm_revenue":      format_number(info.get("totalRevenue", "N/A")),
        "revenue_growth":   format_percentage(info.get("revenueGrowth", 0)),
        "ltm_ebitda":       format_number(info.get("ebitda", 0)),
        "ebitda_margin":    format_percentage(info.get("ebitdaMargins", 0)),
    }

def get_company_summary(company_data):
    info = company_data.get("info", {})
    company_name = info.get("displayName", "N/A")
    description = info.get("longBusinessSummary", "N/A")

    if not description:
        return "No description available."

    prompt = f"Act as an equity research analyst. Provide ONLY a strictly 50-words or fewer summary of the business of {company_name}. Do not include any headers, titles, prefixes, or the word 'Summary'. Description: {description}"

    try:
        response = call_mistral([{"role": "user", "content": prompt}], max_tokens=200)
        return re.sub(r'[*_~`\[\]]', '', response)
    except Exception as e:
        return f"Error generating summary: {str(e)}"

# Slide 2
def get_price_metrics(company_data):
    data = company_data.get("history", {})
    if data.empty or "Close" not in data.columns:
        return {"error": "No historical price data available."}

    info = company_data.get("info", {})
    return {
        "current_price": data["Close"].iloc[-1],
        "mean_price":    data["Close"].mean(),
        "max_price":     data["Close"].max(),
        "min_price":     data["Close"].min(),
        "75p_price":     data["Close"].quantile(0.75),
        "50p_price":     data["Close"].quantile(0.5),
        "25p_price":     data["Close"].quantile(0.25),
        "std_price":     data["Close"].std(),
        "analyst_price": info.get("targetMeanPrice", 0)
    }

def get_price_chart(company_data):
    data = company_data.get("history", {})
    if data.empty or "Close" not in data.columns:
        return None

    info = company_data.get("info", {})
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
    plt.hlines(y=p_mean,
               xmin=x_min + 0.025 * (x_max - x_min),
               xmax=x_max - 0.025 * (x_max - x_min),
               color="#ED7D31",
               linestyle='-',
               linewidth=2,
               label="Mean price")
    plt.hlines(y=p_analyst,
               xmin=x_min + 0.025 * (x_max - x_min),
               xmax=x_max - 0.025 * (x_max - x_min),
               color="#70AD47",
               linestyle='-',
               linewidth=2,
               label="Analyst expectation")

    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    return buffer

# Slide 3
def get_financial_highlights(company_data):
    financials = company_data.get("financials", {})
    cashflow = company_data.get("cashflow", {})
    balance_sheet = company_data.get("balance_sheet", {})

    if financials.empty or cashflow.empty or balance_sheet.empty:
        return {"error": "Financial data not available."}

    years = [str(year.year) for year in financials.columns[:3]]

    def get_metric(metric, source):
        try:
            return source.loc[metric, source.columns[:3]].values.tolist()
        except:
            return [0, 0, 0]

    revenue = get_metric('Total Revenue', financials)
    gross_profit = get_metric('Gross Profit', financials)
    operating_income = get_metric('Operating Income', financials)
    net_income = get_metric('Net Income', financials)
    invested_capital = get_metric('Invested Capital', balance_sheet)
    total_debt = get_metric('Total Debt', balance_sheet)
    operating_cash_flow = get_metric('Operating Cash Flow', cashflow)
    investing_cash_flow = get_metric('Investing Cash Flow', cashflow)
    free_cash_flow = get_metric('Free Cash Flow', cashflow)

    revenue_growth = growth_rate(revenue[0], revenue[-1])
    gross_margin = safe_divide(gross_profit[0], abs(revenue[0]))
    operating_margin = safe_divide(operating_income[0], abs(revenue[0]))
    net_margin = safe_divide(net_income[0], abs(revenue[0]))
    roic = safe_divide(net_income[0], abs(invested_capital[0]))
    debt_to_cap = safe_divide(total_debt[0], abs(invested_capital[0]))
    opr_cash_pct = safe_divide(operating_cash_flow[0], abs(revenue[0]))
    inv_cash_pct = safe_divide(abs(investing_cash_flow[0]), abs(revenue[0]))
    fcf_growth = growth_rate(free_cash_flow[0], free_cash_flow[-1])

    financial_highlights = {
        "Revenue": {**{year: format_number(revenue[i]) for i, year in enumerate(years)}, "Avg growth": format_percentage(revenue_growth)},
        "Gross Profit": {**{year: format_number(gross_profit[i]) for i, year in enumerate(years)}, "Avg margin": format_percentage(gross_margin)},
        "Operating Profit": {**{year: format_number(operating_income[i]) for i, year in enumerate(years)}, "Avg margin": format_percentage(operating_margin)},
        "Net Income": {**{year: format_number(net_income[i]) for i, year in enumerate(years)}, "Avg margin": format_percentage(net_margin)},
        "Invested Capital": {**{year: format_number(invested_capital[i]) for i, year in enumerate(years)}, "Avg return": format_percentage(roic)},
        "Debt": {**{year: format_number(total_debt[i]) for i, year in enumerate(years)}, "Avg debt to capital ratio": format_percentage(debt_to_cap)},
        "Operating Cash Flow": {**{year: format_number(operating_cash_flow[i]) for i, year in enumerate(years)}, "% of revenue": format_percentage(opr_cash_pct)},
        "Investing Cash Flow": {**{year: format_number(investing_cash_flow[i]) for i, year in enumerate(years)}, "% of revenue": format_percentage(inv_cash_pct)},
        "Free Cash Flow": {**{year: format_number(free_cash_flow[i]) for i, year in enumerate(years)}, "% growth": format_percentage(fcf_growth)}
    }
    return financial_highlights

def get_financial_facts(company_data):
    financial_highlights = get_financial_highlights(company_data)
    if "error" in financial_highlights:
        return [f"Error: {financial_highlights['error']}"] * 3

    prompt = f"Act as an equity research analyst. Based on the following data, provide only a Python list of 3 key facts about the company, each exactly 20 words long. Financial Details: {financial_highlights}. Return only a valid Python list like: ['fact 1', 'fact 2', 'fact 3']"

    try:
        response = call_mistral([{"role": "user", "content": prompt}], max_tokens=500)
        cleaned_response = response.strip()
        for prefix in ['```python', '```']:
            if cleaned_response.startswith(prefix):
                cleaned_response = cleaned_response[len(prefix):].strip()
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3].strip()

        if not cleaned_response.startswith('[') or not cleaned_response.endswith(']'):
            return ["Error: Invalid response format."] * 3

        return ast.literal_eval(cleaned_response)
    except Exception as e:
        return [f"Error generating facts: {str(e)}"] * 3

# Slide 4
def get_news(company_data):
    info = company_data.get("info", {})
    company_name = info.get("displayName", "N/A")
    news_items = [f"{item['content']['title']}. {item['content'].get('summary', '')}" for item in company_data.get("news", [])]

    if not news_items:
        return [{"title": "No news available.", "summary": "No news available."}]

    prompt = f"Act as an equity research analyst. Organize these news items relative to {company_name} into 3 main topics. For each topic, provide a title and a 40-word business-relevant summary. Return ONLY a Python list of 3 dictionaries, each with 'title' and 'summary' keys.\n\nNews:\n{chr(10).join(news_items)}"

    try:
        response = call_mistral([{"role": "user", "content": prompt}], max_tokens=1000)
        cleaned_response = response.strip()
        for prefix in ['```python', '```']:
            if cleaned_response.startswith(prefix):
                cleaned_response = cleaned_response[len(prefix):].strip()
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3].strip()

        if not cleaned_response.startswith('[') or not cleaned_response.endswith(']'):
            return [{"title": "Error", "summary": "Invalid response format."}] * 3

        return ast.literal_eval(cleaned_response)
    except Exception as e:
        return [{"title": "Error", "summary": f"Failed to generate news: {str(e)}"}] * 3