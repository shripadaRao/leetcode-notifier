from datetime import datetime
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

print(fetch_user_active_planid("testuser"))

def fetch_daily_problem_list(user_id):
    try:
        active_plan_id = fetch_user_active_planid(user_id)
        if active_plan_id is None:
            raise ValueError("no active plan selected")
            

        conn, cursor = open_db_connection()

        cursor.execute('''SELECT daily_problem_frequency FROM plans WHERE plan_id = ?''', (active_plan_id,))
        daily_problem_frequency = cursor.fetchone()[0]

        cursor.execute('''SELECT problem_id
                    FROM user_progress
                    WHERE user_id = ? AND plan_id = ? AND (
                       (completed = 0) OR (completed_date > DATE('now') AND completed_date < DATE('now','+1 day'))
                    )
                    ORDER BY sequence_number
                    LIMIT ? ''', (user_id, active_plan_id, daily_problem_frequency))

        daily_problem_list = [row[0] for row in cursor.fetchall()]

        return daily_problem_list
    except (sqlite3.Error, TypeError, ValueError) as e:
        print("Error fetching daily problem list:", e)
        return []
    finally:
        close_db_connection(conn)

def fetch_backlog_problem_list(user_id):
    pass

def fetch_daily_pending_problem_list(user_id):
    try:
        conn, cursor = open_db_connection()

        cursor.execute('''SELECT active_plan_id FROM users WHERE user_id = ?''', (user_id,))
        active_plan_id = cursor.fetchone()[0]

        cursor.execute('''SELECT daily_problem_frequency FROM plans WHERE plan_id = ?''', (active_plan_id,))
        daily_problem_frequency = cursor.fetchone()[0]


        cursor.execute('''SELECT problem_id, completed_date
            FROM user_progress
            WHERE user_id = ? AND plan_id = ? AND (
                (completed = 0) OR (completed_date > DATE('now') AND completed_date < DATE('now','+1 day'))
            )
            ORDER BY sequence_number
            LIMIT ? ''', (user_id, active_plan_id, daily_problem_frequency))
        

        pending_daily_problems = []
        for row in cursor.fetchall():
            if row[1] is None:
                pending_daily_problems.append(row[0])
        return pending_daily_problems
    except (sqlite3.Error, TypeError) as e:
        print("Error fetching all pending problem list:", e)
        return []
    finally:
        close_db_connection(conn)   


def fetch_all_pending_problem_list(user_id):
    try:
        conn, cursor = open_db_connection()

        cursor.execute('''SELECT active_plan_id FROM users WHERE user_id = ?''', (user_id,))
        active_plan_id = cursor.fetchone()[0]

        cursor.execute('''SELECT problem_id
                          FROM user_progress
                          WHERE user_id = ? AND plan_id = ? AND completed = 0''', (user_id, active_plan_id))

        pending_problem_list = [row[0] for row in cursor.fetchall()]
        return pending_problem_list
    except (sqlite3.Error, TypeError) as e:
        print("Error fetching all pending problem list:", e)
        return []
    finally:
        close_db_connection(conn)


def fetch_all_completed_problem_list(user_id):
    try:
        conn, cursor = open_db_connection()

        cursor.execute('''SELECT active_plan_id FROM users WHERE user_id = ?''', (user_id,))
        active_plan_id = cursor.fetchone()[0]

        cursor.execute('''SELECT problem_id
                          FROM user_progress
                          WHERE user_id = ? AND plan_id = ? AND completed = 1''', (user_id, active_plan_id))

        completed_problem_list = [row[0] for row in cursor.fetchall()]
        return completed_problem_list
    except (sqlite3.Error, TypeError) as e:
        print("Error fetching all completed problem list:", e)
        return []
    finally:
        close_db_connection(conn)


def is_problemId_valid_for_completion(cursor, active_plan_id, user_id, problem_id):
    try:
        # Check if the problem_id is valid and not completed
        cursor.execute('''SELECT completed FROM user_progress
                          WHERE user_id = ? AND problem_id = ? AND plan_id = ?''', (user_id, problem_id, active_plan_id))
        result = cursor.fetchone()
        print(active_plan_id)
        print(result)
        if result is None:
            print("Error: Problem ID not found for the user")
            return False
        elif result[0] == 1:
            print("Error: Problem already completed")
            return False
        else:
            return True  

    except sqlite3.Error as e:
        print("Error validating problem:", e)
        return False


def complete_problem(user_id, problem_id):
    try:
        conn, cursor = open_db_connection()

        # Fetch user's active plan id
        active_plan_id = fetch_user_active_planid(user_id)
        if not active_plan_id:
            raise ValueError("Error fetching active plan id for user")

        if not is_problemId_valid_for_completion(cursor, active_plan_id, user_id, problem_id):
            raise ValueError("Invalid Problem ID")
        
        # Update the completion status and completion date
        completion_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''UPDATE user_progress
                          SET completed = ?, completed_date = ?
                          WHERE user_id = ? AND problem_id = ? AND plan_id = ?''', (True, completion_date, user_id, problem_id, active_plan_id))

        conn.commit()
        return True
    
    except ValueError as ve:
        return str(ve)            
    except sqlite3.Error as e:
        print("Error marking complete for problem:", e)
    finally:
        close_db_connection(conn)



# complete_problem("srao", 242)
# print(fetch_daily_problem_list("srao"))