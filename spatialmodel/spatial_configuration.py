import math
import random
from agent.agent import Agent
from house.house import House
from utils.pygame_utils import *

class SpatialConfiguration(object):
    """ 
        Populates a city with houses and agents, following a specific design.
        The current designs are line, Circle and Grid. 
    """
    def __init__(self, number_houses, number_agents):
        # need to raise exception when number_agents > number_houses 
        self.number_houses = number_houses
        self.number_agents = number_agents

    def init_houses(self):
        """ Initialize a dicitionary of house intstances """
        houses = {}
        for address in range(1,self.number_houses+1):
            houses[address] = House(address=address) 
        self.houses = houses

    def init_agents(self, types = [('Black',BLACK), ('White',WHITE)], type_assignment='random'):
        """ Initialize a dicitionary of agent intstances """
        agents = {}
        type_list = round(self.number_agents/2)*types
        for name in range(1,self.number_agents+1):
            tag, color = type_list[name-1]
            agents[name] = Agent(color=color, tag=tag, name=name)
        self.agents = agents 

    def populate_line(self, init_coord = (10,300), padding=15):
        """ populates a horizontal line of houses going from left to right, starting at (init_x, init_y) """
        self.init_houses()
        self.shape = 'Line'
        init_x, init_y = init_coord
        for address in self.houses:
            house = self.houses[address]
            house.y = init_y
            house.x = init_x + padding*(house.address -1)

    def populate_circle(self, center = (600, 350), padding=15):
        """ populate a circle of houses clockwise, starting at the midnight position"""
        self.init_houses()
        self.shape = 'Circle'
        center_x, center_y = center
        cironference = self.number_houses*padding
        radius = cironference/(2*math.pi)
        angle = (2*math.pi)/self.number_houses
        init_coord = (center_x + radius, center_y + radius)
        for address in self.houses:
            house = self.houses[address]
            angle_position = angle*(house.address - 1)
            house.x, house.y = apply_rotation((init_coord), center, angle_position)

    def populate_grid(self, init_x=150, init_y=150, padding=15):
        grid_size = math.ceil(math.sqrt(self.number_houses))
        #self.number_houses = grid_size*grid_size
        self.init_houses()
        self.shape = 'Grid'
        for address in self.houses:
            y_pos  = math.floor((address-1)/grid_size)
            x_pos = address % grid_size -1
            house = self.houses[address]
            house.x = init_x + padding*x_pos
            house.y = init_y + padding*y_pos

    def initial_match_of_agents_to_houses(self, matching_type='random'):
        """ 
            Performs initial matching of agents to houses. 
            Matching type can be random or sequential 
        """
        self.init_agents()
        available_houses = [address for address in self.houses]
        for name in self.agents:
            agent = self.agents[name]
            if matching_type=='random':
                address = random.choice(available_houses) # randomly match agent to available house
                available_houses.remove(address) # remove house from list of available houses
            else: address = name
            house = self.houses[address]
            agent.update_housing_info(house=house)
            house.update_occcupant_info(occupant=agent)

if __name__ == 'main':
	main()