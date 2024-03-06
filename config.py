from datetime import time


DEFAULT_WORK_STARTING_TIME = time(9, 0)  # 9 am
DEFAULT_WORK_ENDING_TIME = time(23, 0)   # 11 pm

NOTIFICATION_BIN_INTERVAL = 1 * 60 * 15 # in seconds
BOT_USERNAME = "Leetcode Notifier"
BOT_AVATAR = ""
DEFAULT_TITLE_MESSAGE = "Your Daily problems are pending!!"

def build_notification_embed(user_id, daily_pending_problems_details):
    embed = {
        "title": DEFAULT_TITLE_MESSAGE,
        "description": f"Hi {user_id}, time to tackle your LeetCode problems!",
        "color": 0x00FFFF,
        "fields": [],
    }

    for problem_detail in daily_pending_problems_details:
        embed["fields"].append({
            "name" : problem_detail["problem_title"],
            "value" : f"[Link to problem]({problem_detail['problem_url']})",
            "inline" : False,
        })

    return embed