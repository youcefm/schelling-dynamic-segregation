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
        self.x = 100 + 15*(self.address - 1) #remove when ready

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
        self.x = 100 + 15*(self.address - 1)
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

    def make_moving_decision(self, houses, model='Line'):
        information = self.gather_information(houses=houses, model=model)
        type_list = [information.get(key) for key in information]
        type_counts = Counter(type_list)
        self.is_mover = type_counts[self.type]/sum(type_counts.values()) < self.threshold

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
        for name in range(1,self.number_agents+1):
            tag, color = random.choice(types) # random assignment
            agents[name] = Agent(color=color, tag=tag, name=name)
        self.agents = agents 

    def populate_line(self, init_coord = (100,300), padding=15):
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

    def find_movers(self):
        for name in self.agents:
            self.agents[name].make_moving_decision(houses=self.houses, model=self.shape)

class SimulateDynamics(object):
    """ 
        Required data and methods to simulate moving dynamics
    """
    def __init__(self, city):
        self.city=city
        self.mover_list = []
        self.equilibrium = False
        self.round = 0

    def current_movers(self):
        self.city.find_movers()
        if self.mover_list:
            for name in self.mover_list:
                if not self.city.agents[name].is_mover:
                    self.mover_list.remove(name)
        else:
            self.round +=1
            for name in self.city.agents:
                if self.city.agents[name].is_mover:
                    self.mover_list.append(name)

class Stateofneighborhood(object):
    """ 
        For each house, defines composition of neighborhood, list of movers in current round
        also establishes if current situation is an equilibrium
    """
    def __init__(self, houses, neighborhood_size):
        self.houses = houses
        self.size = neighborhood_size
        self.mover_list = []
        self.equilibrium = False
        self.round = 0

    def define_state(self):
        houses_dict = {house.address: house.occupant_type for house in self.houses}
        neighborhood_data = {}
        for house in self.houses:
            pos = house.address
            #list_of_neighboors = [houses_dict.get(key) for key in range(max(1, pos-self.size), min(len(houses_dict), pos+self.size)+1) if key!=pos]
            list_of_neighboors = [houses_dict.get(key) for key in range(max(1, pos-self.size), min(len(houses_dict), pos+self.size)+1)]
            white_neighboors = list_of_neighboors.count('White')
            black_neighboors = list_of_neighboors.count('Black')
            total_neighboors = white_neighboors + black_neighboors
            neighborhood_data[pos] = {'number_whites': white_neighboors, 'number_blacks': black_neighboors,
            'minimum' : math.ceil(total_neighboors/2),
            'occupant_type': house.occupant_type, 'address': house.address, 'is_mover': False}
        return neighborhood_data

    def find_movers(self):
        neighborhood_data = self.define_state()
        equilibrium_indicator = True
        for house in neighborhood_data:
            neighbour = neighborhood_data[house]
            if (neighbour['occupant_type'] == 'Black')&(neighbour['number_blacks'] < neighbour['minimum']):
                neighbour['is_mover'] = True
                equilibrium_indicator = False
            elif (neighbour['occupant_type'] == 'White')&(neighbour['number_whites'] < neighbour['minimum']):
                neighbour['is_mover'] = True
                equilibrium_indicator = False
            else :
                neighbour['is_mover'] = False
        self.equilibrium = equilibrium_indicator
        city.find_movers()
        return neighborhood_data

    def current_movers(self):
        #neighborhood_data = self.find_movers()
        if self.mover_list:
            for mover in self.mover_list:
                address = agent_dict[mover].address
                #if not neighborhood_data[address]['is_mover']:
                if not city.agents[mover].is_mover:
                    self.mover_list.remove(mover)
        else:
            self.round +=1
            #for house in neighborhood_data:
            for name in city.agents:
                #if neighborhood_data[house]['is_mover']:
                if city.agents[name].is_mover:
                    #self.mover_list.append(house_dict[house].occupant_name)
                    self.mover_list.append(name)


def move_sequence(start, end, State):
    occupant_name = house_dict[start].occupant_name
    start_x = house_dict[start].x
    end_x = house_dict[end].x
    number_displaced = abs(end-start) 
    if start_x < end_x:
        sign = -1
    else: 
        sign = 1
    center_x = round((end_x+start_x)/2)
    center_y = 300
    angular_speed = math.pi/20
    agent = agent_dict[occupant_name]
    if abs(agent.x - end_x) > 10:
        new_x = round((agent.x-center_x)*math.cos(angular_speed) - (agent.y - center_y)*math.sin(angular_speed)) + center_x
        new_y = round((agent.x-center_x)*math.sin(angular_speed) + (agent.y - center_y)*math.cos(angular_speed)) + center_y
        agent.x = new_x
        agent.y = new_y
    else: 
        for ind in range(1,number_displaced+1):
            agent_temp = agent_dict[house_dict[start -sign*ind].occupant_name]
            agent_temp.address = start - sign*ind + sign
            agent_temp.x = 100 + 15*(agent_temp.address -1)
            house_dict[start - sign*ind + sign].occupant_name = agent_temp.name
            house_dict[start - sign*ind + sign].occupant_type = agent_temp.type
        agent.x = end_x
        agent.y = center_y
        agent.address = end
        house_dict[end].occupant_name = agent.name
        house_dict[end].occupant_type = agent.type
        State.mover_list.remove(agent.name)
        return 

city = UrbanDesign(70, 70)
city.populate_line()
#city.populate_circle()
#city.populate_grid()
city.initial_match_of_agents_to_houses()
house_dict = city.houses
agent_dict = city.agents

#agent_dict = {}
#house_dict = {}
#house_list = []
agent_type = [('Black',BLACK), ('White',WHITE)]
mixed_types = 35*agent_type
number_agents = 70
#for ind in range(1,number_agents+1):
#    tag, color = random.choice(agent_type) # random start
    #tag, color = mixed_types[ind-1]         # mixed neighborhood state start
#    house_dict[ind] = House(address = ind, occupant_type = tag, occupant_name = ind)
#    agent_dict[ind] = Agent(color = color , tag = tag, address = ind, name = ind) 
#    house_list.append(house_dict[ind])

house_list = [house_dict.get(key) for key in house_dict]

State = Stateofneighborhood(house_list, 4) # Initiate state object
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
            for ind in range(1,number_agents+1):
                tag, color = random.choice(agent_type) # random start
                house_dict[ind] = House(address = ind, occupant_type = tag, occupant_name = ind)
                agent_dict[ind] = Agent(color = color , tag = tag, address = ind, name = ind) 
                house_list.append(house_dict[ind])
            State = Stateofneighborhood(house_list, 4) # Initiate state object
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_s): # restart simulation with mixed stable start
            for ind in range(1,number_agents+1):
                tag, color = mixed_types[ind-1]         # mixed neighborhood state start
                house_dict[ind] = House(address = ind, occupant_type = tag, occupant_name = ind)
                agent_dict[ind] = Agent(color = color , tag = tag, address = ind, name = ind) 
                house_list.append(house_dict[ind])
            State = Stateofneighborhood(house_list, 4) # Initiate state object

        
 
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.

    screen.fill(GREY)

    for ind in house_dict:
        house_dict[ind].draw(screen)
        occupant_name = house_dict[ind].occupant_name
        agent = agent_dict[occupant_name]
        agent.draw(screen)

    if not State.equilibrium:
        neighborhood_data = State.find_movers()
        State.current_movers()
        list_of_movers = State.mover_list
    #if True:
        for mover in list_of_movers:
            ind = agent_dict[mover].address
            if neighborhood_data[ind]['is_mover']:
                start_ind = ind
                radius = max(start_ind-1, number_agents - start_ind)
                break
        if neighborhood_data[start_ind]['occupant_type'] == 'Black':
            metric = 'number_blacks'
        else:
            metric = 'number_whites'
        for next_ind in range(1, radius+1):
            if neighborhood_data[max(1,start_ind - next_ind)][metric]>=neighborhood_data[max(1,start_ind - next_ind)]['minimum']:
                end_ind = max(1,start_ind - next_ind)
                move_sequence(start_ind,end_ind, State)
                break
            elif neighborhood_data[min(start_ind + next_ind, number_agents)][metric]>=neighborhood_data[min(start_ind + next_ind, number_agents)]['minimum']:
                end_ind = min(start_ind + next_ind, number_agents)
                move_sequence(start_ind,end_ind, State)
                break
        
    #else : State.equilibrium = True


    turn += 1
    text_to_screen(screen, 'Turn: {0}'.format(turn), 10,10, color = BLACK)
    text_to_screen(screen, 'Mover List {0}'.format(list_of_movers), 10,40)
    text_to_screen(screen, 'Rounds: {0}'.format(State.round), 10, 60)
    text_to_screen(screen, 'Mover Address: {0}'.format(ind), 200, 60)
    text_to_screen(screen, 'Mover Minimum: {0}'.format(neighborhood_data[ind]['minimum']), 500, 60)
    text_to_screen(screen, 'Mover White Neighboors: {0} and Black Neighboors: {1}'.format(
        neighborhood_data[ind]['number_whites'], 
        neighborhood_data[ind]['number_blacks']), 10, 100)


    # --- Go ahead and update the screen with what we've drawn.

    pygame.display.flip()
 
    # --- Limit frames per second
    clock.tick(frame_rate)

pygame.quit()