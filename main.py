import time

from vehicle import Vehicle
from simulation import SimulationWithHandlers
from animation_opengl import Animation
from animation_base import AnimationInterrupt
from animation_opengl import Animation
from sim_event_handler import SlowZoneEvHandler, StatsEvHandler

class Config:
    fps = 60
    nb_lanes = 3
    road_len = 600          # meter, set as derived value
    spawn_rate = 1.0        # cars per second
    speed_range = (25, 35)  # (min, max) speed in meter/sec

    speedup = 1.0           # sec in animation = speedup*sec in simulation

    # Animation
    window_height = 370
    scale = 4  
    rows = 3               # number of wrapped roads vertically
    window_width = 1800
    rows = 3                # number of wrapped roads vertically

    # Non-OpenGL animation specific configuration
    #window_height = 500
    #scale = 10
    #road_len = -1

def start_sim():
    conf = Config()

    sim = SimulationWithHandlers(conf)

    stats = StatsEvHandler()
    sim.add_handler(stats)
    #sim.add_handler(SlowZoneEvHandler(300, 350, max_velocity=7))   # uncomment this if you want a slow zone

    anim = Animation(sim, conf)
    dt = 1./conf.fps

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

if __name__ == "__main__":
    start_sim()
