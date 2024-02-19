import uuid
import sqlite3


def open_db_connection(dbname="test.db"):
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

def is_dsa_sheet_id_exists(dsa_sheet_id):
    try:
        conn, cursor = open_db_connection() 
        cursor.execute('''SELECT COUNT(*) FROM dsa_sheet WHERE sheet_id = ?''', (dsa_sheet_id,))
        count = cursor.fetchone()[0]
        return count > 0
    except sqlite3.Error as e:
        print("Error checking if DSA sheet ID exists:", e)
        return False
    finally:
        close_db_connection(conn)

def create_plan(dsa_sheet_id, problem_frequency, user_id):
    plan_id = str(uuid.uuid4())
    conn, cursor = open_db_connection()
    if conn:
        try:
            # check whether dsa_sheet_id exists 
            if not is_dsa_sheet_id_exists:
                raise ValueError("Invalid dsa_sheet_id")
            cursor.execute('''INSERT INTO plans (plan_id, dsa_sheet_id, daily_problem_frequency, user_id)
                              VALUES (?, ?, ?, ?)''', (plan_id, dsa_sheet_id, problem_frequency, user_id))
            conn.commit()
            return plan_id
        except sqlite3.Error as e:
            print("Error creating plan:", e)
            return None
        finally:
            close_db_connection(conn)


def populate_boilerplate_user_progress(user_id, dsa_sheet_id, plan_id):
    conn, cursor = open_db_connection()
    if conn and plan_id:
        try:
            cursor.execute('''INSERT INTO user_progress (user_id, plan_id, problem_id, sequence_number, completed, completed_date)
                              SELECT ?, ?, problem_id, sequence_number, 0, NULL
                              FROM dsa_sheets
                              WHERE dsa_sheet_id = ?''', (user_id, plan_id, dsa_sheet_id))
            conn.commit()
        except sqlite3.Error as e:
            print("Error populating boilerplate user progress:", e)
        finally:
            close_db_connection(conn)


def initiate_plan(dsa_sheet_id, problem_frequency, userid):
    try:
        plan_id = create_plan(dsa_sheet_id, problem_frequency, userid)
        populate_boilerplate_user_progress(userid, dsa_sheet_id, plan_id)
    except Exception as e:
        print("Error initiating plan:", e)

# initiate_plan("1", 4, "srao")