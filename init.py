import sqlite3
import uuid

from problemset_parsers import *

def open_db_connection(dbname):
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


def create_table_data(dbname):
    conn, cursor = open_db_connection(dbname)

    # Create the user table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        username TEXT,
                        email TEXT,
                        active_plan_id TEXT
                    )''')

    # Create the plans table
    cursor.execute('''CREATE TABLE IF NOT EXISTS plans (
                        plan_id TEXT PRIMARY KEY,
                        dsa_sheet_id TEXT,
                        user_id TEXT,
                        daily_problem_frequency INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )''')

    # Create the user_progress table
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_progress (
                        user_id TEXT,
                        plan_id TEXT,
                        problem_id INTEGER,
                        sequence_number INTEGER,
                        completed BOOLEAN,
                        completed_date DATETIME,
                        PRIMARY KEY (user_id, plan_id, sequence_number),
                        FOREIGN KEY (user_id) REFERENCES user(user_id),
                        FOREIGN KEY (plan_id) REFERENCES plans(plan_id)
                    )''')

    # Create indexes on user_id, plan_id, and sequence_number columns
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_user_id ON user_progress (user_id)''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_plan_id ON user_progress (plan_id)''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_sequence_number ON user_progress (sequence_number)''')


    # Create the problems table
    cursor.execute('''CREATE TABLE IF NOT EXISTS problems (
                        problem_id INTEGER PRIMARY KEY,
                        title TEXT,
                        url TEXT
                    )''')

    # Create the dsa_sheets table
    cursor.execute('''CREATE TABLE IF NOT EXISTS dsa_sheets (
                        dsa_sheet_id TEXT ,
                        problem_id INTEGER,
                        problem_url TEXT,
                        sequence_number INTEGER
                    )''')

                        # FOREIGN KEY (problem_id) REFERENCES problems(problem_id)

    close_db_connection(conn)
    return


create_table_data(dbname="test.db")

