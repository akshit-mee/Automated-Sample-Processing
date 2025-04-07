from pymycobot.mycobot import MyCobot
import time
import threading
import requests
import RPi.GPIO as GPIO
import numpy
import logger

mc = MyCobot("/dev/ttyAMA0", 1000000)

########################################################################
#################### Experimet Parameter ###############################
########################################################################

# Time is in seconds (minimum time 2s)
Experiment_Name = "Error_Testing"
Person_Responsible = "Akshit"
Thermomixer_Time = 5  #240 (for medium size vials)
LN2_Time = 5          #60
Waiting_Time = 5        #3
Number_of_Cycles = 30   #43 total
Run_Number = 1

Robot_speed = 100

#########################################################################
#########################################################################
#########################################################################

cobot_speed = Robot_speed

c1 = [181.0, -161.8, 210, 176.08, 0, 45.13]             #LN2 (Fully sumbersed is [181.0, -161.8, 180, 176.08, 0, 45.13])
c2 = [181.0, -161.8, 235, 176.08, 0, 45.13]             #Above LN2


cm = [152.7, -81.7, 267.2, 167.92, -3.03, 59.48]        #Between c2 and cm2 to prevent collision
cm2 = [134.4, -1.3, 298.7, 170.73, -8.85, 55.61]        #Above Water-Bath


cn = [151.1, 7.3, 238, 172.35, -6.58, 56.28]          #Water Bath [151.4, 7.7, 238.3, 172.22, -6.34, 56.17]
#an = [29.79, 20.74, -103.97, 2.1, -3.6, -116.45]
an = [29.61, 17.22, -83.93, -14.5, -4.13, -116.45]      #Water Bath !! Uee this as the adjecent solution form coordinates has different robot pose 

ce1 = [97.7, -125.6, 298.1, 167.36, -6.7, 14.91]        #Between 
ce2 = [-34.7, -145.0, 260, 172.11, -1.88, -10.06]       #Stop position after experiment to easily remove vial
ce3 = [-43.8, -104.1, 216.9, -149.82, 13.39, -4.63]





#c3 = [164.3, 35.5, 261.3, 175.61, -6.06, 68.85]
#c4 = [193.7, 54.5, 200.3, 177.28, -0.41, 66.07]
#a2 = [34.98, -14.15, -52.91, -21.18, -2.1, -121.11] # LN2
#shutdown = [-25.83, -143.17, 156.62, -146.95, 101.68, 165.14]

################################ Basic Coordinate Distance ##########################
def distance(point1, point2):
    sum = 0
    for i in range(3):
        sum = sum + (point1[i] - point2[i])**2
        #print(point1[i] - point2[i], point1[i], point2[i])
    distance = numpy.sqrt(sum) 
    # rot = point1[3]-point2[3] + point1[4]-point2[4] + point1[5]-point2[5]
    return distance   

############################ check loction error ###################################

def is_correct_position(expected_position = None, current_position = None, timeout = 5):
    
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
        distance_error = distance(expected_position, current_position)
        
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
def move(coordinate, speed = cobot_speed, mode = 1, mc = mc):
    mc.send_coords(coordinate, speed, mode)
    time.sleep(2)
    while(not is_correct_position(coordinate)):
        mc.send_coords(coordinate, speed, mode)

################################## Initialization ##############################

log = logger.setup_logger()
log.info("Starting Experiment")
log.info("Experiment Parameters")
log.info(f"Experiment Name: {Experiment_Name}")
log.info(f"Person Responsible: {Person_Responsible}")
log.info(f"Thermomixer Time: {Thermomixer_Time}")
log.info(f"Liquid Nitrogen Time: {LN2_Time}")
log.info(f"Waiting Time {Waiting_Time}")
log.info(f"Number of Cycles {Number_of_Cycles}")
log.info(f"Robot Speed {Robot_speed}")
log.info(f"Run Number {Run_Number}")

################################################################################

def run_cycle(number_of_cycles):
    for i in range(number_of_cycles):   
        move(c2)
        log.info("Moving inside LN2")
        start_ln2_time = time.monotonic()
        move(c1)
        time.sleep(LN2_Time - 2)
        end_ln2_time = time.monotonic()
        ln2_time = {start_ln2_time - end_ln2_time}
        log.info("Outside LN2")
        print(f"LN2 time = {ln2_time}")
        move(c2)
        move(cm)
        move(cm2)
        log.info("Moving Inside Water Bath")
        start_water_bath_time = time.monotonic()
        mc.send_angles(an, cobot_speed)
        time.sleep(1)
        while( not is_correct_position(cn)):
            mc.send_angles(an, cobot_speed)
        time.sleep(Thermomixer_Time -1)
        end_water_bath_time = time.monotonic()
        water_bath_time = start_water_bath_time - end_water_bath_time
        log.info("Moving outside Water Bath")
        print(f"Water Bath time = {water_bath_time}")
        move(cm2)
        move(cm)
        log.info("Waiting")
        time.sleep(Waiting_Time)
        move(c2)
        log.info(f"###################################### Cycle Completed: {i + 1} ####################################################" )
        log.info(f"LN2 Time = {ln2_time} ")
        log.info(f"Water Bath = {water_bath_time} ")
        log.info("######################################################################################################################")

#####################################################################################


def init_experiment():
    move(ce2)
    time.sleep(1)    
    move(ce1)
    time.sleep(1)

def end_experiment():
    move(ce1)
    time.sleep(1)
    move(ce2)
    time.sleep(0.5)
    move(ce3, 20)
    time.sleep(1)
    mc.release_all_servos()
    log.info ("Completed and relesed motors")

################################################################################

try:
    
    init_experiment()
    
    run_cycle(Number_of_Cycles)
    
    end_experiment()

    log.info("Operation Completed Sucessfully")

except KeyboardInterrupt:
    log.error("Experiment manually stooped with Keyboard Interrupt (crtl + c)")
    mc.stop()
    time.sleep(5)
    mc.release_all_servos()
    
except Exception as e:
    log.error(f"Experiment encountered an error: {str(e)}", exc_info = True)
    
finally:
    log.info("Programmed execution completed")
    mc.stop()
    
    
 

