import pymysql

try:
    connection = pymysql.connect(
        host='localhost',  # Replace with your MySQL server host
        user='root',   # Replace with your MySQL username
        password='Bhuvi@123',  # Replace with your MySQL password
        database='college_connect'  # Replace with your database name
    )
    print("Connected to MySQL database!")
except pymysql.err.OperationalError as e:
    print(f"Error: {e}")
finally:
    if connection:
        connection.close()