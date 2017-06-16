import numpy as np

from vehicle_container import VehicleContainer as Container
from vehicle import Vehicle

class Simulation:

    def __init__(self, nb_lanes):
        self._time = 0
        self._nb_lanes = nb_lanes
        self._container = Container(nb_lanes)

    def time_step(self):
        self._time += 1

        # loop over all vehicles, update all vehicles
        # remove vehicles that are dead
        it = iter(self._container)
        for v in it:
            self.time_step_vehicle(v)

        self.try_spawn_vehicle()

    def time_step_vehicle(self, vehicle):
        vehicle.position += 1
        print(vehicle)
        self._container.notify_update(vehicle)

    def try_spawn_vehicle(self):
        # draw a number from some distribution and decide whether to spawn a
        # car in a certain lane
        if self._time % 5 == 0:
            self._container.spawn_in_lane(np.random.randint(self._nb_lanes))

    def __iter__(self):
        return iter(self._container)
