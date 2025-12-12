import streamlit as st
from backend.auth import UserAuth
from components.ui_components import load_design_system
import re

# ========== PAGE SETUP ==========
st.set_page_config(
    page_title="StockReader AI - Register",
    page_icon="📝",
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
    <h1>Buat Akun Baru</h1>
    <p class="text-muted">Bergabung dengan StockReader AI untuk analisis cerdas</p>
</div>
""", unsafe_allow_html=True)

# Register Form Card
st.markdown('<div class="card" style="max-width: 520px; margin: 0 auto; padding: 2rem;">', unsafe_allow_html=True)

with st.form("register_form"):
    st.markdown("#### 📝 Registrasi")
    
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username", placeholder="Pilih username")
    with col2:
        email = st.text_input("Email", placeholder="email@contoh.com")
    
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Nama Lengkap", placeholder="Nama lengkap Anda")
    with col2:
        phone = st.text_input("Telepon (Opsional)", placeholder="+62 812-xxxx-xxxx")
    
    password = st.text_input("Password", type="password", placeholder="Buat password kuat")
    confirm_password = st.text_input("Konfirmasi Password", type="password", placeholder="Ulangi password")
    
    # Password Requirements
    st.markdown("""
    <div style="font-size: 0.8rem; padding: 0.75rem; background: rgba(255,255,255,0.03); border-radius: 8px; margin: 1rem 0;">
        <strong style="color: var(--color-text-secondary);">Syarat Password:</strong>
        <ul style="margin: 0.5rem 0 0 1rem; padding: 0; color: var(--color-text-muted);">
            <li>Minimal 8 karakter</li>
            <li>Huruf besar & kecil</li>
            <li>Angka & karakter khusus</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    agree_terms = st.checkbox("Saya setuju dengan Syarat & Ketentuan")
    
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    
    submitted = st.form_submit_button("Buat Akun", type="primary", use_container_width=True)
    
    if submitted:
        errors = []
        
        if not username:
            errors.append("Username wajib diisi")
        elif len(username) < 3:
            errors.append("Username minimal 3 karakter")
        
        if not email:
            errors.append("Email wajib diisi")
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            errors.append("Format email tidak valid")
        
        if not password:
            errors.append("Password wajib diisi")
        elif len(password) < 8:
            errors.append("Password minimal 8 karakter")
        elif not re.search(r'[A-Z]', password):
            errors.append("Password harus ada huruf besar")
        elif not re.search(r'[a-z]', password):
            errors.append("Password harus ada huruf kecil")
        elif not re.search(r'\d', password):
            errors.append("Password harus ada angka")
        elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password harus ada karakter khusus")
        
        if password != confirm_password:
            errors.append("Password tidak cocok")
        
        if not agree_terms:
            errors.append("Anda harus menyetujui syarat & ketentuan")
        
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
                st.info("Silakan login dengan akun baru Anda")
                st.page_link("pages/login.py", label="Ke Halaman Login")
            else:
                st.error(message)

st.markdown('</div>', unsafe_allow_html=True)

# Login Link
st.markdown("""
<div style="text-align: center; margin-top: 2rem;">
    <p class="text-muted">Sudah punya akun? 
        <a href="/login" style="color: var(--color-accent-blue); text-decoration: none; font-weight: 600;">Login di sini</a>
    </p>
</div>
""", unsafe_allow_html=True)