from utils.pygame_utils import *

class SimulateMovingDynamics(object):
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
                    new_diade = (self.city.agents[diade[1]].address, diade[1])
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

    def move_sequence(self, name, start, end, city):
        occupant_name = name
        start_x, start_y = city.houses[start].x, city.houses[start].y
        end_x, end_y = city.houses[end].x, city.houses[end].y
        end_house = city.houses[end]
        number_displaced = abs(end-start) 
        if start < end:
            sign = -1
        else: 
            sign = 1
        center_x = round((end_x+start_x)/2)
        center_y = round((end_y+start_y)/2)
        angular_speed = math.pi/20
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
            self.mover_list.remove((start, occupant_name))
        return 

if __name__ == 'main':
    main()