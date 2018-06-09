# Base House class
from utils.pygame_utils import *

class House(object):
    """ Defines a house where agents can move in and out """
    def __init__(self, address, size=15, occupant_type='', occupant_name=1): # remove legacy args when ready
        self.occupied = False
        self.address = address
        self.size = size
        self.occupant_type = occupant_type # remove when ready
        self.occupant_name = occupant_name # remove when ready

    def draw(self, screen): 
        pygame.draw.rect(screen, RED, [self.x , self.y , self.size, self.size], 1)

    def update_occcupant_info(self, occupant):
        self.occupant_name = occupant.name
        self.occupant_type = occupant.type
        self.occupied = True

if __name__ == 'main':
    main()