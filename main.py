import time

from vehicle import Vehicle
from simulation import Simulation
from animation import max_road_len
from animation_opengl import Animation, AnimationInterrupt

class Config:
    fps = 60
    nb_lanes = 4
    road_len = 1000         # meter, set as derived value
    spawn_rate = 7.0        # cars per second
    speed_range = (25, 35)  # (min, max) speed in meter/sec
    extremely_safe_distance = 5.0     # meter

    speedup = 1.0           # sec in animation = speedup*sec in simulation

    # Animation
    window_width = 1800
    rows = 3                # number of wrapped roads vertically
    scale = 5               # pixels per meter

def start_sim():
    conf = Config()
    sim = Simulation(conf)
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

if __name__ == "__main__":
    start_sim()
