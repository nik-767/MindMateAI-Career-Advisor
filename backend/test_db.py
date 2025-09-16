import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()
print('ENV DB_NAME=', os.getenv('DB_NAME'))
try:
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    print('Connected OK, server version:', conn.server_version)
    conn.close()
except Exception as e:
    print('Connection failed:', e)
