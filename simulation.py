import numpy as np

from vehicle_container import VehicleContainer as Container
from vehicle import Vehicle, HumanVehicle

class Simulation:

    def __init__(self, conf):
        self._conf = conf
        self._container = Container(conf.nb_lanes)

    def time_step(self, dt):
        # loop over all vehicles, update all vehicles
        # remove vehicles that are dead
        it = iter(self._container)
        for v in it:
            self.time_step_vehicle(v, dt)

        self.try_spawn_vehicle()

    def time_step_vehicle(self, vehicle, dt):
        vehicle.update(self._conf, self._container, dt)

        if vehicle.position > self._conf.road_len:
            self._container.despawn(vehicle)

    def try_spawn_vehicle(self):
        if np.random.rand() < self._conf.spawn_rate / self._conf.fps:
            lane = np.random.randint(self._conf.nb_lanes)

            if self._container.last(lane):
                last = self._container.last(lane)
                if last.position < self._conf.safe_distance:
                    return

            vehicle = HumanVehicle(lane)
            vehicle.velocity = np.random.uniform( \
                    self._conf.speed_range[0],    \
                    self._conf.speed_range[1])
            self._container.spawn(vehicle)

    def __iter__(self):
        return iter(self._container)
