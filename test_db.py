# test_db.py

from db_config import create_connection

# Try to connect
conn = create_connection()

# If connected, print success
if conn:
    print("✅ MySQL connection test passed!")

    # Optional: run a query to test database access
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    print("📄 Tables in grade_db:")
    for table in tables:
        print(" -", table[0])

    conn.close()
else:
    print("❌ MySQL connection test failed.")
