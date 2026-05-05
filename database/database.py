import mysql.connector
from mysql.connector import Error

def connect_to_database():
    """
    Establishes a connection to the Hospital Management System database in MySQL.
    
    Returns:
        connection (mysql.connector.connection_cext.CMySQLConnection): 
            The connection object if successful, None otherwise.
    """
    try:
        # Initializing the connection using credentials from the security setup
        connection = mysql.connector.connect(
            host='localhost',
            database='HospitalManagement',
            user='admin_hospital',
            password='AdminPass123'
        )

        if connection.is_connected():
            db_info = connection.server_info
            print(f"Successfully connected to MySQL Server version {db_info}")
            return connection

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def close_connection(connection):
    """
    Closes the active database connection.
    
    Args:
        connection: The connection object to be closed.
    """
    if connection and connection.is_connected():
        connection.close()
        print("MySQL connection is now closed.")

if __name__ == "__main__":
    # Unit Test: Check if the connection works when running this file directly
    print("Testing Database Connection...")
    conn = connect_to_database()
    if conn:
        close_connection(conn)