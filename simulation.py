import random
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
        self.make_move(vehicle, dt)
        self.update_position(vehicle, dt)

        if vehicle.position > self._road_len:
            self._container.despawn(vehicle)
            print(vehicle, " despawned")
        else:
            print(vehicle)

    def update_position(self, vehicle, dt):
        vehicle.position += dt*vehicle.velocity \
                + .5*dt*dt*vehicle.acceleration

    def update_acceleration(self,vehicle,acc):
        vehicle.acceleration = acc

    def update_velocity(self,vehicle,acc,dt):
        vehicle.velocity += acc * dt

    def go_right(self,vehicle):
        print(vehicle.lane, self._nb_lanes)
        vehicle.lane += 1
        self._container.notify_lane_change(vehicle, vehicle.lane-1)

    def go_left(self,vehicle):
        # print(vehicle.lane, self._nb_lanes)
        vehicle.lane -= 1
        self._container.notify_lane_change(vehicle, vehicle.lane+1)

    def make_move(self, vehicle, dt):
        veh_f = self._container.front(vehicle)
        af = veh_f.acceleration if veh_f else None
        vf = veh_f.velocity if veh_f else None
        df = veh_f.position  - vehicle.position if veh_f else None

        veh_b = self._container.back(vehicle)
        db = veh_b.position  - vehicle.position if veh_b else None

        veh_lf = self._container.left_front(vehicle)
        dlf = veh_lf.position - vehicle.position if veh_lf else None

        veh_lb = self._container.left_back(vehicle)
        dlb = veh_lb.position - vehicle.position if veh_lb else None

        veh_rf = self._container.right_front(vehicle)
        vrf = veh_rf.velocity if veh_rf else None
        drf = veh_rf.position - vehicle.position if veh_rf else None

        veh_rb = self._container.right_back(vehicle)
        drb = veh_rb.position - vehicle.position if veh_rb else None

        p = random.random()
        p_right = vehicle.prob_right(db, vrf, drf, drb)

        if p > p_right and vehicle.lane+1 < self._nb_lanes:
            self.go_right(vehicle)
        else:
            acc = vehicle.calc_acceleration(vf, df)

            if acc != 0:
                self.update_acceleration(vehicle, acc)
                self.update_velocity(vehicle, acc, dt)
            else:
                p = random.random()
                p_left = vehicle.prob_left(af, vf, df, dlf, vlf, dlb)

                if p > l_left and vehicle.lane > 0:
                    self.go_left(vehicle)


    def try_spawn_vehicle(self):
        # draw a number from some distribution and decide whether to spawn a
        # car in a certain lane
        if np.random.rand() > .9:
            v = Vehicle(np.random.randint(self._nb_lanes))
            self._container.spawn(v)

    def __iter__(self):
        return iter(self._container)
