import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration ---
CORRECT_PASSWORD = "cancer25"
st.set_page_config(layout="wide", page_title="Cancer Dashboard", page_icon="🧬")

# --- Color Palette ---
palette = ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854']

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
        pwd = st.text_input("Password", type="password", key="password_attempt")
        if pwd == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()

# --- Main App ---
if st.session_state.authenticated:
    df = pd.read_csv("cancer_lebanon.csv")
    df = df[df["age"] != "All ages"]

    ages = ["15-19 years", "20-54 years", "55-59 years", "60-64 years", "65-74 years"]
    gender_colors = {"Male": palette[0], "Female": palette[1]}

    st.markdown("## 🧬 Cancer Burden in Lebanon Dashboard")
    st.markdown("Explore cancer incidence & mortality by number and rate, gender and age (2000–2020).")
    tabs = st.tabs(["Number / Incidence", "Number / Death", "Rate / Incidence", "Rate / Death"])

    def render(measure, metric, tab):
        d = df[(df["measure"] == measure) & (df["metric"] == metric)]
        if d.empty:
            tab.warning("No data.")
            return

        with tab:
            year_max = d["year"].max()
            total = int(d["val"].sum())

            # fixed boolean filtering
            male_val = int(d[(d["gender"] == "Male") & (d["year"] == year_max)]["val"].sum())
            female_val = int(d[(d["gender"] == "Female") & (d["year"] == year_max)]["val"].sum())

            c1, c2, c3 = st.columns(3)
            c1.metric(f"Total {measure} ({metric})", f"{total:,}")
            c2.metric("Latest Male", f"{male_val:,}")
            c3.metric("Latest Female", f"{female_val:,}")

            # Row 1
            r1, r2, r3 = st.columns(3)

            # Heatmap
            hm = d.pivot(index="age", columns="year", values="val").reindex(index=ages)
            fig_h = px.imshow(
                hm,
                labels={"x":"Year", "y":"Age", "color":"Value"},
                color_continuous_scale="YlOrRd"
            )
            fig_h.update_layout(
                height=260,
                margin=dict(t=40, b=10),
                title=dict(text="Heatmap: Cancer Burden by Age & Year", x=0.5)
            )
            r1.plotly_chart(fig_h, use_container_width=True)

            # Stacked bar
            sb = d.groupby(["age","gender"])["val"].sum().reset_index()
            fig_s = px.bar(
                sb, x="age", y="val", color="gender",
                barmode="stack",
                category_orders={"age": ages},
                color_discrete_map=gender_colors
            )
            fig_s.update_layout(
                height=260,
                title=dict(text="20-Year Distribution by Age & Gender", x=0.5)
            )
            r2.plotly_chart(fig_s, use_container_width=True)

            # Line chart
            ld = d[d["age"].isin(ages)].sort_values("year")
            fig_l = px.line(
                ld, x="year", y="val", color="age",
                line_shape="linear", markers=False,
                category_orders={"age": ages},
                color_discrete_sequence=palette,
                labels={"val":f"{measure} ({metric})", "year":"Year", "age":"Age"}
            )
            fig_l.update_layout(
                height=260,
                plot_bgcolor="white",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                margin=dict(t=30, b=10),
                title=dict(text=f"{measure} Over Time by Age Group", x=0.5)
            )
            r3.plotly_chart(fig_l, use_container_width=True)

            st.markdown("---")

            # Row 2
            p1, p2, p3 = st.columns(3)

            # Pie chart
            gs = d.groupby("gender")["val"].sum()
            fig_p = px.pie(
                values=gs.values, names=gs.index,
                color_discrete_map=gender_colors
            )
            fig_p.update_traces(textinfo="percent+label", pull=[0.03, 0.03])
            fig_p.update_layout(
                height=260,
                title=dict(text="Total Distribution by Gender", x=0.5)
            )
            p1.plotly_chart(fig_p, use_container_width=True)

            # Age bar
            ag = d.groupby("age")["val"].sum().reindex(ages)
            fig_a = px.bar(
                x=ag.index, y=ag.values,
                labels={"x":"Age", "y":"Total"},
                color_discrete_sequence=[palette[1]]
            )
            fig_a.update_layout(
                height=260,
                title=dict(text="Total Burden by Age Group", x=0.5)
            )
            p2.plotly_chart(fig_a, use_container_width=True)

            # Box plot
            fig_b = px.box(
                d, x="age", y="val",
                category_orders={"age": ages},
                color_discrete_sequence=[palette[4]]
            )
            fig_b.update_layout(
                height=260,
                title=dict(text="Value Distribution by Age Group", x=0.5)
            )
            p3.plotly_chart(fig_b, use_container_width=True)

    render("Incidence", "Number", tabs[0])
    render("Deaths",    "Number", tabs[1])
    render("Incidence", "Rate",   tabs[2])
    render("Deaths",    "Rate",   tabs[3])

else:
    st.warning("🔒 This dashboard is password-protected. Please login to continue.")
