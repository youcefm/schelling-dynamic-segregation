from spatialmodel.spatial_configuration import SpatialConfiguration as UrbanDesign
from spatialmodel.simulate_moving_dynamics import SimulateMovingDynamics as SimulateDynamics
from utils.pygame_utils import *

# Initialize the game engine
pygame.init()

city = UrbanDesign(80, 80)
#city.populate_line()
city.populate_circle()
#city.populate_grid()
city.initial_match_of_agents_to_houses()
dynamics = SimulateDynamics(city)

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
        current_diade = next(iter(dynamics.mover_list), False)
        if current_diade:
            diade = current_diade
            current_address = diade[0]
            name = diade[1]
            new_address = city.agents[name].find_nearest_new_house(houses=city.houses)
            dynamics.move_sequence(name, current_address, new_address, city)


    turn += 1
    text_to_screen(screen, 'Frames: {0}'.format(turn), 10,10, color = BLACK)
    text_to_screen(screen, 'Rounds: {0}'.format(dynamics.round), 10, 60)

    # --- Go ahead and update the screen with what we've drawn.

    pygame.display.flip()
 
    # --- Limit frames per second
    clock.tick(frame_rate)

pygame.quit()