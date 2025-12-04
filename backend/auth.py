import bcrypt
import jwt
import datetime
from backend.database import db
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here-change-in-production')

class UserAuth:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storing"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(stored_hash: str, provided_password: str) -> bool:
        """Verify a stored password against one provided by user"""
        return bcrypt.checkpw(
            provided_password.encode('utf-8'),
            stored_hash.encode('utf-8')
        )
    
    @staticmethod
    def register_user(username: str, email: str, password: str, full_name: str = None, phone: str = None):
        """Register a new user"""
        try:
            conn = db.get_connection()
            with conn.cursor() as cursor:
                # Check if username or email already exists
                cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
                if cursor.fetchone():
                    return False, "Username or email already exists"
                
                # Hash password
                password_hash = UserAuth.hash_password(password)
                
                # Insert new user
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, full_name, phone)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, email, password_hash, full_name, phone))
                
                conn.commit()
                return True, "Registration successful"
                
        except Exception as e:
            return False, f"Registration error: {str(e)}"
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def login_user(username: str, password: str):
        """Authenticate user and return user data"""
        try:
            conn = db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, email, password_hash, full_name, is_admin 
                    FROM users 
                    WHERE username = %s AND is_active = TRUE
                """, (username,))
                
                user = cursor.fetchone()
                
                if not user:
                    return False, "User not found or inactive", None
                
                # Verify password
                if not UserAuth.verify_password(user['password_hash'], password):
                    return False, "Invalid password", None
                
                # Update last login
                cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user['id'],))
                conn.commit()
                
                # Remove password hash from returned data
                del user['password_hash']
                return True, "Login successful", user
                
        except Exception as e:
            return False, f"Login error: {str(e)}", None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def create_token(user_id: int, username: str, is_admin: bool = False):
        """Create JWT token for user"""
        payload = {
            'user_id': user_id,
            'username': username,
            'is_admin': is_admin,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verify_token(token: str):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, "Token expired"
        except jwt.InvalidTokenError:
            return False, "Invalid token"
    
    @staticmethod
    def get_current_user():
        """Get current user from session state"""
        if 'user' in st.session_state:
            return st.session_state.user
        return None
    
    @staticmethod
    def is_authenticated():
        """Check if user is authenticated"""
        return 'user' in st.session_state and st.session_state.user is not None
    
    @staticmethod
    def is_admin():
        """Check if current user is admin"""
        user = UserAuth.get_current_user()
        return user and user.get('is_admin', False)
    
    @staticmethod
    def logout():
        """Logout current user"""
        if 'user' in st.session_state:
            del st.session_state.user
        st.success("Logged out successfully")
        st.rerun()