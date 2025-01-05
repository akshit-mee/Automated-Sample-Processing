robot_actions = ['Innitial Setting Updated',
                 'Wainting', 
                 'Place Sample in Thermomixer', 
                 'Place Sample in Liquid Nitrogen', 
                 'Pick up Sample from Thermomixer', 
                 'Pick up Sample from Liquid Nitrogen',
                 'Moving Sample to Thermomixer', 
                 'Moving Sample to Liquid Nitrogen'
                 'Completed'
                 'Stopped by User'
                 'Restarted by User']

class RobotActions:

    def __init__(self):
        self.thermomixer = [0,0,0]   #add coordinates of thermomixer
        self.liquid_nitrogen = [0,0,0] #add coordinates of liquid nitrogen
        self.current_cycle = 0
        self.thermomixer_time = 60
        self.liquid_nitrogen_time = 60

    def sample_position(self):
        pass

    def wait(self, time):
        pass

    def pick_up_sample_from(self, location):
        pass

    def move_sample_to(self, location):
        pass

    def place_sample_in(self, location):
        pass

    def complete(self):
        pass

    def stop(self):
        pass

    def cycle(self):
        while self.current_cycle < self.number_of_cycles:
            self.wait(self.thermomixer_time)
            self.pick_up_sample_from(self.thermomixer)
            self.move_sample_to(self.liquid_nitrogen)
            self.place_sample_in(self.liquid_nitrogen)
            self.wait(self.liquid_nitrogen_time)
            self.pick_up_sample_from(self.liquid_nitrogen)
            self.move_sample_to(self.thermomixer)
            self.place_sample_in(self.thermomixer)
            self.current_cycle += 1
        self.complete()
        
