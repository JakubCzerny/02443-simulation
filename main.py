import time

from vehicle import Vehicle
from simulation import Simulation
from animation import Animation, AnimationInterrupt, max_road_len

class Config:
    fps = 60
    nb_lanes = 3
    road_len = -1           # meter, set as derived value
    spawn_rate = 1.2       # cars per second
    speed_range = (25, 35)  # (min, max) speed in meter/sec
    safe_distance = 7.0     # meter

    # Animation
    window_width = 1800
    window_height = 600
    rows = 4               # number of wrapped roads vertically
    scale = 8              # pixels per meter

    def __init__(self):
        if self.road_len == -1:
            self.road_len = max_road_len(self)
            print('road_len set to', self.road_len)

def start_sim():
    conf = Config()
    sim = Simulation(conf)
    anim = Animation(sim, conf)
    dt = 1./conf.fps

    try:
        while True:
            sim.time_step(dt)
            anim.draw_frame()
    except (KeyboardInterrupt, AnimationInterrupt):
        print()
        print("Simulation interrupted.")
    finally:
        anim.destroy()

if __name__ == "__main__":
    start_sim()
