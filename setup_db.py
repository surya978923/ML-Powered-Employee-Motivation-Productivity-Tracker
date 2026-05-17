import MySQLdb

try:
    db = MySQLdb.connect(host="localhost", user="root", passwd="9789")
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS productivity_db")
    db.commit()
    db.close()
    print("Database created or already exists!")
except Exception as e:
    print(f"Error: {e}")
