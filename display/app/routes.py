from flask import request, jsonify, render_template, redirect, url_for, flash
from app import app, db
from datetime import datetime, timedelta
from app.forms import ExperimentSettingForm
from app.models import ExperimentSetting, RobotLog

gripper_status = {"gripper_status": "no status", "last_updated": None}

## Griper status standarized
gripper_status_posible = ['CLOSE', 'OPEN', 'STOP', ]


current_experiment_id = None
current_robot_log_id = None

robot_log = {
            "project_id": None,
            "project_name": None,
            "action_start": None,
            "cycle_number": None,
            "gripper_status": None,
            "time_stamp": None,
            "error": None
}

## robot actions standarized
robot_actions = ['Innitial Setting Updated',
                 'Wainting', 
                 'Place Sample in Thermomixer', 
                 'Place Sample in Liquid Nitrogen', 
                 'Pick up Sample from Thermomixer', 
                 'Pick up Sample from Liquid Nitrogen',
                 'Moving Sample to Thermomixer', 
                 'Moving Sample to Liquid Nitrogen'
                 'Completed'
                 'Stopped by User'
                 'Restarted by User']

robot_control = {"running": False}

@app.route('/')
def home():
    settings = None
    robot_log = None
    time_difference = None
    if current_experiment_id != None:
        settings = ExperimentSetting.query.get(current_experiment_id)
    if current_robot_log_id != None:
        robot_log = RobotLog.query.get(current_robot_log_id)
        if robot_log and robot_log.time_stamp:
            time_difference = datetime.now() - robot_log.time_stamp
    return render_template('index.html', status=gripper_status, settings=settings, robot_logs=robot_log, time_difference=time_difference)

@app.route('/start', methods=['GET', 'POST'])
def start():

    global current_experiment_id, current_robot_log_id, robot_control
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
                experiment_name=settings.experiment_name,
                action_start="Start",
                cycle_number=0,
                time_stamp=datetime.now(),
                experiment_setting=settings
            )
            db.session.add(log)
            db.session.commit()
            current_experiment_id = settings.experiment_id
            current_robot_log_id = log.id
            robot_control['running'] = True
            flash('Experiment started successfully!', 'success')
        
        return redirect(url_for('home'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    global experiment_setting
    form = ExperimentSettingForm()
    if form.validate_on_submit():
        experiment = ExperimentSetting(
            experiment_name=form.experiment_name.data,
            person_responsible=form.person_responsible.data,
            experiment_description=form.experiment_description.data,
            number_of_samples=form.number_of_samples.data,
            thermomixer_time_s=form.thermomixer_time_s.data,
            liquid_nitrogen_time_s=form.liquid_nitrogen_time_s.data,
            number_of_cycles=form.number_of_cycles.data,
            additional_notes=form.additional_notes.data,
            update_time=datetime.now()
        )
        db.session.add(experiment)
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', title='Robot Settings', form=form)

@app.route('/update_status', methods=['POST'])
def update_status():
    global gripper_staus
    data = request.get_json()
    if not data or 'gripper_status' not in data:
        return jsonify({"error": "Invalid data"}), 400
        
    gripper_status["gripper_status"] = data["gripper_status"]
    gripper_status["last_updated"] = data.get('timestamp')
    return jsonify({"message": "Status updated sucessfully"}), 200
    
@app.route('/get_status', methods=['GET'])
def get_status():
    return jsonify(gripper_status), 200

@app.route('/control', methods=['GET', 'POST'])
def control():
    return render_template('control.html', robot_control = robot_control)

@app.route('/control_robot', methods=['POST'])
def control_robot():
    global robot_control
    action = request.form.get('action')
    if action == 'start':
        robot_control['running'] = True
    if action == 'stop':
        robot_control['running'] = False
    return redirect(url_for('control'))

@app.route('/view_experiment_settings', methods=['GET'])
def view_experiment_settings():
    experiment_settings = ExperimentSetting.query.all()
    robot_logs = RobotLog.query.all()
    return render_template('view_experiment_settings.html', experiment_settings=experiment_settings, robot_logs=robot_logs)
    
if __name__ == "__main__":
    app.run(debug = True)
