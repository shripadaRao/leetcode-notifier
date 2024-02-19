from flask import Flask, jsonify, request
import sqlite3
from utils.user import create_user, update_plan_daily_frequency, fetch_user_plan_ids, set_active_plan_id, fetch_user_active_planid
from utils.plans import initiate_plan
from utils.user_progress import fetch_all_pending_problem_list, fetch_all_completed_problem_list, complete_problem, fetch_daily_problem_list, fetch_daily_pending_problem_list

app = Flask(__name__)

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

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/users/create', methods=['POST'])
def create_user_route():
    try:
        data = request.json
        user_id, username = data["user_id"], data["username"]
        email, active_plan_id = data["email"], data.get('active_plan_id')

        if not all([user_id, username, email ]):
            return jsonify({'error': 'Missing required fields'}), 400

        create_user(user_id, username, email, active_plan_id)
        return jsonify({'message': 'User created successfully'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    

# create plan
@app.route('/plans/initiate', methods=['POST'])
def initiate_plan_route():
    try:
        data = request.json
        dsa_sheet_id = data["dsa_sheet_id"]
        problem_frequency = data["problem_frequency"]
        userid = data["user_id"]
        if not all([dsa_sheet_id, problem_frequency, userid]):
            return jsonify({'error': 'Missing required fields'}), 400
        # handle edge cases for input of problem_frequency
        initiate_plan(dsa_sheet_id, problem_frequency, userid)
        return jsonify({'message': 'Plan initiated successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# api for updating daily problem frequency
@app.route('/plans/update-frequency', methods=['PUT'])
def update_plan_frequency_route():
    try:
        data = request.json
        userid = data["user_id"]
        new_freq = data["new_frequency"]
        if not all([userid, new_freq]):
            return jsonify({'error': 'Missing required fields'}), 400
        # handle edge cases for input for new daily frequency
        active_plan_id = update_plan_daily_frequency(userid, new_freq)
        return jsonify({'message': 'Daily frequency updated successfully', 'active_plan_id':str(active_plan_id)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# apis for plan progress
@app.route('/problems/complete', methods=['POST'])
def complete_problem_route():
    try:
        # Get data from the request
        data = request.json
        user_id = data.get('user_id')
        problem_id = data.get('problem_id')

        if not all([user_id, problem_id]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Call the function to complete the problem
        result = complete_problem(user_id, problem_id)

        if result is True:
            return jsonify({'message': 'Problem marked as complete'}), 200
        else:
            return jsonify({'error': result}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# api for fetching daily problems
@app.route('/problems/daily', methods=['GET'])
def fetch_daily_problem_list_route():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        daily_problem_list = fetch_daily_problem_list(user_id)

        if len(daily_problem_list) >= 0:
            return jsonify({'daily_problem_list': daily_problem_list}), 200
        else:
            return jsonify({'message': 'No daily problems available'}), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# # api for viewing backlog
# @app.route('/problems/backlog', methods=['GET'])
# def fetch_backlog_problem_list_route():
#     try:
#         user_id = request.args.get('user_id')
#         if not user_id:
#             return jsonify({'error': 'User ID is required'}), 400

#         backlog_problem_list = fetch_backlog_problem_list(user_id)

#         if len(backlog_problem_list) >= 0:
#             return jsonify({'backlog_problem_list': backlog_problem_list}), 200
#         else:
#             return jsonify({'message': 'No daily problems available'}), 200

#     except ValueError as ve:
#         return jsonify({'error': str(ve)}), 400
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# api to fetch pending problems for the day
@app.route('/users/problems/daily-pending', methods=['GET'])
def fetch_daily_pending_problem_list_route():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            raise ValueError("User ID is required")

        pending_problem_list = fetch_daily_pending_problem_list(user_id)
        return jsonify({'pending_problem_list': pending_problem_list}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# api for getting all pending problems for user_id for their current active plan
@app.route('/users/problems/all-pending', methods=['GET'])
def fetch_all_pending_problem_list_route():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            raise ValueError("User ID is required")

        pending_problem_list = fetch_all_pending_problem_list(user_id)
        return jsonify({'pending_problem_list': pending_problem_list}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# api for getting completed problems for user_id for their current active plan
@app.route('/users/problems/all-completed', methods=['GET'])
def fetch_all_completed_problem_list_route():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            raise ValueError("User ID is required")

        completed_problem_list = fetch_all_completed_problem_list(user_id)
        return jsonify({'completed_problem_list': completed_problem_list}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/users/active-plan-id/<user_id>', methods=['GET'])
def fetch_user_active_planid_route(user_id):
    try:
        if not user_id:
            raise ValueError("User ID is required")

        active_plan_id = fetch_user_active_planid(user_id)
        if active_plan_id is None:
            raise ValueError("No active plan ID found for the user")

        return jsonify({'active_plan_id': active_plan_id}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/users/plan-ids/<user_id>', methods=['GET'])
def fetch_user_plan_ids_route(user_id):
    try:
        if not user_id:
            raise ValueError("User ID is required")
        
        plan_ids = fetch_user_plan_ids(user_id)
        if plan_ids is None or len(plan_ids)==0:
            raise ValueError("There are no user plan IDs")

        return jsonify({'plan_ids': plan_ids}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/set-active-plan', methods=['PUT'])
def set_active_plan_id_route():
    try:
        data = request.json
        user_id = data.get('user_id')
        active_plan_id = data.get('active_plan_id')
        if not user_id and not active_plan_id:
            raise ValueError("User ID and Active plan ID is required")
        
        set_active_plan_id(user_id, active_plan_id)
        return jsonify({'message': 'Active plan ID updated successfully', 'active_plan_id':active_plan_id}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


if __name__ == '__main__':
    app.run(debug=True)