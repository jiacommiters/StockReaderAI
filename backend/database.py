import pymysql
from pymysql import Error
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'stockreader_ai')
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def get_connection(self):
        """Get or create database connection"""
        if self.connection is None or not self.connection.open:
            return self.connect()
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.open:
            self.connection.close()

# Singleton instance
db = DatabaseConnection()

def create_tables():
    """Create necessary tables if they don't exist"""
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            # Check if users table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    phone VARCHAR(20),
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_portfolios (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    symbol VARCHAR(10) NOT NULL,
                    company_name VARCHAR(100),
                    entry_price DECIMAL(10,2),
                    quantity INT,
                    notes TEXT,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_user_stock (user_id, symbol)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_analyses (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    symbol VARCHAR(10) NOT NULL,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    analysis_data JSON,
                    recommendation ENUM('BUY', 'HOLD', 'SELL'),
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            print("✅ Database tables created/verified successfully")
            
    except Error as e:
        print(f"❌ Error creating tables: {e}")
    finally:
        if conn:
            conn.close()

# Initialize database on import
create_tables()