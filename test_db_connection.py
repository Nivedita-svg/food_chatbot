# test_db_connection.py
import mysql.connector

try:
    cnx = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="pandeyji_eatery"
    )
    if cnx.is_connected():
        print("Database connection successful!")
    cnx.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")
