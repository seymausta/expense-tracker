import os
import psycopg2
from flask import request

conn = psycopg2.connect(database="ExpenseTracker",
                        user="postgres",
                        password="123456",
                        host="localhost", port="5432")

cur = conn.cursor()

"""cur.execute('INSERT INTO users (email, password, name, surname)'
            'VALUES (%s, %s, %s, %s)',
            ('seyma@gmail.com',
             '123456',
             'Seyma',
             'Usta')
            ) """

