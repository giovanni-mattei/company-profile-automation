import streamlit as st
import requests
import os
from pathlib import Path

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(layout="centered")
st.title("Automated company profile deck")
st.write("Automated equity research tool generating PowerPoint profiles from stock tickers using Yahoo Finance data and Mistral AI")

st.caption("""
Technical workflow: fetches financial data from Yahoo Finance (prices, financials, cash flows), calls Mistral API for business summaries and investment analysis, calculates key metrics (revenue CAGR, margins, ROIC, debt ratios), and compiles everything into a standardized PowerPoint deck. Modular architecture with separate data, analysis, and presentation layers.
""")

ticker = st.text_input("Stock ticker", placeholder="CMG, TSLA, TREX")

if st.button("Generate company profile deck"):
    if ticker:
        with st.spinner("Generating deck..."):
            try:
                api_url = f"{API_BASE_URL}/generate_profile/{ticker.upper()}"
                response = requests.get(api_url, timeout=120)

                if response.ok:
                    st.success("Deck generated")
                    st.download_button(
                        "Download .pptx",
                        response.content,
                        f"{ticker}_profile.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a ticker")

st.caption("Created by [Giovanni Mattei](https://giovanni.mattei.github.io)")