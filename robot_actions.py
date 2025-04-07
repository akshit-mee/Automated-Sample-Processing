from pymycobot.mycobot import MyCobot
import time
import threading
import requests
import RPi.GPIO as GPIO
import numpy
import logger

setting_flag = 0
log = logger.setup_logger()

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

# p1 = [113.2, -65.3, -28.56, 4.04, -2.81, 57.39]
# p2 = [113.2, -27.07, -28.47, -28.3, 1.31, 68.99]
# p3 = [161.71, -30.32, -28.56, -25.92, -1.31, 129.46]
# p4 = [162.15, -63.54, -28.56, 7.2, 1.93, 136.23]

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
        self.waiting_time = 1
        # self.p1 = [113.2, -65.3, -28.56, 4.04, -2.81, 57.39] #in thermo mixer
        # self.p2 = [113.2, -27.07, -28.47, -28.3, 1.31, 68.99] #above thermo mixer
        # self.p3 = [161.71, -30.32, -28.56, -25.92, -1.31, 129.46] #above liquid nitrogen
        # self.p4 = [162.15, -63.54, -28.56, 7.2, 1.93, 136.23] #in liquid nitrogen

        self.c1 = [181.0, -161.8, 210, 176.08, 0, 45.13]             #LN2 (Fully sumbersed is [181.0, -161.8, 180, 176.08, 0, 45.13])
        self.c2 = [181.0, -161.8, 235, 176.08, 0, 45.13]             #Above LN2


        self.cm = [152.7, -81.7, 267.2, 167.92, -3.03, 59.48]        #Between c2 and cm2 to prevent collision
        self.cm2 = [134.4, -1.3, 298.7, 170.73, -8.85, 55.61]        #Above Water-Bath


        self.cn = [151.1, 7.3, 238, 172.35, -6.58, 56.28]          #Water Bath [151.4, 7.7, 238.3, 172.22, -6.34, 56.17]
        #self.an = [29.79, 20.74, -103.97, 2.1, -3.6, -116.45]
        self.an = [29.61, 17.22, -83.93, -14.5, -4.13, -116.45]      #Water Bath !! Uee this as the adjecent solution form coordinates has different robot pose 

        self.ce1 = [97.7, -125.6, 298.1, 167.36, -6.7, 14.91]        #Between 
        self.ce2 = [-34.7, -145.0, 260, 172.11, -1.88, -10.06]       #Stop position after experiment to easily remove vial
        self.ce3 = [-43.8, -104.1, 216.9, -149.82, 13.39, -4.63]
        
    def update_settings(self, settings):
        global setting_flag
        if setting_flag:
            self.thermomixer_time = settings['thermomixer_time_s']
            self.liquid_nitrogen_time = settings['liquid_nitrogen_time_s']
            self.waiting_time = settings['waiting_time_s']
            self.number_of_cycles = settings['number_of_cycles']
            print('updated')

    ################################ Basic Coordinate Distance ##########################
    def distance(self, point1, point2):
        sum = 0
        for i in range(3):
            sum = sum + (point1[i] - point2[i])**2
            #print(point1[i] - point2[i], point1[i], point2[i])
        distance = numpy.sqrt(sum) 
        # rot = point1[3]-point2[3] + point1[4]-point2[4] + point1[5]-point2[5]
        return distance   

    ############################ check loction error ###################################

    def is_correct_position(self, expected_position = None, current_position = None, timeout = 5):
        
        position_value_flag = False
        
        if current_position == None: 
            start_time = time.monotonic() 
            
            while(time.monotonic() - start_time < timeout):
                current_position = mc.get_coords()
                if len(current_position) == 6:
                    position_value_flag = True
                    break
                time.sleep(0.1)
            print(time.monotonic() - start_time)
        
        if position_value_flag:
            distance_error = self.distance(expected_position, current_position)
            
            if distance_error <= 5:
                print(f'\033[92m{current_position = }: \033[0m')
                log.info(f"Distance Error is {distance_error}")
                return True
            elif 5 < distance_error <=15:
                print(f'\033[33m{current_position = } \033[0m')
                log.warning(f"Distance Error is {distance_error}")
                return True
            else:
                print(f'\033[31m{current_position = } \033[0m')
                log.error(f"Distance Error is {distance_error}")
                log.error(f"Error Function returns {mc.get_error_information() =}")
                return False
        else:
            log.error("Timeout, cannot detect current position")
            log.error(f"Error Function returns {mc.get_error_information() =}")
            return False   
                
    ######################### move function #############################################
    def move(self, coordinate, speed = cobot_speed, mode = 1, mc = mc):
        mc.send_coords(coordinate, speed, mode)
        time.sleep(2)
        while(not self.is_correct_position(coordinate)):
            mc.send_coords(coordinate, speed, mode)


    def sample_position(self):
        pass

    def wait(self, time):
        pass

    # def pick_up_sample_from(self, location):
    #     global gripper_state
    #     if location == 'thermomixer':
    #         while mc.is_in_position(p2, 0) != 1:
    #             mc.send_angles(p2, cobot_speed)
    #         update_robot_log("Pick up Sample from Thermomixer", self.current_cycle, gripper_state)
    #         while mc.is_in_position(p1, 0) != 1:
    #             mc.send_angles(p1, cobot_speed)
    #         with gripper_lock:
    #             gripper_state = "GRIP"
    #         while mc.is_in_position(p2, 0) != 1:
    #             mc.send_angles(p2, cobot_speed)
    #     elif location == 'liquid_nitrogen':
    #         while mc.is_in_position(p3, 0) == 0:
    #             mc.send_angles(p3, cobot_speed)
    #         update_robot_log("Pick up Sample from Liquid Nitrogen", self.current_cycle, gripper_state)
    #         while mc.is_in_position(p4, 0) == 0:
    #             mc.send_angles(p4, cobot_speed)
    #         with gripper_lock:
    #             gripper_state = "GRIP"
    #         while mc.is_in_position(p3, 0) == 0:
    #             mc.send_angles(p3, cobot_speed)

    # def move_sample_to(self, location):
    #     global gripper_state
    #     if location == 'thermomixer':
            
    #         if gripper_state != "GRIP":
    #             update_robot_log("Moving Sample to Thermomixer", self.current_cycle, gripper_state, "Gripper not holding is open")
    #         else:
    #             update_robot_log("Moving Sample to Thermomixer", self.current_cycle, gripper_state)
    #         while mc.is_in_position(p2, 0) == 0:
    #             mc.send_angles(p2, cobot_speed)
            
    #     elif location == 'liquid_nitrogen':
         
    #         if gripper_state != "GRIP":
    #             update_robot_log("Moving Sample to Liquid Nitrogen", self.current_cycle, gripper_state, "Gripper not holding is open")
    #         else:             
    #             update_robot_log("Moving Sample to Liquid Nitrogen", self.current_cycle, gripper_state)
    #         while mc.is_in_position(p3, 0) == 0:
    #             mc.send_angles(p3, cobot_speed)

    # def place_sample_in(self, location):
    #     global gripper_state
    #     if location == 'thermomixer':
            
    #         while mc.is_in_position(p2, 0) == 0:
    #             mc.send_angles(p2, cobot_speed)

    #         if gripper_state != "GRIP":
    #             update_robot_log("Place Sample in Thermomixer", self.current_cycle, gripper_state, "Gripper not holding is open")
    #         else:
    #             update_robot_log("Place Sample in Thermomixer", self.current_cycle, gripper_state)
    #         while mc.is_in_position(p1, 0) == 0:
    #             mc.send_angles(p1, cobot_speed)
    #         with gripper_lock:
    #             gripper_state = "OPEN"
    #         while mc.is_in_position(p2, 0) == 0:
    #             mc.send_angles(p2, cobot_speed)
    #         with gripper_lock:
    #             gripper_state = "STOP"
            
    #     elif location == 'liquid_nitrogen':
    #         while mc.is_in_position(p3, 0) == 0:
    #             mc.send_angles(p3, cobot_speed)
    #         if gripper_state != "GRIP":
    #             update_robot_log("Place Sample in Liquid Nitrogen", self.current_cycle, gripper_state, "Gripper not holding is open")
    #         else:
    #             update_robot_log("Place Sample in Liquid Nitrogen", self.current_cycle, gripper_state)
    #         while mc.is_in_position(p4, 0) == 0:
    #             mc.send_angles(p4, cobot_speed)
    #         with gripper_lock:
    #             gripper_state = "OPEN"
    #         while mc.is_in_position(p3, 0) == 0:
    #             mc.send_angles(p3, cobot_speed)
    #         with gripper_lock:
    #             gripper_state = "STOP"

    def init_experiment(self):
        update_robot_log("Start", self.current_cycle, gripper_state, mc.get_error_information())
        self.move(self.ce2)
        time.sleep(1)    
        self.move(self.ce1)
        time.sleep(1)

    def end_experiment(self):
        # update_robot_log("End of Experiment", self.current_cycle, gripper_state)
        update_robot_log("Completed", self.current_cycle, gripper_state, mc.get_error_information())
        self.move(self.ce1)
        time.sleep(1)
        self.move(self.ce2)
        time.sleep(0.5)
        self.move(self.ce3, 20)
        time.sleep(1)
        mc.release_all_servos()
        log.info ("Completed and relesed motors")
        update_robot_log("Completed and released motors", self.current_cycle, gripper_state, mc.get_error_information())



    def run_cycle(self):

        self.init_experiment()

        while self.current_cycle-1 < self.number_of_cycles:   
            self.move(self.c2)
            update_robot_log("Moving inside LN2", self.current_cycle, gripper_state, mc.get_error_information())
            log.info("Moving inside LN2")
            start_ln2_time = time.monotonic()
            self.move(self.c1)
            time.sleep(self.liquid_nitrogen_time - 2)
            end_ln2_time = time.monotonic()
            ln2_time = {start_ln2_time - end_ln2_time}
            log.info("Outside LN2")
            print(f"LN2 time = {ln2_time}")
            update_robot_log("Outside outside LN2", self.current_cycle, gripper_state, mc.get_error_information())
            self.move(self.c2)
            update_robot_log("Moving sample to Water Bath", self.current_cycle, gripper_state, mc.get_error_information())
            self.move(self.cm)
            self.move(self.cm2)
            log.info("Moving Inside Water Bath")
            start_water_bath_time = time.monotonic()
            update_robot_log("Moving Inside Water Bath", self.current_cycle, gripper_state, mc.get_error_information())
            mc.send_angles(self.an, cobot_speed)
            time.sleep(1)
            while( not self.is_correct_position(self.cn) and time.monotonic() - start_water_bath_time < 5):
                mc.send_angles(self.an, cobot_speed)
            time.sleep(self.thermomixer_time -1)
            end_water_bath_time = time.monotonic()
            water_bath_time = start_water_bath_time - end_water_bath_time
            log.info("Moving outside Water Bath")
            print(f"Water Bath time = {water_bath_time}")
            update_robot_log("Moving outside Water Bath", self.current_cycle, gripper_state, mc.get_error_information())
            self.move(self.cm2)
            self.move(self.cm)
            log.info("Waiting")
            update_robot_log("Waiting", self.current_cycle, gripper_state, mc.get_error_information())
            time.sleep(self.waiting_time)
            update_robot_log("Moving to Liuid Nitrogen", self.current_cycle, gripper_state, mc.get_error_information())
            self.move(self.c2)
            log.info(f"###################################### Cycle Completed: {self.current_cycle} ####################################################" )
            log.info(f"LN2 Time = {ln2_time} ")
            log.info(f"Water Bath = {water_bath_time} ")
            log.info("######################################################################################################################")

        self.end_experiment()
    ################################################################################


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
            ra.run_cycle()
            if ra.cycle_number == settings['number_of_cycles']:
                cycle_number = 1
                break
            
            
        
