
from config import RUNNING_DB
from utils.database import open_db_connection, close_db_connection
from problemset_parsers import *
from problemset_parsers.dsa_sheet_parser import read_raw_neetcode150_problems, populate_problems_in_dsa_sheet, add_problem_id_to_dsa_sheet
from problemset_parsers.problem_parser import populate_problems_table,  read_leetcode_problems  
import os.path

def create_table_data(dbname):
    conn, cursor = open_db_connection(dbname)

    # Create the user table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        username TEXT,
                        email TEXT,
                        active_plan_id TEXT,
                        webhook_string TEXT,
                        is_deactive BOOLEAN,
                        work_starting_time TIME,
                        work_ending_time TIME
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
    
    # Create the notification parameters table
    cursor.execute('''CREATE TABLE IF NOT EXISTS notification_parameter (
                        user_id TEXT ,
                        time_intervals_start TIME,
                        time_intervals_end TIME,
                        likelihood_parameter INTEGER,
                   
                        FOREIGN KEY (user_id) REFERENCES user(user_id)
                    )''')



    close_db_connection(conn)
    return


dbname = "test.db"

if __name__ == "__main__":
    if os.path.isfile(dbname):
        print("DB already present")
        exit(0)

    create_table_data(dbname)

    problem_ids, problem_titles, problem_urls = read_leetcode_problems(file_path = "problemset_parsers/leetcode-all-problems.txt")
    populate_problems_table(problem_ids, problem_titles, problem_urls, dbname)

    problem_urls = read_raw_neetcode150_problems()
    populate_problems_in_dsa_sheet(problem_urls)
    add_problem_id_to_dsa_sheet()

