import mysql.connector
from werkzeug.security import generate_password_hash

# 👉 1. Enter teacher info
name = "Teacher One"
email = "teacher1@example.com"
password = "mypassword123"  # your real password

# 👉 2. Hash the password
hashed_password = generate_password_hash(password)
print(f"Generated Hash:\n{hashed_password}\n")

# 👉 3. Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="your_mysql_user",         # change this
    password="your_mysql_password"  # change this
)

cursor = conn.cursor()
cursor.execute("USE grade_db")

# 👉 4. Insert into `users` table
cursor.execute("""
    INSERT INTO users (name, email, password, role)
    VALUES (%s, %s, %s, %s)
""", (name, email, hashed_password, 'teacher'))

conn.commit()
cursor.close()
conn.close()

print("✅ Teacher account created successfully!")
