import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os
import time

def setup_logger(log_dir = 'logs'):
    os.makedirs(log_dir, exist_ok = True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = os.path.join(log_dir, f'app_{timestamp}.log')
    
    logger = logging.getLogger('my_app')
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
    
    
    
