from vehicle import Vehicle
from vehicle_container import VehicleContainer as Container

class Simulation:

    def __init__(self, nb_lanes=1):
        self._time = 0
        self._nb_lanes = nb_lanes
        self._container = Container(nb_lanes)

    def time_step(self):
        self._time += 1

        # loop over all vehicles, update all vehicles
        # remove vehicles that are dead
        it = iter(self._container)
        for v in it:
            v.time_step(self._container, self._time)

        self.try_spawn_vehicle()

    def try_spawn_vehicle(self):
        # draw a number from some distribution and decide whether to spawn a
        # car in a certain lane
        if self._time % 5 == 0:
            self._container.insert(Vehicle())
