from pathlib import Path
from io import BytesIO
import pandas as pd
import plotly.express as px
import streamlit as st
from agent import answer_with_ai, build_analysis_context
from tools import build_insights, profile_dataset, read_csv_safely

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="AI Data Analyst", page_icon="📊", layout="wide")
st.title("📊 AI Data Analyst")
st.caption("Explore datasets, uncover patterns, and ask questions in plain English.")

with st.sidebar:
    st.header("Data source")
    uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
    use_sample = st.checkbox("Use included sales dataset", value=uploaded is None)
    st.divider()
    st.caption("Analysis runs locally. Aggregate statistics are sent to OpenAI only when you submit a question and configure an API key.")

try:
    if uploaded is not None:
        df = read_csv_safely(BytesIO(uploaded.getvalue()))
        dataset_name = uploaded.name
    elif use_sample and (ROOT / "dataset.csv").exists():
        df = read_csv_safely(ROOT / "dataset.csv")
        dataset_name = "dataset.csv"
    else:
        st.info("Upload a CSV file or select the included sample dataset.")
        st.stop()
except Exception as exc:
    st.error(f"Could not read the CSV: {exc}")
    st.stop()

if df.empty:
    st.warning("The selected CSV has no data rows.")
    st.stop()

profile = profile_dataset(df)
insights = build_insights(df, profile)
st.success(f"Loaded {dataset_name}")
m = st.columns(4)
m[0].metric("Rows", f"{profile['rows']:,}")
m[1].metric("Columns", f"{profile['columns']:,}")
m[2].metric("Missing cells", f"{profile['missing_cells']:,}")
m[3].metric("Duplicate rows", f"{profile['duplicate_rows']:,}")

overview, quality, explore, analyst = st.tabs(["Overview", "Data quality", "Explore", "Ask the analyst"])
with overview:
    st.subheader("Dataset preview")
    st.dataframe(df.head(100), width="stretch")
    st.subheader("Column profile")
    st.dataframe(pd.DataFrame(profile["column_profiles"]), width="stretch")
    st.subheader("Automated observations")
    for insight in insights:
        st.write("• " + insight)

with quality:
    missing = df.isna().sum().rename("Missing values").reset_index()
    missing.columns = ["Column", "Missing values"]
    missing = missing.sort_values("Missing values", ascending=False)
    st.dataframe(missing, width="stretch")
    positive = missing[missing["Missing values"] > 0]
    if positive.empty:
        st.success("No missing values detected.")
    else:
        st.plotly_chart(px.bar(positive, x="Column", y="Missing values", title="Missing values by column"), width="stretch")
    st.write(f"Duplicate rows: **{profile['duplicate_rows']}**")
    if profile["duplicate_rows"]:
        st.dataframe(df[df.duplicated(keep=False)].head(100), width="stretch")

with explore:
    numeric = df.select_dtypes(include="number").columns.tolist()
    categorical = [c for c in df.columns if c not in numeric and df[c].nunique(dropna=True) <= 100]
    kind = st.selectbox("Chart type", ["Bar", "Line", "Scatter", "Histogram", "Box"])
    if kind in ("Histogram", "Box"):
        if not numeric:
            st.info("No numeric columns are available for this chart.")
        else:
            y = st.selectbox("Numeric column", numeric)
            if kind == "Histogram":
                fig = px.histogram(df, x=y, title=f"Distribution of {y}")
            else:
                group = st.selectbox("Group by (optional)", ["None"] + categorical)
                fig = px.box(df, x=None if group == "None" else group, y=y, title=f"{y} distribution")
            st.plotly_chart(fig, width="stretch")
    elif kind in ("Bar", "Line"):
        if not numeric:
            st.info("At least one numeric column is required.")
        else:
            x = st.selectbox("Category / X axis", df.columns.tolist())
            y = st.selectbox("Numeric / Y axis", numeric)
            agg = st.selectbox("Aggregation", ["sum", "mean", "median", "count"])
            values = getattr(df.groupby(x, dropna=False)[y], agg)().reset_index(name=y)
            if kind == "Bar":
                fig = px.bar(values, x=x, y=y, title=f"{agg.title()} of {y} by {x}")
            else:
                fig = px.line(values, x=x, y=y, markers=True, title=f"{agg.title()} of {y} by {x}")
            st.plotly_chart(fig, width="stretch")
    else:
        if len(numeric) < 2:
            st.info("At least two numeric columns are required for a scatter plot.")
        else:
            x = st.selectbox("X axis", numeric)
            y = st.selectbox("Y axis", [c for c in numeric if c != x])
            color = st.selectbox("Color by (optional)", ["None"] + categorical)
            fig = px.scatter(df, x=x, y=y, color=None if color == "None" else color, title=f"{y} vs {x}")
            st.plotly_chart(fig, width="stretch")

with analyst:
    st.subheader("Ask a question about your data")
    st.caption("Examples: Which region has the highest total sales? What stands out? Are there data-quality issues?")
    question = st.text_area("Your question", placeholder="Ask something about the dataset…", height=100)
    if st.button("Analyze question", type="primary", disabled=not question.strip()):
        with st.spinner("Analyzing…"):
            context = build_analysis_context(df, profile, insights)
            answer, mode = answer_with_ai(question.strip(), context)
        st.markdown(answer)
        st.caption("Answer mode: " + mode)

st.divider()
st.download_button("Download current dataset", df.to_csv(index=False).encode("utf-8"), "analyzed_dataset.csv", "text/csv", width="stretch")
st.caption("Built with Python, Pandas, Plotly, Streamlit, and optional OpenAI.")
