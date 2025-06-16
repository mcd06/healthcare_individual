import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Configuration
CORRECT_PASSWORD = "cancer25"

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
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.password_attempt = ""
            st.rerun()
    else:
        st.text("Please enter the password")
        st.text_input("Password", type="password", key="password_attempt")
        if st.session_state.password_attempt == CORRECT_PASSWORD:
            st.session_state.authenticated = True

# Main App Content 
if st.session_state.authenticated:
    # Load Dataset
    df = pd.read_csv("cancer_lebanon.csv")

    # Sort age groups ascendingly
    sorted_ages = sorted(df["age"].unique(), key=lambda x: int(x.split('-')[0]) if '-' in x else (100 if '75+' in x else 0))

    # Sidebar Toggles 
    st.sidebar.markdown("## 📊 Data Analysis Configuration")
    show_analysis = st.sidebar.checkbox("Show Data Analysis") 

    if show_analysis:
        with st.sidebar.expander("Analysis Controls", expanded=True):
            analysis_measures = ["Incidence", "Prevalence", "Deaths"]
            selected_measure = st.selectbox("Choose a measure to analyze:", analysis_measures)
            st.markdown("### Visualizations")
            show_box_age = st.checkbox("Boxplot of Distribution by Age Group")
            show_box_gender = st.checkbox("Boxplot of Distribution by Gender")
            show_heatmap = st.checkbox("Heatmap of Mean by Age and Gender")
            show_bar_age = st.checkbox("Bar Chart of Sum by Age Group")
            show_bar_gender = st.checkbox("Bar Chart of Sum by Gender")

    # Dashboard Section Header
    st.sidebar.markdown("## 📈 Interactive Dashboard Setup")
    show_dashboard = st.sidebar.checkbox("Show Interactive Dashboard")

    if show_dashboard:
        metric_display_names = {
            "Number": "Number",
            "Rate": "Rate (per 100,000)"
        }
        selected_dash_metric = st.sidebar.radio(
            "Select Metric:",
            options=list(metric_display_names.keys()),
            format_func=lambda x: metric_display_names[x]
        )
        with st.sidebar.expander("Dashboard Controls", expanded=True):
            dashboard_order = [
                "Incidence",
                "Prevalence",
                "Deaths",
                "YLLs (Years of Life Lost)",
                "YLDs (Years Lived with Disability)",
                "DALYs (Disability-Adjusted Life Years)"
            ]
            actual_measures = list(df["measure"].unique())
            final_order = [m for m in dashboard_order if m in actual_measures]
            selected_dash_measure = st.selectbox("Choose Measure for Dashboard:", final_order)
            selected_dash_gender = st.selectbox("Select Gender:", df['gender'].unique())
            selected_dash_ages = st.multiselect("Select Age Group(s):", options=sorted_ages)
            selected_dash_years = st.slider(
                "Select Year Range:",
                min_value=int(df['year'].min()),
                max_value=int(df['year'].max()),
                value=(2003, 2018)
            )

    # Header 
    st.markdown("## 🧬 Cancer Burden in Lebanon: Trends and Insights")
    st.markdown(
        "Explore trends in cancer-related indicators such as incidence, prevalence, and mortality "
        "across different age groups and genders in Lebanon from 2000 to 2021. "
        "Use the visual analysis and interactive tools to uncover patterns, disparities, and key insights."
    )
    st.markdown("---")

    # Common Setup
    year_min = int(df["year"].min())
    year_max = int(df["year"].max())

    # Tabs Layout
    if show_analysis and show_dashboard:
        tab1, tab2 = st.tabs(["📊 Data Analysis", "📈 Interactive Dashboard"])
    elif show_analysis:
        tab1 = st.tabs(["📊 Data Analysis"])[0]
    elif show_dashboard:
        tab2 = st.tabs(["📈 Interactive Dashboard"])[0]
    else:
        st.info("Please enable one or both views from the sidebar to continue.")

    # TAB 1: Data Analysis 
    if show_analysis:
        with tab1:

            df_m = df[(df["measure"] == selected_measure) & (df["metric"] == "Number")]

            if df_m.empty:
                st.warning(f"No data available for {selected_measure}")
            else:
                st.markdown(f"### Overview of {selected_measure} Trends ({year_min}–{year_max})")

                if show_box_age:
                    st.markdown("**Distribution by Age Group**")
                    fig_age, ax_age = plt.subplots(figsize=(10, 4))
                    sns.boxplot(data=df_m, x="age", y="val", order=sorted_ages, ax=ax_age)
                    ax_age.set_xlabel("Age Group")
                    ax_age.set_ylabel(selected_measure)
                    sns.despine(top=True, right=True)
                    st.pyplot(fig_age)

                if show_box_gender:
                    st.markdown("**Distribution by Gender**")
                    fig_gender, ax_gender = plt.subplots(figsize=(6, 4))
                    sns.boxplot(data=df_m, x="gender", y="val", ax=ax_gender)
                    ax_gender.set_xlabel("Gender")
                    ax_gender.set_ylabel(selected_measure)
                    sns.despine(top=True, right=True)
                    st.pyplot(fig_gender)

                if show_heatmap:
                    st.markdown("**Mean by Age and Gender**")
                    heatmap_data = df_m.pivot_table(index="age", columns="gender", values="val", aggfunc="mean").reindex(index=sorted_ages)
                    fig_heat, ax_heat = plt.subplots(figsize=(8, 5))
                    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax_heat)
                    st.pyplot(fig_heat)

                if show_bar_age:
                    st.markdown("**Sum by Age Group**")
                    bar_age = df_m.groupby("age")["val"].sum().reindex(sorted_ages)
                    fig_bar_age, ax_bar_age = plt.subplots(figsize=(10, 4))
                    sns.barplot(x=bar_age.index, y=bar_age.values, ax=ax_bar_age)
                    ax_bar_age.set_xlabel("Age Group")
                    ax_bar_age.set_ylabel(f"Sum of {selected_measure}")
                    sns.despine(top=True, right=True)
                    st.pyplot(fig_bar_age)

                if show_bar_gender:
                    st.markdown("**Sum by Gender**")
                    bar_gender = df_m.groupby("gender")["val"].sum()
                    fig_bar_gender, ax_bar_gender = plt.subplots(figsize=(5, 4))
                    sns.barplot(x=bar_gender.index, y=bar_gender.values, ax=ax_bar_gender)
                    ax_bar_gender.set_xlabel("Gender")
                    ax_bar_gender.set_ylabel(f"Sum of {selected_measure}")
                    sns.despine(top=True, right=True)
                    st.pyplot(fig_bar_gender)

    # TAB 2: Interactive Dashboard 
    if show_dashboard:
        with tab2:

            if selected_dash_ages:
                filtered_df = df[
                    (df['measure'] == selected_dash_measure) &
                    (df['metric'] == selected_dash_metric) &
                    (df['gender'] == selected_dash_gender) &
                    (df['age'].isin(selected_dash_ages)) &
                    (df['year'].between(selected_dash_years[0], selected_dash_years[1]))
                ]

                if not filtered_df.empty:
                    fig = px.line(
                    filtered_df.sort_values("year"),
                    x='year',
                    y='val',
                    color='age',
                    markers=False,
                    line_shape="linear",
                    title=f"Time Trend of {selected_dash_measure} in {selected_dash_gender}s by Age Group",,
                    labels={
                        "val": f"{selected_dash_measure} ({metric_display_names[selected_dash_metric]})",
                        "year": "Year",
                        "age": "Age Group"
                    }
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data found for the selected filters.")
            else:
                st.info("Please select at least one age group to display results.")

else:
    st.warning("🔒 This cancer analytics dashboard is password-protected. Enter the correct password in the sidebar to access.")
