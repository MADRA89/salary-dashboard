import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import random
import time
from io import BytesIO

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

def get_step_interval(score):
    if score >= 25:
        return list(range(12, 16)), "Top Range"
    elif score >= 20:
        return list(range(9, 12)), "Mid-Upper Range"
    elif score >= 15:
        return list(range(6, 9)), "Mid Range"
    elif score >= 10:
        return list(range(3, 6)), "Lower-Mid Range"
    else:
        return list(range(1, 3)), "Bottom Range"

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="EquityAnalysis", index=False)
    processed_data = output.getvalue()
    return processed_data

# --- Streamlit UI ---
st.set_page_config(page_title="Salary Evaluation Dashboard", layout="wide")
st.title("📊 Salary Evaluation Dashboard")

tab1, tab2 = st.tabs(["Evaluation & Scoring Matrices", "Candidate Analysis"])

# --- Tab 1: Matrices ---
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎓 Candidate Evaluation Matrix")
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

    with col2:
        st.subheader("📈 Score-to-Step Matrix")
        st.markdown("""
        | Score Range | Step Interval | Placement |
        |-------------|----------------|-----------|
        | 25–30 | Steps 12–15 | Top Range |
        | 20–24 | Steps 9–11 | Mid-Upper Range |
        | 15–19 | Steps 6–8 | Mid Range |
        | 10–14 | Steps 3–5 | Lower-Mid Range |
        | <10   | Steps 1–2 | Bottom Range |
        """)

# --- Tab 2: Main Dashboard ---
with tab2:
    st.subheader("Step 1: Candidate Profile")
    name = st.text_input("Candidate Name")
    title = st.text_input("Position Title (used for equity comparison)")
    grade = st.text_input("Position Grade")

    st.subheader("Step 2: Upload Documents")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        uploaded_cv = st.file_uploader("📄 CV", type=["pdf", "docx"])
    with col2:
        uploaded_jd = st.file_uploader("📝 Job Description", type=["pdf", "docx"])
    with col3:
        uploaded_interview = st.file_uploader("🗒️ Interview Sheet", type=["pdf", "docx"])
    with col4:
        uploaded_equity = st.file_uploader("📊 Internal Equity Excel", type=["xlsx"])

    st.subheader("Step 3: Evaluation Scoring")
    if uploaded_cv and uploaded_jd:
        with st.spinner("Evaluating CV & JD..."):
            time.sleep(1)
            scores = mock_parse_cv_and_jd()
            education_score = scores["educationScore"]
            experience_score = scores["experienceScore"]
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
    interval_options, placement = get_step_interval(total_score)

    st.markdown(f"**Total Score:** {total_score}/30 → Step Interval: {interval_options} → Placement: **{placement}**")
    selected_step = st.selectbox("Select Step from Suggested Interval", interval_options)

    st.subheader("Step 4: Salary Recommendation")
    budget_threshold = st.number_input("💰 Budget Threshold (AED)", step=500)
    recommended_salary = st.number_input("🤖 AI-Recommended Salary (AED)", step=500)
    final_salary = st.number_input("✅ Final Recommended Salary (AED)", step=500)

    st.subheader("Step 5: Internal Equity Analysis")
    if uploaded_equity:
        df_peers = pd.read_excel(uploaded_equity)
        if "compRate" in df_peers.columns and "id" in df_peers.columns:
            df_peers = df_peers.append({
                "id": "Candidate",
                "positionTitle": title,
                "compRate": final_salary
            }, ignore_index=True)

            st.dataframe(df_peers)

            avg = df_peers["compRate"].mean()
            min_val = df_peers["compRate"].min()
            max_val = df_peers["compRate"].max()

            st.markdown(f"**Equity Range:** Min AED {min_val:,} | Avg AED {avg:,.0f} | Max AED {max_val:,}")

            chart = alt.Chart(df_peers).mark_bar().encode(
                x=alt.X("id:N", title="Employee ID"),
                y=alt.Y("compRate:Q", title="Compensation (AED)"),
                color=alt.condition(alt.datum.id == "Candidate", alt.value("orange"), alt.value("steelblue")),
                tooltip=["id", "compRate"]
            ).properties(title="Compensation Comparison", width=700, height=350)

            st.altair_chart(chart, use_container_width=True)

            excel_data = convert_df_to_excel(df_peers)
            st.download_button(
                label="📥 Download Equity Data (Excel)",
                data=excel_data,
                file_name="equity_analysis.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("⚠️ Excel file must contain 'id' and 'compRate' columns.")

    st.subheader("Step 6: Budget Status Check")
    if final_salary and budget_threshold:
        if final_salary <= budget_threshold:
            st.success(f"✅ Within Budget (AED {final_salary:,.0f} ≤ AED {budget_threshold:,.0f})")
        else:
            st.error(f"❌ Out of Budget (AED {final_salary:,.0f} > AED {budget_threshold:,.0f})")

    st.subheader("Step 7: Final Summary & HR Comments")
    hr_comments = st.text_area("📝 HR Final Comments or Notes")

    if st.button("Generate Final Summary"):
        summary = f"""
        ### Final Recommendation Summary

        - Candidate Name: {name}
        - Position Title: {title}
        - Total Score: {total_score}/30 → Step Interval: {interval_options} → Placement: {placement}
        - Selected Step: {selected_step}
        - Recommended Salary (AI): AED {recommended_salary:,.0f}
        - Final Recommended Salary: AED {final_salary:,.0f}
        - Budget Threshold: AED {budget_threshold:,.0f}
        - Budget Status: {"Within" if final_salary <= budget_threshold else "Out of"} Budget
        - HR Final Comments: {hr_comments}
        """
        st.text_area("📋 Final Summary", summary, height=250)
        st.download_button("📤 Download Final Summary (Text)", data=summary, file_name="salary_summary.txt")
