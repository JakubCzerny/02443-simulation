import numpy as np

from vehicle_container import VehicleContainer as Container
from vehicle import Vehicle, HumanVehicle, Car, Truck
import pygame

class Simulation:

    def __init__(self, conf):
        self._conf = conf
        self._container = Container(conf.nb_lanes)
        self._sim_time = 0
        self._time_to_next_spawn = 0
        self.sound = conf.sound

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
            self._despawn_vehicle(vehicle)

    def _despawn_vehicle(self, vehicle):
        self._container.despawn(vehicle)

    def try_spawn_vehicle(self): #Tried to fix the spawning issue

        # If the time has come to spawn new vehicle.
        if self._sim_time >= self._time_to_next_spawn:
            p = np.random.rand()
            if p > 0.9:
                lane = self._conf.nb_lanes - 1
                vehicle = Truck(lane)
            else:
                lane = np.random.randint(self._conf.nb_lanes)
                vehicle = Car(lane)
            vehicle.velocity = np.random.uniform(
                        self._conf.speed_range[0],
                        self._conf.speed_range[1])

            # If there already exists a vehicle in the lane.
            if self._container.last(lane):
                last = self._container.last(lane)
                # If the safe distance is not held, don't spawn.
                if last.position < last.extremely_safe_distance * 2:
                    self._time_to_next_spawn = self._sim_time + \
                        np.random.exponential(1/self._conf.spawn_rate)
                    return

                # Else if distance is below 5 safe_distances, spawn with
                # velocity depending on car in front.
                elif last.position < (last.extremely_safe_distance * last.velocity*10):
                    vehicle.velocity = np.random.uniform(
                        last.velocity*0.5,
                        last.velocity*min(1, last.position/(2*last.extremely_safe_distance) + 1))


            # Spawn the car.
            self._container.spawn(vehicle)
            if isinstance(vehicle, Truck) and self.sound:
                truckyeah = pygame.mixer.Sound('truckyeah.wav')
                truckyeah.play()

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


###############################################################################
#                      SIMULATION WITH HANDLERS                               #
###############################################################################

class SimulationWithHandlers(Simulation):

    def __init__(self, conf, handlers=[]):
        super().__init__(conf)
        self._handlers = handlers

        for h in self._handlers:
            h._sim = self

    def add_handler(self, handler):
        self._handlers.append(handler)

    def time_step(self, dt):
        for h in self._handlers:
            h.before_time_step(dt, self._sim_time)

        super().time_step(dt)

        for h in self._handlers:
            h.after_time_step(dt, self._sim_time)

    def time_step_vehicle(self, vehicle, dt):
        for h in self._handlers:
            h.before_vehicle_update(dt, vehicle)

        super().time_step_vehicle(vehicle, dt)

        for h in self._handlers:
            h.after_vehicle_update(dt, vehicle)

    def _despawn_vehicle(self, vehicle):
        for h in self._handlers:
            h.before_vehicle_despawn(vehicle)

        super()._despawn_vehicle(vehicle)
