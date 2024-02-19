# import sqlite3

# """
# sheet_id dsa sheet mapping
# 1 -> neetcode 150

# """

# problem_titles = []
# problem_urls = []

# with open("neetcode-150-problems.txt", "r") as file:
#     for sequence_no, data in enumerate(file):
#         if sequence_no >= 1:
#             problem_title = data.split("\t")[0].strip()
#             problem_url = data.split("\t")[2].strip()

#             problem_titles.append(problem_title)
#             problem_urls.append(problem_url)


# print(problem_urls[:10])


# # remove "/accounts/login/?next=" if present from urls
# problem_urls = [problem_url.replace("/accounts/login/?next=", "") if "/accounts/login/?next=" in problem_url else problem_url for problem_url in problem_urls]


# # do mapping of problem_id from problem_url
# problem_ids = []


# conn = sqlite3.connect('leetcode-notiifier-db.db')
# cursor = conn.cursor()

# # Create a table to store the data
# cursor.execute('''CREATE TABLE IF NOT EXISTS dsa_sheet (
#                     sheet_id INTEGER,
#                     sequence_number INTEGER,
#                     problem_url TEXT
#                     problem_id TEXT
#                 )''')

# sheet_id = 1
# sequence_number = 0

# for problem_url in problem_urls:
#     sequence_number += 1
#     cursor.execute("INSERT INTO dsa_sheet (sheet_id, sequence_number, problem_url) VALUES (?, ?, ?)",
#                    (sheet_id, sequence_number, problem_url))

# # Commit changes and close the connection
# conn.commit()
# conn.close()


import sqlite3


def open_db_connection(dbname='test.db'):
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


def read_raw_neetcode150_problems(file_path="problemset_parsers/neetcode-150-problems.txt"):
    problem_titles = []
    problem_urls = []

    with open(file_path, "r") as file:
        for sequence_no, data in enumerate(file):
            if sequence_no >= 1:
                problem_title = data.split("\t")[0].strip()
                problem_url = data.split("\t")[2].strip()

                problem_titles.append(problem_title)
                problem_urls.append(problem_url)

    return problem_urls

def remove_login_next(problem_urls):
    return [problem_url.replace("/accounts/login/?next=", "") if "/accounts/login/?next=" in problem_url else problem_url for problem_url in problem_urls]

def create_dsa_sheet_table(problem_urls):
    conn, cursor = open_db_connection()

    sheet_id = 1
    sequence_number = 0

    for problem_url in problem_urls:
        sequence_number += 1
        cursor.execute("INSERT INTO dsa_sheets (dsa_sheet_id, sequence_number, problem_url) VALUES (?, ?, ?)",
                       (sheet_id, sequence_number, problem_url))

    close_db_connection(conn)


def add_problem_id_to_dsa_sheet():
    conn, cursor = open_db_connection()

    # Update the problem_id column by joining the dsa_sheet and problems tables
    cursor.execute('''UPDATE dsa_sheets
                    SET problem_id = (SELECT problems.problem_id
                                        FROM problems
                                        WHERE dsa_sheets.problem_url = problems.url)''')

    close_db_connection(conn)
    return


problem_urls = read_raw_neetcode150_problems()
create_dsa_sheet_table(problem_urls)
add_problem_id_to_dsa_sheet()