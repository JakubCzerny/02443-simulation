import time

from vehicle import Vehicle
from simulation import Simulation

def start_sim():
    sim = Simulation()

    try:
        while True:
            sim.time_step()
            # call animation stuff
            time.sleep(0.2)
    except KeyboardInterrupt:
        print()
        print("Simulation interrupted.")

if __name__ == "__main__":
    start_sim()

