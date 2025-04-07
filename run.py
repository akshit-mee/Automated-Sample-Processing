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
Experiment_Name = "MLB-BQ-022-2_15cyc"
Person_Responsible = "Ben Quach"
Thermomixer_Time = 5  #240 (for medium size vials)
LN2_Time = 5          #60
Waiting_Time = 5        #3
Number_of_Cycles = 30   #43 total
Run_Number = 30

Robot_speed = 100

#########################################################################
#########################################################################

cobot_speed = Robot_speed

c1 = [181.0, -161.8, 210, 176.08, 0, 45.13]             #LN2 (Fully sumbersed is [181.0, -161.8, 180, 176.08, 0, 45.13])
c2 = [181.0, -161.8, 235, 176.08, 0, 45.13]             #Above LN2


cm = [152.7, -81.7, 267.2, 167.92, -3.03, 59.48]        #Between c2 and cm2 to prevent collision
cm2 = [134.4, -1.3, 298.7, 170.73, -8.85, 55.61]        #Above Water-Bath


cn = [151.1, 7.3, 210.7, 172.35, -6.58, 56.28]          #Water Bath [151.4, 7.7, 238.3, 172.22, -6.34, 56.17]
#an = [29.79, 20.74, -103.97, 2.1, -3.6, -116.45]
an = [29.61, 17.22, -83.93, -14.5, -4.13, -116.45]      #Water Bath !! Uee this as the adjecent solution form coordinates has different robot pose 

ce1 = [97.7, -125.6, 298.1, 167.36, -6.7, 14.91]        #Between 
ce2 = [-34.7, -145.0, 260, 172.11, -1.88, -10.06]       #Stop position after experiment to easily remove vial





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




######################### move function #############################################
def move(coordinate, speed = cobot_speed, mode = 1, mc = mc):
    mc.send_coords(coordinate, speed, 1)
    time.sleep(2)
    if mc.is_in_position(coordinate, 1):
        current = mc.get_coords()
        print(f'\033[92m{current = }: SUCESS \033[0m')
        try:
            print(distance(coordinate,mc.get_coords()))
        except:
            try:
                print(distance(coordinate,mc.get_coords()))
            except:
                print("Error")
    else:
         print(f'\033[31m{mc.get_coords() = } FALIURE \033[0m')
         
         try:
            print(distance(coordinate,mc.get_coords()))
         except:
            try:
                print(distance(coordinate,mc.get_coords()))
            except:
                print("Error")

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

################################ Basic Coordinate Distance ##########################
def distance(point1, point2):
    sum = 0
    for i in range(3):
        sum = sum + (point1[i] - point2[i])**2
        #print(point1[i] - point2[i], point1[i], point2[i])
    distance = numpy.sqrt(sum) 
    # rot = point1[3]-point2[3] + point1[4]-point2[4] + point1[5]-point2[5]
    return distance   




######################### move function #############################################
def move(coordinate, speed = cobot_speed, mode = 1, mc = mc):
    mc.send_coords(coordinate, speed, 1)
    time.sleep(2)
    if mc.is_in_position(coordinate, 1):
        current = mc.get_coords()
        print(f'\033[92m{current = }: SUCESS \033[0m')
        try:
            log.info(f"distance error {distance(coordinate,mc.get_coords())} mm")
        except:
            try:
                log.info(f"distance error {distance(coordinate,mc.get_coords())} mm")
            except:
                log.error("Error")
    else:
         print(f'\033[31m{mc.get_coords() = } \033[0m')
         
         try:
            log.info(f"distance error {distance(coordinate,mc.get_coords())} mm")
         except:
            try:
                log.info(f"distance error {distance(coordinate,mc.get_coords())} mm")
                return distance(coordinate,mc.get_coords())
            except:
                log.error("Can't calculate distance error")
    #return distance(coordinate,mc.get_coords())





try:
    
    move(ce2)
    time.sleep(1)    
    move(ce1)
    time.sleep(1)
    
    for i in range(Number_of_Cycles):   
        move(c2)
        log.info("Moving inside LN2")
        move(c1)
        time.sleep(LN2_Time - 2)
        log.info("Outside LN2")
        move(c2)
        move(cm)
        move(cm2)
        log.info("Moving Inside Water Bath")
        mc.send_angles(an, cobot_speed)
        time.sleep(1)
        log.warning("Bug, can't find distance error")
        time.sleep(Thermomixer_Time -2)
        log.info("Moving outside Water Bath")
        move(cm2)
        move(cm)
        log.info("Waiting")
        time.sleep(Waiting_Time)
        move(c2)
        log.info(f"###################################### Cycle Completed: {i + 1} ####################################################" )
    
    move(ce1)
    time.sleep(1)
    move(ce2)
    time.sleep(1)
    mc.release_all_servos()
    log.info ("Completed and relesed motors")

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
    
    
 

