# test_connection.py
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    print("✅ Database connected successfully!")
    print(f"Database: {os.getenv('DB_NAME')}")
    
    # Cek tables
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"Tables found: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Database error: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Pastikan Laragon MySQL running")
    print("2. Database 'stockreader_db' sudah dibuat")
    print("3. Username: root, Password: (kosong)")