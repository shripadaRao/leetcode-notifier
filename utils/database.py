import sqlite3


def open_db_connection(dbname="test2.db"):
    try:
        conn = sqlite3.connect(dbname)
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        print("Error connecting to the database:", e)
        return None, None

def close_db_connection(conn):
    if conn:
        try:
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print("Error closing the database connection:", e)
