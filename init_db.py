import psycopg2
from psycopg2 import pool

# Veritabanı bağlantı havuzu oluşturma
db_pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=10,
                                             database="ExpenseTracker",
                                             user="postgres",
                                             password="123456",
                                             host="localhost",
                                             port="5432")

def get_database_connection():
    try:
        # Bağlantı havuzundan bir bağlantı al
        conn = db_pool.getconn()
        return conn
    except psycopg2.Error as e:
        print("Veritabanına bağlanırken bir hata oluştu:", e)
        return None

def close_database_connection(conn):
    if conn:
        # Bağlantıyı havuza geri ver
        db_pool.putconn(conn)

def close_all_database_connections():
    # Havuzdaki tüm bağlantıları kapat
    db_pool.closeall()