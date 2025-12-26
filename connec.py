import pymysql
import os

try:
    connection = pymysql.connect(
        host='mysql-2e3285f6-bhuvibarla-9349.i.aivencloud.com',
        port=17494,
        user='avnadmin',
        password='AVNS__MrHlHumj797xzKdlpK',
        database='defaultdb',
        ssl_verify_identity=True  # Important for Aiven
    )
    print("Successfully connected to Aiven Cloud Database!")
except pymysql.err.OperationalError as e:
    print(f"Connection Failed: {e}")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()