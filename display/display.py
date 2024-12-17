from flask import Flask, request, jsonify, render_template, redirect, url_for
from datetime import datetime

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


project_setting = {
                'project_id': None,
                'project_name': None,
                'person_responsible': None,              
                'thermomixer_time_s': 60,
                'liquid_nitrogen_time_s': 60,
                'number_of_cycles': 20,
                'update_time': None             
                }


robot_control = {"running": False}

@app.route('/')
def home():
    return render_template('index.html', status = gripper_status)

@app.route('/settings', methods =['GET','POST'])
def settings():
    global project_setting
    if request.method == 'POST':
        project_id = request.form.get('project_id', type = str)
        project_name = request.form.get('project_name', type = str)
        person_responsible = request.form.get('person_responsible', type = str)
        thermomixer_time_s = request.form.get('thermomixer_time_s', type = int)
        liquid_nitrogen_time_s = request.form.get('liquid_nitrogen_time_s', type = int)
        number_of_cycles = request.form.get('number_of_cycles', type = int)
        if project_name is not None or person_responsible is not None or thermomixer_time_s is not None or liquid_nitrogen_time_s is not None or number_of_cycles is not None:
            if project_id is not None:
                project_setting['project_id'] = project_id
            project_setting['project_name'] = project_name
            project_setting['person_responsible'] = person_responsible
            project_setting['thermomixer_time_s'] = thermomixer_time_s
            project_setting['liquid_nitrogen_time_s'] = liquid_nitrogen_time_s
            project_setting['number_of_cycles'] = number_of_cycles
            project_setting['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return redirect(url_for('settings'))
    return render_template('settings.html', title = 'Robot Settings', settings = project_setting)


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
