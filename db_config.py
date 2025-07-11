# db_config.py

import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",         # ✅ Localhost for XAMPP
            user="root",              # ✅ Default XAMPP MySQL user
            password="",              # ❗ Usually empty in XAMPP
            database="grade_db"       # ✅ Use your local database name
        )
        if connection.is_connected():
            print("✅ Connected to local MySQL database")
            return connection
    except Error as e:
        print(f"❌ Error connecting to database: {e}")
        return None
