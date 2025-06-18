import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration ---
CORRECT_PASSWORD = "cancer25"
st.set_page_config(layout="wide", page_title="Cancer Dashboard", page_icon="🧬")

# --- Seaborn Palette for Plotly ---
seaborn_palette = ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854']

# --- Session State Initialization ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "password_attempt" not in st.session_state:
    st.session_state.password_attempt = ""

# --- Sidebar Login ---
with st.sidebar:
    st.image("IHME.webp", width=150)
    st.title("🔒 Login")
    if st.session_state.authenticated:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.password_attempt = ""
            st.rerun()
    else:
        st.text("Enter password to access the dashboard")
        st.text_input("Password", type="password", key="password_attempt")
        if st.session_state.password_attempt == CORRECT_PASSWORD:
            st.session_state.authenticated = True

# --- Main Content ---
if st.session_state.authenticated:
    df = pd.read_csv("cancer_lebanon.csv")
    df = df[df["age"] != "All ages"]
    sorted_ages = ["15-19 years", "20-54 years", "55-59 years", "60-64 years", "65-74 years"]
    gender_colors = {"Male": seaborn_palette[0], "Female": seaborn_palette[1]}

    # --- Tabs Setup ---
    st.markdown("## 🧬 Cancer Burden in Lebanon Dashboard")
    st.markdown("Explore cancer incidence and mortality in Lebanon by number and rate, gender, and age groups (2000–2020).")
    tab1, tab2, tab3, tab4 = st.tabs([
        "Number by Incidence",
        "Number by Death",
        "Rate by Incidence",
        "Rate by Death"
    ])

    def render_dashboard(measure, metric, tab):
        filtered_df = df[(df["measure"] == measure) & (df["metric"] == metric)]
        if filtered_df.empty:
            tab.warning("No data available.")
            return

        with tab:
            # --- KPI Section ---
            total_val = filtered_df["val"].sum()
            latest_year = filtered_df["year"].max()
            latest_df = filtered_df[filtered_df["year"] == latest_year]
            male_val = latest_df[latest_df["gender"] == "Male"]["val"].sum()
            female_val = latest_df[latest_df["gender"] == "Female"]["val"].sum()

            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric(f"Total {measure} ({metric})", f"{int(total_val):,}")
            kpi2.metric("Latest Male Cases", f"{int(male_val):,}")
            kpi3.metric("Latest Female Cases", f"{int(female_val):,}")

            # --- Chart Section ---
            col1, col2, col3 = st.columns([1, 1, 2])

            # Pie Chart
            gender_sum = filtered_df.groupby("gender")["val"].sum()
            fig_pie = px.pie(
                values=gender_sum.values,
                names=gender_sum.index,
                title="Gender Distribution",
                color=gender_sum.index,
                color_discrete_map=gender_colors
            )
            col1.plotly_chart(fig_pie, use_container_width=True)

            # Bar Chart
            age_sum = filtered_df.groupby("age")["val"].sum().reindex(sorted_ages)
            fig_bar = px.bar(
                x=age_sum.index,
                y=age_sum.values,
                labels={"x": "Age Group", "y": "Total"},
                title="By Age Group",
                color_discrete_sequence=[seaborn_palette[2]]
            )
            fig_bar.update_layout(height=300)
            col2.plotly_chart(fig_bar, use_container_width=True)

            # Line Chart
            line_df = filtered_df[filtered_df["age"].isin(sorted_ages)].sort_values("year")
            fig_line = px.line(
                line_df,
                x="year",
                y="val",
                color="age",
                title=f"{measure} Over Time",
                color_discrete_sequence=seaborn_palette,
                category_orders={"age": sorted_ages},
                markers=False,
                line_shape="linear",
                labels={"val": f"{measure} ({metric})", "year": "Year", "age": "Age Group"},
                hover_data={"year": False, "val": ':.0f', "age": True}
            )
            fig_line.update_layout(
                height=350,
                plot_bgcolor='white',
                hovermode="x unified",
                margin=dict(t=40, b=10, l=0, r=0)
            )
            col3.plotly_chart(fig_line, use_container_width=True)

    render_dashboard("Incidence", "Number", tab1)
    render_dashboard("Deaths", "Number", tab2)
    render_dashboard("Incidence", "Rate", tab3)
    render_dashboard("Deaths", "Rate", tab4)

else:
    st.warning("🔒 This cancer analytics dashboard is password-protected. Enter the correct password in the sidebar to access.")
