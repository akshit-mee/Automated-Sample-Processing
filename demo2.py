from pymycobot.mycobot import MyCobot
import time
import threading
import requests
import RPi.GPIO as GPIO

####################Innitialization ##################
mc = MyCobot("/dev/ttyAMA0", 1000000)

# p1 = [113.2, -65.3, -28.56, 4.04, -2.81, 57.39]
p1 = [112.76, -65.12, -29.09, -0.17, -3.86, 80.77]
p2 = [113.2, -27.07, -28.47, -28.3, 1.31, 68.99]
p3 = [161.71, -30.32, -28.56, -25.92, -1.31, 129.46]
# p4 = [162.15, -63.54, -28.56, 7.2, 1.93, 136.23]
p4 = [167.34, -69.59, -28.56, 11.68, 2.37, 132.53]

cobot_speed = 70

gripper_pin = 19 #Change for different pin for make a config file
gripper_open = 2 #Completle open, can change for less opening
gripper_closed = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(gripper_pin, GPIO.OUT)

pwm = GPIO.PWM(gripper_pin, 50)

gripper_state = "STOP" #Possible values "STOP" "CLOSE" "OPEN"



####################Gripper###########################
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

################ Code ################################
mc.send_angles(p2, cobot_speed)
gripper_state = "OPEN"
time.sleep(0.5)
gripper_state = "STOP"
time.sleep(2)


while True:
    mc.send_angles(p1, cobot_speed)
    print("P1")
    time.sleep(1.5)
    gripper_state = "GRIP"
    time.sleep(0.5)
    mc.send_angles(p2, cobot_speed)
    print("P2")
    time.sleep(1.5)
    mc.send_angles(p3, cobot_speed)
    print("P3")
    time.sleep(1.5)
    mc.send_angles(p4, cobot_speed)
    print("P4")
    time.sleep(1.5)
    gripper_state = "OPEN"
    time.sleep(0.5)
    gripper_state = "STOP"
    mc.send_angles(p4, cobot_speed)
    print("P4")
    time.sleep(0.5)
    gripper_state = "GRIP"
    time.sleep(0.5)
    print("P3")
    time.sleep(1.5)
    mc.send_angles(p2, cobot_speed)
    print("P2")
    time.sleep(1.5)
    mc.send_angles(p1, cobot_speed)
    print("P1")
    time.sleep(1.5)
    gripper_state = "OPEN"
    time.sleep(0.5)
    gripper_state = "STOP"
    mc.send_angles(p2, cobot_speed)
    print("P2")
    time.sleep(1.5)
    
     

