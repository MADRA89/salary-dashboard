import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from docx.shared import Pt
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="HR Salary Evaluation", layout="wide")

# --- STYLES ---
st.markdown("""
    <style>
    .title { font-size:32px; font-weight: bold; margin-bottom: 20px; }
    .subtitle { font-size:24px; font-weight: bold; margin-top: 30px; }
    .center { text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- TITLE ---
st.markdown('<div class="title center">Faculty Salary Evaluation System</div>', unsafe_allow_html=True)

# --- FILE UPLOAD ---
uploaded_files = st.file_uploader("Upload Excel file(s)", type=["xlsx"], accept_multiple_files=True)

# --- ANALYZE BUTTON ---
analyze = st.button("Analyze")

if analyze and uploaded_files:
    for uploaded_file in uploaded_files:
        st.markdown(f'<div class="subtitle">📄 File: {uploaded_file.name}</div>', unsafe_allow_html=True)
        try:
            df = pd.read_excel(uploaded_file)

            # --- CLEANING DATA ---
            df.columns = df.columns.str.strip()
            df = df.dropna(subset=["Name"])

            # --- RANK CATEGORY BASED ON GRADE ---
            def determine_rank(grade):
                if pd.isna(grade):
                    return "Unknown"
                grade = str(grade).lower()
                if "12" in grade:
                    return "Professor"
                elif "11" in grade:
                    return "Associate Professor"
                elif "10" in grade:
                    return "Assistant Professor"
                else:
                    return "Other"

            df["Rank"] = df["Grade"].apply(determine_rank)

            # --- MARITAL STATUS & CAMPUS LOGIC ---
            def calculate_allowance(row):
                campus = str(row.get("Campus", "")).lower()
                status = str(row.get("Marital Status", "")).lower()
                grade = str(row.get("Grade", "")).lower()
                base = float(row.get("Basic Salary", 0))

                housing = transportation = phone = furniture = education = 0

                if "12" in grade:  # Professor
                    housing = 85000
                    transportation = 3500
                    phone = 300
                    furniture = 50000
                    education = 5000
                elif "11" in grade:  # Associate Professor
                    housing = 80000
                    transportation = 3000
                    phone = 200
                    furniture = 40000
                    education = 5000
                elif "10" in grade:  # Assistant Professor
                    housing = 70000
                    transportation = 2500
                    phone = 100
                    furniture = 30000
                    education = 5000

                if "al ain" in campus:
                    transportation += 1000

                if "single" in status:
                    education = 0

                total = base + housing + transportation + phone + education
                return pd.Series({
                    "Housing": housing,
                    "Transportation": transportation,
                    "Phone": phone,
                    "Furniture": furniture,
                    "Education": education,
                    "Total Salary": total
                })

            df = df.join(df.apply(calculate_allowance, axis=1))

            # --- DISPLAY ---
            st.dataframe(df)

            # --- SUMMARY ---
            st.markdown("### Summary Statistics")
            st.write(df.describe(include='all'))

        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {e}")