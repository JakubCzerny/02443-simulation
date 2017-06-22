import time
import pygame

from vehicle import Vehicle
from simulation import SimulationWithHandlers
from animation import max_road_len
from animation_opengl import Animation

from animation_base import AnimationInterrupt
from animation_opengl import Animation
from sim_event_handler import SlowZoneEvHandler, StatsEvHandler, AverageSpeedHandler

class Config:
    fps = 60
    nb_lanes = 3
    road_len = 600          # meter, set as derived value
    spawn_rate = 1.0        # cars per second
    speed_range = (25, 35)  # (min, max) speed in meter/sec

    speedup = 1.0           # sec in animation = speedup*sec in simulation

    # Animation
    window_height = 370
    rows = 3               # number of wrapped roads vertically
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

    slow_zone1 = SlowZoneEvHandler(300, 450, max_velocity=7)
    slow_zone1.enabled = False   # disabled by default, enable by pressing S
    sim.add_handler(slow_zone1)
    anim.register_interactive_sim_handler(slow_zone1, pygame.K_s)
    slow_zone2 = SlowZoneEvHandler(300, 450, max_velocity=0)
    slow_zone2.enabled = False   # disabled by default, enable by pressing T
    sim.add_handler(slow_zone2)
    anim.register_interactive_sim_handler(slow_zone2, pygame.K_t)

    try:
        while True:
            sim.time_step(conf.speedup*dt)
            anim.draw_frame()
    except (KeyboardInterrupt, AnimationInterrupt):
        print()
        print("Simulation interrupted.")
    finally:
        anim.destroy()

    print(stats)
    # avgspeed.plot()

if __name__ == "__main__":
    start_sim()
