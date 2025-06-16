import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# === Configuration ===
CORRECT_PASSWORD = "cancer25"

# === Session State Initialization ===
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "password_attempt" not in st.session_state:
    st.session_state.password_attempt = ""

# === Sidebar Login Logic ===
with st.sidebar:
    st.image("IHME.webp", width=150)
    st.title("🔒 Login")

    if st.session_state.authenticated:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.password_attempt = ""
            st.experimental_rerun()
    else:
        st.text("Please enter the password")
        st.text_input("Password", type="password", key="password_attempt")

        if st.session_state.password_attempt == CORRECT_PASSWORD:
            st.session_state.authenticated = True

# === Main App Content ===
if st.session_state.authenticated:
    # === Load Dataset ===
    df = pd.read_csv("cancer_lebanon.csv")

    # Sort age groups
    sorted_ages = sorted(df["age"].unique(), key=lambda x: int(x.split('-')[0]) if '-' in x else (100 if '75+' in x else 0))

    # === Sidebar Filters ===
    st.sidebar.markdown("## 🧪 Select Analysis Options")
    selected_measure = st.sidebar.selectbox(
        "Choose a metric to analyze:",
        options=["Deaths", "Prevalence", "Incidence"]
    )

    st.sidebar.markdown("## 📊 Select Visualizations")
    show_box_age = st.sidebar.checkbox("📦 Boxplot of Distribution by Age Group")
    show_box_sex = st.sidebar.checkbox("📦 Boxplot of Distribution by Sex")
    show_heatmap = st.sidebar.checkbox("🔥 Heatmap of Average by Age and Sex")
    show_bar_age = st.sidebar.checkbox("📊 Bar Chart of Total by Age Group")
    show_bar_sex = st.sidebar.checkbox("📊 Bar Chart of Total by Sex")

    st.sidebar.markdown("## 📈 Dashboard Settings")
    show_dashboard = st.sidebar.selectbox("Show Interactive Dashboard?", ["No", "Yes"])

    if show_dashboard == "Yes":
        selected_dash_metric = st.sidebar.radio("Select Metric:", df['metric'].unique())
        selected_dash_sex = st.sidebar.selectbox("Select Sex:", df['sex'].unique())
        selected_dash_ages = st.sidebar.multiselect("Select Age Group(s):", options=sorted_ages)
        selected_dash_years = st.sidebar.slider(
            "Select Year Range:",
            min_value=int(df['year'].min()),
            max_value=int(df['year'].max()),
            value=(2005, 2021)
        )
    else:
        selected_dash_metric = None

    # === Header ===
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("## 🧬 Lebanon Cancer Burden Dashboard")
        st.markdown("### Explore age, gender, and time trends of cancer mortality and incidence")
    with col2:
        st.image("IHME.webp", width=120)

    st.markdown("---")

    # === Common Setup ===
    year_min = int(df["year"].min())
    year_max = int(df["year"].max())
    df_m = df[(df["measure"] == selected_measure) & (df["metric"] == "Number")]

    # === Tabs Layout ===
    if show_dashboard == "Yes":
        tab1, tab2 = st.tabs(["📊 Data Analysis", "📈 Interactive Dashboard"])
    else:
        tab1 = st.tabs(["📊 Data Analysis"])[0]

    # === TAB 1: Data Analysis ===
    with tab1:
        st.markdown("## 📊 Data Analysis")

        if df_m.empty:
            st.warning(f"No data available for {selected_measure}")
        else:
            st.markdown(f"### 🧪 {selected_measure} ({year_min}–{year_max})")

            if show_box_age:
                st.markdown("**📦 Distribution by Age Group**")
                fig_age, ax_age = plt.subplots(figsize=(10, 4))
                sns.boxplot(data=df_m, x="age", y="val", order=sorted_ages, ax=ax_age)
                ax_age.set_title(f"Boxplot of {selected_measure} by Age Group ({year_min}–{year_max})")
                st.pyplot(fig_age)

            if show_box_sex:
                st.markdown("**📦 Distribution by Sex**")
                fig_sex, ax_sex = plt.subplots(figsize=(6, 4))
                sns.boxplot(data=df_m, x="sex", y="val", ax=ax_sex)
                ax_sex.set_title(f"Boxplot of {selected_measure} by Sex ({year_min}–{year_max})")
                st.pyplot(fig_sex)

            if show_heatmap:
                st.markdown("**🔥 Average by Age and Sex**")
                heatmap_data = df_m.pivot_table(index="age", columns="sex", values="val", aggfunc="mean").reindex(index=sorted_ages)
                fig_heat, ax_heat = plt.subplots(figsize=(8, 5))
                sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax_heat)
                ax_heat.set_title(f"Heatmap of Average {selected_measure} by Age and Sex ({year_min}–{year_max})")
                st.pyplot(fig_heat)

            if show_bar_age:
                st.markdown("**📊 Total by Age Group**")
                bar_age = df_m.groupby("age")["val"].sum().reindex(sorted_ages)
                fig_bar_age, ax_bar_age = plt.subplots(figsize=(10, 4))
                sns.barplot(x=bar_age.index, y=bar_age.values, ax=ax_bar_age)
                ax_bar_age.set_title(f"Total {selected_measure} by Age Group ({year_min}–{year_max})")
                st.pyplot(fig_bar_age)

            if show_bar_sex:
                st.markdown("**📊 Total by Sex**")
                bar_sex = df_m.groupby("sex")["val"].sum()
                fig_bar_sex, ax_bar_sex = plt.subplots(figsize=(5, 4))
                sns.barplot(x=bar_sex.index, y=bar_sex.values, ax=ax_bar_sex)
                ax_bar_sex.set_title(f"Total {selected_measure} by Sex ({year_min}–{year_max})")
                st.pyplot(fig_bar_sex)

    # === TAB 2: Interactive Dashboard ===
    if show_dashboard == "Yes":
        with tab2:
            st.markdown("## 📈 Interactive Dashboard")

            if selected_dash_metric and selected_dash_ages:
                filtered_df = df[
                    (df['measure'] == selected_measure) &
                    (df['metric'] == selected_dash_metric) &
                    (df['sex'] == selected_dash_sex) &
                    (df['age'].isin(selected_dash_ages)) &
                    (df['year'].between(selected_dash_years[0], selected_dash_years[1]))
                ]

                if not filtered_df.empty:
                    fig = px.line(
                        filtered_df,
                        x='year',
                        y='val',
                        color='age',
                        markers=True,
                        title=f"{selected_dash_metric} of {selected_measure} ({selected_dash_sex}) by Age Group",
                        labels={"val": selected_dash_metric}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data found for the selected filters.")
            else:
                st.info("Please select at least one age group to display results.")

else:
    st.warning("🔒 This cancer analytics dashboard is password-protected. Enter the correct password in the sidebar to access.")
