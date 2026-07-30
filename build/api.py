from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import os
from io import BytesIO
from .data_fetcher import get_company_data
from .data_computer import analyze_company
from .pptx_writer import generate_deck

app = FastAPI()

@app.get("/generate_profile/{symbol}")
def generate_profile(symbol: str):
    try:
        company_data = get_company_data(symbol)
        analysis = analyze_company(company_data)
        result = generate_deck(company_data, analysis)

        return StreamingResponse(
            result["file_content"],
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": f"attachment; filename={result['filename']}"
            }
        )
    except Exception as e:
        return {"error": str(e)}