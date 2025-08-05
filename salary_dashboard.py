import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import random
import time

# --- Helper Functions ---
def mock_parse_cv_and_jd():
    education_scores = [10, 7, 4, 2]
    experience_scores = [10, 7, 5, 3]
    return {
        "educationScore": random.choice(education_scores),
        "experienceScore": random.choice(experience_scores)
    }

def mock_parse_interview_sheet():
    performance_scores = [10, 7, 5, 2]
    return {
        "performanceScore": random.choice(performance_scores)
    }

def mock_parse_equity_sheet(position_title):
    peer_count = random.randint(3, 8)
    peers = []
    for _ in range(peer_count):
        peer = {
            "id": f"EMP-{random.randint(1, 100):03}",
            "positionTitle": position_title,
            "hireDate": f"202{random.randint(0, 3)}-{random.randint(1, 12):02}-01",
            "compRate": random.randint(7000, 17000)
        }
        peers.append(peer)
    return peers

def get_step_interval(score):
    if score >= 25:
        return "12-15", "Top Range"
    elif score >= 20:
        return "9-11", "Mid-Upper Range"
    elif score >= 15:
        return "6-8", "Mid Range"
    elif score >= 10:
        return "3-5", "Lower-Mid Range"
    else:
        return "1-2", "Bottom Range"

# --- Streamlit UI ---
st.set_page_config(page_title="Salary Evaluation Dashboard", layout="wide")
st.title("💼 Salary Evaluation Dashboard")

tab1, tab2 = st.tabs(["Reference Matrices", "Candidate Analysis"])

with tab1:
    st.subheader("Candidate Evaluation Matrix")
    st.markdown("""
    | Criteria | Points |
    |----------|--------|
    | Master’s degree or higher | 10 |
    | Bachelor’s degree | 7 |
    | Diploma/Associate degree | 4 |
    | High school diploma or less | 2 |
    | 10+ years experience | 10 |
    | 5-10 years experience | 7 |
    | 2-5 years experience | 5 |
    | <2 years experience | 3 |
    | High performance | 10 |
    | Above average performance | 7 |
    | Average performance | 5 |
    | Limited performance | 2 |
    """)

    st.subheader("Score-to-Step Matrix")
    st.markdown("""
    | Score Range | Step Interval | Placement |
    |-------------|----------------|-----------|
    | 25–30 | Steps 12–15 | Top Range |
    | 20–24 | Steps 9–11 | Mid-Upper Range |
    | 15–19 | Steps 6–8 | Mid Range |
    | 10–14 | Steps 3–5 | Lower-Mid Range |
    | <10   | Steps 1–2 | Bottom Range |
    """)

with tab2:
    st.subheader("Candidate Inputs")
    name = st.text_input("Candidate Name")
    title = st.text_input("Position Title")
    grade = st.text_input("Position Grade")

    uploaded_cv = st.file_uploader("Upload CV", type=["pdf", "docx"])
    uploaded_jd = st.file_uploader("Upload Job Description", type=["pdf", "docx"])
    uploaded_interview = st.file_uploader("Upload Interview Sheet", type=["pdf", "docx"])
    uploaded_equity = st.file_uploader("Upload Internal Equity Sheet", type=["xlsx"])

    if uploaded_cv and uploaded_jd:
        with st.spinner("Evaluating Education & Experience..."):
            time.sleep(1)
            cv_result = mock_parse_cv_and_jd()
            education_score = cv_result["educationScore"]
            experience_score = cv_result["experienceScore"]
    else:
        education_score = st.slider("Education Score", 0, 10, 0)
        experience_score = st.slider("Experience Score", 0, 10, 0)

    if uploaded_interview:
        with st.spinner("Evaluating Interview..."):
            time.sleep(1)
            interview_result = mock_parse_interview_sheet()
            performance_score = interview_result["performanceScore"]
    else:
        performance_score = st.slider("Performance Score", 0, 10, 0)

    total_score = education_score + experience_score + performance_score
    step_range, placement = get_step_interval(total_score)

    st.markdown(f"### Total Score: `{total_score}/30` → Step Range: `{step_range}` ({placement})")

    selected_step = st.selectbox("Select Final Step", list(range(1, 16)))
    budget_threshold = st.number_input("Budget Threshold (AED)", step=500)
    recommended_salary = st.number_input("Recommended Salary Based on Evaluation (AED)", step=500)
    final_salary = st.number_input("Final Recommended Salary (AED)", step=500)

    # --- Equity Analysis Chart ---
    if uploaded_equity:
        with st.spinner("Analyzing Equity Data..."):
            time.sleep(2)
            peers = mock_parse_equity_sheet(title)
            df_peers = pd.DataFrame(peers)
            avg = df_peers["compRate"].mean()
            min_val = df_peers["compRate"].min()
            max_val = df_peers["compRate"].max()

            st.markdown(f"**Equity Range:** Min AED {min_val:,} | Avg AED {avg:,.0f} | Max AED {max_val:,}")

            chart = alt.Chart(df_peers).mark_bar().encode(
                x="id:N",
                y=alt.Y("compRate:Q", title="Compensation (AED)"),
                tooltip=["id", "compRate"]
            ).properties(title="Peer Compensation", width=600, height=300)

            st.altair_chart(chart, use_container_width=True)

    # --- Summary ---
    if st.button("Generate Summary"):
        summary = f"""
        ### Final Recommended Salary: AED {final_salary:,.0f} (Step {selected_step})
       
        **Evaluation Summary:**\n
        Candidate scored `{total_score}/30`, falling into **{placement}**.\n
        Initial suggested salary: AED {recommended_salary:,.0f}\n
        Budget Threshold: AED {budget_threshold:,.0f}\n
        """
        st.text_area("Final Summary & Justification", summary, height=200)
        st.success("Summary Generated!")
