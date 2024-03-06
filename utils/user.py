from datetime import datetime
import sqlite3
import uuid
from utils.database import open_db_connection, close_db_connection
from config import DEFAULT_WORK_STARTING_TIME, DEFAULT_WORK_ENDING_TIME

def generate_user_id():
    return str(uuid.uuid4())


def create_user(user_id, username, email, active_plan_id=None, webhook_string = None, is_deactive=False, work_starting_time= DEFAULT_WORK_STARTING_TIME, work_ending_time=DEFAULT_WORK_ENDING_TIME):
    conn, cursor = open_db_connection()
    if conn:
        try:
            cursor.execute('''INSERT INTO users (user_id, username, email, active_plan_id, webhook_string, is_deactive, work_starting_time, work_ending_time)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (user_id, username, email, active_plan_id, webhook_string, is_deactive, work_starting_time, work_ending_time))
            conn.commit()
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("User ID already taken")
            else:
                print("Error creating user:", e)
        finally:
            close_db_connection(conn)


def fetch_user_plan_ids(userid):
    try:
        conn, cursor = open_db_connection()

        cursor.execute('''SELECT plan_id FROM plans WHERE user_id = ?''', (userid,))
        plan_ids = [row[0] for row in cursor.fetchall()]

        close_db_connection(conn)

        return plan_ids
    except sqlite3.Error as e:
        print("Error fetching user plan IDs:", e)
        return None
    

def is_user_plan_valid(userid, plainid):
    try:
        conn, cursor = open_db_connection()

        cursor.execute('''SELECT plan_id FROM plans WHERE user_id = ?''', (userid,))
        plan_ids = [row[0] for row in cursor.fetchall()]

        close_db_connection(conn)

        if plainid in plan_ids:
            return True
        return False
    except sqlite3.Error as e:
        print("Error fetching user plan IDs:", e)
        return None


def fetch_user_active_planid(user_id):
    try:
        conn, cursor = open_db_connection()
        cursor.execute('''SELECT active_plan_id FROM users WHERE user_id = ?''', (user_id,))
        active_plan_id = cursor.fetchone()[0]
        return active_plan_id
    except (sqlite3.Error, TypeError) as e:
        print("Error fetching user active plan id:", e)
        return None
    finally:
        close_db_connection(conn)

def set_active_plan_id(user_id, active_plan_id):
    conn, cursor = open_db_connection()
    if conn:
        try:
            # check whether plan id exists and belongs to user
            if not is_user_plan_valid(user_id, active_plan_id):
                raise ValueError("Invalid plan for user")
            
            cursor.execute('''UPDATE users
                              SET active_plan_id = ?
                              WHERE user_id = ?''', (active_plan_id, user_id))
            conn.commit()
        except sqlite3.Error as e:
            print("Error setting active plan id:", e)
        finally:
            close_db_connection(conn)


def activate_plan():
    pass


def update_plan_daily_frequency(user_id, new_frequency):
    try:
        conn, cursor = open_db_connection()
        active_plan_id = fetch_user_active_planid(user_id)

        cursor.execute('''UPDATE plans
                          SET daily_problem_frequency = ?
                          WHERE plan_id = ?''', (new_frequency, active_plan_id))

        conn.commit()
        close_db_connection(conn)
        return active_plan_id

    except sqlite3.Error as e:
        print("Error updating daily frequency:", e)


def set_user_webhook(user_id, webhook_string):
    try:
        conn, cursor = open_db_connection()

        cursor.execute('''UPDATE users
                          SET webhook_string = ?
                          WHERE user_id = ?''', (webhook_string, user_id))

        conn.commit()
        close_db_connection(conn)
        return 

    except sqlite3.Error as e:
        print("Error updating webhook:", e)


def update_work_time_for_user(user_id, work_start_time, work_end_time):
    conn, cursor = open_db_connection()
    work_start_time = datetime.strptime(work_start_time, "%H:%M:%S").time().strftime("%H:%M:%S")
    work_end_time = datetime.strptime(work_end_time, "%H:%M:%S").time().strftime("%H:%M:%S")

    try:
        cursor.execute("""
            UPDATE users
            SET work_starting_time = ?, work_ending_time = ?
            WHERE user_id = ?
        """, (work_start_time, work_end_time, user_id))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        close_db_connection(conn)