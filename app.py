from flask import Flask, jsonify, request
from utils.notifications import update_or_insert_notification_parameters
from utils.user import create_user, update_plan_daily_frequency, fetch_user_plan_ids, set_active_plan_id, fetch_user_active_planid, set_user_webhook, update_work_time_for_user
from utils.plans import initiate_plan
from utils.user_progress import fetch_all_pending_problem_list, fetch_all_completed_problem_list, complete_problem, fetch_daily_problem_list, fetch_daily_pending_problem_list
from config import DEFAULT_WORK_STARTING_TIME, DEFAULT_WORK_ENDING_TIME


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/users/create', methods=['POST'])
def create_user_route():
    try:
        data = request.json
        user_id, username = data["user_id"], data["username"]
        email, active_plan_id = data["email"], data.get('active_plan_id')
        webhook_string, is_deactive = data["webhook_string"], data.get("is_deactive", False)
        work_starting_time = data.get("work_starting_time", DEFAULT_WORK_STARTING_TIME)
        work_ending_time = data.get("work_ending_time", DEFAULT_WORK_ENDING_TIME)

        if not all([user_id, username, email, webhook_string ]):
            return jsonify({'error': 'Missing required fields'}), 400

        create_user(user_id, username, email, active_plan_id, webhook_string, is_deactive, work_starting_time, work_ending_time)
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


@app.route('/users/set-webhook', methods=['PUT'])
def set_user_webhook_route():
    try:
        data = request.json
        userid = data["user_id"]
        webhook_string = data["webhook_string"]
        if not all([userid, webhook_string]):
            return jsonify({'error': 'Missing required fields'}), 400

        set_user_webhook(userid, webhook_string)

        return jsonify({'message': 'Webhook successfully updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# apis for plan progress
@app.route('/problems/mark-complete', methods=['POST'])
def complete_problem_route():
    try:
        data = request.json
        user_id = data.get('user_id')
        problem_id = data.get('problem_id')

        if not all([user_id, problem_id]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            complete_problem(user_id, problem_id)
            return jsonify({'message': 'problem marked completed successfully'}), 200

        except ValueError as e:
            return jsonify({"error": str(e)}, 400)
        
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
    
@app.route('/users/notification-parameters/update', methods=['POST'])
def update_notification_parameters():
    try:
        data = request.json
        user_id = data["user_id"]
        for params in data["notification_parameters"]:
            time_intervals_start = params.get('time_interval_start')
            time_intervals_end = params.get('time_interval_end')
            likelihood_parameter = params.get('likelihood_parameter')

            update_or_insert_notification_parameters(user_id, time_intervals_start, time_intervals_end, likelihood_parameter)

        return jsonify({"message": "Notification parameters updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@app.route('/users/update-work-time', methods=['PUT'])
def update_work_time():
    try:
        data = request.json
        user_id = data["user_id"]
        work_start_time = data.get("work_start_time")
        work_end_time = data.get("work_end_time")

        if not all([user_id, work_start_time, work_end_time]):
            return jsonify({'error': 'Missing required fields'}), 400
        try:
            update_work_time_for_user(user_id, work_start_time, work_end_time)
            return jsonify({'message': 'Work time updated successfully'}), 200
        except TypeError as e:
            return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run()
