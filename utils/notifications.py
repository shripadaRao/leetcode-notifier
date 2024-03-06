import asyncio
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from config import NOTIFICATION_BIN_INTERVAL, BOT_AVATAR, BOT_USERNAME, build_notification_embed
from utils.user_progress import fetch_daily_pending_problem_list, fetch_problem_by_id
import datetime
from utils.database import open_db_connection, close_db_connection


def test_scheduler():
  scheduler = BackgroundScheduler()
  scheduler.add_job(func=test_func, trigger='interval', seconds=10)
  scheduler.start()

def test_func():
    print("Hello")
    print(datetime.now())


async def send_user_notifications():
    batch_size = 100
    active_users = fetch_active_users_with_webhooks()
    print("running notification scheduler ", datetime.datetime.now())
    
    if len(active_users) == 0:
        return

    for i in range(0, len(active_users), batch_size):
        batch = active_users[i:i+batch_size]
        tasks = [asyncio.create_task(send_user_notification(user_id, webhook_url))
                 for user_id, webhook_url in batch]
        await asyncio.gather(*tasks)

def fetch_active_users_with_webhooks():
    result = []
    try:
        conn, cursor = open_db_connection()
        if conn:
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            q = """
                SELECT user_id, webhook_string
                FROM users
                WHERE ? BETWEEN work_starting_time AND work_ending_time
                    AND is_deactive = 0
            """
            cursor.execute(q, (current_time,))
            result = cursor.fetchall()
    except sqlite3.Error as e:
        raise e + "\n Error fetching active users"
    finally:
        if conn:
            conn.close()
    return result

async def send_user_notification(userid, webhook_url):
    notification_parameters = await fetch_notification_parameters_for_user(userid)
    if not notification_parameters:
        raise ValueError("Failed to fetch notification parameters for user:", userid)

    daily_pending_problems = notification_parameters["daily_pending_problems"]   

    # Calculate whether or not to send notification
    if should_send_notification(notification_parameters):
        tasks = [fetch_problem_by_id(problem_id) for problem_id in daily_pending_problems]
        problem_details = await asyncio.gather(*tasks)
        embed = build_notification_embed(userid, problem_details)
        await send_discord_message(webhook_url, "", embed=embed)
        print("SENT NOTIFICATION \n ", embed)
    
    else:
        print("Didn't choose to send notification")

async def send_discord_message(webhook_url, message_content, embed, mentions = None):
    """Sends a message to a Discord channel using a webhook.   """

    if not webhook_url:
        raise ValueError("Webhook URL is required.")

    payload = {
        "content": message_content,
    }

    payload["username"] = BOT_USERNAME

    payload["avatar_url"] = BOT_AVATAR

    if mentions:
        payload["mentions"] = mentions

    if embed:
        payload["embeds"] = [embed]

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()  

        print("Discord message sent successfully!")

    except requests.exceptions.RequestException as e:
        print(f"Error sending Discord message: {e}")

def should_send_notification(notification_parameters):
    # compute notification equation and compare with weights 
    threshold_val = 1
    a = 10
    r = notification_parameters["remaining_time_bins_per_problem"]
    k = notification_parameters["likelihood_factor"]
    w1, w2 = 0.5, 0.8
    p = (a/r)*w1 + k*w2
    print("p val: ", p)
    return p > threshold_val

async def fetch_notification_parameters_for_user(userid):
    daily_pending_problems = fetch_daily_pending_problem_list(userid)
    remaining_time_bins = number_of_remaining_time_bins(userid) 
    remaining_time_bins_per_problem = remaining_time_bins//len(daily_pending_problems)

    # fetch likeihood factor for time interval
    likelihood_factor = fetch_likelihood_factor_for_time_interval(userid)

    print("dialy pending problem", daily_pending_problems)
    print("remaining time :", remaining_time_bins_per_problem)
    print("likeihood", likelihood_factor)

    if not all([len(daily_pending_problems), likelihood_factor, remaining_time_bins_per_problem]):
        raise Exception("Failed to fetch all required notification parameters")

    return {"remaining_time_bins_per_problem" : remaining_time_bins_per_problem, "likelihood_factor": likelihood_factor, "daily_pending_problems": daily_pending_problems}



def number_of_remaining_time_bins(user_id):
    try:
        conn, cursor = open_db_connection()
        if conn:
            q = """
                SELECT work_ending_time
                FROM users
                WHERE user_id = ?
            """
            cursor.execute(q, (user_id,))
            user_work_ending_time_str = cursor.fetchone()[0]

        user_work_ending_time = datetime.datetime.strptime(user_work_ending_time_str, "%H:%M:%S").time()

        current_date = datetime.date.today()
        current_datetime = datetime.datetime.now()

        user_datetime = datetime.datetime.combine(current_date, user_work_ending_time)
        remaining_time_in_min = (user_datetime - current_datetime).total_seconds()//60


    except (sqlite3.Error, TypeError) as e:
        print("Error fetching user's work_ending_time:", e)
        raise Exception("Error fetching user's work_ending_time")
    finally:
        close_db_connection(conn)

    remaining_number_of_bins = remaining_time_in_min // NOTIFICATION_BIN_INTERVAL
    return remaining_number_of_bins


def fetch_likelihood_factor_for_time_interval(user_id):
    try:
        conn, cursor = open_db_connection()
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        if conn:
            q = """
                SELECT likelihood_parameter
                FROM notification_parameter
                WHERE user_id = ? AND 
                time_intervals_start <= ? AND time_intervals_end >= ?
            """
            cursor.execute(q, (user_id, current_time, current_time))
            likelihood_factor = cursor.fetchone()
            if likelihood_factor:
                return likelihood_factor[0]
            else:
                raise Exception("No likeihood parameter found for current time")
            
    except (sqlite3.Error, TypeError) as e:
        print("Error fetching user likeihood factor:", e)
        raise Exception("Error fetching user likehood factor")
    finally:
        close_db_connection(conn)


def update_or_insert_notification_parameters(user_id, time_intervals_start, time_intervals_end, likelihood_parameter):
    conn, cursor = open_db_connection()
    try:
        time_intervals_start = datetime.datetime.strptime(time_intervals_start, "%H:%M:%S").time().strftime("%H:%M:%S")
        time_intervals_end = datetime.datetime.strptime(time_intervals_end, "%H:%M:%S").time().strftime("%H:%M:%S")

        cursor.execute("""
            SELECT * FROM notification_parameter
            WHERE user_id = ? AND time_intervals_start = ? AND time_intervals_end = ?
        """, (user_id, time_intervals_start, time_intervals_end))
        existing_record = cursor.fetchone()

        if existing_record:
            cursor.execute("""
                UPDATE notification_parameter
                SET likelihood_parameter = ?
                WHERE user_id = ? AND time_intervals_start = ? AND time_intervals_end = ?
            """, (likelihood_parameter, user_id, time_intervals_start, time_intervals_end))
        else:
            cursor.execute("""
                INSERT INTO notification_parameter (user_id, time_intervals_start, time_intervals_end, likelihood_parameter)
                VALUES (?, ?, ?, ?)
            """, (user_id, time_intervals_start, time_intervals_end, likelihood_parameter))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        close_db_connection(conn)
