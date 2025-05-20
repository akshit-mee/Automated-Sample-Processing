from pymycobot.mycobot import MyCobot
import time
import threading
import requests
import RPi.GPIO as GPIO
import numpy
import logger

setting_flag = 0
log = logger.setup_logger()
log.info("Starting Robot Actions")

class StopCycleException(Exception):
    pass

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
cobot_speed = 100



###################################################################################################################################################
######################################################## GRIPPER ##################################################################################
###################################################################################################################################################


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

###################################################################################################################################################

display_url = "http://0.0.0.0:8000/"

def update_robot_log(action, cycle_number, gripper_status, error=None):
    message = {
        "action": action,
        "cycle_number": cycle_number,
        "error": error,
        "gripper_status": gripper_status
    }
    try:
        response = requests.post(display_url + "update_robot_log", json=message)
        if response.status_code == 200:
            log.info("Robot log updated successfully")
        else:
            log.info("Failed to update robot log", response.json())
    except requests.exceptions.RequestException as e:
        log.info("Error connecting to the server", e)


get_robot_control_flag_1 = False
get_robot_control_flag_2 = False
get_robot_control_flag_3 = False

def get_robot_control():
    global get_robot_control_flag_1, get_robot_control_flag_2, get_robot_control_flag_3
    try:
        response = requests.get(display_url + "get_robot_control")
        if response.status_code == 200:
            get_robot_control_flag_1 = True
            get_robot_control_flag_2 = True
            if not get_robot_control_flag_3:
                log.info("Robot control retrieved successfully")
                get_robot_control_flag_3 = True
            return response.json()
        else:
            log.info("Failed to get robot control", response.json())
            get_robot_control_flag_2 = True
            get_robot_control_flag_3 = True
            if not get_robot_control_flag_1:
                log.info("Failed to get robot control", response.json())
                get_robot_control_flag_1 = True
            return None
    except requests.exceptions.RequestException as e:
        get_robot_control_flag_1 = True
        get_robot_control_flag_3 = True
        if not get_robot_control_flag_2:
            log.info("Error connecting to the server", e)
            get_robot_control_flag_2 = True
        return None

get_experiment_settings_flag_1 = False
get_experiment_settings_flag_2 = False

def get_experiment_settings():
    global setting_flag, get_experiment_settings_flag_1, get_experiment_settings_flag_2
    try:
        response = requests.get(display_url + "get_experiment_settings")
        if response.status_code == 200:
            setting_flag = 1
            return response.json()
        else:
            if not get_experiment_settings_flag_1:
                log.info("Failed to get experiment settings", response.json())
                get_experiment_settings_flag_1 = True
            return None
    except requests.exceptions.RequestException as e:
        if not get_experiment_settings_flag_2:
            log.info("Error connecting to the server", e)
            get_experiment_settings_flag_2 = True
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

        self.c1 = [-18.0, -207.0, 210.0, -175.0, -5.0, -144.08]             #LN2 (Fully sumbersed is [181.0, -161.8, 180, 176.08, 0, 45.13])
        self.c2 = [-2.7, -206.6, 253.6, -175.6, -5.0, -144.88]            #Above LN2
        self.a2 = [-70.92, -27.24, -19.59, -41.39, -6.5, 45.35]
        
        self.c3 = [205.2, -16.0, 260, 178.65, -6.81, -64.68]
        self.c4 = [205.2, -16.0, 215, 180.0, 0.0, -64.68]
        self.a4 = [15.11, -11.42, -71.1, -3.51, -5.71, -10.81]

        self.cm = [103.0, -24.2, 286.2, 175.16, -2.62, -20.54]
        self.cr = [104.0, 187.1, 245.3, -175.69, -0.98, -52.58]   
        # self.cm2 = [134.4, -1.3, 298.7, 170.73, -8.85, 55.61]        #Above Water-Bath

        
    def update_settings(self, settings):
        global setting_flag
        if setting_flag:
            self.thermomixer_time = settings['thermomixer_time_s']
            self.liquid_nitrogen_time = settings['liquid_nitrogen_time_s']
            self.waiting_time = settings['waiting_time_s']
            self.number_of_cycles = settings['number_of_cycles']
            log.info('Updated settings')
            log.info(f"Thermomixer time: {self.thermomixer_time}")
            log.info(f"Liquid Nitrogen time: {self.liquid_nitrogen_time}")
            log.info(f"Waiting time: {self.waiting_time}")
            log.info(f"Number of cycles: {self.number_of_cycles}")

    ################################ Basic Coordinate Distance ##########################
    def distance(self, point1, point2):
        sum = 0
        for i in range(3):
            sum = sum + (point1[i] - point2[i])**2
        distance = numpy.sqrt(sum)
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
        
        if position_value_flag:
            distance_error = self.distance(expected_position, current_position)
            
            if distance_error <= 10:
                #print(f'\033[92m{current_position = }: \033[0m')
                log.info(f"Distance Error is {distance_error}")
                return True
            elif 10 < distance_error <=15:
                #print(f'\033[33m{current_position = } \033[0m')
                log.info(f"Distance Error is {distance_error}")
                return True
            else:
                #print(f'\033[31m{current_position = } \033[0m')
                log.error(f"Distance Error is {distance_error}")
                log.error(f"Error Function returns {mc.get_error_information() =}")
                return False
        else:
            log.error("Timeout, cannot detect current position")
            log.error(f"Error Function returns {mc.get_error_information() =}")
            return False   
                
    ######################### move function #############################################
    def move(self, coordinate, speed = cobot_speed, mode = 1, mc = mc, exception = True):
        mc.send_coords(coordinate, speed, mode)
        if exception:
            self.delay(2)
        if not exception:
            time.sleep(2)
        while(not self.is_correct_position(coordinate)):
            mc.send_coords(coordinate, speed, mode)


    def sample_position(self):
        pass

    def wait(self, time):
        pass
    
        
    def _check_staus(self):
        control = get_robot_control()
        if not control['running']:
            log.info("Stopping cycle, Raising Exception")
            raise StopCycleException("Stopped Manually using Webapp")
        
    
    def delay(self, delay, interval = 0.2):
        start_time = time.monotonic()
        while (time.monotonic() - start_time) < delay:
            self._check_staus()
            time.sleep(interval)
            
    def init_experiment(self):
        update_robot_log("Start", self.current_cycle, gripper_state, mc.get_error_information())
        self.move(self.cr)    
        self.move(self.cm)

    def end_experiment(self):
        # update_robot_log("End of Experiment", self.current_cycle, gripper_state)
        update_robot_log("Completed", self.current_cycle-1, gripper_state, mc.get_error_information())
        self.move(self.cm)
        self.move(self.cr)
        mc.release_all_servos()
        time.sleep(0.5)
        mc.release_all_servos()
        log.info ("Completed and relesed motors")
        
    def closest_point(self, position = mc.get_coords()):
        d1 = self.distance(position, self.c2)
        d2 = self.distance(position, self.c3)
        d3 = self.distance(position, self.cr)
    
        if d1 <= d2 and d1 <= d3:
            return self.c2
        
        if d2 <= d3 and d2 <= d1:
            return self.c3
    
        if d3 <= d1 and d3 <= d1:
            return self.cr
    
    def manual_stop(self, timeout = 5):
        
        close_point = None
        position_value_flag = False
        start_time = time.monotonic() 
        
        update_robot_log("Manually Stopped", self.current_cycle-1, gripper_state, mc.get_error_information())
        
        while(time.monotonic() - start_time) < timeout:
            current_position = mc.get_coords()
            if len(current_position) == 6:
                position_value_flag = True
                break
            time.sleep(0.1)
        #print(time.monotonic() - start_time)
        
        if position_value_flag:
            close_point = self.closest_point(current_position)
            log.info(f"Currently at {current_position}")
            log.info(f"Moving to {close_point}")
            self.move(close_point, cobot_speed, 1, mc, False)
            if close_point != self.cr:
                self.move(self.cm, cobot_speed, 1, mc, False)
            log.info("Moving to rest position")
            self.move(self.cr,cobot_speed, 1, mc, False)
            log.info("releasing all servos")
            mc.release_all_servos()
            time.sleep(0.5)
            mc.release_all_servos()
            update_robot_log("Completed", self.current_cycle-1, gripper_state, mc.get_error_information())
        
        else:
            log.error("Timeout, cannot detect current position")
            log.error(f"Error Function returns {mc.get_error_information() =}")
            update_robot_log("Error: Can't return to home", self.current_cycle-1, gripper_state, mc.get_error_information())
            update_robot_log("Completed", self.current_cycle-1, gripper_state, mc.get_error_information())


    def run_cycle(self):
        
        while self.current_cycle-1 < self.number_of_cycles:
            mc.send_angles(self.a2, 100)
            self.delay(1)
            update_robot_log("Moving to Liuid Nitrogen", self.current_cycle, gripper_state, mc.get_error_information())   
            self.move(self.c2)          #Lower Speed to prevent splashing
            update_robot_log("Moving inside LN2", self.current_cycle, gripper_state, mc.get_error_information())
            log.info("Moving inside LN2")
            start_ln2_time = time.monotonic()
            self.move(self.c1, 30)
            self.delay(self.liquid_nitrogen_time - 2)
            end_ln2_time = time.monotonic()
            ln2_time = {start_ln2_time - end_ln2_time}
            log.info("Outside LN2")
            # print(f"LN2 time = {ln2_time}")
            update_robot_log("Outside outside LN2", self.current_cycle, gripper_state, mc.get_error_information())
            self.move(self.c2)
            update_robot_log("Moving sample to Water Bath", self.current_cycle, gripper_state, mc.get_error_information())
            self.move(self.c3)
            log.info("Moving Inside Water Bath")
            start_water_bath_time = time.monotonic()
            update_robot_log("Moving Inside Water Bath", self.current_cycle, gripper_state, mc.get_error_information())
            self.move(self.c4)
            self.delay(self.thermomixer_time -2)
            end_water_bath_time = time.monotonic()
            water_bath_time = start_water_bath_time - end_water_bath_time
            log.info("Moving outside Water Bath")
            # print(f"Water Bath time = {water_bath_time}")
            update_robot_log("Moving outside Water Bath", self.current_cycle, gripper_state, mc.get_error_information())
            self.move(self.c3)
            log.info("Waiting")
            update_robot_log("Waiting", self.current_cycle, gripper_state, mc.get_error_information())
            self.delay(self.waiting_time)
            log.info(f"###################################### Cycle Completed: {self.current_cycle} ####################################################" )
            log.info(f"LN2 Time = {ln2_time} ")
            log.info(f"Water Bath = {water_bath_time} ")
            log.info("######################################################################################################################")
            self.current_cycle += 1
            
        self.end_experiment()
    ################################################################################


    def complete(self):
        pass

    def stop(self):
        pass

        
if __name__ == "__main__":
    
    ra = RobotActions(mc)
    settings_old = get_experiment_settings()
    settings = get_experiment_settings()
    
    while True:
        controll = get_robot_control()
        if settings_old != settings:
            settings_old = settings
            settings = get_experiment_settings()
            ra.update_settings(settings)
            ra.current_cycle = 1       
        
        while controll['running'] and setting_flag:
            ra.init_experiment()
            try:
                ra.run_cycle()
            except StopCycleException:
                ra.manual_stop()
            ra.complete()
            break
            
            
        
