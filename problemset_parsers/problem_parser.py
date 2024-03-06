from utils.database import open_db_connection, close_db_connection

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

def populate_problems_table(problem_ids, problem_titles, problem_urls, dbname):
    conn, cursor = open_db_connection(dbname)

    for problem_id, problem_title, problem_url in zip(problem_ids, problem_titles, problem_urls):
        cursor.execute("INSERT INTO problems (problem_id, title, url) VALUES (?, ?, ?)",
                       (problem_id, problem_title, problem_url))

    close_db_connection(conn)

# file_path = "problemset_parsers/leetcode-all-problems.txt"
# problem_ids, problem_titles, problem_urls = read_leetcode_problems(file_path)
# populate_problems_table(problem_ids, problem_titles, problem_urls, dbname)
