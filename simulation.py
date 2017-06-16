import numpy as np

from vehicle_container import VehicleContainer as Container
from vehicle import Vehicle

class Simulation:

    def __init__(self, nb_lanes, road_len):
        self._time = 0
        self._nb_lanes = nb_lanes
        self._road_len = road_len
        self._container = Container(nb_lanes)

    def time_step(self, dt):
        self._time += 1

        # loop over all vehicles, update all vehicles
        # remove vehicles that are dead
        it = iter(self._container)
        for v in it:
            self.time_step_vehicle(v, dt)

        self.try_spawn_vehicle()

    def time_step_vehicle(self, vehicle, dt):
        vehicle.position += dt*vehicle.velocity \
                + .5*dt*dt*vehicle.acceleration

        if vehicle.position > self._road_len:
            self._container.despawn(vehicle)
            print(vehicle, " despawned")
        else:
            print(vehicle)

        # notify container if lane change!

    def try_spawn_vehicle(self):
        # draw a number from some distribution and decide whether to spawn a
        # car in a certain lane
        if np.random.rand() > .9:
            v = Vehicle(np.random.randint(self._nb_lanes))
            self._container.spawn(v)

    def __iter__(self):
        return iter(self._container)
