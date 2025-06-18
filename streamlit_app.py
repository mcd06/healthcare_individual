import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration
CORRECT_PASSWORD = "cancer25"
st.set_page_config(layout="wide", page_title="Cancer Burden in Lebanon", page_icon="🧬")

# Color Palette
seaborn_palette = ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854']
gender_colors = {"Male": seaborn_palette[0], "Female": seaborn_palette[1]}
sorted_ages = ["15-19 years", "20-54 years", "55-59 years", "60-64 years", "65-74 years"]

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "password_attempt" not in st.session_state:
    st.session_state.password_attempt = ""

# Sidebar Login
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
            st.rerun()

# Main Content
if st.session_state.authenticated:
    df = pd.read_csv("cancer_lebanon.csv")
    df = df[df["age"] != "All ages"]
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # Sidebar year slider
    min_year = int(df["year"].min())
    max_year = int(df["year"].max())
    selected_years = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))

    st.markdown("## 🧬 Cancer Burden in Lebanon: Multi-Dimensional Dashboard")
    st.markdown("Explore Lebanon's cancer burden across gender, age, time, and metrics with interactive 2D insights.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Number by Incidence", "Number by Death", "Rate by Incidence", "Rate by Death"
    ])

    def render_dashboard(measure, metric, tab):
        label_y = f"{measure} ({metric})"
        filtered_df = df[
            (df["measure"] == measure) &
            (df["metric"] == metric) &
            (df["year"].between(selected_years[0], selected_years[1]))
        ]
        if filtered_df.empty:
            tab.warning("No data available.")
            return

        with tab:
            # KPI Metrics
            total_val = filtered_df["val"].sum()
            latest_df = filtered_df[filtered_df["year"] == filtered_df["year"].max()]
            male_val = latest_df[latest_df["gender"] == "Male"]["val"].sum()
            female_val = latest_df[latest_df["gender"] == "Female"]["val"].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric(f"Total {label_y}", f"{int(total_val):,}")
            col2.metric("Latest Male Cases", f"{int(male_val):,}")
            col3.metric("Latest Female Cases", f"{int(female_val):,}")

            # Row 1: Heatmap | Box Plot | Line Chart
            r1c1, r1c2, r1c3 = st.columns(3)

            heat_df = filtered_df.pivot_table(index="age", columns="year", values="val", aggfunc="sum").reindex(index=sorted_ages)
            fig_heat = px.imshow(
                heat_df,
                labels={"x": "Year", "y": "Age Group", "color": label_y},
                color_continuous_scale="YlOrRd"
            )
            fig_heat.update_layout(title="Cancer Burden by Age and Year", title_font=dict(size=18), title_x=0.0, height=260, margin=dict(t=50, b=10))
            r1c1.plotly_chart(fig_heat, use_container_width=True)

            fig_box = px.box(
                filtered_df,
                x="age", y="val",
                category_orders={"age": sorted_ages},
                color="age",
                color_discrete_sequence=seaborn_palette,
                title="Distribution of Values by Age Group",
                labels={"age": "Age Group", "val": label_y}
            )
            fig_box.update_layout(height=260, title_x=0.0, showlegend=False)
            r1c2.plotly_chart(fig_box, use_container_width=True)

            trend_df = (
                filtered_df[filtered_df["age"].isin(sorted_ages)]
                .groupby(["year", "age"], as_index=False)["val"]
                .sum()
                .reset_index(drop=True)
            )
            fig_line = px.line(
                trend_df,
                x="year", y="val", color="age",
                line_shape="linear",
                color_discrete_sequence=seaborn_palette,
                title=f"Time Trend of {measure} by Age Group",
                labels={"year": "Year", "val": label_y, "age": "Age Group"},
                hover_data={"year": True, "age": True, "val": ':.0f'}
            )
            fig_line.update_layout(
                height=260,
                title_font_size=18,
                title_x=0.0,
                plot_bgcolor='white',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                hovermode="closest"
            )
            r1c3.plotly_chart(fig_line, use_container_width=True)

            st.markdown("---")

            # Row 2: Pie | Scatter | Stacked Bar
            r2c1, r2c2, r2c3 = st.columns(3)

            gender_sum = filtered_df.groupby("gender")["val"].sum()
            fig_pie = px.pie(
                values=gender_sum.values,
                names=gender_sum.index,
                title="Total Distribution by Gender",
                color=gender_sum.index,
                color_discrete_map=gender_colors
            )
            fig_pie.update_traces(textinfo="percent+label", textposition="outside", pull=[0.03, 0.03])
            fig_pie.update_layout(height=260, title_font_size=16, title_x=0.0)
            r2c1.plotly_chart(fig_pie, use_container_width=True)

            scatter_df = filtered_df.groupby(["year", "gender"], as_index=False)["val"].sum()
            fig_scatter = px.scatter(
                scatter_df,
                x="year", y="val",
                color="gender",
                color_discrete_map=gender_colors,
                title=f"Gender-wise Total {measure} per Year",
                labels={"year": "Year", "val": label_y, "gender": "Gender"}
            )
            fig_scatter.update_traces(mode="markers", marker=dict(size=4, opacity=0.85, line=dict(width=0.4, color="gray")))
            fig_scatter.update_layout(height=260, title_font_size=16, title_x=0.0, plot_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), hovermode="closest")
            r2c2.plotly_chart(fig_scatter, use_container_width=True)

            bar_df = filtered_df.groupby(["age", "gender"])["val"].sum().reset_index()
            fig_stack = px.bar(
                bar_df,
                x="age", y="val", color="gender",
                barmode="stack",
                color_discrete_map=gender_colors,
                category_orders={"age": sorted_ages},
                title="20-Year Distribution by Age and Gender",
                labels={"age": "Age Group", "val": label_y}
            )
            fig_stack.update_layout(height=260, title_x=0.0)
            r2c3.plotly_chart(fig_stack, use_container_width=True)

    # Render All Tabs
    render_dashboard("Incidence", "Number", tab1)
    render_dashboard("Deaths", "Number", tab2)
    render_dashboard("Incidence", "Rate", tab3)
    render_dashboard("Deaths", "Rate", tab4)

else:
    st.warning("🔒 This cancer analytics dashboard is password-protected. Enter the correct password in the sidebar to access.")

else:
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.warning("🔒 This cancer analytics dashboard is password-protected. Enter the correct password in the sidebar to access.")
    with col_right:
        st.image("A_flat-style_digital_illustration_informs_about_ca.png", use_column_width=True)
