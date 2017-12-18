# Base Agent class
from collections import Counter
from utils.pygame_utils import *

NEIGHBORHOOD_SIZE = 4

class Agent(object):
    """ Define an agent of the game """
    def __init__(self, color, tag, name, minimum_same_type=0.5):
        self.color = color
        self.type = tag
        self.name = name
        self.threshold = minimum_same_type

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, [self.x+7, self.y+7], 7)

    def update_housing_info(self, house):
        self.address = house.address
        self.x = house.x 
        self.y = house.y

    def gather_information(self, houses, model='Line'):
        neighbours_list = [address for address in \
            range(max(1, self.address-NEIGHBORHOOD_SIZE), \
                min(len(houses), self.address+NEIGHBORHOOD_SIZE)+1) \
            if address!=self.address]
        information = {address: house.occupant_type for (address, house) in houses.items() \
            if address in neighbours_list}
        return information

    def make_moving_decision(self, houses, model='Line'): # name this make_moveout_decision and add method make_movein_decision
        information = self.gather_information(houses=houses, model=model)
        type_list = [information.get(key) for key in information]
        type_counts = Counter(type_list)
        if sum(type_counts.values()) == NEIGHBORHOOD_SIZE*2:
            self.is_mover = type_counts[self.type]/sum(type_counts.values()) < self.threshold
        else:
            self.is_mover = (type_counts[self.type]+1)/(sum(type_counts.values())+1) < self.threshold


    def find_nearest_new_house(self, houses, model='Line'):
        candidate_houses = [houses.get(key).occupant_type for key in houses if key!=self.address]
        start_pos = self.address -1
        radius = max(start_pos - 1, len(candidate_houses) - start_pos)
        for ind in range(0,radius):
            key_plus = min(start_pos + ind, len(candidate_houses)) 
            key_minus = max(start_pos - ind, 0) 
            neighborhood_plus = candidate_houses[max(key_plus - NEIGHBORHOOD_SIZE-1,0): min(key_plus + NEIGHBORHOOD_SIZE, len(candidate_houses))]
            type_counts = Counter(neighborhood_plus)
            if type_counts[self.type]/sum(type_counts.values()) >= self.threshold:
                return (key_plus +1) + 1
            neighborhood_minus = candidate_houses[max(key_minus - NEIGHBORHOOD_SIZE, 0):\
            min(key_minus + NEIGHBORHOOD_SIZE-1, len(candidate_houses)-1)]
            type_counts = Counter(neighborhood_minus)
            if type_counts[self.type]/sum(type_counts.values()) >= self.threshold:
                return key_minus + 1

if __name__ == 'main':
	main()
