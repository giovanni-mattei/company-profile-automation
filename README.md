## Introduction
This project is an **equity research tool** that generates **company profile reports** from stock tickers. It leverages:
- **Yahoo Finance API** (`yfinance`) for financial data fetching.
- **Mistral API** for AI-generated textual analysis.
- **FastAPI** for the backend.
- **Streamlit** for the frontend.

The output is a **structured PowerPoint slide deck** containing:
- Company overview (name, sector, market cap, etc.).
- Historical trading price analysis.
- Key financial highlights.
- Recent news summaries.

---

---


## Key Features
- **Automated Data Fetching**: Real-time financial data from Yahoo Finance.
- **Dynamic Analysis**: Automated calculations for ratios, growth rates, and margins.
- **Customizable Reports**: PowerPoint template (`deck.pptx`) for consistent formatting.
- **LLM Integration**: Mistral API for AI-generated insights.


---
---


## Project Structure

company-profile-automation/
│
├── build/                  # Core Python modules
│   ├── __init__.py         # Package initializer
│   ├── api.py              # FastAPI backend (HTTP endpoint: /generate_profile/{symbol})
│   ├── app.py              # Streamlit frontend
│   ├── yahoo_fetcher.py    # Fetches financial data from Yahoo Finance
│   ├── company_analyser.py # Processes raw data into structured metrics
│   ├── fields_computer.py  # Computes financial ratios and highlights
│   ├── pptx_writer.py      # Generates PowerPoint reports from analyzed data
│   ├── mistral_handler.py  # Handles Mistral API interactions
│   └── utils.py            # Utility functions (e.g., formatting, calculations)
│
├── templates/              # PowerPoint templates
│   └── deck.pptx           # Base template for reports
│
└── notebooks/              # Development and testing
    └── dev.ipynb           # Jupyter Notebook for debugging


---
---


## Module Breakdown

| **File**               | **Purpose**                                                                                          |
|------------------------|------------------------------------------------------------------------------------------------------|
| `api.py`               | FastAPI backend exposing `/generate_profile/{symbol}` to generate reports via HTTP.                  |
| `app.py`               | Streamlit frontend for user interaction.                                                             |
| `yahoo_fetcher.py`     | Fetches raw financial data (info, income statement, balance sheet, cash flow, trading price, news).  |
| `company_analyser.py`  | Processes raw data into structured analysis.                                                         |
| `fields_computer.py`   | Computes financial data (e.g. company info, financials, ratios, price metrics).                      |
| `pptx_writer.py`       | Populates the PowerPoint template (`deck.pptx`) with analyzed data.                                  |
| `mistral_handler.py`   | Handles Mistral API calls for AI-generated text.                                                     |
| `utils.py`             | Utility functions.                                                                                   |

