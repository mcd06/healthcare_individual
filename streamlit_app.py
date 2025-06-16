import streamlit as st

# === Configuration ===
CORRECT_PASSWORD = "health25"

# === Session State Initialization ===
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "password_attempt" not in st.session_state:
    st.session_state.password_attempt = ""

# === Sidebar Login Logic (no image here anymore) ===
with st.sidebar:
    st.title("Login")
    if st.session_state.authenticated:
        st.success("Access granted.")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.password_attempt = ""
            st.experimental_rerun()
    else:
        st.text("Please enter the password")
        st.text_input("Password", type="password", key="password_attempt")

        if st.session_state.password_attempt == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.experimental_rerun()
        elif st.session_state.password_attempt != "":
            st.error("Incorrect password")

# === Main App Layout with Right-Aligned Logo ===
if st.session_state.authenticated:
    # Create two columns: left for title, right for logo
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("## 🧬 Lebanon Cancer Burden Dashboard")
        st.markdown("### Explore age, gender, and time trends of cancer mortality and incidence")
    
    with col2:
        st.image("IHME.webp", width=120)

    st.markdown("---")
    st.info("Upload cleaned data and add charts below this line.")

else:
    st.warning("This cancer analytics dashboard is password-protected. Enter the correct password in the sidebar to access.")
