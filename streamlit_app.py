import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Configuration 
CORRECT_PASSWORD = "cancer2025"

# Session State Initialization 
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "password_attempt" not in st.session_state:
    st.session_state.password_attempt = ""

# Sidebar Login Logic 
with st.sidebar:
    st.image("IHME.webp", width=150)  

    st.title("🔒 Login")
    if st.session_state.authenticated:
        st.success("Access granted.")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.password_attempt = ""
            st.experimental_rerun()
    else:
        st.text("Please enter the password")
        st.text_input("Password", type="password", key="password_attempt")

        if st.session_state.password_attempt == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.experimental_rerun()
        elif st.session_state.password_attempt != "":
            st.error("Incorrect password")

# Main App Content 
if st.session_state.authenticated:
    # Header: title left, logo right
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("## 🧬 Lebanon Cancer Burden Dashboard")
        st.markdown("### Explore age, gender, and time trends of cancer mortality and incidence")

    with col2:
        st.image("IHME.webp", width=120) 

    st.markdown("---")

    # === Load dataset from repo ===
    df = pd.read_csv("cancer_lebanon.csv")
    st.success("Dataset loaded: cancer_lebanon.csv")

    # === SECTION 1: Data Analysis ===
    st.markdown("## 📊 Data Analysis")
    st.dataframe(df.head(10))

    st.markdown("### 🔎 Summary statistics by sex and age")
    summary = df[df['metric'] == "Number"].groupby(['sex', 'age'])['val'].describe().round(2)
    st.dataframe(summary)

    st.markdown("### 🔥 Heatmap of Average Number by Age and Sex")
    heatmap_df = df[df['metric'] == "Number"].pivot_table(index='age', columns='sex', values='val', aggfunc='mean')
    fig, ax = plt.subplots()
    sns.heatmap(heatmap_df, annot=True, fmt=".1f", cmap="YlOrRd", ax=ax)
    st.pyplot(fig)

    st.markdown("### 📈 Total Values Over Time by Sex (Number Only)")
    pivot_time = df[df['metric'] == "Number"].pivot_table(index="year", columns="sex", values="val", aggfunc="sum")
    st.line_chart(pivot_time)

    # === SECTION 2: Interactive Dashboard ===
    st.markdown("## 📈 Interactive Dashboard")
    selected_measure = st.selectbox("Select Measure:", sorted(df['measure'].unique()))
    selected_metric = st.radio("Select Metric:", df['metric'].unique())
    selected_sex = st.selectbox("Select Sex:", df['sex'].unique())
    selected_ages = st.multiselect("Select Age Group(s):", df['age'].unique(), default=df['age'].unique())
    selected_years = st.slider("Select Year Range:", min_value=int(df['year'].min()), max_value=int(df['year'].max()), value=(2005, 2021))

    # Filter dataset
    filtered_df = df[
        (df['measure'] == selected_measure) &
        (df['metric'] == selected_metric) &
        (df['sex'] == selected_sex) &
        (df['age'].isin(selected_ages)) &
        (df['year'].between(selected_years[0], selected_years[1]))
    ]

    if not filtered_df.empty:
        fig = px.line(
            filtered_df,
            x='year',
            y='val',
            color='age',
            markers=True,
            title=f"{selected_metric} of {selected_measure} ({selected_sex}) by Age Group",
            labels={"val": selected_metric}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data found for the selected filters.")

else:
    st.warning("🔒 This cancer analytics dashboard is password-protected. Enter the correct password in the sidebar to access.")
