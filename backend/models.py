from datetime import datetime
from backend.database import db

class User:
    def __init__(self, id, username, email, full_name=None, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.is_admin = is_admin
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        try:
            conn = db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, email, full_name, phone, is_admin, created_at, last_login
                    FROM users 
                    WHERE id = %s AND is_active = TRUE
                """, (user_id,))
                return cursor.fetchone()
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def update_profile(user_id, full_name=None, phone=None):
        """Update user profile"""
        try:
            conn = db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET full_name = %s, phone = %s, updated_at = NOW()
                    WHERE id = %s
                """, (full_name, phone, user_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False
        finally:
            if conn:
                conn.close()

class UserPortfolio:
    @staticmethod
    def add_stock(user_id, symbol, company_name=None, entry_price=None, quantity=None, notes=None):
        """Add stock to user's portfolio"""
        try:
            conn = db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_portfolios (user_id, symbol, company_name, entry_price, quantity, notes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    entry_price = VALUES(entry_price),
                    quantity = VALUES(quantity),
                    notes = VALUES(notes)
                """, (user_id, symbol, company_name, entry_price, quantity, notes))
                conn.commit()
                return True, "Stock added to portfolio"
        except Exception as e:
            return False, f"Error adding stock: {str(e)}"
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_portfolio(user_id):
        """Get user's portfolio"""
        try:
            conn = db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, symbol, company_name, entry_price, quantity, notes, added_date
                    FROM user_portfolios 
                    WHERE user_id = %s
                    ORDER BY added_date DESC
                """, (user_id,))
                return cursor.fetchall()
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def remove_stock(user_id, symbol):
        """Remove stock from user's portfolio"""
        try:
            conn = db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM user_portfolios WHERE user_id = %s AND symbol = %s", (user_id, symbol))
                conn.commit()
                return True, "Stock removed from portfolio"
        except Exception as e:
            return False, f"Error removing stock: {str(e)}"
        finally:
            if conn:
                conn.close()

class SavedAnalysis:
    @staticmethod
    def save_analysis(user_id, symbol, analysis_data, recommendation=None, notes=None):
        """Save stock analysis for user"""
        try:
            conn = db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO saved_analyses (user_id, symbol, analysis_data, recommendation, notes)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, symbol, analysis_data, recommendation, notes))
                conn.commit()
                return True, "Analysis saved successfully"
        except Exception as e:
            return False, f"Error saving analysis: {str(e)}"
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_user_analyses(user_id, limit=10):
        """Get user's saved analyses"""
        try:
            conn = db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, symbol, analysis_date, recommendation, notes
                    FROM saved_analyses 
                    WHERE user_id = %s
                    ORDER BY analysis_date DESC
                    LIMIT %s
                """, (user_id, limit))
                return cursor.fetchall()
        finally:
            if conn:
                conn.close()