import streamlit as st
import os
import json
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
from pdf_utils import extract_text_from_pdf

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash-lite")

# AI function
def analyze_invoice(text):
    prompt = f"""
    Extract the following details from the invoice:

    - Vendor Name
    - Invoice Number (if available)
    - Invoice Date
    - Total Amount
    - GST Amount (if available)

    Return ONLY raw JSON.
    Do NOT include backticks or markdown.

    Format:
    {{
      "Vendor": "",
      "Invoice Number": "",
      "Date": "",
      "Total Amount": "",
      "GST": ""
    }}

    Invoice:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text


# Clean JSON function
def clean_json(result):
    cleaned = result.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    return cleaned


# Streamlit UI
st.set_page_config(page_title="AI Invoice Analyzer", layout="wide")

st.title("🧾 AI Invoice Analyzer")
st.markdown("Upload an invoice and extract structured business data instantly.")

uploaded_file = st.file_uploader("📂 Upload Invoice PDF", type=["pdf"])

if uploaded_file:

    st.subheader("📄 Uploaded File")
    st.write(uploaded_file.name)

    if st.button("🚀 Analyze Invoice"):

        with st.spinner("Analyzing invoice..."):

            text = extract_text_from_pdf(uploaded_file)
            result = analyze_invoice(text)

            try:
                cleaned_result = clean_json(result)
                data = json.loads(cleaned_result)

                st.success("✅ Invoice Processed Successfully")

                # Show table
                st.subheader("📊 Extracted Data")
                df = pd.DataFrame([data])
                st.dataframe(df, use_container_width=True)

                # Metrics
                st.subheader("📈 Insights")

                try:
                    amount = float(data["Total Amount"].replace("₹", "").replace(",", ""))
                    gst = float(data["GST"].replace("₹", "").replace(",", ""))

                    col1, col2 = st.columns(2)
                    col1.metric("💰 Total Amount", f"₹{amount}")
                    col2.metric("🧾 GST", f"₹{gst}")

                except:
                    st.info("Some financial values not available")

                # Download CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="⬇ Download CSV",
                    data=csv,
                    file_name="invoice_data.csv",
                    mime="text/csv"
                )

                # History
                if "history" not in st.session_state:
                    st.session_state.history = []

                st.session_state.history.append(data)

                st.subheader("📚 Invoice History")
                st.table(pd.DataFrame(st.session_state.history))

            except Exception as e:
                st.error("⚠️ Could not parse AI response")
                st.text(result)