import streamlit as st
import pandas as pd
import random

# ---------- Mock AI Scoring Functions ----------
def mock_parse_cv_and_jd():
    return {
        "educationScore": random.choice([10, 7, 4, 2]),
        "experienceScore": random.choice([10, 7, 5, 3]),
    }

def mock_parse_interview():
    return {
        "performanceScore": random.choice([10, 7, 5, 2])
    }

def mock_parse_equity(position_title):
    count = random.randint(3, 8)
    peers = []
    for _ in range(count):
        peers.append({
            "id": f"EMP-00{random.randint(1,99)}",
            "positionTitle": position_title,
            "hireDate": f"202{random.randint(0,3)}-{random.randint(1,12):02}-01",
            "compRate": random.randint(7000, 17000)
        })
    return peers

def get_step_interval(score):
    if score >= 25: return { "range": "12–15", "label": "Top Range", "min": 12, "max": 15 }
    if score >= 20: return { "range": "9–11", "label": "Mid-Upper Range", "min": 9, "max": 11 }
    if score >= 15: return { "range": "6–8", "label": "Mid Range", "min": 6, "max": 8 }
    if score >= 10: return { "range": "3–5", "label": "Lower-Mid Range", "min": 3, "max": 5 }
    return { "range": "1–2", "label": "Bottom Range", "min": 1, "max": 2 }

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Salary Evaluation Dashboard", layout="wide")
st.title("💼 Salary Evaluation Dashboard")

with st.sidebar:
    st.header("📄 Candidate Info")
    name = st.text_input("Candidate Name")
    title = st.text_input("Position Title", "Administrative Officer")
    grade = st.text_input("Grade")
    salary_input = st.number_input("Final Salary (AED)", 0, 50000, 10000)

st.markdown("### 📁 Upload Evaluation Files")
col1, col2, col3 = st.columns(3)
with col1:
    cv = st.file_uploader("CV")
with col2:
    jd = st.file_uploader("Job Description")
with col3:
    interview = st.file_uploader("Interview Sheet")

# Simulate score calculation
if cv and jd:
    parsed = mock_parse_cv_and_jd()
    education = parsed["educationScore"]
    experience = parsed["experienceScore"]
else:
    education = st.slider("Education Score", 0, 10, 0)
    experience = st.slider("Experience Score", 0, 10, 0)

if interview:
    performance = mock_parse_interview()["performanceScore"]
else:
    performance = st.slider("Performance Score", 0, 10, 0)

# Score and Step Logic
total_score = education + experience + performance
interval = get_step_interval(total_score)
st.success(f"Total Score: {total_score}/30 – {interval['label']} ({interval['range']})")

steps = list(range(interval["min"], interval["max"] + 1))
selected_step = st.selectbox("Select Final Step", steps)

# Internal Equity Simulation
st.markdown("### 📊 Internal Equity Comparison")
equity_data = mock_parse_equity(title)
df = pd.DataFrame(equity_data)

min_val, max_val = df['compRate'].min(), df['compRate'].max()
avg_val = df['compRate'].mean()
range_third = (max_val - min_val) / 3

if salary_input < min_val:
    placement = "Below Min"
elif salary_input < min_val + range_third:
    placement = "Lower"
elif salary_input <= max_val - range_third:
    placement = "Mid"
elif salary_input <= max_val:
    placement = "Higher"
else:
    placement = "Above Max"

st.dataframe(df)
st.bar_chart(df.set_index("id")["compRate"])

st.markdown(f"**Salary Range:** AED {min_val:,} – AED {max_val:,}")
st.markdown(f"**Proposed Placement:** {placement}")

# Summary Generation
st.markdown("### 📝 Summary")
summary = f"""**Final Recommended Salary:** AED {salary_input:,} (Step {selected_step})

**Evaluation Summary:**
The candidate scored a total of {total_score}/30, placing them in the {interval['label']} ({interval['range']}).
Scores:
- Education: {education}
- Experience: {experience}
- Performance: {performance}

**Internal Equity:**
Salary Placement: {placement}  
Compared to {len(df)} peers (Range: AED {min_val:,} – AED {max_val:,}, Avg: AED {avg_val:,.0f})
"""
st.text_area("Summary Output", summary, height=300)
