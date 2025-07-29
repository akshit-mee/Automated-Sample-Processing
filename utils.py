import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os
import time
import numpy
import glob
import pygame

import config



################################ Logging Functionality ##########################
def setup_logger(log_dir = '/home/er/Desktop/Code/logs'):
    os.makedirs(log_dir, exist_ok = True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = os.path.join(log_dir, f'asp_{timestamp}.log')
    
    logger = logging.getLogger('ASP')
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes = 1024 * 1024, #1 mb
        backupCount = 1,
        encoding = 'utf-8',
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger



################################ Basic Coordinate Distance ##########################
def distance(point1, point2):
    sum = 0
    for i in range(3):
        sum = sum + (point1[i] - point2[i])**2
    distance = numpy.sqrt(sum)
    return distance

################################ Temperature Sensor Functionality ##########################
### One Wire ##################
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
    
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':       #check if it is a valid reading
        time.sleep(0.2)
        lines = read_temp_raw()
    equal_pos = lines[1].find('t=')
    if equal_pos != -1:
        temp_strings = lines[1][equal_pos+2:]
        temp_c = float(temp_strings)/1000.0
        return temp_c
    else:
        return "Sensor Error"


################################ Closest Point Functionality ##########################
def closest_point(position):
    d1 = distance(position, config.c2)
    d2 = distance(position, config.c3)
    d3 = distance(position, config.cr)

    if d1 <= d2 and d1 <= d3:
        return config.c2

    if d2 <= d3 and d2 <= d1:
        return config.c3

    if d3 <= d1 and d3 <= d2:
        return config.cr
    
    
################################ Sound Functionality ##########################
def play_notification_sound():
    pygame.mixer.init()
    beep_sound = pygame.mixer.Sound('/usr/share/sounds/alsa/Front_Center.wav')
    beep_sound.play()
    # pygame.time.wait(2000)  # Uncomment this line if you want to wait for the sound to finish