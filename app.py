print("🔧 Testing database connection...")
try:
    import pymysql
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='stockmind_ai'
    )
    print("✅ Database connected successfully!")
    conn.close()
except Exception as e:
    print(f"❌ Database error: {e}")