# salary_dashboard_ai.py
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF for extracting text from PDF
import docx2txt  # For .docx files
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="💼 Salary Evaluation", layout="wide", page_icon="📊")

# --- STYLE ---
st.markdown("""
    <style>
    .main {
        background-color: #f4f6fa;
    }
    h1, h2, h3, .stTextInput>label, .stSlider>label {
        color: #1f3b57;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💼 Administrative Staff Salary Evaluation Dashboard v2")
st.markdown("### Evaluate candidates using AI and internal equity data")

# --- FUNCTIONS ---
def extract_text(file):
    if file.name.endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = " ".join([page.get_text() for page in doc])
        return text
    elif file.name.endswith(".docx"):
        return docx2txt.process(file)
    else:
        return ""

def score_cv(text):
    # Simple AI logic (placeholder, can integrate ML later)
    text = text.lower()
    edu_score = 5 if re.search(r"master|phd|mba", text) else 3 if re.search(r"bachelor", text) else 1
    exp_years = sum([int(x) for x in re.findall(r"(\d+)(?=\s+years)", text)])
    exp_score = 5 if exp_years >= 10 else 3 if exp_years >= 5 else 1
    perf_score = 5 if re.search(r"leadership|initiative|achievements|performance", text) else 3
    return edu_score, exp_score, perf_score

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Candidate Info", "📎 Uploads", "📈 Scoring", "📊 Equity", "✅ Summary"
])

with tab1:
    st.header("1. Candidate Information")
    candidate_name = st.text_input("Candidate Name")
    position_title = st.text_input("Position Title")

with tab2:
    st.header("2. Upload Documents")
    cv_file = st.file_uploader("Upload CV", type=["pdf", "docx"])
    jd_file = st.file_uploader("Upload Job Description", type=["pdf", "docx"])
    interview_file = st.file_uploader("Upload Interview Evaluation", type=["pdf", "docx"])
    equity_file = st.file_uploader("Upload Internal Equity Sheet (Excel)", type=["xlsx"])

with tab3:
    st.header("3. AI-Powered Scoring")
    if cv_file:
        with st.spinner("Analyzing CV..."):
            text = extract_text(cv_file)
            edu_score, exp_score, perf_score = score_cv(text)
            st.success("✅ AI Scoring Complete")
    else:
        edu_score = st.slider("🎓 Education & Qualifications", 0, 10, 5)
        exp_score = st.slider("🛠️ Experience", 0, 10, 5)
        perf_score = st.slider("🚀 Performance Potential", 0, 10, 5)

    total_score = edu_score + exp_score + perf_score
    st.metric("⭐ Total Score", total_score)

    if total_score >= 25:
        step_interval = "Top Range"
    elif total_score >= 20:
        step_interval = "Mid-Upper Range"
    elif total_score >= 15:
        step_interval = "Mid Range"
    elif total_score >= 10:
        step_interval = "Lower-Mid Range"
    else:
        step_interval = "Bottom Range"

    st.success(f"🔎 Step Interval: **{step_interval}**")

with tab4:
    st.header("4. Internal Equity Analysis")
    if equity_file:
        df = pd.read_excel(equity_file)
        filtered_df = df[df['Position Title'].str.lower() == position_title.strip().lower()]
        if not filtered_df.empty:
            avg_salary = filtered_df['Comp Rate'].mean()
            min_salary = filtered_df['Comp Rate'].min()
            max_salary = filtered_df['Comp Rate'].max()
            st.dataframe(filtered_df)
            st.markdown(f"""
            - **Peer Average Salary:** 💲{avg_salary:,.2f}  
            - **Min Salary:** 💲{min_salary:,.2f}  
            - **Max Salary:** 💲{max_salary:,.2f}  
            """)
            equity_recommendation = st.selectbox("Equity Placement", [
                "Above Peers (Higher in Interval)",
                "Aligned with Peers (Mid Interval)",
                "Below Peers (Lower in Interval)"
            ])
        else:
            st.warning("⚠️ No matching records found.")
            equity_recommendation = st.selectbox("Manual Placement", [
                "Above Peers (Higher in Interval)",
                "Aligned with Peers (Mid Interval)",
                "Below Peers (Lower in Interval)"
            ])
    else:
        equity_recommendation = st.selectbox("Internal Equity Placement (No file uploaded)", [
            "Above Peers (Higher in Interval)",
            "Aligned with Peers (Mid Interval)",
            "Below Peers (Lower in Interval)"
        ])

with tab5:
    st.header("5. Final Recommendation")
    budget = st.selectbox("Organizational Budget Flexibility", [
        "High Budget Flexibility", "Moderate Flexibility", "Minimal Flexibility"])
    negotiation = st.selectbox("Candidate Negotiation/Expectations", [
        "Expectations Aligned", "Slight Gap - Negotiable", "Significant Gap"])

    final_summary = f"""
**Candidate:** {candidate_name}  
**Position Title:** {position_title}  

### Primary Scoring:
- Education: {edu_score}
- Experience: {exp_score}
- Performance: {perf_score}
- **Total Score:** {total_score} → **{step_interval}**

### Equity Placement:
- Recommendation: {equity_recommendation}

### Budget & Negotiation:
- Budget: {budget}
- Negotiation: {negotiation}
    """
    st.text_area("📋 Final Summary", final_summary, height=300)
    st.markdown("✅ *Copy this summary or save it as PDF using your browser print option.*")

