import os
import json
import re
import fitz  # PyMuPDF
import tempfile
import streamlit as st
from dotenv import load_dotenv
import openai

# Load API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit UI
st.title("📄Data Extractor (Text-based PDF)")
st.write("Upload a PDF with readable text. We'll extract structured info using GPT-3.5 Turbo.")

uploaded_file = st.file_uploader("Upload RR PDF", type=["pdf"])

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    return "\n".join(page.get_text() for page in doc)

def build_prompt(text):
    return f"""
Extract the following fields from the text:

- RR No
- RR Date
- Station From
- Station To
- No. of Wagon
- Total Freight
- Actual Weight

Text:
{text}

Respond in this JSON format:
{{
  "RR No": "...",
  "RR Date": "...",
  "Station From": "...",
  "Station To": "...",
  "No. of Wagon": "...",
  "Total Freight": "...",
  "Actual Weight": "..."
}}
"""

def query_openai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-1106",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"OpenAI Error: {e}")
        return None

if uploaded_file:
    with st.spinner("Processing PDF..."):
        # Save file and extract text
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_pdf_path = tmp_file.name

        extracted_text = extract_text_from_pdf(tmp_pdf_path)
        prompt = build_prompt(extracted_text)
        gpt_response = query_openai(prompt)

        # Try parsing response
        if gpt_response:
            match = re.search(r"\{.*\}", gpt_response, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                    st.subheader("✅ Extracted Info")
                    st.json(data)
                except json.JSONDecodeError:
                    st.warning("⚠️ Couldn't parse JSON from OpenAI response.")
            else:
                st.warning("⚠️ GPT response didn't contain valid JSON.")