import time

from vehicle import Vehicle
from simulation import Simulation

def start_sim():
    time_delta = 0.1 # << seconds, vv meters
    sim = Simulation(nb_lanes=3, road_len=100)

    try:
        while True:
            sim.time_step(time_delta)
            # call animation stuff
            time.sleep(time_delta)
    except KeyboardInterrupt:
        print()
        print("Simulation interrupted.")

if __name__ == "__main__":
    start_sim()

