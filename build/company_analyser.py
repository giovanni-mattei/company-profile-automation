from .fields_computer import (
    get_company_info,
    get_company_summary,
    get_price_metrics,
    get_price_chart,
    get_financial_highlights,
    get_financial_facts,
    get_news
)

def get_company_analysis(company_data):
    if not company_data:
        return {"error": "Company data cannot be empty."}

    try:
        return {
            "company_info":         get_company_info(company_data),
            "company_summary":      get_company_summary(company_data),
            "price_metrics":        get_price_metrics(company_data),
            "price_chart":          get_price_chart(company_data),
            "financial_highlights": get_financial_highlights(company_data),
            "financial_facts":      get_financial_facts(company_data),
            "news":                 get_news(company_data),
        }
    except Exception as e:
        return {"error": f"Failed to analyze company data: {str(e)}"}