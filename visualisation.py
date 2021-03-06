import pygame
import random
import numpy as np
import math

BLACK = (  0,   0,   0)
GREY  = (100, 100, 100)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)

class Visualisation:
    def __init__(self, simulation):
        pygame.init()

        self.simulation = simulation
        self.world = World(self)

        self.screen_width = (60*simulation._nb_lanes) + 30
        self.screen_height = simulation._road_len*8
        self.screen = pygame.display.set_mode([self.screen_width, self.screen_height])
        
    def update(self):
        for event in pygame.event.get(): 
           if event.type == pygame.QUIT: 
               return true # inform the outer loop 
        

        self.world.draw()

        pygame.display.flip()
        return None
        
    def destruct(self):
        pygame.quit()

class World:
    def __init__(self, vis):
        self.vis = vis

    def draw(self):
        self.vis.screen.fill(WHITE)
        pygame.draw.line(self.vis.screen, GREY, (5, 0), (5, self.vis.screen_height), 3)
        pygame.draw.line(self.vis.screen, GREY, (self.vis.screen_width - 5, 0), (5, self.vis.screen_height), 3)

# pygame.init()

# import pygame
# import random
# import numpy as np
# import math
 
# # Define some colors
# BLACK = (  0,   0,   0)
# GREY  = (100, 100, 100)
# WHITE = (255, 255, 255)
# RED   = (255,   0,   0)

# def draw_dashed_line(surf, color, start_pos, end_pos, width=1, dash_length=10):
#     x1, y1 = start_pos
#     x2, y2 = end_pos
#     dl = dash_length

#     if (x1 == x2):
#         ycoords = [y for y in range(y1, y2, dl if y1 < y2 else -dl)]
#         xcoords = [x1] * len(ycoords)
#     elif (y1 == y2):
#         xcoords = [x for x in range(x1, x2, dl if x1 < x2 else -dl)]
#         ycoords = [y1] * len(xcoords)
#     else:
#         a = abs(x2 - x1)
#         b = abs(y2 - y1)
#         c = round(math.sqrt(a**2 + b**2))
#         dx = dl * a / c
#         dy = dl * b / c

#         xcoords = [x for x in np.arange(x1, x2, dx if x1 < x2 else -dx)]
#         ycoords = [y for y in np.arange(y1, y2, dy if y1 < y2 else -dy)]

#     next_coords = list(zip(xcoords[1::2], ycoords[1::2]))
#     last_coords = list(zip(xcoords[0::2], ycoords[0::2]))
#     for (x1, y1), (x2, y2) in zip(next_coords, last_coords):
#         start = (round(x1), round(y1))
#         end = (round(x2), round(y2))
#         pygame.draw.line(surf, color, start, end, width)
 
# class Car(pygame.sprite.Sprite):
#     """
#     This class represents the car.
#     It derives from the "Sprite" class in Pygame.
#     """
 
#     def __init__(self, color, width, height):
#         """ Constructor. Pass in the color of the block,
#         and its x and y position. """
 
#         # Call the parent class (Sprite) constructor
#         super().__init__()
 
#         # Create an image of the block, and fill it with a color.
#         # This could also be an image loaded from the disk.
#         self.image = pygame.image.load('car.png')
#         self.image = pygame.transform.scale(self.image, (26,62))
#         #self.image = pygame.Surface([width, height])
#         #self.image.fill(color)
        
#         # Fetch the rectangle object that has the dimensions of the image
#         # image.
#         # Update the position of this object by setting the values
#         # of rect.x and rect.y
#         self.rect = self.image.get_rect()
#         self.speed = np.random.randint(2,6)
#         self.lane = 0
#         self.desiredlane = 0
#         self.minfrontdist = 40
        
 
    
    
# # Initialize Pygame
# pygame.init()
 
# # Set the height and width of the screen
# screen_width = 160
# screen_height = 700

# #Variables
# road_width  = screen_width - 10
# lane_width = road_width / 3
# screen = pygame.display.set_mode([screen_width, screen_height])
# #Keep track of the "center of the lanes" not that rect are drawn from upper eft
# #so we keep track of which upperleft_x corrosponds to a car in the middle
# lane_center = [5 + (lane_width - 26)/2, 5 + lane_width + (lane_width - 26)/2, 5 + 2* lane_width + (lane_width - 26)/2] 


# FPS = 30
 
# # This is a list of 'sprites.' Each block in the program is
# # added to this list. The list is managed by a class called 'Group.'
# car_list = pygame.sprite.Group()
# car_list2 = pygame.sprite.Group()
# car_list3 = pygame.sprite.Group()
# waiting_list = pygame.sprite.Group()


# #Make waiting cars (out of screen)
# for i in range(3):
#     # This represents a block
#     car = Car(BLACK, 26, 40)
 
#     # Set a random location for the block
#     car.rect.x = lane_center[i]
#     car.lane = i-1
#     car.rect.y = screen_height + 40
 
#     # Add the block to the list of objects
#     waiting_list.add(car)

 
# # Loop until the user clicks the close button.
# done = False
 
# # Used to manage how fast the screen updates
# clock = pygame.time.Clock()
 
# # -------- Main Program Loop -----------
# while not done:
#     for event in pygame.event.get(): 
#         if event.type == pygame.QUIT: 
#             done = True
 
#     # Clear the screen
#     screen.fill(WHITE)
    
#     #Draw road
#     pygame.draw.line(screen, GREY, (5, 0), (5, screen_height), 3)
#     pygame.draw.line(screen, GREY, (screen_width-5, 0), (screen_width-5, screen_height), 3)
#     draw_dashed_line(screen, BLACK, (5 + lane_width, 0), (5 + lane_width, screen_height), dash_length=5)
#     draw_dashed_line(screen, BLACK, (5 + 2* lane_width, 0), (5 + 2* lane_width, screen_height), dash_length=5)
 
 
#     #See if we spawn a new car
#     for i, waiting_car in enumerate(waiting_list):
#         if np.random.rand() > 0.99 and (pygame.sprite.spritecollideany(waiting_car, car_list, collided = None) == None):
#             car_list.add(waiting_car)
#             waiting_car.remove(waiting_list)
#             car = Car(BLACK, 25, 40)
#             car.lane = np.random.randint(0,3)
#             car.desiredlane = car.lane
#             car.rect.x = lane_center[car.lane]
#             car.rect.y = screen_height + 40
#             waiting_list.add(car)
    
#     #Update cars
#     for car in car_list:
#         #Kill the car when it goes over the edge
#         if car.rect.y < -40:
#             #print("WTF")
#             car_list.remove(car)
#             car.kill()
        
#         #Move car foward in steps of its speed
#         car.rect.y -= car.speed
        
#         ##### FRONT CHECK ############ WORKS
#         # Create new list with all other cars in it
#         car_list2.empty()
#         car_list2 = car_list.copy()
#         car_list2.remove(car) #Remove from the list so we can check collision
        
#         #Put the car 0.5 car in front and see if it collides with any other car
#         car.rect.top -= car.rect.height*0.5
#         car_blocker = (pygame.sprite.spritecollideany(car, car_list2, collided = None))
#         car.rect.top += car.rect.height*0.5
#         if car_blocker:
#             #Move the car back to initial position if change caussed collision
#             car.rect.y += car.speed
#             #Set the speed to the speed of the car ahead
#             car.speed = car_blocker.speed
             
     
        
        
        
#         #### LANE CHANGING ###################### #Changes lange 2/3 down the road
#         #Change lane at 2/3 the road
#         if (car.rect.y < screen_height/3):
#             car.desiredlane = 0
            
#         #### Check lane ######################### Doesn't work fully, still dodgy
#         if car.rect.left in lane_center:
#             car.rect = pygame.rect.Rect(car.rect[0] - lane_width, car.rect[1] + 40*0.5, car.rect[2], car.rect[3] + 40*0.5)
#             #car_list3.add(car)
#             #car_list3.draw(screen)
#             check = (pygame.sprite.spritecollideany(car, car_list2, collided = None)) == None
#             car.rect = pygame.rect.Rect(car.rect[0] + lane_width, car.rect[1] - 40*0.5, car.rect[2], car.rect[3] - 40*0.5)
#         else:
#             check = True
            
#         #Begin changing lane -> Animate a lane change
#         if (car.desiredlane != car.lane) and check:
#             if car.desiredlane < car.lane:
#                 car.rect.x -= 1
#             else:
#                 car.rect.x += 1
#             if abs(car.rect.x - lane_center[car.desiredlane]) < 2:
#                 car.lane = car.desiredlane
#         #########################################
                
            
#     # Draw all the spites
#     car_list.draw(screen)
 
#     # Go ahead and update the screen with what we've drawn.
#     pygame.display.flip()
#     # print(len(car_list))
#     #print(pygame.time.get_ticks())
 
#     # Limit to 60 frames per second
#     clock.tick(FPS)
 
# pygame.quit()
