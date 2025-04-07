from pymycobot.mycobot import MyCobot
import time
import threading
import requests
import RPi.GPIO as GPIO
import numpy

mc = MyCobot("/dev/ttyAMA0", 1000000)

cobot_speed = 100

c1 = [181.0, -161.8, 180, 176.08, 0, 45.13] #thermomixer
c2 = [181.0, -161.8, 235, 176.08, 0, 45.13]


cm = [152.7, -81.7, 267.2, 167.92, -3.03, 59.48]
cm2 = [134.4, -1.3, 298.7, 170.73, -8.85, 55.61]


c3 = [164.3, 35.5, 261.3, 175.61, -6.06, 68.85]
c4 = [193.7, 54.5, 200.3, 177.28, -0.41, 66.07] # LN2

cn = [151.1, 7.3, 210.7, 172.35, -6.58, 56.28]
an = [29.79, 20.74, -103.97, 2.1, -3.6, -116.45]

ce1 = [97.7, -125.6, 298.1, 167.36, -6.7, 14.91]
ce2 = [-34.7, -145.0, 260, 172.11, -1.88, -10.06]


a2 = [34.98, -14.15, -52.91, -21.18, -2.1, -121.11] # LN2

shutdown = [-25.83, -143.17, 156.62, -146.95, 101.68, 165.14]

time.sleep(1)


#################### Experimet Parameter ###############################
#Subtract 2s
#Thermomixer_Time = 118 ;
#LN2_Time = 28;
#Waiting_Time = 118;

Thermomixer_Time = 5 ;
LN2_Time = 2;
Waiting_Time = 5;
Number_of_Cycles = 5
#########################################################################

def distance(point1, point2):
    sum = 0
    for i in range(3):
        sum = sum + (point1[i] - point2[i])**2
        #print(point1[i] - point2[i], point1[i], point2[i])
    distance = numpy.sqrt(sum) 
    # rot = point1[3]-point2[3] + point1[4]-point2[4] + point1[5]-point2[5]
    return distance   

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

#mc.send_angles([0,0,0,0,0,0], cobot_speed)
#time.sleep(2)

for i in range(Number_of_Cycles):
    if i == 0:
        move(ce1)
        time.sleep(1)
    
    move(c2)
    move(c1)
    time.sleep(LN2_Time - 2)
    move(c2)
    move(cm)
    move(cm2)
    mc.send_angles(an, cobot_speed)
    time.sleep(1)
    time.sleep(Thermomixer_Time -2)
    move(cm2)
    move(cm)
    time.sleep(Waiting_Time)
    move(c2)
    print(f"###################### {i + 1} ######################" )
    if i == Number_of_Cycles -1:
        move(ce1)
        time.sleep(1)
        move(ce2)
        time.sleep(1)
        mc.release_all_servos()
        
    
    

try:
    for x in range(15):
        move(c2)
        move(c1)
        time.sleep(LN2_Time)  # ~2s in the move function
        move(c2)
        move(cm)
        move(cm2)
        mc.send_angles(an, cobot_speed)
        #move(c3)
        #move(c4)
        time.sleep(Thermomixer_Time)
        move(cm2)
        move(cm)
        move(c2)
        time.sleep(Waiting_Time)
        #move(c1)
        print(f'Cycle Number: {x}')
except KeyboardInterrupt:
        mc.stop()
        print("Stopped Properly if next output is 0")
        print(mc.get_error_information())
