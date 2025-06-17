from pymycobot.mycobot import MyCobot
import time
import threading
import requests
import RPi.GPIO as GPIO
import numpy
import logger

mc = MyCobot("/dev/ttyAMA0", 1000000)

log = logger.setup_logger()
Robot_speed = 100
cobot_speed = Robot_speed

c1 = [-18.0, -207.0, 210.0, -179.76, -9.14, -144.08]            #LN2 (Fully sumbersed is [181.0, -161.8, 180, 176.08, 0, 45.13])
c2 = [-2.7, -206.6, 253.6, -172.6, -2.29, 153.88]
a2 = [-70.92, -27.24, -19.59, -41.39, -6.5, 45.35]            #Above LN2

c3 = [205.2, -16.0, 260, 178.65, -6.81, -64.68]
c4 = [205.2, -16.0, 215, 178.65, -6.81, -64.68]


cm = [103.0, -24.2, 286.2, 175.16, -2.62, -20.54]
cr = [104.0, 187.1, 245.3, -175.69, -0.98, -52.58]

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


def closest_point(position = mc.get_coords()):
    d1 = distance(position, c2)
    d2 = distance(position, c3)
    d3 = distance(position, cr)
    
    if d1 <= d2 and d1 <= d3:
        return c2
        
    if d2 <= d3 and d2 <= d1:
        return c3
    
    if d3 <= d1 and d3 <= d1:
        return cr
        
def move_to_rest(timeout = 5):
    
    close_point = None
    position_value_flag = False
    start_time = time.monotonic() 
        
    while(time.monotonic() - start_time < timeout):
        current_position = mc.get_coords()
        if len(current_position) == 6:
            position_value_flag = True
            break
        time.sleep(0.1)
    print(time.monotonic() - start_time)
        
    if position_value_flag:
        print(current_position)
        print(closest_point(current_position))
        close_point = closest_point(current_position)
        
        move(close_point)
        if close_point != cr:
            move(cm)
        log.info("Moving to rest position")
        move(cr)
        log.info("releasing all servos")
        mc.release_all_servos()
        time.sleep(0.5)
        mc.release_all_servos()
        
    else:
        log.error("Timeout, cannot detect current position")
        log.error(f"Error Function returns {mc.get_error_information() =}")
        
move_to_rest()

