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
            # --- KPI Metrics ---
            total_val = filtered_df["val"].sum()
            latest_year = filtered_df["year"].max()
            latest_df = filtered_df[filtered_df["year"] == latest_year]
            male_val = latest_df[latest_df["gender"] == "Male"]["val"].sum()
            female_val = latest_df[latest_df["gender"] == "Female"]["val"].sum()

            k1, k2, k3 = st.columns(3)
            k1.metric(f"Total {measure} ({metric})", f"{int(total_val):,}")
            k2.metric("Latest Male Cases", f"{int(male_val):,}")
            k3.metric("Latest Female Cases", f"{int(female_val):,}")

            # --- Row 1: Heatmap | Stacked Bar | Line Plot ---
            r1c1, r1c2, r1c3 = st.columns(3)

            # Heatmap: Age × Year
            heat_df = filtered_df.pivot_table(index="age", columns="year", values="val", aggfunc="sum").reindex(index=sorted_ages)
            fig_heat = px.imshow(
                heat_df,
                labels=dict(x="Year", y="Age Group", color="Value"),
                color_continuous_scale="YlOrRd"
            )
            fig_heat.update_layout(
                title=dict(text="Heatmap: Age × Year", font=dict(size=18)),
                height=240,
                margin=dict(t=40, b=10)
            )
            r1c1.plotly_chart(fig_heat, use_container_width=True)

            # Stacked Bar (sum of all years)
            bar_df = filtered_df.groupby(["age", "gender"])["val"].sum().reset_index()
            fig_stack = px.bar(
                bar_df,
                x="age", y="val", color="gender",
                title="20-Year Distribution by Age and Gender",
                category_orders={"age": sorted_ages},
                barmode="stack",
                color_discrete_map=gender_colors
            )
            fig_stack.update_layout(height=240)
            r1c2.plotly_chart(fig_stack, use_container_width=True)

            # Line Chart (hovermode = closest)
            line_df = filtered_df[filtered_df["age"].isin(sorted_ages)].sort_values("year")
            fig_line = px.line(
                line_df,
                x='year',
                y='val',
                color='age',
                markers=False,
                line_shape="linear",
                category_orders={"age": sorted_ages},
                title=f"{measure} Over Time by Age Group",
                labels={"val": f"{measure} ({metric})", "year": "Year", "age": "Age Group"},
                hover_data={"year": False, "age": True, "val": ':.0f'},
                color_discrete_sequence=seaborn_palette
            )
            fig_line.update_layout(
                title_font_size=16,
                plot_bgcolor='white',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                hovermode="closest",
                height=240,
                margin=dict(t=30, b=10)
            )
            r1c3.plotly_chart(fig_line, use_container_width=True)

            st.markdown("---")

            # --- Row 2: Pie | Age Bar | Boxplot ---
            r2c1, r2c2, r2c3 = st.columns(3)

            # Pie Chart: Gender Share (total) — enlarged
            gender_sum = filtered_df.groupby("gender")["val"].sum()
            fig_pie = px.pie(
                values=gender_sum.values,
                names=gender_sum.index,
                title="Total Distribution by Gender",
                color=gender_sum.index,
                color_discrete_map=gender_colors
            )
            fig_pie.update_traces(textinfo="percent+label", pull=[0.03, 0.03])
            fig_pie.update_layout(height=260, title_font_size=16)
            r2c1.plotly_chart(fig_pie, use_container_width=True)

            # Age Bar: Total by Age Group
            age_sum = filtered_df.groupby("age")["val"].sum().reindex(sorted_ages)
            fig_age = px.bar(
                x=age_sum.index,
                y=age_sum.values,
                labels={"x": "Age Group", "y": "Total"},
                title="Total Burden by Age Group",
                color_discrete_sequence=[seaborn_palette[1]]  # orange
            )
            fig_age.update_layout(height=240)
            r2c2.plotly_chart(fig_age, use_container_width=True)

            # Box Plot: Distribution by Age
            fig_box = px.box(
                filtered_df,
                x="age", y="val",
                category_orders={"age": sorted_ages},
                title="Distribution of Values by Age Group",
                color_discrete_sequence=[seaborn_palette[4]]  # light green
            )
            fig_box.update_layout(height=240)
            r2c3.plotly_chart(fig_box, use_container_width=True)

    render_dashboard("Incidence", "Number", tab1)
    render_dashboard("Deaths", "Number", tab2)
    render_dashboard("Incidence", "Rate", tab3)
    render_dashboard("Deaths", "Rate", tab4)

else:
    st.warning("🔒 This cancer analytics dashboard is password-protected. Enter the correct password in the sidebar to access.")
