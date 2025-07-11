from db_config import create_connection

conn = create_connection()
cursor = conn.cursor()

# Insert student
try:
    cursor.execute("""
        INSERT INTO students (name, email)
        VALUES (%s, %s)
    """, ("John Doe", "john@example.com"))
    conn.commit()
    print("✅ Student inserted successfully.")
except Exception as e:
    print("❌ Failed to insert student:", e)
finally:
    cursor.close()
    conn.close()
