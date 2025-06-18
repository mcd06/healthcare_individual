import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration ---
CORRECT_PASSWORD = "cancer25"
st.set_page_config(layout="wide", page_title="Cancer Dashboard", page_icon="🧬")

# --- Color Palette ---
seaborn_palette = ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854']

# --- Session State ---
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
    df["year"] = pd.to_numeric(df["year"], errors="coerce")  # Ensure year is numeric

    sorted_ages = ["15-19 years", "20-54 years", "55-59 years", "60-64 years", "65-74 years"]
    gender_colors = {"Male": seaborn_palette[0], "Female": seaborn_palette[1]}

    st.markdown("## 🧬 Cancer Burden in Lebanon Dashboard")
    st.markdown("Explore cancer incidence and mortality in Lebanon by number and rate, gender, and age groups (2000–2020).")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Number by Incidence", "Number by Death", "Rate by Incidence", "Rate by Death"
    ])

    def render_dashboard(measure, metric, tab):
        filtered_df = df[(df["measure"] == measure) & (df["metric"] == metric)]
        if filtered_df.empty:
            tab.warning("No data available.")
            return

        with tab:
            total_val = filtered_df["val"].sum()
            latest_year = filtered_df["year"].max()
            latest_df = filtered_df[filtered_df["year"] == latest_year]
            male_val = latest_df[latest_df["gender"] == "Male"]["val"].sum()
            female_val = latest_df[latest_df["gender"] == "Female"]["val"].sum()

            k1, k2, k3 = st.columns(3)
            k1.metric(f"Total {measure} ({metric})", f"{int(total_val):,}")
            k2.metric("Latest Male Cases", f"{int(male_val):,}")
            k3.metric("Latest Female Cases", f"{int(female_val):,}")

            # --- Row 1: Heatmap | Stacked Bar | Line Chart ---
            r1c1, r1c2, r1c3 = st.columns(3)

            heat_df = filtered_df.pivot_table(
                index="age", columns="year", values="val", aggfunc="sum"
            ).reindex(index=sorted_ages)

            fig_heat = px.imshow(
                heat_df,
                labels=dict(x="Year", y="Age Group", color="Value"),
                color_continuous_scale="YlOrRd"
            )
            fig_heat.update_layout(
                title="Cancer Burden by Age and Year",
                title_font=dict(size=18),
                title_x=0.0,
                height=260,
                margin=dict(t=50, b=10)
            )
            r1c1.plotly_chart(fig_heat, use_container_width=True)

            bar_df = filtered_df.groupby(["age", "gender"])["val"].sum().reset_index()
            fig_stack = px.bar(
                bar_df,
                x="age", y="val", color="gender",
                title="20-Year Distribution by Age and Gender",
                category_orders={"age": sorted_ages},
                barmode="stack",
                color_discrete_map=gender_colors
            )
            fig_stack.update_layout(height=260, title_x=0.0)
            r1c2.plotly_chart(fig_stack, use_container_width=True)

            line_df = filtered_df[filtered_df["age"].isin(sorted_ages)].sort_values("year")
            fig_line = px.line(
                line_df,
                x="year", y="val", color="age",
                title=f"Time Trend of {measure} by Age Group",
                markers=False,
                line_shape="linear",
                category_orders={"age": sorted_ages},
                labels={
                    "val": f"{measure} ({metric})",
                    "year": "Year",
                    "age": "Age Group"
                },
                hover_data={"year": False, "age": True, "val": ':.0f'},
                color_discrete_sequence=seaborn_palette
            )
            fig_line.update_layout(
                title_font_size=18,
                title_x=0.0,
                showlegend=True,
                plot_bgcolor='white',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                hovermode="x unified",
                height=260,
                margin=dict(t=30, b=10)
            )
            r1c3.plotly_chart(fig_line, use_container_width=True)

            # ━━ Divider
            st.markdown("---")

            # --- Row 2: Pie | Cohort Comparison | Box Plot ---
            r2c1, r2c2, r2c3 = st.columns(3)

            gender_sum = filtered_df.groupby("gender")["val"].sum()
            fig_pie = px.pie(
                values=gender_sum.values,
                names=gender_sum.index,
                title="Total Distribution by Gender",
                color=gender_sum.index,
                color_discrete_map=gender_colors
            )
            fig_pie.update_traces(
                textinfo="percent+label",
                textposition="outside",
                pull=[0.03, 0.03]
            )
            fig_pie.update_layout(height=260, title_font_size=16, title_x=0.0)
            r2c1.plotly_chart(fig_pie, use_container_width=True)

            cohorts = [
                ("Male", "65-74 years"),
                ("Female", "60-64 years"),
                ("Male", "20-54 years")
            ]
            cohort_df = filtered_df[filtered_df[["gender", "age"]].apply(tuple, axis=1).isin(cohorts)]
            cohort_df["Cohort"] = cohort_df["gender"] + " " + cohort_df["age"]

            fig_cohort = px.line(
                cohort_df.sort_values("year"),
                x="year", y="val", color="Cohort",
                title="Cohort Comparison: Trends Over Time",
                labels={
                    "val": f"{measure} ({metric})",
                    "year": "Year",
                    "Cohort": "Cohort Group"
                },
                color_discrete_sequence=seaborn_palette,
                hover_data={"year": False, "Cohort": True, "val": ':.0f'}
            )
            fig_cohort.update_layout(
                title_font_size=18,
                title_x=0.0,
                showlegend=True,
                plot_bgcolor='white',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                hovermode="x unified",
                height=260
            )
            r2c2.plotly_chart(fig_cohort, use_container_width=True)

            fig_box = px.box(
                filtered_df,
                x="age", y="val",
                category_orders={"age": sorted_ages},
                title="Distribution of Values by Age Group",
                color_discrete_sequence=[seaborn_palette[0]]  # darker green
            )
            fig_box.update_layout(height=260, title_x=0.0)
            r2c3.plotly_chart(fig_box, use_container_width=True)

    # Render dashboards for all tabs
    render_dashboard("Incidence", "Number", tab1)
    render_dashboard("Deaths", "Number", tab2)
    render_dashboard("Incidence", "Rate", tab3)
    render_dashboard("Deaths", "Rate", tab4)

else:
    st.warning("🔒 This cancer analytics dashboard is password-protected. Enter the correct password in the sidebar to access.")
