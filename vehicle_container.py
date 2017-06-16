from vehicle import Vehicle
from sortedcontainers import SortedList

class SneakyVehicle(Vehicle):

    def __init__(self, lane):
        self._sneaky_lane = lane
        super().__init__(lane)

class VehicleContainer:
    def __init__(self, nb_lanes):
        self._nb_lanes = nb_lanes
        self._lists = [SortedList() for i in range(nb_lanes)]

    def __iter__(self):
        return VehicleContainerIter(self)

    def get_front(self, vehicle):
        i = self._lists[vehicle.lane].index(vehicle)
        return self._lists[vehicle.lane][i+1]

    def get_back(self, vehicle):
        i = self._lists[vehicle.lane].index(vehicle)
        return self._lists[vehicle.lane][i-1]

    def get_left(self, vehicle):
        lane = vehicle.lane - 1
        return self.get_closest_vehicle(vehicle, vehicle.lane-1)

    def get_right(self, vehicle):
        return self.get_closest_vehicle(vehicle, vehicle.lane+1)

    def get_closest_vehicle(self, vehicle, lane):
        if lane in range(self._nb_lanes) and len(self._lists[lane]) > 0:
            l = self._lists[lane]
            b = l.bisect(vehicle)
            v1 = l[max(0, b-1)]
            v2 = l[min(b, len(l)-1)]
            d1 = abs(v1.position-vehicle.position)
            d2 = abs(v2.position-vehicle.position)
            if d1 < d2:
                return v1
            else:
                return v2
        return None

    def spawn_in_lane(self, lane):
        vehicle = SneakyVehicle(lane)
        self._lists[lane].add(vehicle)
        return vehicle

    def notify_update(self, vehicle):
        # lane change -> update data structure
        # if vehicle off the road -> remove from data structure
        if not vehicle._sneaky_lane is vehicle.lane:
            print('lane change for vehicle ', vehicle)

class VehicleContainerIter:

    def __init__(self, container):
        self._container = container
        self._iters = [iter(l) for l in container._lists]

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

###########################################################
#                       UNIT TESTS                        #
###########################################################

import unittest

class VehicleContainerTest(unittest.TestCase):

    def test_front_behind(self):
        container = VehicleContainer(1)

        v1 = container.spawn_in_lane(0)
        v1.position = 1 # move v1 forward a little bit
        v2 = container.spawn_in_lane(0)

        assert container.get_front(v2) is v1
        assert container.get_back(v1) is v2

    def test_left_right1(self):
        container = VehicleContainer(3)

        v1 = container.spawn_in_lane(0)
        v2 = container.spawn_in_lane(1)

        assert container.get_left(v2) is v1
        assert container.get_right(v1) is v2

    def test_left_right2(self):
        container = VehicleContainer(2)

        v1 = container.spawn_in_lane(0)
        v1.position = 2 # move v1 forward
        v2 = container.spawn_in_lane(0)
        v2.position = 1 # move v2 forward
        v3 = container.spawn_in_lane(1)

        assert container.get_left(v3) is v2
        assert container.get_front(v2) is v1
        assert container.get_left(v1) is None
        assert container.get_right(v1) is v3
        assert container.get_right(v2) is v3

    def test_left_right3(self):
        container = VehicleContainer(2)

        v1 = container.spawn_in_lane(0)
        v1.position = 5
        v2 = container.spawn_in_lane(0)
        v2.position = 1
        v3 = container.spawn_in_lane(1)
        v3.position = 2

        assert container.get_left(v3) is v2
        v3.position = 5
        assert container.get_left(v3) is v1

    def test_left_right4(self):
        container = VehicleContainer(3)

        v1 = container.spawn_in_lane(0)
        v1.position = 4
        v2 = container.spawn_in_lane(0)
        v2.position = 3
        v3 = container.spawn_in_lane(0)
        v3.position = 0
        v4 = container.spawn_in_lane(1)
        v4.position = 2
        v5 = container.spawn_in_lane(2)
        v5.position = 4
        v6 = container.spawn_in_lane(2)
        v6.position = 2

        assert container.get_left(v4) is v2
        assert container.get_right(v4) is v6

if __name__ == '__main__':
    unittest.main()
