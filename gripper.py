from pymycobot.mycobot import MyCobot
import time
import threading
import requests
import RPi.GPIO as GPIO

#################### Innitialising myCobot #####################################
mc = MyCobot("/dev/ttyAMA0", 1000000)

p1 = [113.2, -65.3, -28.56, 4.04, -2.81, 57.39]
p2 = [113.2, -27.07, -28.47, -28.3, 1.31, 68.99]
p3 = [161.71, -30.32, -28.56, -25.92, -1.31, 129.46]
p4 = [162.15, -63.54, -28.56, 7.2, 1.93, 136.23]

cobot_speed = 100


######################### Send to Display ######################################
display_url = "http://127.0.0.1:5000/update_status"
def update_gripper_status(new_status):

    #message = {
    #    "gripper_status": new_status,
    #    "timestamp": time.strftime('%Y-%m-%d %H-%M-%S')
    #    }
    #try:
    #    response = requests.post(display_url, json=message)
    #    if response.status_code == 200:
    #        s = 1
    #        # print("Gripper Status Updates", new_status)
    #    else:
    #        print("Failed to update status", response.json())
    #except requests.exceptions.RequestException as e:
    #    print("Error connecting to the server", e)
    print("server not needed")


######################### Gripper Manager ######################################
#TODO: Config file

############ Innitialising ###############
gripper_pin = 19 #Change for different pin for make a config file
gripper_open = 6.5 #Completle open, can change for less opening
gripper_closed = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(gripper_pin, GPIO.OUT)

pwm = GPIO.PWM(gripper_pin, 50)

gripper_state = "STOP" #Possible values "STOP" "CLOSE" "OPEN"

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
            update_gripper_status(gripper_state)
            
    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup()
        
gripper_thread = threading.Thread(target=manage_gripper, daemon = True)
gripper_thread.start()


########################## Testing ############################################
#try:
#    while True:
#        command = input("gripper ??").strip().lower()
#        if command == "grip":
#            gripper_state = "GRIP"
#        if command == "open":
#            gripper_state = "OPEN"
#        if command == "STOP":
#            gripper_state = "STOP"
#        if command == "quit":
#            break
#        else:
#            print("invalid command")
#            
#except KeyboardInterrupt:
#    print("program interrupted")
 
 
while True:
    while not mc.is_in_position(p1, 0):
        mc.send_angles(p1, cobot_speed)
    
    gripper_state = "GRIP"
    time.sleep(0.5)
    while not mc.is_in_position(p1, 0):
        mc.send_angles(p2, cobot_speed)
    
    while not mc.is_in_position(p1, 0):
        mc.send_angles(p3, cobot_speed)
    
    while not mc.is_in_position(p1, 0):
        mc.send_angles(p4, cobot_speed)
    
    gripper_state = "OPEN"
    time.sleep(0.5)
    gripper_state = "STOP"
    while not mc.is_in_position(p1, 0):
        mc.send_angles(p3, cobot_speed)
    
    while not mc.is_in_position(p1, 0):
        mc.send_angles(p2, cobot_speed)
     
 
    
    
    
############################ cleanup ###########################################
gripper_state = "STOP"
pwm.stop()
GPIO.cleanup()
             

