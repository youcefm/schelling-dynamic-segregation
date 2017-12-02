import pygame   # for visual interface
import math
import random
import os
from collections import Counter

# Initialize the game engine
pygame.init()

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREY	 = ( 150, 150, 150)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
BLUE     = (   0,   0, 255)
MYGREEN  = (  40, 100,  40)
YELLOW 	 = ( 255, 255,   0)
SAND 	 = ( 255, 255, 100)

# Function that prints text on screen
def text_to_screen(screen, text, x, y, size = 20,
            color = BLACK):
    text = str(text)
    font = pygame.font.SysFont('avenir', size)
    text = font.render(text, True, color)
    screen.blit(text, (x, y))

# Function that applies a rotation to some coordinates around a center
def apply_rotation(init_coord, center, angle):
    init_x, init_y = init_coord
    center_x, center_y = center
    new_x = round((init_x-center_x)*math.cos(angle) - (init_y - center_y)*math.sin(angle)) + center_x
    new_y = round((init_x-center_x)*math.sin(angle) + (init_y - center_y)*math.cos(angle)) + center_y
    new_coord = (new_x, new_y)
    return new_coord


### Schelling Model objects ###

#Parameters:
NUMBER_OF_HOUSES = 70
NUMBER_OF_AGENTS = 70
SHAPE = 'Line'
TYPES = [('Black',BLACK), ('White',WHITE)]
NEIGHBORHOOD_SIZE = 4
HOUSE_SIZE = 15

class House(object):
    """ Defines a house where agents can move in and out """
    def __init__(self, address, size=15, occupant_type ='', occupant_name =1): # remove legacy args when ready
        self.occupied = False
        self.address = address
        self.size = size
        self.occupant_type = occupant_type # remove when ready
        self.occupant_name = occupant_name # remove when ready
        self.y = 300 # remove when ready
        self.x = 10 + self.size*(self.address - 1) #remove when ready

    def draw(self, screen): 
        pygame.draw.rect(screen, RED, [self.x , self.y , self.size, self.size], 1)

    def update_occcupant_info(self, occupant):
        self.occupant_name = occupant.name
        self.occupant_type = occupant.type
        self.occupied = True

class Agent(object):
    """ Define an agent of the game """
    def __init__(self, color, tag, name, minimum_same_type=0.5, address=1): #remove legacy args when ready
        self.color = color
        self.type = tag
        self.name = name
        self.threshold = minimum_same_type
        self.address = address # remove when ready
        self.x = 10 + 15*(self.address - 1)
        self.y = 300

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
        for ind in range(0,radius+1):
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

    #def move_sequence(self, new_address):

class UrbanDesign(object):
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

class SimulateDynamics(object):
    """ 
        Required data and methods to simulate moving dynamics
    """
    def __init__(self, city):
        self.city = city
        self.mover_list = []
        self.equilibrium = False
        self.round = 0

    def find_movers(self):
        for name in self.city.agents:
            self.city.agents[name].make_moving_decision(houses=self.city.houses, model=self.city.shape)

    def current_movers(self):
        self.find_movers()
        if self.mover_list:
            for index, diade in enumerate(self.mover_list):
                if not self.city.agents[diade[1]].is_mover:
                    self.mover_list.remove(diade)
                else:
                    new_diade = (city.agents[diade[1]].address, diade[1])
                    self.mover_list[index] = new_diade
        else:
            self.round +=1
            for name in self.city.agents:
                if self.city.agents[name].is_mover:
                    address = self.city.agents[name].address
                    self.mover_list.append((address, name))
        self.mover_list.sort()

    def determine_stability(self):
        if self.mover_list:
            self.equilibrium = False
        else: self.equilibrium = True

def move_sequence(name, start, end, city, dynamics):
    occupant_name = name
    start_x, start_y = city.houses[start].x, city.houses[start].y
    end_x, end_y = city.houses[end].x, city.houses[end].y
    end_house = city.houses[end]
    number_displaced = abs(end-start) 
    if start_x < end_x:
        sign = -1
    else: 
        sign = 1
    center_x = round((end_x+start_x)/2)
    center_y = round((end_y+start_y)/2)
    angular_speed = math.pi/30
    agent = city.agents[occupant_name]
    if abs(agent.x - end_x) > 5:
        new_x = round((agent.x-center_x)*math.cos(angular_speed) - (agent.y - center_y)*math.sin(angular_speed)) + center_x
        new_y = round((agent.x-center_x)*math.sin(angular_speed) + (agent.y - center_y)*math.cos(angular_speed)) + center_y
        agent.x = new_x
        agent.y = new_y 
    else:
        for ind in range(1,number_displaced+1):
            house_temp = city.houses[start -sign*ind + sign]
            agent_temp = city.agents[city.houses[start -sign*ind].occupant_name]
            agent_temp.update_housing_info(house_temp)
            house_temp.update_occcupant_info(agent_temp)
        agent.update_housing_info(end_house)
        end_house.update_occcupant_info(agent)
        dynamics.mover_list.remove((start, occupant_name))
    return 


city = UrbanDesign(70, 70)
city.populate_line()
#city.populate_circle()
#city.populate_grid()
city.initial_match_of_agents_to_houses()
#house_dict = city.houses
#agent_dict = city.agents

dynamics = SimulateDynamics(city)

#agent_type = [('Black',BLACK), ('White',WHITE)]
#mixed_types = 35*agent_type
#number_agents = 70

#house_list = [house_dict.get(key) for key in house_dict]

#Open a window
size = (1200, 700)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Schelling Dynamic Segregation Game")

# Loop until the user clicks the close button.
done = False
# Used to manage how fast the screen updates
clock = pygame.time.Clock()

frame_rate = 40
turn =0

# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get(): # User did something
        if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): # If user clicked close
            done = True # Flag that we are done so we exit this loop
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE): # restart simulation with random start
            city.initial_match_of_agents_to_houses(matching_type='random') #random assignment
            dynamics = SimulateDynamics(city)
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_s): # restart simulation with mixed stable start
            city.initial_match_of_agents_to_houses(matching_type='alternate') # gives integrated and stable initial configuration
            dynamics = SimulateDynamics(city)

        
 
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.

    screen.fill(GREY)

    for ind in city.houses:
        city.houses[ind].draw(screen)
        occupant_name = city.houses[ind].occupant_name
        city.agents[occupant_name].draw(screen)

    if not dynamics.equilibrium:
        dynamics.current_movers()
        dynamics.determine_stability()
        #current_diade = next(iter(dynamics.mover_list), False)
        for diade in dynamics.mover_list:
            current_address = diade[0]
            name = diade[1]
            new_address = city.agents[name].find_nearest_new_house(houses=city.houses)
            move_sequence(name, current_address, new_address, city, dynamics)
            break


    turn += 1
    text_to_screen(screen, 'Frames: {0}'.format(turn), 10,10, color = BLACK)
    text_to_screen(screen, 'Rounds: {0}'.format(dynamics.round), 10, 60)

    # --- Go ahead and update the screen with what we've drawn.

    pygame.display.flip()
 
    # --- Limit frames per second
    clock.tick(frame_rate)

pygame.quit()