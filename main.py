import time

from vehicle import Vehicle
from simulation import Simulation
from animation import Animation, AnimationInterrupt

class Config:
    fps = 30
    nb_lanes = 3
    road_len = 350          # meter
    spawn_rate = 5.0        # cars per second
    speed_range = (25, 35)  # (min, max) speed in meter/sec
    safe_distance = 10.0    # meter

def start_sim():
    conf = Config()
    sim = Simulation(conf)
    anim = Animation(sim, conf)
    dt = 1./conf.fps

    try:
        while True:
            sim.time_step(dt)    # update simulation step
            anim.draw_frame()    # update animation
    except (KeyboardInterrupt, AnimationInterrupt):
        print()
        print("Simulation interrupted.")
    finally:
        anim.destroy()

if __name__ == "__main__":
    start_sim()
