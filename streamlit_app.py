import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration ---
CORRECT_PASSWORD = "cancer25"
st.set_page_config(layout="wide", page_title="Cancer Dashboard", page_icon="🧬")

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
    years = sorted(df["year"].unique())
    gender_colors = {"Male": "#66C2A5", "Female": "#FC8D62"}

    # --- Tabs Setup ---
    st.markdown("## 🧬 Cancer Burden in Lebanon Dashboard")
    st.markdown("Explore cancer incidence and mortality by number and rate, gender, and age groups (2000–2020).")
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Number by Incidence", "📉 Number by Death", "📈 Rate by Incidence", "📉 Rate by Death"])
    
    def render_dashboard(measure, metric, tab):
        filtered_df = df[(df["measure"] == measure) & (df["metric"] == metric)]
        if filtered_df.empty:
            tab.warning("No data available.")
            return

        with tab:
            st.markdown(f"### {measure} – {metric}")
            col1, col2 = st.columns(2)

            # Pie Chart by Gender
            gender_sum = filtered_df.groupby("gender")["val"].sum()
            fig_gender = px.pie(
                values=gender_sum.values,
                names=gender_sum.index,
                title="Distribution by Gender",
                color=gender_sum.index,
                color_discrete_map=gender_colors
            )
            col1.plotly_chart(fig_gender, use_container_width=True)

            # Bar Chart by Age Group
            age_sum = filtered_df.groupby("age")["val"].sum().reindex(sorted_ages)
            fig_age = px.bar(
                x=age_sum.index,
                y=age_sum.values,
                labels={"x": "Age Group", "y": "Total"},
                title="Distribution by Age Group",
                color_discrete_sequence=["#8DA0CB"]
            )
            col2.plotly_chart(fig_age, use_container_width=True)

            # Line Chart Over Time by Age
            fig_line = px.line(
                filtered_df[filtered_df["age"].isin(sorted_ages)],
                x="year", y="val", color="age",
                title=f"{measure} Over Time by Age Group",
                category_orders={"age": sorted_ages},
                markers=True
            )
            st.plotly_chart(fig_line, use_container_width=True)

    render_dashboard("Incidence", "Number", tab1)
    render_dashboard("Deaths", "Number", tab2)
    render_dashboard("Incidence", "Rate", tab3)
    render_dashboard("Deaths", "Rate", tab4)
else:
    st.warning("🔒 This cancer analytics dashboard is password-protected. Enter the correct password in the sidebar to access.")
