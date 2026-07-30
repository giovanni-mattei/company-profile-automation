from pptx import Presentation
from datetime import datetime
import os
from io import BytesIO

def generate_deck(company_data, analysis):
    template_path = "templates/deck.pptx"
    prs = Presentation(template_path)

    company_info = analysis["company_info"]
    company_summary = analysis["company_summary"]
    price_metrics = analysis["price_metrics"]
    price_chart = analysis["price_chart"]
    financial_highlights = analysis["financial_highlights"]
    financial_facts = analysis["financial_facts"]
    news = analysis["news"]

    # Slide 1
    slide = prs.slides[1]
    text_fields = {
        "name": str(company_info["company_name"]),
        "symbol": str(company_info["company_ticker"]),
        "sector": str(company_info["company_sector"]),
        "industry": str(company_info["company_industry"]),
        "market_cap": str(company_info["market_cap"]),
        "earnings": str(company_info["share_earnings"]),
        "stock_price": str(company_info["share_price"]),
        "analyst_rating": str(company_info["analyst_rating"]),
        "beta": str(company_info["beta"]),
        "description": str(company_summary),
        "ltm_revenue": str(company_info["ltm_revenue"]),
        "revenue_growth": str(company_info["revenue_growth"]),
        "ltm_ebitda": str(company_info["ltm_ebitda"]),
        "ebitda_margin": str(company_info["ebitda_margin"])
    }
    for shape in slide.shapes:
        if shape.name in text_fields and shape.has_text_frame:
            paragraph = shape.text_frame.paragraphs[0]
            if paragraph.runs:
                paragraph.runs[0].text = text_fields[shape.name]
            else:
                paragraph.add_run().text = text_fields[shape.name]

    # Slide 2
    slide = prs.slides[2]
    for shape in slide.shapes:
        if shape.name == "price_chart":
            left = shape.left
            top = shape.top
            width = shape.width
            height = shape.height
            shape.element.getparent().remove(shape.element)
            slide.shapes.add_picture(price_chart, left, top, width=width, height=height)
            break
    text_fields = {
        "current_price": f"{price_metrics['p_current']:.0f}",
        "mean_price": f"{price_metrics['p_mean']:.0f}",
        "max_price": f"{price_metrics['p_max']:.0f}",
        "q75_price": f"{price_metrics['p_75q']:.0f}",
        "q50_price": f"{price_metrics['p_50q']:.0f}",
        "q25_price": f"{price_metrics['p_25q']:.0f}",
        "min_price": f"{price_metrics['p_min']:.0f}",
        "std_price": f"{price_metrics['p_std']:.0f}",
        "analyst_expectation": f"{price_metrics['p_analyst']:.0f}"
    }
    for shape in slide.shapes:
        if shape.name in text_fields and shape.has_text_frame:
            paragraph = shape.text_frame.paragraphs[0]
            if paragraph.runs:
                paragraph.runs[0].text = text_fields[shape.name]
            else:
                paragraph.add_run().text = text_fields[shape.name]

    # Slide 3
    slide = prs.slides[3]
    years = list(financial_highlights["Revenue"].keys())[:3]
    text_fields = {f"year_{i+1}": str(y) for i, y in enumerate(years)}
    metrics = ["Revenue", "Gross Profit", "Operating Profit", "Net Income", "CapEx", "Free Cash Flow", "Op. Cash Flow", "Debt", "Equity", "Invested Capital"]
    financial_data = {}
    for metric in metrics:
        if metric in financial_highlights:
            financial_data[metric] = [financial_highlights[metric][y] for y in years if y in financial_highlights[metric]]
    for metric in metrics:
        for i in range(3):
            if metric in financial_data and len(financial_data[metric]) > i:
                text_fields[f"{metric.lower().replace(' ', '_').replace('.', '')}_y{i+1}"] = str(financial_data[metric][i])
    detail_map = {
        "revenue_detail": financial_highlights["Revenue"].get("Avg growth", ""),
        "gross_profit_detail": financial_highlights["Gross Profit"].get("Avg margin", ""),
        "operating_profit_detail": financial_highlights["Operating Profit"].get("Avg margin", ""),
        "net_income_detail": financial_highlights["Net Income"].get("Avg margin", ""),
        "capex_detail": financial_highlights["CapEx"].get("% of revenue", ""),
        "free_cash_flow_detail": financial_highlights["Free Cash Flow"].get("% growth", ""),
        "op_cash_flow_detail": financial_highlights["Op. Cash Flow"].get("% of revenue", ""),
        "invested_capital_detail": financial_highlights["Invested Capital"].get("Avg return", ""),
        "debt_detail": financial_highlights["Invested Capital"].get("Avg debt to capital ratio", "")
    }
    text_fields.update(detail_map)
    text_fields.update({"comment_1": financial_facts[0], "comment_2": financial_facts[1], "comment_3": financial_facts[2]})
    for shape in slide.shapes:
        if shape.name in text_fields and shape.has_text_frame:
            paragraph = shape.text_frame.paragraphs[0]
            if paragraph.runs:
                paragraph.runs[0].text = text_fields[shape.name]
            else:
                paragraph.add_run().text = text_fields[shape.name]

    # Slide 4
    slide = prs.slides[4]
    text_fields = {
        "news_name_1": news[0]['title'],
        "news_1": news[0]['summary'],
        "news_name_2": news[1]['title'],
        "news_2": news[1]['summary'],
        "news_name_3": news[2]['title'],
        "news_3": news[2]['summary']
    }
    for shape in slide.shapes:
        if shape.name in text_fields and shape.has_text_frame:
            paragraph = shape.text_frame.paragraphs[0]
            if paragraph.runs:
                paragraph.runs[0].text = str(text_fields[shape.name])
            else:
                paragraph.add_run().text = str(text_fields[shape.name])

    # All slides
    formatted_date = datetime.now().strftime("%d %B %Y")
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if "{company_name}" in run.text:
                            run.text = run.text.replace("{company_name}", company_info["company_name"])
                        if "{current_date}" in run.text:
                            run.text = run.text.replace("{current_date}", formatted_date)

    buffer = BytesIO()
    prs.save(buffer)
    buffer.seek(0)

    symbol = company_info["company_ticker"]
    current_date = datetime.now().strftime("%d-%m-%Y")
    filename = f"{symbol}_{current_date}.pptx"
    return {"file_content": buffer, "filename": filename}