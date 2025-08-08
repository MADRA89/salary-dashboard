import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from docx import Document
from docx.shared import Pt
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="HR Salary Evaluation", layout="wide")

# --- STYLES ---
st.markdown("""
    <style>
        .title { text-align: center; font-size: 36px; font-weight: bold; margin-bottom: 30px; }
        .subtitle { font-size: 24px; font-weight: bold; margin-top: 20px; }
        .footer { margin-top: 50px; font-size: 14px; text-align: center; color: #888; }
    </style>
""", unsafe_allow_html=True)

# --- TITLE ---
st.markdown('<div class="title">HR Salary Evaluation Dashboard</div>', unsafe_allow_html=True)

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Show the dataframe
    st.markdown('<div class="subtitle">Uploaded Data</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

    # --- ANALYSIS BUTTON ---
    if st.button("Analyze Salaries"):
        st.markdown('<div class="subtitle">Salary Distribution</div>', unsafe_allow_html=True)
        plt.figure(figsize=(10, 4))
        df['Salary'].plot(kind='hist', bins=20, edgecolor='black')
        plt.title('Salary Distribution')
        plt.xlabel('Salary')
        plt.ylabel('Frequency')
        st.pyplot(plt)

    # --- GENERATE WORD DOC ---
    st.markdown('<div class="subtitle">Generate Salary Report</div>', unsafe_allow_html=True)

    if st.button("Generate Report"):
        buffer = BytesIO()
        doc = Document()
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(11)

        doc.add_heading('Salary Report', 0)
        doc.add_paragraph(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")

        table = doc.add_table(rows=1, cols=len(df.columns))
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        for i, column in enumerate(df.columns):
            hdr_cells[i].text = str(column)

        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, item in enumerate(row):
                row_cells[i].text = str(item)

        doc.save(buffer)
        st.download_button(
            label="Download Report",
            data=buffer.getvalue(),
            file_name="salary_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# --- FOOTER ---
st.markdown('<div class="footer">Developed by HR Analytics Team</div>', unsafe_allow_html=True)