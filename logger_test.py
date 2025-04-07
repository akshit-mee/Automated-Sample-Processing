import logger


Experiment_Name = "Name"
Person_Responsible = "Person"
Thermomixer_Time = 120 
LN2_Time = 30
Waiting_Time = 120
Number_of_Cycles = 15

Robot_speed = 100


log = logger.setup_logger()
log.info("Starting Experiment")
log.info("Experiment Parameters")
log.info(f"Experiment Name: {Experiment_Name}")
log.info(f"Person Responsible: {Person_Responsible}")
log.info(f"Thermomixer Time: {Thermomixer_Time}")
log.info(f"Liquid Nitrogen Time: {LN2_Time}")
log.info(f"Waiting Time {Waiting_Time}")
log.info(f"Number of Cycles {Number_of_Cycles}")
log.info(f"Robot Speed {Robot_speed}")
