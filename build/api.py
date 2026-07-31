from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from .yahoo_fetcher import get_company_data
from .company_analyser import get_company_analysis
from .pptx_writer import generate_deck

app = FastAPI()

@app.get("/generate_profile/{symbol}")
def generate_profile(symbol: str):
    company_data = get_company_data(symbol)
    if "error" in company_data:
        return {"error": company_data["error"]}

    analysis = get_company_analysis(company_data)
    if "error" in analysis:
        return {"error": analysis["error"]}

    result = generate_deck(company_data, analysis)

    result["file_content"].seek(0)

    return StreamingResponse(
        result["file_content"],
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
    )