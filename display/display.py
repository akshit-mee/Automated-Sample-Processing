from flask import Flask, request, jsonify

app = Flask(__name__)

gripper_status = {"gripper_status": "no status", "last_updated": None}

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
