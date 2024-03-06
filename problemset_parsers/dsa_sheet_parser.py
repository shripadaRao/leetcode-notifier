from utils.database import open_db_connection, close_db_connection


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

def populate_problems_in_dsa_sheet(problem_urls):
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


# problem_urls = read_raw_neetcode150_problems()
# populate_problems_in_dsa_sheet(problem_urls)
# add_problem_id_to_dsa_sheet()