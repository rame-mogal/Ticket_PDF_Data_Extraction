import os
import re
import fitz  # PyMuPDF
import tempfile
import streamlit as st

# Streamlit UI
st.title("📄 Data Extractor (Text-based PDF using Regex)")
st.write("Upload a PDF with readable text. We'll extract structured info using regular expressions.")

uploaded_file = st.file_uploader("Upload RR PDF", type=["pdf"])

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    return "\n".join(page.get_text() for page in doc)

def extract_rr_data_with_regex(text):
    rr_entries = []

    # Flexible regex patterns to account for inconsistent formats
    rr_numbers = re.findall(r'RR\s*No[:\-]?\s*([A-Z0-9\-\/]+)', text, re.IGNORECASE)
    rr_dates = re.findall(r'RR\s*Date[:\-]?\s*([\d]{1,2}[\/\-\.][\d]{1,2}[\/\-\.][\d]{2,4})', text, re.IGNORECASE)
    stations_from = re.findall(r'Station\s*From[:\-]?\s*([\w\s]+)', text, re.IGNORECASE)
    stations_to = re.findall(r'Station\s*To[:\-]?\s*([\w\s]+)', text, re.IGNORECASE)

    # Flexible patterns for Wagons
    wagons = re.findall(r'No\.?\s*of\s*Wagons?[:\-]?\s*(\d+)', text, re.IGNORECASE)
    if not wagons:
        wagons = re.findall(r'Wagons?\s*[:\-]?\s*(\d+)', text, re.IGNORECASE)

    # Freight
    freights = re.findall(r'Total\s*Freight[:\-]?\s*(?:₹|Rs\.?)?\s?([\d,]+(?:\.\d{1,2})?)', text, re.IGNORECASE)
    if not freights:
        freights = re.findall(r'Freight\s*[:\-]?\s*(?:₹|Rs\.?)?\s?([\d,]+(?:\.\d{1,2})?)', text, re.IGNORECASE)

    # Weight
    weights = re.findall(r'Actual\s*Weight[:\-]?\s*([\d,]+(?:\.\d{1,2})?)', text, re.IGNORECASE)

    # Determine maximum length to loop through all possible matches
    max_len = max(len(rr_numbers), len(rr_dates), len(stations_from), len(stations_to), len(wagons), len(freights), len(weights), 1)

    for i in range(max_len):
        no_of_wagon = wagons[i] if i < len(wagons) else ""
        if not no_of_wagon:
            continue  # Skip entries without 'No. of Wagon'

        entry = {
            "RR No": rr_numbers[i] if i < len(rr_numbers) else "",
            "RR Date": rr_dates[i] if i < len(rr_dates) else "",
            "Station From": stations_from[i] if i < len(stations_from) else "",
            "Station To": stations_to[i] if i < len(stations_to) else "",
            "No. of Wagon": no_of_wagon,
            "Total Freight": freights[i] if i < len(freights) else "",
            "Actual Weight": weights[i] if i < len(weights) else "",
        }
        rr_entries.append(entry)

    return rr_entries

if uploaded_file:
    with st.spinner("Processing PDF..."):
        # Save uploaded PDF to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_pdf_path = tmp_file.name

        # Extract text and data
        extracted_text = extract_text_from_pdf(tmp_pdf_path)
        extracted_data = extract_rr_data_with_regex(extracted_text)

        # Display results
        if extracted_data:
            st.subheader("✅ Extracted Records (via Regex)")
            st.dataframe(extracted_data)
        else:
            st.warning("⚠️ No data found using regex or 'No. of Wagon' field was missing.")
