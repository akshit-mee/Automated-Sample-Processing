import time
import threading
import requests

display_url = "http://127.0.0.1:5000/"

def update_robot_log(action, cycle_number, gripper_status, error=None):
    message = {
        "action": action,
        "cycle_number": cycle_number,
        "error": error,
        "gripper_status": gripper_status
    }
    print(action)
    print(cycle_number)
    try:
        response = requests.post(display_url + "update_robot_log", json=message)
        if response.status_code == 200:
            print("Robot log updated successfully")
        else:
            print("Failed to update robot log", response.json())
    except requests.exceptions.RequestException as e:
        print("Error connecting to the server", e)

def get_robot_control():
    try:
        response = requests.get(display_url + "get_robot_control")
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to get robot control", response.json())
            return None
    except requests.exceptions.RequestException as e:
        print("Error connecting to the server", e)
        return None

def get_experiment_settings():
    try:
        response = requests.get(display_url + "get_experiment_settings")
        print(response.status_code)
        if response.status_code == 200:
            return response.json()
        else:
            
            # print("Failed to get experiment settings", response.json())
            return None
    except requests.exceptions.RequestException as e:
        print("Error connecting to the server", e)
        return None

# Example usage
if __name__ == "__main__":
    settings = get_experiment_settings()
    cycle_number = 1

    while True:
        control = get_robot_control()
        settings = get_experiment_settings()
        while control['running'] and settings is not None and cycle_number-1 < settings['number_of_cycles']:
            update_robot_log("Pich up Sample from Thermomixer", cycle_number, "GRIP")
            time.sleep(1)
            update_robot_log("Move Sample to Liquid Nitrogen", cycle_number, "GRIP")
            time.sleep(1)
            update_robot_log("Place Sample in Liquid Nitrogen", cycle_number, "OPEN")
            time.sleep(1)
            update_robot_log("Pick up Sample from Liquid Nitrogen", cycle_number, "GRIP")
            time.sleep(1)
            update_robot_log("Move Sample to Thermomixer", cycle_number, "GRIP")
            time.sleep(1)
            update_robot_log("Place Sample in Thermomixer", cycle_number, "OPEN")
            time.sleep(1)
            if cycle_number == settings['number_of_cycles']:
                update_robot_log("Completed", cycle_number, "OPEN")
                break
            cycle_number += 1
    time.sleep(2)

        

