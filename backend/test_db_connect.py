import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
print('Testing DB connection with:')
print('DB_NAME=', os.getenv('DB_NAME'))
print('DB_USER=', os.getenv('DB_USER'))
print('DB_HOST=', os.getenv('DB_HOST'))
print('DB_PORT=', os.getenv('DB_PORT'))

try:
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    print('Connected OK, server_version=', conn.server_version)
    conn.close()
except Exception as e:
    print('Connection failed:', repr(e))
