import mysql.connector
from mysql.connector import Error

# Establishing the connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="pandeyji_eatery"
        )
        if connection.is_connected():
            print("Database connection successful!")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

cnx = create_connection()

# Function to call the MySQL stored procedure and insert an order item
def insert_order_item(food_item, quantity, order_id):
    try:
        cursor = cnx.cursor()
        cursor.callproc('insert_order_item', (food_item, quantity, order_id))
        cnx.commit()
        print("Order item inserted successfully!")
        return 1
    except Error as err:
        print(f"Error inserting order item: {err}")
        cnx.rollback()
        return -1
    finally:
        cursor.close()

# Function to insert a record into the order_tracking table
def insert_order_tracking(order_id, status):
    try:
        cursor = cnx.cursor()
        insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
        cursor.execute(insert_query, (order_id, status))
        cnx.commit()
    except Error as err:
        print(f"Error inserting order tracking: {err}")
        cnx.rollback()
    finally:
        cursor.close()

# Function to get the total order price
def get_total_order_price(order_id):
    try:
        cursor = cnx.cursor()
        query = "SELECT get_total_order_price(%s)"
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()[0]
        return result
    except Error as err:
        print(f"Error fetching total order price: {err}")
        return None
    finally:
        cursor.close()

# Function to get the next available order_id
def get_next_order_id():
    try:
        cursor = cnx.cursor()
        query = "SELECT MAX(order_id) FROM orders"
        cursor.execute(query)
        result = cursor.fetchone()[0]
        return 1 if result is None else result + 1
    except Error as err:
        print(f"Error fetching next order ID: {err}")
        return None
    finally:
        cursor.close()

# Function to fetch the order status
def get_order_status(order_id):
    try:
        cursor = cnx.cursor()
        query = "SELECT status FROM order_tracking WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as err:
        print(f"Error fetching order status: {err}")
        return None
    finally:
        cursor.close()

if __name__ == "__main__":
    # Example usage
    print(get_next_order_id())
