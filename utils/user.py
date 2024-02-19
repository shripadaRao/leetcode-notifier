import sqlite3
import uuid


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



def generate_user_id():
    return str(uuid.uuid4())


def create_user(user_id, username, email, active_plan_id=None):
    conn, cursor = open_db_connection()
    if conn:
        try:
            cursor.execute('''INSERT INTO users (user_id, username, email, active_plan_id)
                              VALUES (?, ?, ?, ?)''', (user_id, username, email, active_plan_id))
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

        # Update the daily frequency in the plans table
        cursor.execute('''UPDATE plans
                          SET daily_problem_frequency = ?
                          WHERE plan_id = ?''', (new_frequency, active_plan_id))

        conn.commit()
        close_db_connection(conn)
        return active_plan_id

    except sqlite3.Error as e:
        print("Error updating daily frequency:", e)


update_plan_daily_frequency("srao", 2)
# create_user("srao", "srao", "srao@gmail.com")
# set_active_plan_id("srao", "cb527474-3370-4fef-bdbc-acfe8047bf5e")