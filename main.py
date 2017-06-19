import time

from vehicle import Vehicle
from simulation import Simulation
from animation import Animation, AnimationInterrupt

def start_sim():
    fps = 30
    sim = Simulation(nb_lanes=3, road_len=350) # road len in meters
    anim = Animation(sim, fps)

    try:
        while True:
            sim.time_step(anim.delta_time())   # update simulation step
            anim.draw_frame()                  # update animation
    except (KeyboardInterrupt, AnimationInterrupt):
        print()
        print("Simulation interrupted.")
    finally:
        anim.destroy()

if __name__ == "__main__":
    start_sim()
