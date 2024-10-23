from pymycobot.mycobot import MyCobot
import time
import threading
import RPi.GPIO as GPIO

mc = MyCobot("/dev/ttyAMA0", 1000000)

mc.release_all_servos()
red_led = 19
servo = 19


GPIO.setmode(GPIO.BCM)
GPIO.setup(servo, GPIO.OUT)

pwm = GPIO.PWM(servo, 50)
pwm.start(0)

def SetAngle(angle):
    duty = angle / 18 + 2
    GPIO.output(servo, 1)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(servo, 0)
    pwm.ChangeDutyCycle(0)

SetAngle(180)

while True:
    GPIO.output(red_led, 0)
    time.sleep(1)
    GPIO.output(red_led,1)
    time.sleep(1)
