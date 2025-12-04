import streamlit as st
from backend.auth import UserAuth
import re

st.set_page_config(
    page_title="STOCKREADER AI - Register",
    page_icon="📝",
    layout="centered"
)

# Redirect if already logged in
if UserAuth.is_authenticated():
    st.success("You are already logged in!")
    st.page_link("app.py", label="Go to Dashboard")
    st.stop()

st.markdown("""
<style>
    .register-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .register-header {
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
    
    .register-button {
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
    
    .register-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .login-link {
        text-align: center;
        margin-top: 1.5rem;
        color: #666;
    }
    
    .password-requirements {
        font-size: 0.85rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="register-header">
    <h1 style="color: #667eea;">📝 Create Account</h1>
    <p>Join STOCKREADER AI today</p>
</div>
""", unsafe_allow_html=True)

with st.form("register_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        username = st.text_input("Username", placeholder="Choose a username")
    
    with col2:
        email = st.text_input("Email", placeholder="your.email@example.com")
    
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name", placeholder="Your full name")
    
    with col2:
        phone = st.text_input("Phone (Optional)", placeholder="+62 812-3456-7890")
    
    password = st.text_input("Password", type="password", placeholder="Create a strong password")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
    
    st.markdown("""
    <div class="password-requirements">
        <strong>Password must contain:</strong>
        <ul style="margin: 0.5rem 0 0 1.5rem; padding: 0;">
            <li>At least 8 characters</li>
            <li>One uppercase letter</li>
            <li>One lowercase letter</li>
            <li>One number</li>
            <li>One special character</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
    
    if submitted:
        # Validation
        errors = []
        
        if not username:
            errors.append("Username is required")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters")
        
        if not email:
            errors.append("Email is required")
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            errors.append("Invalid email format")
        
        if not password:
            errors.append("Password is required")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters")
        elif not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        elif not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        elif not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        if not agree_terms:
            errors.append("You must agree to the terms and conditions")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            success, message = UserAuth.register_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name,
                phone=phone if phone else None
            )
            
            if success:
                st.success(message)
                st.info("You can now login with your credentials")
                st.page_link("pages/2_Login.py", label="Go to Login")
            else:
                st.error(message)

st.markdown("""
<div class="login-link">
    <p>Already have an account? <a href="/2_Login" style="color: #667eea; text-decoration: none; font-weight: 500;">Login here</a></p>
</div>
""", unsafe_allow_html=True)