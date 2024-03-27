import psycopg2


def connect_to_database():
    try:
        # Veritabanına bağlan
        conn = psycopg2.connect(database="ExpenseTracker",
                                user="postgres",
                                password="123456",
                                host="localhost",
                                port="5432")
        return conn
    except psycopg2.Error as e:
        print("Veritabanına bağlanırken bir hata oluştu:", e)
        return None