import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
from pandas import ExcelWriter
from docx import Document
from docx.shared import Pt
import datetime

# إعداد الصفحة
st.set_page_config(page_title="HR Salary Evaluation", layout="wide")

# العنوان
st.title("HR Salary Evaluation Dashboard")

# تحميل ملف إكسل
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
analyze_clicked = st.button("Analyze Data")

# تحليل البيانات يتم فقط بعد الضغط على الزر
if uploaded_file and analyze_clicked:
    df = pd.read_excel(uploaded_file)
    
    # إضافة تقييمات وهمية إذا لم تكن موجودة
    if "Evaluation" not in df.columns:
        df["Evaluation"] = [""] * len(df)

    # إجراء التحليل فقط لمرة واحدة
    df["New Salary"] = df["Salary"]
    df["Evaluation"] = [
        "Excellent" if sal > 15000 else
        "Good" if sal > 10000 else
        "Average" if sal > 5000 else
        "Poor"
        for sal in df["Salary"]
    ]

    df["New Salary"] = [
        sal * 1.10 if eval == "Excellent" else
        sal * 1.07 if eval == "Good" else
        sal * 1.03 if eval == "Average" else
        sal
        for sal, eval in zip(df["Salary"], df["Evaluation"])
    ]

    st.session_state["analyzed_df"] = df.copy()

# عرض الجدول القابل للتعديل بعد التحليل
if "analyzed_df" in st.session_state:
    edited_df = st.data_editor(
        st.session_state["analyzed_df"],
        num_rows="dynamic",
        use_container_width=True
    )

    st.markdown("### Updated Table:")
    st.dataframe(edited_df, use_container_width=True)

    # تصدير البيانات إلى Excel
    def to_excel(df):
        output = BytesIO()
        with ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            writer.save()
        output.seek(0)
        return output

    excel_data = to_excel(edited_df)
    st.download_button("📥 Download as Excel", data=excel_data, file_name="Updated_Salaries.xlsx")

    # تصدير البيانات إلى Word
    def generate_word_report(df):
        doc = Document()
        doc.add_heading("Salary Evaluation Report", 0)
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        doc.add_paragraph(f"Date: {date_str}")
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, column in enumerate(df.columns):
            hdr_cells[i].text = str(column)
        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, cell in enumerate(row):
                row_cells[i].text = str(cell)
        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf

    word_file = generate_word_report(edited_df)
    st.download_button("📄 Download as Word", data=word_file, file_name="Salary_Report.docx")

    # رسم بياني للتقييمات
    st.markdown("### Evaluation Chart:")
    chart = alt.Chart(edited_df).mark_bar().encode(
        x='Evaluation:N',
        y='count():Q',
        color='Evaluation:N'
    ).properties(width=600)
    st.altair_chart(chart)

else:
    st.info("Please upload an Excel file and click the 'Analyze Data' button.")