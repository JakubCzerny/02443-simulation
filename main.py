import time

from vehicle import Vehicle
from simulation import SimulationWithHandlers
from animation import max_road_len
from animation_opengl import Animation, AnimationInterrupt
from sim_event_handler import SlowZoneEvHandler, StatsEvHandler

class Config:
    fps = 60
    nb_lanes = 3
    road_len = 600          # meter, set as derived value
    spawn_rate = 1.0        # cars per second
    speed_range = (25, 35)  # (min, max) speed in meter/sec

    speedup = 2.0           # sec in animation = speedup*sec in simulation

    # Animation
    window_width = 1800
    rows = 2                # number of wrapped roads vertically

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
