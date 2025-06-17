from tqdm import tqdm
import time
from pymycobot.mycobot import MyCobot
import time
import threading
import requests
import RPi.GPIO as GPIO
import numpy
import logger
from tqdm import tqdm


mc = MyCobot("/dev/ttyAMA0", 1000000)

Thermomixer_Time = 10
start_water_bath_time = time.monotonic()


def sleep_progress(duration_s, cycle_name = "Waiting"):
    increment = 90
    with tqdm(total = duration_s, desc = cycle_name, unit = "s") as pbar:
        for i in range(duration_s):
            mc.jog_increment(6, increment, 70)
            increment = - increment
            
            time.sleep(1)
            pbar.update(1)
            remaining = duration_s - i +1
            pbar.set_postfix_str(f"Remaining: {remaining} s")
            



   
    
sleep_progress(Thermomixer_Time)
end_water_bath_time = time.monotonic()
water_bath_time = start_water_bath_time - end_water_bath_time
print(f"{water_bath_time = }")
