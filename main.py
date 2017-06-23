#!/usr/bin/python

import time
import pygame

from vehicle import Vehicle
from simulation import SimulationWithHandlers
from animation import max_road_len
from animation_opengl import Animation

from animation_base import AnimationInterrupt
from animation_opengl import Animation
from sim_event_handler import *

class Config:
    fps = 60
    nb_lanes = 3
    road_len = 600          # meter
    spawn_rate = 5.0        # cars per second
    speed_range = (25, 35)  # (min, max) speed in meter/sec

    speedup = 1             # int speed up factor: 1 sec in anim = speedup sec in sim

    # Animation
    window_height = 370
    rows = 3                # number of wrapped roads vertically
    window_width = 1800

    sound = False

    # Non-OpenGL animation specific configuration
    #window_height = 500
    #scale = 10
    #road_len = -1

def start_sim():
    conf = Config()

    sim = SimulationWithHandlers(conf)
    anim = Animation(sim, conf)
    dt = 1./conf.fps

    stats = StatsEvHandler()
    sim.add_handler(stats)
    avgspeed = AverageSpeedHandler()
    sim.add_handler(avgspeed)
    throughput = ThroughPutHandler()
    sim.add_handler(throughput)
    traveltime = TravelTimeHandler()
    sim.add_handler(traveltime)
    vehicle_count = VehicleCountHandler()
    sim.add_handler(vehicle_count)

    slow_zone1 = SlowZoneEvHandler(300, 450, max_velocity=7)
    slow_zone1.enabled = False   # disabled by default, enable by pressing O
    sim.add_handler(slow_zone1)
    anim.register_interactive_sim_handler(slow_zone1, pygame.K_o)
    slow_zone2 = SlowZoneEvHandler(300, 450, max_velocity=0)
    slow_zone2.enabled = False   # disabled by default, enable by pressing P
    sim.add_handler(slow_zone2)
    anim.register_interactive_sim_handler(slow_zone2, pygame.K_p)

    try:
        while True:
            for i in range(conf.speedup):
                sim.time_step(conf.speedup*dt)
            anim.draw_frame()
    except (KeyboardInterrupt, AnimationInterrupt):
        print()
        print("Simulation interrupted.")
    finally:
        anim.destroy()

    print(stats)
    avgspeed.plot()
    throughput.plot()
    traveltime.plot()
    vehicle_count.plot()

if __name__ == "__main__":
    start_sim()
