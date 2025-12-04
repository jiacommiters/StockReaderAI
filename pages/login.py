import streamlit as st
from backend.auth import UserAuth

st.set_page_config(
    page_title="STOCKREADER AI - Login",
    page_icon="🔐",
    layout="centered"
)

# Redirect if already logged in
if UserAuth.is_authenticated():
    st.success("You are already logged in!")
    st.page_link("app.py", label="Go to Dashboard")
    st.stop()

st.markdown("""
<style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #333;
    }
    
    .form-input {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 1rem;
    }
    
    .login-button {
        width: 100%;
        padding: 0.75rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: 0.3s;
    }
    
    .login-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .register-link {
        text-align: center;
        margin-top: 1.5rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="login-header">
    <h1 style="color: #667eea;">🔐 Login</h1>
    <p>Welcome back to STOCKREADER AI</p>
</div>
""", unsafe_allow_html=True)

with st.form("login_form"):
    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.markdown('<label class="form-label">Username</label>', unsafe_allow_html=True)
    username = st.text_input("", placeholder="Enter your username", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.markdown('<label class="form-label">Password</label>', unsafe_allow_html=True)
    password = st.text_input("", type="password", placeholder="Enter your password", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
    
    if submitted:
        if not username or not password:
            st.error("Please fill in all fields")
        else:
            success, message, user_data = UserAuth.login_user(username, password)
            if success:
                st.session_state.user = user_data
                st.success(message)
                st.rerun()
            else:
                st.error(message)

st.markdown("""
<div class="register-link">
    <p>Don't have an account? <a href="/3_Register" style="color: #667eea; text-decoration: none; font-weight: 500;">Register here</a></p>
</div>
""", unsafe_allow_html=True)