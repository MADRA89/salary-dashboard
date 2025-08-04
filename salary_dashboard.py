import streamlit as st
import pandas as pd
import docx2txt
import re

st.set_page_config(page_title="💼 Salary Evaluation", layout="wide", page_icon="📊")

# --- STYLE ---
st.markdown("""
    <style>
    .main { background-color: #f4f6fa; }
    h1, h2, h3, .stTextInput>label, .stSlider>label { color: #1f3b57; }
    </style>
""", unsafe_allow_html=True)

st.title("💼 Administrative Staff Salary Evaluation Dashboard v2")
st.markdown("### Evaluate candidates using internal equity and scoring")

def extract_text(file):
    if file.name.endswith(".docx"):
        return docx2txt.process(file)
    return ""

def score_cv(text):
    text = text.lower()
    edu_score = 5 if re.search(r"master|phd|mba", text) else 3 if re.search(r"bachelor", text) else 1
    exp_years = sum([int(x) for x in re.findall(r"(\\d+)(?=\\s+years)", text)])
    exp_score = 5 if exp_years >= 10 else 3 if exp_years >= 5 else 1
    perf_score = 5 if re.search(r"leadership|initiative|achievements|performance", text) else 3
    return edu_score, exp_score, perf_score

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Candidate Info", "📎 Uploads", "📈 Scoring", "📊 Equity", "✅ Summary"
])

with tab1:
    st.header("1. Candidate Information")
    candidate_name = st.text_input("Candidate Name")
    position_title = st.text_input("Position Title")

with tab2:
    st.header("2. Upload Documents")
    cv_file = st.file_uploader("Upload CV (.docx only)", type=["docx"])
    equity_file = st.file_uploader("Upload Internal Equity Sheet (Excel)", type=["xlsx"])

with tab3:
    st.header("3. Scoring")
    if cv_file:
        text = extract_text(cv_file)
        edu_score, exp_score, perf_score = score_cv(text)
        st.success("✅ CV analyzed successfully")
    else:
        edu_score = st.slider("🎓 Education", 0, 10, 5)
        exp_score = st.slider("🛠️ Experience", 0, 10, 5)
        perf_score = st.slider("🚀 Performance", 0, 10, 5)

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
        filtered = df[df['Position Title'].str.lower() == position_title.strip().lower()]
        if not filtered.empty:
            avg = filtered['Comp Rate'].mean()
            st.dataframe(filtered)
            st.markdown(f"**Average Salary:** ${avg:,.2f}")
            equity_recommendation = st.selectbox("Placement", [
                "Above Peers", "Aligned with Peers", "Below Peers"
            ])
        else:
            st.warning("No match found.")
            equity_recommendation = st.selectbox("Manual Placement", [
                "Above Peers", "Aligned with Peers", "Below Peers"
            ])
    else:
        equity_recommendation = st.selectbox("Equity Placement", [
            "Above Peers", "Aligned with Peers", "Below Peers"
        ])

with tab5:
    st.header("5. Final Recommendation")
    budget = st.selectbox("Budget Flexibility", [
        "High Budget", "Moderate", "Minimal"
    ])
    negotiation = st.selectbox("Negotiation", [
        "Aligned", "Slight Gap", "Significant Gap"
    ])
    summary = f"""
**Candidate:** {candidate_name}
**Position Title:** {position_title}

### Scores:
- Education: {edu_score}
- Experience: {exp_score}
- Performance: {perf_score}
- **Total:** {total_score} → {step_interval}

### Equity:
- Placement: {equity_recommendation}

### Budget & Negotiation:
- Budget: {budget}
- Negotiation: {negotiation}
"""
    st.text_area("📋 Final Summary", summary, height=300)
    st.markdown("✅ *You can copy or print the summary using your browser.*")
