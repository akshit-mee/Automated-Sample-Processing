from pymycobot.mycobot import MyCobot
import time
import threading
import RPi.GPIO as GPIO

mc = MyCobot("/dev/ttyAMA0", 1000000)

red_led = 19
servo = 19


GPIO.setmode(GPIO.BCM)
GPIO.setup(servo, GPIO.OUT)

pwm = GPIO.PWM(servo, 50)

def SetAngle(angle):
    try:
        duty = angle / 18 + 2
        pwm.start(duty)
        print("servo")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup()

def servo():
    SetAngle(180)
    
servo_thread = threading.Thread(target=servo, daemon = True)
servo_thread.start()

try:
    for i in range(10):
        print(f"moving to point {i}")
        time.sleep(1)
except KeyboardInterrupt:
     print("Program terminated")
        
pwm.stop()
GPIO.cleanup()
    


