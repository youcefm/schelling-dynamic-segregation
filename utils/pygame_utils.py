# Contains variables and functions useful for pygame interface renderings and animations
import pygame 
import math

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREY     = ( 150, 150, 150)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
BLUE     = (   0,   0, 255)
MYGREEN  = (  40, 100,  40)
YELLOW   = ( 255, 255,   0)
SAND     = ( 255, 255, 100)

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

if __name__ == 'main':
	main()