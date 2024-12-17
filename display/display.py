from flask import Flask, request, jsonify, render_template, redirect, url_for
from datetime import datetime

app = Flask(__name__)

gripper_status = {"gripper_status": "no status", "last_updated": None}
robot_setting = {'project_name': None,
                 'person_responsible': None,              
                 'thermomixer_time_s': 60,
                 'liquid_nitrogen_time_s': 60,
                 'number_of_cycles': 20                
                }


@app.route('/')
def home():
    return render_template('index.html', status = gripper_status)

@app.route('/settings', methods =['GET','POST'])
def settings():
    global robot_setting
    if request.method == 'POST':
        project_name = request.form.get('project_name', type = str)
        person_responsible = request.form.get('person_responsible', type = str)
        thermomixer_time_s = request.form.get('thermomixer_time_s', type = int)
        liquid_nitrogen_time_s = request.form.get('liquid_nitrogen_time_s', type = int)
        number_of_cycles = request.form.get('number_of_cycles', type = int)
        if project_name is not None or person_responsible is not None or thermomixer_time_s is not None or liquid_nitrogen_time_s is not None or number_of_cycles is not None:
            robot_setting['project_name'] = project_name
            robot_setting['person_responsible'] = person_responsible
            robot_setting['thermomixer_time_s'] = thermomixer_time_s
            robot_setting['liquid_nitrogen_time_s'] = liquid_nitrogen_time_s
            robot_setting['number_of_cycles'] = number_of_cycles
        return redirect(url_for('settings'))
    return render_template('settings.html', title = 'Robot Settings', settings = robot_setting)


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
    
if __name__ == "__main__":
    app.run(debug = True)
