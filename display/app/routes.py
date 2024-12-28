from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from datetime import datetime
from forms import ExperimentSettingForm

app = Flask(__name__)

gripper_status = {"gripper_status": "no status", "last_updated": None}

## Griper status standarized
gripper_status_posible = ['CLOSE', 'OPEN', 'STOP', ]


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



experiment_setting = {
                'experiment_id': None,
                'experiment_name': "Name of the Experiment",
                'person_responsible': None,
                'experiment_description': "Write a brief description of the experiment here (mandatory)",
                'number_of_samples': 0,            
                'thermomixer_time_s': 60,
                'liquid_nitrogen_time_s': 60,
                'number_of_cycles': 20,
                'additional_notes': "Type any additional notes here (optional)",
                'update_time': None             
                }


robot_control = {"running": False}

@app.route('/')
def home():
    return render_template('index.html', status = gripper_status)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    global experiment_setting
    form = ExperimentSettingForm()
    if form.validate_on_submit():
        experiment_setting['experiment_name'] = form.experiment_name.data
        experiment_setting['person_responsible'] = form.person_responsible.data
        experiment_setting['experiment_description'] = form.experiment_description.data
        experiment_setting['number_of_samples'] = form.number_of_samples.data
        experiment_setting['thermomixer_time_s'] = form.thermomixer_time_s.data
        experiment_setting['liquid_nitrogen_time_s'] = form.liquid_nitrogen_time_s.data
        experiment_setting['number_of_cycles'] = form.number_of_cycles.data
        experiment_setting['additional_notes'] = form.additional_notes.data
        experiment_setting['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings'))
    
    # Pre-fill form with current settings
    form.experiment_name.data = experiment_setting['experiment_name']
    form.person_responsible.data = experiment_setting['person_responsible']
    form.experiment_description.data = experiment_setting['experiment_description']
    form.number_of_samples.data = experiment_setting['number_of_samples']
    form.thermomixer_time_s.data = experiment_setting['thermomixer_time_s']
    form.liquid_nitrogen_time_s.data = experiment_setting['liquid_nitrogen_time_s']
    form.number_of_cycles.data = experiment_setting['number_of_cycles']
    form.additional_notes.data = experiment_setting['additional_notes']
    
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
    
if __name__ == "__main__":
    app.run(debug = True)
