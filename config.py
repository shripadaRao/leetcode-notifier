from datetime import time


DEFAULT_WORK_STARTING_TIME = time(9, 0)  # 9 am
DEFAULT_WORK_ENDING_TIME = time(23, 0)   # 11 pm

NOTIFICATION_BIN_INTERVAL = 1 * 15 # in minutes
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


DEFAULT_NOTIFICATION_PARAMS = {
  "notification_parameters": [
    {
      "time_interval_start": "09:00:00",
      "time_interval_end": "10:00:00",
      "likelihood_parameter": 7
    },
    {
      "time_interval_start": "10:00:00",
      "time_interval_end": "11:00:00",
      "likelihood_parameter": 5
    },
    {
      "time_interval_start": "11:00:00",
      "time_interval_end": "12:00:00",
      "likelihood_parameter": 5
    },
    {
      "time_interval_start": "12:00:00",
      "time_interval_end": "13:00:00",
      "likelihood_parameter": 3
    },
    {
      "time_interval_start": "13:00:00",
      "time_interval_end": "14:00:00",
      "likelihood_parameter": 3
    },
    {
      "time_interval_start": "14:00:00",
      "time_interval_end": "15:00:00",
      "likelihood_parameter": 3
    },
    {
      "time_interval_start": "15:00:00",
      "time_interval_end": "16:00:00",
      "likelihood_parameter": 3
    },
    {
      "time_interval_start": "16:00:00",
      "time_interval_end": "17:00:00",
      "likelihood_parameter": 5
    },
    {
      "time_interval_start": "17:00:00",
      "time_interval_end": "18:00:00",
      "likelihood_parameter": 5
    },
    {
      "time_interval_start": "18:00:00",
      "time_interval_end": "19:00:00",
      "likelihood_parameter": 5
    },
    {
      "time_interval_start": "19:00:00",
      "time_interval_end": "20:00:00",
      "likelihood_parameter": 7
    },
    {
      "time_interval_start": "20:00:00",
      "time_interval_end": "21:00:00",
      "likelihood_parameter": 7
    },
    {
      "time_interval_start": "21:00:00",
      "time_interval_end": "22:00:00",
      "likelihood_parameter": 5
    },
    {
      "time_interval_start": "22:00:00",
      "time_interval_end": "23:00:00",
      "likelihood_parameter": 5
    }
  ]
}