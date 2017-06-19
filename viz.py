    # -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 13:30:19 2017

@author: Jake
"""

"""
Use sprites to collect blocks.
 
Sample Python/Pygame Programs
Simpson College Computer Science
http://programarcadegames.com/
http://simpson.edu/computer-science/
 
Explanation video: http://youtu.be/4W2AqUetBi4
"""
#%%
import pygame
import random
import numpy as np
import math
import bisect
from draw_dashed_line import draw_dashed_line
 
# Define some colors
BLACK = (  0,   0,   0)
GREY  = (100, 100, 100)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)

class Block(pygame.sprite.Sprite):
    """
    This class represents the ball.
    It derives from the "Sprite" class in Pygame.
    """
 
    def __init__(self, color, width, height):
        """ Constructor. Pass in the color of the block,
        and its x and y position. """
 
        # Call the parent class (Sprite) constructor
        super().__init__()
 
        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
 
        # Fetch the rectangle object that has the dimensions of the image
        # image.
        # Update the position of this object by setting the values
        # of rect.x and rect.y
        self.rect = self.image.get_rect()
        
        
class Car(pygame.sprite.Sprite):
    """
    This class represents the car.
    It derives from the "Sprite" class in Pygame.
    """
 
    def __init__(self, color, x, y):
        """ Constructor. Pass in the color of the block,
        and its x and y position. """
 
        # Call the parent class (Sprite) constructor
        super().__init__()
 
        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.image.load('car.png')
        self.image = pygame.transform.scale(self.image, (26,62))
        #self.image = pygame.Surface([width, height])
        #self.image.fill(color)
        
        # Fetch the rectangle object that has the dimensions of the image
        # image.
        # Update the position of this object by setting the values
        # of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = np.random.randint(2,6)
        self.lane = 0
        self.desiredlane = 0
        self.minfrontdist = 40
        
 
    
    
# Initialize Pygame
pygame.init()
 
# Set the height and width of the screen
screen_width = 160
screen_height = 700

#Variables
road_width  = screen_width - 10
lane_width = road_width / 3
screen = pygame.display.set_mode([screen_width, screen_height])
#Keep track of the "center of the lanes" not that rect are drawn from upper eft
#so we keep track of which upperleft_x corrosponds to a car in the middle
lane_center = [5 + (lane_width - 26)/2, 5 + lane_width + (lane_width - 26)/2, 5 + 2* lane_width + (lane_width - 26)/2] 


FPS = 30
 
# This is a list of 'sprites.' Each block in the program is
# added to this list. The list is managed by a class called 'Group.'
car_list = pygame.sprite.Group()
car_list2 = pygame.sprite.Group()
car_list3 = pygame.sprite.Group()
waiting_list = pygame.sprite.Group()


#Make waiting cars (out of screen)
for i in range(3):
    # This represents a block
    car = Car(BLACK, lane_center[i],screen_height + 40)
 
    # Set a random location for the block
    car.lane = i-1
 
    # Add the block to the list of objects
    waiting_list.add(car)

 
# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
lane_speed = 4
lane_animate = 0
# -------- Main Program Loop -----------
while not done:
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            done = True
 
    # Clear the screen
    screen.fill(WHITE)
    
    #Draw road
    pygame.draw.line(screen, GREY, (5, 0), (5, screen_height), 3)
    pygame.draw.line(screen, GREY, (screen_width-5, 0), (screen_width-5, screen_height), 3)
    draw_dashed_line(screen, BLACK, (5 + lane_width, lane_animate), (5 + lane_width, screen_height), dash_length=lane_speed*3)
    draw_dashed_line(screen, BLACK, (5 + 2* lane_width, lane_animate), (5 + 2* lane_width, screen_height), dash_length=lane_speed*3)
    lane_animate += lane_speed
    lane_animate = lane_animate % (lane_speed * 5)

 
 
    #See if we spawn a new car
    for i, waiting_car in enumerate(waiting_list):
        #Spawn a car with propability and check it doesnt crash another car
        if np.random.rand() > 0.99 and (pygame.sprite.spritecollideany(waiting_car, car_list, collided = None) == None):
            #Add car to list of active cars
            car_list.add(waiting_car)
            waiting_car.remove(waiting_list)
            #Make a new car wait to spawn
            car = Car(BLACK, lane_center[car.lane], screen_height + 40)
            car.lane = np.random.randint(0,3)
            car.desiredlane = car.lane
            waiting_list.add(car)
    
    #Update cars
    for car in car_list:
        #Kill the car when it goes over the edge WORKS
        if car.rect.y < -40:
            car_list.remove(car)
            car.kill()
        
        #Move car foward in steps of its speed
        car.rect.y -= car.speed
        
        ##### FRONT CHECK ################################### WORKS
        # Create new list with all other cars in it
        car_list2.empty()
        car_list2 = car_list.copy()
        car_list2.remove(car) #Remove from the list so we can check collision
        
        #Put the car 0.5 car in front and see if it collides with any other car
        car.rect.top -= car.rect.height*0.5
        car_blocker = (pygame.sprite.spritecollideany(car, car_list2, collided = None))
        car.rect.top += car.rect.height*0.5
        if car_blocker:
            #Move the car back to initial position if change caussed collision
            car.rect.y += car.speed
            #Set the speed to the speed of the car ahead
            car.speed = car_blocker.speed
             
        ################################################
     
        
        
        
        #### LANE CHANGING ###################### #Changes lange 2/3 down the road
        #Change lane at 2/3 the road
        if (car.rect.y <= 3*screen_height/4):
            car.desiredlane = 0
         
        """    
        #### Check lane ######################### Doesn't work fully, still dodgy
        if car.rect.left in lane_center:
            car.rect = pygame.rect.Rect(car.rect[0] - lane_width, car.rect[1] + 40*0.5, car.rect[2], car.rect[3] + 40*0.5)
            car_list3.add(car)
            car_list3.draw(screen)
            check = (pygame.sprite.spritecollideany(car, car_list2, collided = None)) == None
            car.rect = pygame.rect.Rect(car.rect[0] + lane_width, car.rect[1] - 40*0.5, car.rect[2], car.rect[3] - 40*0.5)
            car_list3.remove(car)
        else:
            check = True
        """
            
            
        #### Lane Check ver 2 ##############################
        check = True
        if car.rect.x in lane_center:
            ghostcar = Block(BLACK, car.rect.width, 2*car.rect.height)
            ghostcar.rect.x = lane_center[car.desiredlane]
            ghostcar.rect.y = car.rect.y - car.rect.height
            check = (pygame.sprite.spritecollideany(ghostcar, car_list2, collided = None)) == None
            if not check:
                ghostcar.image.fill(RED)
            car_list3.add(ghostcar)
            car_list3.draw(screen)
            car_list3.remove(ghostcar)
        
        
        
        ####################################################
            
        #Begin changing lane -> Animate a lane change
        if (car.desiredlane != car.lane) and check:
            if car.desiredlane < car.lane:
                car.rect.x -= 1
            else:
                car.rect.x += 1
            if abs(car.rect.x - lane_center[car.desiredlane]) < 2:
                car.lane = car.desiredlane
        #########################################
                
            
    # Draw all the spites
    car_list.draw(screen)
 
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
    print(len(car_list))
    #print(pygame.time.get_ticks())
 
    # Limit to 60 frames per second
    clock.tick(FPS)
 
pygame.quit()
