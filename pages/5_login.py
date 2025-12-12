import streamlit as st
from backend.auth import UserAuth
from components.ui_components import load_design_system

# ========== PAGE SETUP ==========
st.set_page_config(
    page_title="StockReader AI - Login",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load Design System
load_design_system()

# ========== AUTH CHECK ==========
if 'user' not in st.session_state:
    st.session_state.user = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if UserAuth.is_authenticated():
    st.success("Anda sudah login!")
    st.page_link("app.py", label="Ke Dashboard")
    st.stop()

# ========== PAGE CONTENT ==========
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1>Selamat Datang Kembali</h1>
    <p class="text-muted">Masuk ke akun StockReader AI Anda</p>
</div>
""", unsafe_allow_html=True)

# Login Form Card
st.markdown('<div class="card" style="max-width: 420px; margin: 0 auto; padding: 2rem;">', unsafe_allow_html=True)

with st.form("login_form"):
    st.markdown("#### 🔐 Login")
    
    username = st.text_input("Username", placeholder="Masukkan username Anda")
    password = st.text_input("Password", type="password", placeholder="Masukkan password Anda")
    
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    
    submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
    
    if submitted:
        if not username or not password:
            st.error("Harap isi semua field")
        else:
            success, message, user_data = UserAuth.login_user(username, password)
            if success:
                st.session_state.user = user_data
                st.session_state.authenticated = True
                st.success(message)
                import time
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(message)

st.markdown('</div>', unsafe_allow_html=True)

# Register Link
st.markdown("""
<div style="text-align: center; margin-top: 2rem;">
    <p class="text-muted">Belum punya akun? 
        <a href="/register" style="color: var(--color-accent-blue); text-decoration: none; font-weight: 600;">Daftar di sini</a>
    </p>
</div>
""", unsafe_allow_html=True)