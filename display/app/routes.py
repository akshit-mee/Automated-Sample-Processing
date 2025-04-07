from flask import request, jsonify, render_template, redirect, url_for, flash, send_file
from app import app, db
from datetime import datetime, timedelta
from app.forms import ExperimentSettingForm
from app.models import ExperimentSetting, RobotLog, ExperimentCompleted, CurrentActive
import json
import os

gripper_status = {"gripper_status": "no status", "last_updated": None}



current_experiment_id = None
experiment_start_robot_log_id = None
current_robot_log_id = None
experiment_end_robot_log_id = None
update_flag = False
robot_control = {"running": False}


robot_log = {
            "project_id": None,
            "project_name": None,
            "action_start": None,
            "cycle_number": None,
            "gripper_status": None,
            "time_stamp": None,
            "error": None
}

@app.route('/')
def home():
    settings = None
    current_robot_log = None
    time_difference = None
    global robot_control, current_experiment_id, current_robot_log_id, experiment_end_robot_log_id, experiment_start_robot_log_id
    
    if current_experiment_id is not None:
        settings = ExperimentSetting.query.get(current_experiment_id)
    if current_robot_log_id is not None:
        experiment_end_robot_log_id = current_robot_log_id
        current_robot_log = RobotLog.query.get(current_robot_log_id)
        if current_robot_log and current_robot_log.time_stamp:
            time_difference = datetime.now() - current_robot_log.time_stamp
    return render_template('index.html', settings=settings, robot_logs=current_robot_log, time_difference=time_difference, running_status = robot_control['running'])


@app.route('/download_experiment_data', methods=['GET'])
def download_experiment_data():
    global current_experiment_id, experiment_start_robot_log_id, experiment_end_robot_log_id

    if current_experiment_id is None or experiment_start_robot_log_id is None or experiment_end_robot_log_id is None:
        flash('No experiment data available for download.', 'error')
        return redirect(url_for('home'))

    settings = ExperimentSetting.query.get(current_experiment_id)
    logs = RobotLog.query.filter(RobotLog.id.between(experiment_start_robot_log_id, experiment_end_robot_log_id)).all()

    data = {
        'settings': settings.to_dict(),
        'logs': [log.to_dict() for log in logs]
    }

    file_path = f'/tmp/experiment_{settings.experiment_id}_{settings.experiment_name}_data.json'
    with open(file_path, 'w') as f:
        json.dump(data, f)

    return send_file(file_path, as_attachment=True, download_name=f'experiment_{settings.experiment_id}_{settings.experiment_name}_data.json')

##################################################
@app.route('/robot_status', methods=['GET', 'POST'])
def robot_status():
    # gripper and robot_contoller threads active?
    # robot on
    # controller connected
    # test gripper
    # modify gripper open and close
    # robot home position
    # safe shut down

    robot_status.power = True
    robot_status.connected = True
    robot_status.error = False


    return render_template('robot_status.html', robot_status=robot_status)

##################################################
@app.route('/help', methods=['GET', 'POST'])
def help():

    return render_template('help.html')


##################################################
@app.route('/start', methods=['GET', 'POST'])
def start():

    global current_experiment_id, current_robot_log_id, robot_control, experiment_start_robot_log_id
    if request.method == 'GET':
        search_query = request.args.get('search')
        selected_project_id = request.args.get('project')
        settings = None

        if search_query:
            settings = ExperimentSetting.query.filter(
                (ExperimentSetting.experiment_id == search_query) | 
                (ExperimentSetting.experiment_name.ilike(f"%{search_query}%"))
            ).first()
        elif selected_project_id:
            settings = ExperimentSetting.query.get(selected_project_id)
        
        projects = ExperimentSetting.query.all()
        return render_template('start.html', projects=projects, settings=settings)
    
    elif request.method == 'POST':
        action = request.form.get('action')
        experiment_id = request.form.get('experiment_id')
        settings = ExperimentSetting.query.get(experiment_id)
        
        if action == "Start" and settings:
            log = RobotLog(
                experiment_id=settings.experiment_id,
                # experiment_name=settings.experiment_name,
                action_start="Start",
                cycle_number=0,
                time_stamp=datetime.now(),
                experiment_setting=settings
            )            
            db.session.add(log)
            cur_active = CurrentActive(
                id = 1,
                experiment_id=settings.experiment_id,
                # experiment_name=settings.experiment_name,
                robotlog_id=log.id,
                cycle_number=0
            )
            db.session.add(cur_active)
            db.session.commit()
 

            experiment_start_robot_log_id = log.id
            current_experiment_id = settings.experiment_id
            current_robot_log_id = log.id
            robot_control['running'] = True
            flash('Experiment started successfully!', 'success')
        
        return redirect(url_for('home'))


##################################################
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    form = ExperimentSettingForm()
    if form.validate_on_submit():
        experiment = ExperimentSetting(
            experiment_name=form.experiment_name.data,
            person_responsible=form.person_responsible.data,
            experiment_description=form.experiment_description.data,
            number_of_samples=form.number_of_samples.data,
            thermomixer_time_s=form.thermomixer_time_s.data,
            liquid_nitrogen_time_s=form.liquid_nitrogen_time_s.data,
            waiting_time_s=form.waiting_time_s.data,
            number_of_cycles=form.number_of_cycles.data,
            additional_notes=form.additional_notes.data,
            update_time=datetime.now()
        )
        db.session.add(experiment)
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', title='Robot Settings', form=form)


##################################################
@app.route('/control', methods=['GET', 'POST'])
def control():
    return render_template('control.html', robot_control = robot_control)


##################################################
@app.route('/view_experiment_settings', methods=['GET'])
def view_experiment_settings():
    experiment_settings = ExperimentSetting.query.all()
    return render_template('view_experiment_settings.html', experiment_settings=experiment_settings)


##################################################
@app.route('/view_robot_logs', methods=['GET'])
def view_robot_logs():
    robot_logs = RobotLog.query.all()
    return render_template('view_robot_logs.html', robot_logs=robot_logs)

@app.route('/view_completed_experiments', methods=['GET'])
def view_completed_experiments():
    completed_experiments = ExperimentCompleted.query.all()
    return render_template('view_completed_experiments.html', completed_experiments=completed_experiments)

@app.route('/view_completed_experiments/<int:experiment_id>', methods=['GET'])
def show_completed_experiment(experiment_id):
    completed_experiment = ExperimentCompleted.query.get(experiment_id)
    if not completed_experiment:
        flash('Completed experiment not found.', 'error')
        return redirect(url_for('view_completed_experiments'))
    
    logs = RobotLog.query.filter(RobotLog.id.between(completed_experiment.Robot_log_start_id, completed_experiment.Robot_log_end_id)).all()
    return render_template('completed_expriment.html', log=logs)

# @app.route('/download_completed_data', methods=['GET'])
# def download_experiment_data():
    
#     if current_experiment_id is None or experiment_start_robot_log_id is None or experiment_end_robot_log_id is None:
#         flash('No experiment data available for download.', 'error')
#         return redirect(url_for('home'))

#     settings = ExperimentSetting.query.get(current_experiment_id)
#     logs = RobotLog.query.filter(RobotLog.id.between(experiment_start_robot_log_id, experiment_end_robot_log_id)).all()

#     data = {
#         'settings': settings.to_dict(),
#         'logs': [log.to_dict() for log in logs]
#     }

#     file_path = f'/tmp/experiment_{settings.experiment_id}_{settings.experiment_name}_data.json'
#     with open(file_path, 'w') as f:
#         json.dump(data, f)

#     return send_file(file_path, as_attachment=True, download_name=f'experiment_{settings.experiment_id}_{settings.experiment_name}_data.json')
 

e = ExperimentCompleted(experiment_id = 11, experiment_name = 'New Experiment', start_time = datetime.strptime('2025-01-10 12:00:37.553810', "%Y-%m-%d %H:%M:%S.%f"), end_time = datetime.strptime('2025-01-10 12:00:56.789757', "%Y-%m-%d %H:%M:%S.%f"), Robot_log_start_id = 536, Robot_log_end_id = 555, post_experiment_notes = 'completed sucessfully')

##################################################
@app.route('/contact')
def contact():
    contacts = [
        {"name": "Akshit Gupta, B. Tech.", "email": "gupta@dwi.rwth-aachen.de", "room": "Technikum"},
        {"name": "Till Hülsmann, M.Sc", "email": "huelsmann@dwi.rwth-aachen.de", "room": "B3.56"},
        {"name": "Johannes Hahmann, M.Sc.", "email": "hahmann@dwi.rwth-aachen.de", "room": "A0.14|0.18"}
    ]
    return render_template('contact.html', contacts=contacts)

if __name__ == "__main__":
    app.run(debug = True)

############################################################################################################

# @app.route('/update_status', methods=['POST'])
# def update_status():
#     global gripper_status
#     data = request.get_json()
#     if not data or 'gripper_status' not in data:
#         return jsonify({"error": "Invalid data"}), 400
        
#     gripper_status["gripper_status"] = data["gripper_status"]
#     gripper_status["last_updated"] = data.get('timestamp')
#     return jsonify({"message": "Status updated successfully"}), 200
    
# @app.route('/get_status', methods=['GET'])
# def get_status():
#     return jsonify(gripper_status), 200


@app.route('/control_robot', methods=['POST'])
def control_robot():
    global robot_control
    action = request.form.get('action')
    if action == 'start':
        robot_control['running'] = True
    if action == 'stop':
        robot_control['running'] = False
        
    return redirect(url_for('home'))


@app.route('/update_robot_log', methods=['POST'])
def update_robot_log():
    global current_experiment_id, current_robot_log_id, update_flag
    data = request.get_json()
    if not data or 'action' not in data or 'cycle_number' not in data or 'gripper_status' not in data:
        return jsonify({"error": "Invalid data"}), 400

    log = RobotLog(
        experiment_id=current_experiment_id,
        # experiment_name=ExperimentSetting.query.get(current_experiment_id).experiment_name,
        action_start=data["action"],
        cycle_number=data["cycle_number"],
        gripper_status=data["gripper_status"],
        time_stamp=datetime.now(),
        error=data.get("error")
    )
    db.session.add(log)
    db.session.commit()
    current_robot_log_id = log.id
    update_flag = True
    if data["action"] == "Completed":
        robot_control['running'] = False
    return jsonify({"message": "Robot log updated successfully"}), 200

@app.route('/update_process_details', methods=['POST'])
def update_process_details():
    global current_robot_log_id, experiment_end_robot_log_id
    process_details = request.form.get('process_details')
    if not process_details:
        process_details = "No details provided"
    experiment_end_robot_log_id = current_robot_log_id
    if current_robot_log_id is not None:
        log = RobotLog.query.get(current_robot_log_id)
        if log:
            log.action_start = "Completed: details - " + process_details
            db.session.commit()
            flash('Process details updated successfully!', 'success')
    return redirect(url_for('home'))


@app.route('/get_robot_control', methods=['GET'])
def get_robot_control():
    return jsonify(robot_control), 200

@app.route('/get_experiment_settings', methods=['GET'])
def get_experiment_settings():
    global current_experiment_id
    if current_experiment_id is not None:
        settings = ExperimentSetting.query.get(current_experiment_id)
        return jsonify(settings.to_dict()), 200
    return jsonify({"error": "No experiment settings found"}), 404


@app.route("/status_page_update")
def status_page_update():
    global update_flag
    response = {"reload": update_flag}
    update_flag = False
    return jsonify(response)


