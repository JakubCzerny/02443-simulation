import numpy as np

from vehicle_container import VehicleContainer as Container
from vehicle import Vehicle, HumanVehicle

class Simulation:

    def __init__(self, conf):
        self._conf = conf
        self._container = Container(conf.nb_lanes)
        self._sim_time = 0
        self._time_to_next_spawn = 0

    def time_step(self, dt):
        # loop over all vehicles, update all vehicles
        # remove vehicles that are dead
        for v in self:
            self.time_step_vehicle(v, dt)

        self.try_spawn_vehicle()
        self._sim_time += dt

    def time_step_vehicle(self, vehicle, dt):
        vehicle.update(self._conf, self._container, dt)

        if vehicle.position > self._conf.road_len:
            self._container.despawn(vehicle)

    def try_spawn_vehicle(self): #Tried to fix the spawning issue

        # If the time has come to spawn new vehicle.
        if self._sim_time >= self._time_to_next_spawn:
            lane = np.random.randint(self._conf.nb_lanes)
            vehicle = HumanVehicle(lane)
            vehicle.velocity = np.random.uniform(
                        self._conf.speed_range[0],
                        self._conf.speed_range[1])

            # If there already exists a vehicle in the lane.
            if self._container.last(lane):
                last = self._container.last(lane)
                # If the safe distance is not held, don't spawn.
                if last.position < self._conf.extremely_safe_distance * 2:
                    self._time_to_next_spawn = self._sim_time + \
                        np.random.exponential(1/self._conf.spawn_rate)
                    return

                # Else if distance is below 5 safe_distances, spawn with
                # velocity depending on car in front.
                elif last.position < self._conf.extremely_safe_distance * 5:
                    vehicle.velocity = np.random.uniform(
                        last.velocity*0.5,
                        last.velocity*min(1, last.position/(2*self._conf.extremely_safe_distance) + 1))


            # Spawn the car.
            self._container.spawn(vehicle)

            # Find time to next car.
            self._time_to_next_spawn = self._sim_time + \
                    np.random.exponential(1/self._conf.spawn_rate)

    def find_vehicle(self, pos, lane, max_dist=10):
        v = Vehicle(lane)
        v.position = pos
        w = self._container.get_closest_vehicle(v, lane)

        if w and abs(w.position-pos) < max_dist:
            return w
        return None

    def __iter__(self):
        return iter(self._container)
