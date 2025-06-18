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
        st.text("Please enter the password")
        st.text_input("Password", type="password", key="password_attempt")
        if st.session_state.password_attempt == CORRECT_PASSWORD:
            st.session_state.authenticated = True

# --- Main Content ---
if st.session_state.authenticated:
    df = pd.read_csv("cancer_lebanon.csv")
    df = df[df["age"] != "All ages"]
    sorted_ages = ["15-19 years", "20-54 years", "55-59 years", "60-64 years", "65-74 years"]
    gender_colors = {"Male": seaborn_palette[0], "Female": seaborn_palette[1]}

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
            prev_year = latest_year - 1
            latest_df = filtered_df[filtered_df["year"] == latest_year]
            prev_df = filtered_df[filtered_df["year"] == prev_year]
            male_val = latest_df[latest_df["gender"] == "Male"]["val"].sum()
            female_val = latest_df[latest_df["gender"] == "Female"]["val"].sum()

            # YoY calculation
            latest_total = latest_df["val"].sum()
            prev_total = prev_df["val"].sum()
            yoy_change = ((latest_total - prev_total) / prev_total * 100) if prev_total > 0 else 0

            k1, k2, k3, k4 = st.columns(4)
            k1.metric(f"Total {measure} ({metric})", f"{int(total_val):,}")
            k2.metric("Latest Male Cases", f"{int(male_val):,}")
            k3.metric("Latest Female Cases", f"{int(female_val):,}")
            k4.metric("YoY Change", f"{yoy_change:.1f}%", delta_color="inverse")

            # --- Insights Box: Top 3 Contributors ---
            top_contrib = latest_df.groupby(["age", "gender"])["val"].sum().sort_values(ascending=False).head(3)
            top_insight = ", ".join([f"{age} {gender} ({int(val):,})" for (age, gender), val in top_contrib.items()])
            st.success(f"Top 3 contributors in {latest_year}: {top_insight}")

            # --- Row 2: Heatmap + Stacked Bar ---
            col1, col2 = st.columns(2)

            # Heatmap (Age × Year)
            heat_df = filtered_df.pivot_table(index="age", columns="year", values="val", aggfunc="sum").reindex(index=sorted_ages)
            fig_heat = px.imshow(
                heat_df,
                labels=dict(x="Year", y="Age Group", color="Value"),
                aspect="auto",
                color_continuous_scale="YlOrRd",
                title="Heatmap: Age × Year"
            )
            fig_heat.update_layout(height=260, margin=dict(t=30, b=10))
            col1.plotly_chart(fig_heat, use_container_width=True)

            # Stacked Bar (Age split by Gender)
            bar_df = latest_df.groupby(["age", "gender"])["val"].sum().reset_index()
            fig_stack = px.bar(
                bar_df,
                x="age", y="val", color="gender",
                title=f"{latest_year} Distribution by Age and Gender",
                category_orders={"age": sorted_ages},
                barmode="stack",
                color_discrete_map=gender_colors
            )
            fig_stack.update_layout(height=260)
            col2.plotly_chart(fig_stack, use_container_width=True)

            # --- Line Chart: Age over Time ---
            line_df = filtered_df[filtered_df["age"].isin(sorted_ages)].sort_values("year")
            fig_line = px.line(
                line_df,
                x="year", y="val", color="age",
                title=f"{measure} Over Time",
                color_discrete_sequence=seaborn_palette,
                category_orders={"age": sorted_ages},
                markers=False, line_shape="linear",
                labels={"val": f"{measure} ({metric})", "year": "Year", "age": "Age Group"},
                hover_data={"year": False, "val": ':.0f', "age": True}
            )
            fig_line.update_layout(
                height=320,
                plot_bgcolor='white',
                hovermode="x unified",
                margin=dict(t=40, b=10)
            )
            st.plotly_chart(fig_line, use_container_width=True)

    render_dashboard("Incidence", "Number", tab1)
    render_dashboard("Deaths", "Number", tab2)
    render_dashboard("Incidence", "Rate", tab3)
    render_dashboard("Deaths", "Rate", tab4)

else:
    st.warning("🔒 This cancer analytics dashboard is password-protected. Enter the correct password in the sidebar to access.")
