from pymycobot.mycobot import MyCobot
import time
import threading
import requests
import RPi.GPIO as GPIO

setting_flag = 0

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

mc = MyCobot("/dev/ttyAMA0", 1000000)

p1 = [113.2, -65.3, -28.56, 4.04, -2.81, 57.39]
p2 = [113.2, -27.07, -28.47, -28.3, 1.31, 68.99]
p3 = [161.71, -30.32, -28.56, -25.92, -1.31, 129.46]
p4 = [162.15, -63.54, -28.56, 7.2, 1.93, 136.23]

cobot_speed = 100

gripper_pin = 19 #Change for different pin for make a config file
gripper_open = 6.5 #Completle open, can change for less opening
gripper_closed = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(gripper_pin, GPIO.OUT)

pwm = GPIO.PWM(gripper_pin, 50)

gripper_state = "STOP" #Possible values "STOP" "CLOSE" "OPEN"
gripper_lock = threading.Lock()
def manage_gripper():
    global gripper_state
    pwm.start(0)
    
    try:
        while True:
            if gripper_state == "GRIP":
                pwm.ChangeDutyCycle(gripper_closed) 
            if gripper_state == "OPEN":
                pwm.ChangeDutyCycle(gripper_open) 
            if gripper_state == "STOP":
                pwm.ChangeDutyCycle(0)
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup()
        
gripper_thread = threading.Thread(target=manage_gripper, daemon = True)
gripper_thread.start()



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
    global setting_flag
    try:
        response = requests.get(display_url + "get_experiment_settings")
        print(response.status_code)
        if response.status_code == 200:
            setting_flag = 1
            return response.json()
        else:
            
            # print("Failed to get experiment settings", response.json())
            return None
    except requests.exceptions.RequestException as e:
        print("Error connecting to the server", e)
        return None
    
class RobotActions:

    global gripper_state, cobot_speed

    def __init__(self, mc):
        self.thermomixer = [0,0,0]   #add coordinates of thermomixer
        self.liquid_nitrogen = [0,0,0] #add coordinates of liquid nitrogen
        self.current_cycle = 1
        self.number_of_cycles = 1
        self.thermomixer_time = 1
        self.liquid_nitrogen_time = 1
        self.p1 = [113.2, -65.3, -28.56, 4.04, -2.81, 57.39] #in thermo mixer
        self.p2 = [113.2, -27.07, -28.47, -28.3, 1.31, 68.99] #above thermo mixer
        self.p3 = [161.71, -30.32, -28.56, -25.92, -1.31, 129.46] #above liquid nitrogen
        self.p4 = [162.15, -63.54, -28.56, 7.2, 1.93, 136.23] #in liquid nitrogen
        
    def update_settings(self, settings):
        global setting_flag
        if setting_flag:
            self.thermomixer_time = settings['thermomixer_time_s']
            self.liquid_nitrogen_time = settings['liquid_nitrogen_time_s']
            self.number_of_cycles = settings['number_of_cycles']
            print('updated')

    def sample_position(self):
        pass

    def wait(self, time):
        pass

    def pick_up_sample_from(self, location):
        global gripper_state
        if location == 'thermomixer':
            while mc.is_in_position(p2, 0) != 1:
                mc.send_angles(p2, cobot_speed)
            update_robot_log("Pick up Sample from Thermomixer", self.current_cycle, gripper_state)
            while mc.is_in_position(p1, 0) != 1:
                mc.send_angles(p1, cobot_speed)
            with gripper_lock:
                gripper_state = "GRIP"
            while mc.is_in_position(p2, 0) != 1:
                mc.send_angles(p2, cobot_speed)
        elif location == 'liquid_nitrogen':
            while mc.is_in_position(p3, 0) == 0:
                mc.send_angles(p3, cobot_speed)
            update_robot_log("Pick up Sample from Liquid Nitrogen", self.current_cycle, gripper_state)
            while mc.is_in_position(p4, 0) == 0:
                mc.send_angles(p4, cobot_speed)
            with gripper_lock:
                gripper_state = "GRIP"
            while mc.is_in_position(p3, 0) == 0:
                mc.send_angles(p3, cobot_speed)

    def move_sample_to(self, location):
        global gripper_state
        if location == 'thermomixer':
            
            if gripper_state != "GRIP":
                update_robot_log("Moving Sample to Thermomixer", self.current_cycle, gripper_state, "Gripper not holding is open")
            else:
                update_robot_log("Moving Sample to Thermomixer", self.current_cycle, gripper_state)
            while mc.is_in_position(p2, 0) == 0:
                mc.send_angles(p2, cobot_speed)
            
        elif location == 'liquid_nitrogen':
         
            if gripper_state != "GRIP":
                update_robot_log("Moving Sample to Liquid Nitrogen", self.current_cycle, gripper_state, "Gripper not holding is open")
            else:             
                update_robot_log("Moving Sample to Liquid Nitrogen", self.current_cycle, gripper_state)
            while mc.is_in_position(p3, 0) == 0:
                mc.send_angles(p3, cobot_speed)

    def place_sample_in(self, location):
        global gripper_state
        if location == 'thermomixer':
            
            while mc.is_in_position(p2, 0) == 0:
                mc.send_angles(p2, cobot_speed)

            if gripper_state != "GRIP":
                update_robot_log("Place Sample in Thermomixer", self.current_cycle, gripper_state, "Gripper not holding is open")
            else:
                update_robot_log("Place Sample in Thermomixer", self.current_cycle, gripper_state)
            while mc.is_in_position(p1, 0) == 0:
                mc.send_angles(p1, cobot_speed)
            with gripper_lock:
                gripper_state = "OPEN"
            while mc.is_in_position(p2, 0) == 0:
                mc.send_angles(p2, cobot_speed)
            with gripper_lock:
                gripper_state = "STOP"
            
        elif location == 'liquid_nitrogen':
            while mc.is_in_position(p3, 0) == 0:
                mc.send_angles(p3, cobot_speed)
            if gripper_state != "GRIP":
                update_robot_log("Place Sample in Liquid Nitrogen", self.current_cycle, gripper_state, "Gripper not holding is open")
            else:
                update_robot_log("Place Sample in Liquid Nitrogen", self.current_cycle, gripper_state)
            while mc.is_in_position(p4, 0) == 0:
                mc.send_angles(p4, cobot_speed)
            with gripper_lock:
                gripper_state = "OPEN"
            while mc.is_in_position(p3, 0) == 0:
                mc.send_angles(p3, cobot_speed)
            with gripper_lock:
                gripper_state = "STOP"

    def complete(self):
        pass

    def stop(self):
        pass

    def cycle(self):
        while self.current_cycle-1 < self.number_of_cycles:
            self.wait(self.thermomixer_time)
            print(1)
            self.pick_up_sample_from('thermomixer')
            print(2)
            self.move_sample_to('liquid_nitrogen')
            print(3)
            self.place_sample_in('liquid_nitrogen')
            print(4)
            self.wait('liquid_nitrogen_time')
            print(5)            
            self.pick_up_sample_from('liquid_nitrogen')
            print(6)
            self.move_sample_to('thermomixer')
            print(7)
            self.place_sample_in('thermomixer')
            print(8)
            self.current_cycle += 1
        self.complete()
        
if __name__ == "__main__":
    settings = get_experiment_settings()
    ra = RobotActions(mc)
    while True:
        controll = get_robot_control()
        settings = get_experiment_settings()
        ra.update_settings(settings)
        ra.current_cycle = 1
        print(ra.current_cycle)
        print(ra.number_of_cycles)        
        
        while controll['running'] and setting_flag:
            ra.cycle()
            
        
