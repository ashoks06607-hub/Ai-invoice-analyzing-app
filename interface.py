import streamlit as st
from pdf_utils import extract_text_from_pdf

st.title("🧾 AI Invoice Analyzer")

uploaded_file = st.file_uploader("Upload Invoice PDF", type=["pdf"])

if uploaded_file:
    if st.button("Analyze Invoice"):
        with st.spinner("Processing..."):

            text = extract_text_from_pdf(uploaded_file)
            result = analyze_invoice(text)

            st.subheader("📊 Extracted Data")
            st.text(result)