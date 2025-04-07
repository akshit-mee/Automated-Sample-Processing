from pymycobot.mycobot import MyCobot
import time
import threading
import requests
import RPi.GPIO as GPIO
import numpy
import logger

mc = MyCobot("/dev/ttyAMA0", 1000000)

cobot_speed = 100

c1 = [181.0, -161.8, 210, 176.08, 0, 45.13]             #LN2 (Fully sumbersed is [181.0, -161.8, 180, 176.08, 0, 45.13])
c2 = [181.0, -161.8, 235, 176.08, 0, 45.13]             #Above LN2


cm = [152.7, -81.7, 267.2, 167.92, -3.03, 59.48]        #Between c2 and cm2 to prevent collision
cm2 = [134.4, -1.3, 298.7, 170.73, -8.85, 55.61]        #Above Water-Bath


cn = [151.1, 7.3, 210.7, 172.35, -6.58, 56.28]          #Water Bath [151.4, 7.7, 238.3, 172.22, -6.34, 56.17]
#an = [29.79, 20.74, -103.97, 2.1, -3.6, -116.45]
an = [29.61, 17.22, -83.93, -14.5, -4.13, -116.45]      #Water Bath !! Uee this as the adjecent solution form coordinates has different robot pose 

ce1 = [97.7, -125.6, 298.1, 167.36, -6.7, 14.91]        #Between 
ce2 = [-34.7, -145.0, 260, 172.11, -1.88, -10.06]       #Stop position after experiment to easily remove vial
