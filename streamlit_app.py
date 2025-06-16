import streamlit as st

# === Configuration ===
CORRECT_PASSWORD = "health2025"

# === Session State Initialization ===
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "password_attempt" not in st.session_state:
    st.session_state.password_attempt = ""

# === Sidebar Login Logic ===
with st.sidebar:
    st.title("🔒 Login")
    if st.session_state.authenticated:
        st.success("Access granted.")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.password_attempt = ""
            st.experimental_rerun()
    else:
        st.text("Please enter the password")
        password_input = st.text_input("Password", type="password", key="password_attempt")

        if st.session_state.password_attempt == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.experimental_rerun()
        elif st.session_state.password_attempt != "":
            st.error("Incorrect password")

# === Main Dashboard Content ===
if st.session_state.authenticated:
    st.image("https://cdn-icons-png.flaticon.com/512/2897/2897823.png", width=100)
    st.markdown("## 🧬 Lebanon Cancer Burden Dashboard")
    st.markdown("### Explore age, gender, and time trends of cancer mortality and incidence")
    st.markdown("---")

    # Placeholder for your visualizations
    st.info("Upload cleaned data and add charts below this line.")
    # e.g., st.line_chart(df)

else:
    st.warning("🔒 This cancer analytics dashboard is password-protected. Enter the correct password in the sidebar to access.")
