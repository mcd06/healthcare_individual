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

    # === Data Analysis Section ===
    st.markdown("## 📊 Data Analysis")
    st.write("Explore distribution and burden of key health metrics (Deaths, Prevalence, Incidence) by age and sex.")

    relevant_measures = ["Deaths", "Prevalence", "Incidence"]
    year_min = int(df["year"].min())
    year_max = int(df["year"].max())

     for measure in relevant_measures:
        df_m = df[(df["measure"] == measure) & (df["metric"] == "Number")]

        if df_m.empty:
            st.warning(f"No data available for {measure}")
            continue
        st.markdown(f"### 🧪 {measure} (Number) | {year_min}–{year_max}")

        # Boxplot by Age Group
        st.markdown(f"**Distribution of {measure} by Age Group ({year_min}–{year_max})**")
        fig_age, ax_age = plt.subplots(figsize=(10, 4))
        sns.boxplot(data=df_m, x="age", y="val", ax=ax_age)
        ax_age.set_title(f"{measure} Distribution by Age Group ({year_min}–{year_max})")
        ax_age.set_ylabel(f"{measure} Count")
        ax_age.set_xlabel("Age Group")
        st.pyplot(fig_age)

        # Boxplot by Sex
        st.markdown(f"**Distribution of {measure} by Sex ({year_min}–{year_max})**")
        fig_sex, ax_sex = plt.subplots(figsize=(6, 4))
        sns.boxplot(data=df_m, x="sex", y="val", ax=ax_sex)
        ax_sex.set_title(f"{measure} Distribution by Sex ({year_min}–{year_max})")
        ax_sex.set_ylabel(f"{measure} Count")
        ax_sex.set_xlabel("Sex")
        st.pyplot(fig_sex)

        # Heatmap (Age × Sex)
        st.markdown(f"**Average {measure} by Age and Sex (Heatmap, {year_min}–{year_max})**")
        heatmap_data = df_m.pivot_table(index="age", columns="sex", values="val", aggfunc="mean")
        fig_heat, ax_heat = plt.subplots(figsize=(8, 5))
        sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax_heat)
        ax_heat.set_title(f"Average {measure} by Age and Sex ({year_min}–{year_max})")
        st.pyplot(fig_heat)

        # Bar Chart: Total by Age
        st.markdown(f"**Total {measure} by Age Group ({year_min}–{year_max})**")
        bar_age = df_m.groupby("age")["val"].sum().sort_values(ascending=False)
        fig_bar_age, ax_bar_age = plt.subplots(figsize=(10, 4))
        sns.barplot(x=bar_age.index, y=bar_age.values, ax=ax_bar_age)
        ax_bar_age.set_title(f"Total {measure} by Age Group ({year_min}–{year_max})")
        ax_bar_age.set_ylabel(f"Total {measure}")
        ax_bar_age.set_xlabel("Age Group")
        st.pyplot(fig_bar_age)

        # Bar Chart: Total by Sex
        st.markdown(f"**Total {measure} by Sex ({year_min}–{year_max})**")
        bar_sex = df_m.groupby("sex")["val"].sum()
        fig_bar_sex, ax_bar_sex = plt.subplots(figsize=(5, 4))
        sns.barplot(x=bar_sex.index, y=bar_sex.values, ax=ax_bar_sex)
        ax_bar_sex.set_title(f"Total {measure} by Sex ({year_min}–{year_max})")
        ax_bar_sex.set_ylabel(f"Total {measure}")
        ax_bar_sex.set_xlabel("Sex")
        st.pyplot(fig_bar_sex)

        st.markdown("---")

    # === SECTION 2: Interactive Dashboard ===
    st.markdown("## 📈 Interactive Dashboard")
    selected_measure = st.selectbox("Select Measure:", sorted(df['measure'].unique()))
    selected_metric = st.radio("Select Metric:", df['metric'].unique())
    selected_sex = st.selectbox("Select Sex:", df['sex'].unique())
    selected_ages = st.multiselect("Select Age Group(s):", options=df['age'].unique())
    selected_years = st.slider(
        "Select Year Range:",
        min_value=int(df['year'].min()),
        max_value=int(df['year'].max()),
        value=(2005, 2021)
    )

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
