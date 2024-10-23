import time
import threading
import requests
import RPi.GPIO as GPIO


######################### Send to Display ######################################
display_url = "http://127.0.0.1:5000/update_status"
def update_gripper_status(new_status):
    message = {
        "gripper_status": new_status,
        "timestamp": time.strftime('%Y-%m-%d %H-%M-%S')
        }
    try:
        response = requests.post(display_url, json=message)
        if response.status_code == 200:
            print("Gripper Status Updates", new_status)
        else:
            print("Failed to update status", response.json())
    except requests.exceptions.RequestException as e:
        print("Error connecting to the server", e)


######################### Gripper Manager ######################################
#TODO: Config file

############ Innitialising ###############
gripper_pin = 19 #Change for different pin for make a config file
gripper_open = 8 #Completle open, can change for less opening
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
            # update_gripper_status(gripper_state)
            
    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup()
        
gripper_thread = threading.Thread(target=manage_gripper, daemon = True)
gripper_thread.start()


########################## Testing ############################################
try:
    while True:
        command = input("gripper ??").strip().lower()
        if command == "grip":
            gripper_state = "GRIP"
        if command == "open":
            gripper_state = "OPEN"
        if command == "STOP":
            gripper_state = "STOP"
        if command == "quit":
            break
        else:
            print("invalid command")
            
except KeyboardInterrupt:
    print("program interrupted")
    
    
    
############################ cleanup ###########################################
gripper_state = "STOP"
pwm.stop()
GPIO.cleanup()
             

