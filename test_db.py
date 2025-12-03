import pymysql

print("🔧 Testing Connection to Empty Database...")

try:
    g
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='stockreader_ai'
    )
    
    print("✅ SUCCESS! Database connected!")
    print("📊 Database: stockreader_ai")
    print("👤 User: root")
    print("🔗 Host: localhost")
    
    # Simple check - no tuple/dict issues
    cursor = connection.cursor()
    cursor.execute("SELECT 'CONNECTION_OK' as status")
    status = cursor.fetchone()[0]
    print(f"✅ Status: {status}")
    
    cursor.close()
    connection.close()
    
    print("\n🎉 Database ready for application!")
    print("📝 Tables will be created automatically by the app.")
    
except pymysql.err.OperationalError as e:
    if "Unknown database" in str(e):
        print("❌ ERROR: Database 'stockreader_ai' not found!")
        print("\n🔧 SOLUSI: Buat database dengan:")
        print("1. Buka Laragon Terminal")
        print("2. Ketik: mysql -u root -p")
        print("3. Tekan Enter untuk password (kosong)")
        print("4. Ketik: CREATE DATABASE stockreader_ai;")
        print("5. Ketik: EXIT;")
    else:
        print(f"❌ Connection error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")