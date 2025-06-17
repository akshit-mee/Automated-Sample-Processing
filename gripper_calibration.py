from pymycobot.mycobot import MyCobot
import time
import threading
import requests
import RPi.GPIO as GPIO

####################Innitialization ##################
mc = MyCobot("/dev/ttyAMA0", 1000000)
cobot_speed = 70
gripper_pin = 19 #Change for different pin for make a config file
gripper_open = 6.5 #Completle open, can change for less opening
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

################################################################
start = input("enter to close gripper")
gripper_state = "GRIP"
grip = input("Gripper (default: 12)")
grip = int(grip)
while grip != 999:
    gripper_closed = grip
    grip = input("Gripper (default: 12)")
    grip = int(grip)

start = input("enter to open gripper")
gripper_state = "OPEN"

close = input("Gripper (default: 12)")
close = int(close)
while close != 999:
    gripper_open = close
    close = input("Gripper (default: 12)")
    close = int(close)
    
print(grip)
print(close)

        
