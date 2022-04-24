# import db
import pymysql

db = pymysql.connect(
        host = 'localhost',
        user = 'root',
        password = '12345678',
        database = 'secretary')

cursor = db.cursor()