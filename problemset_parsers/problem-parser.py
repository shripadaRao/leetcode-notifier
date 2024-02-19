# import sqlite3


# problem_ids = []
# problem_titles = []
# problem_urls = []


# with open("leetcode-all-problems.txt", 'r') as file:
#     for line_number, line in enumerate(file, start=1):
#         if line_number > 4:
#             data_columns = line.strip().split('|')
#             # print(data_columns)
#             problem_id = data_columns[1].strip()
#             title_url_break_index = data_columns[2].find("]")
#             problem_title = data_columns[2].strip()[1:title_url_break_index]
#             problem_url = data_columns[2].strip()[title_url_break_index+2:-1]

#             problem_ids.append(problem_id)
#             problem_titles.append(problem_title)
#             problem_urls.append(problem_url)
            


# conn = sqlite3.connect('leetcode-notiifier-db.db')
# cursor = conn.cursor()

# cursor.execute('''CREATE TABLE IF NOT EXISTS problems (
#                     problem_id INTEGER,
#                     problem_title TEXT,
#                     problem_url TEXT
#                 )''')


# for problem_id, problem_title, problem_url in zip(problem_ids, problem_titles, problem_urls):
#     cursor.execute("INSERT INTO problems (problem_id, problem_title, problem_url) VALUES (?, ?, ?)", (problem_id, problem_title, problem_url))

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



def read_leetcode_problems(file_path="problemset_parsers/leetcode-all-problems.txt"):
    problem_ids = []
    problem_titles = []
    problem_urls = []

    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if line_number > 4:
                data_columns = line.strip().split('|')
                problem_id = data_columns[1].strip()
                title_url_break_index = data_columns[2].find("]")
                problem_title = data_columns[2].strip()[1:title_url_break_index]
                problem_url = data_columns[2].strip()[title_url_break_index+2:-1]

                problem_ids.append(problem_id)
                problem_titles.append(problem_title)
                problem_urls.append(problem_url)

    return problem_ids, problem_titles, problem_urls

def populate_problems_table(problem_ids, problem_titles, problem_urls):
    conn, cursor = open_db_connection()

    for problem_id, problem_title, problem_url in zip(problem_ids, problem_titles, problem_urls):
        cursor.execute("INSERT INTO problems (problem_id, title, url) VALUES (?, ?, ?)",
                       (problem_id, problem_title, problem_url))

    close_db_connection(conn)

if __name__ == "__main__":
    file_path = "problemset_parsers/leetcode-all-problems.txt"
    problem_ids, problem_titles, problem_urls = read_leetcode_problems(file_path)
    populate_problems_table(problem_ids, problem_titles, problem_urls)
