from pymycobot.mycobot import MyCobot
import time
import threading
import requests
import RPi.GPIO as GPIO

mc = MyCobot("/dev/ttyAMA0", 1000000)

cobot_speed = 100

c1 = [181.0, -161.8, 205, 176.08, 0, 45.13] #thermomixer
c2 = [181.0, -161.8, 235, 176.08, 0, 45.13]


cm = [152.7, -81.7, 267.2, 167.92, -3.03, 59.48]
cm2 = [134.4, -1.3, 298.7, 170.73, -8.85, 55.61]


c3 = [164.3, 35.5, 261.3, 175.61, -6.06, 68.85]
c4 = [193.7, 54.5, 229.3, 177.28, -0.41, 66.07] # LN2

a2 = [34.98, -14.15, -52.91, -21.18, -2.1, -121.11] # LN2

shutdown = [-25.83, -143.17, 156.62, -146.95, 101.68, 165.14]

for x in range(3):
    mc.send_coords(c1, 50, 1)
    time.sleep(1)
    mc.send_coords(c2, 50, 1)
    time.sleep(1)
    mc.send_coords(cm2, 50, 1)
    time.sleep(1)
    mc.send_coords(c3, 50, 1)
    time.sleep(1)
    mc.send_coords(c4, 50, 1)
    time.sleep(1)
    mc.send_coords(cm2, 50, 1)
    time.sleep(1)
    mc.send_coords(c2, 50, 1)
    time.sleep(1)
    mc.send_coords(c1, 50, 1)
    time.sleep(1)
