from vehicle import Vehicle
from sortedcontainers import SortedList

class VehicleContainer:
    def __init__(self, nb_lanes):
        self._nb_lanes = nb_lanes
        self._lists = [SortedList() for i in range(nb_lanes)]

    def __iter__(self):
        return VehicleContainerIter(self)

    def front(self, vehicle):
        i = self._lists[vehicle.lane].index(vehicle)
        if i+1 >= len(self._lists[vehicle.lane]):
            return None
        return self._lists[vehicle.lane][i+1]

    def back(self, vehicle):
        i = self._lists[vehicle.lane].index(vehicle)
        if i == 0:
            return None
        return self._lists[vehicle.lane][i-1]

    def left(self, vehicle):
        lane = vehicle.lane - 1
        return self.get_closest_vehicle(vehicle, vehicle.lane-1)

    def right(self, vehicle):
        return self.get_closest_vehicle(vehicle, vehicle.lane+1)

    def first(self, lane):
        if len(self._lists[lane]) > 0:
            return self._lists[lane][-1]
        return None

    def last(self, lane):
        if len(self._lists[lane]) > 0:
            return self._lists[lane][0]
        return None

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

    def spawn(self, vehicle):
        self._lists[vehicle.lane].insert(0, vehicle)
        return vehicle

    def despawn(self, vehicle):
        if not vehicle in self._lists[vehicle.lane]:
            raise ValueError("vehicle not in container")
        self._lists[vehicle.lane].discard(vehicle)

    def notify_lane_change(self, vehicle, old_lane):
        i = self._lists[old_lane].index(vehicle)
        del self._lists[old_lane][i]

        self._lists[vehicle.lane].add(vehicle)

_DUMMY_VEHICLE = Vehicle(0);
_DUMMY_VEHICLE.position = -999;

class VehicleContainerIter:
    def __init__(self, container):
        self._container = container
        self._iters = [reversed(l) for l in container._lists]
        self._values = [_next_aux(it) for it in self._iters]

    def __iter__(self):
        return self

    def __next__(self):
        mi, mv = max(enumerate(self._values), key=lambda t: t[1])
        if mv is _DUMMY_VEHICLE:
            raise StopIteration

        self._values[mi] = _next_aux(self._iters[mi])
        return mv

def _next_aux(it):
    try:
        return it.__next__()
    except StopIteration:
        return _DUMMY_VEHICLE

###########################################################
#                       UNIT TESTS                        #
###########################################################

import unittest

class VehicleContainerTest(unittest.TestCase):

    def test_front_behind(self):
        container = VehicleContainer(1)

        v1 = container.spawn(Vehicle(0, position=1))
        v2 = container.spawn(Vehicle(0))

        self.assertEqual(container.front(v2), v1)
        self.assertEqual(container.back(v1), v2)
        self.assertIsNone(container.front(v1))
        self.assertIsNone(container.back(v2))

    def test_left_right1(self):
        container = VehicleContainer(3)

        v1 = container.spawn(Vehicle(0))
        v2 = container.spawn(Vehicle(1))

        self.assertEqual(container.left(v2), v1)
        self.assertEqual(container.right(v1), v2)

    def test_left_right2(self):
        container = VehicleContainer(2)

        v1 = container.spawn(Vehicle(0, position=2))
        v2 = container.spawn(Vehicle(0, position=1))
        v3 = container.spawn(Vehicle(1))

        self.assertEqual(container.left(v3), v2)
        self.assertEqual(container.front(v2), v1)
        self.assertEqual(container.right(v1), v3)
        self.assertEqual(container.right(v2), v3)
        self.assertIsNone(container.left(v1))

    def test_left_right3(self):
        container = VehicleContainer(2)

        v1 = container.spawn(Vehicle(0, position=5))
        v2 = container.spawn(Vehicle(0, position=1))
        v3 = container.spawn(Vehicle(1, position=2))

        self.assertEqual(container.left(v3), v2)
        v3.position = 5
        self.assertEqual(container.left(v3), v1)

    def test_left_right4(self):
        container = VehicleContainer(3)

        v1 = container.spawn(Vehicle(0, position=4))
        v2 = container.spawn(Vehicle(0, position=3))
        v3 = container.spawn(Vehicle(0, position=0))
        v4 = container.spawn(Vehicle(1, position=2))
        v5 = container.spawn(Vehicle(2, position=4))
        v6 = container.spawn(Vehicle(2, position=2))

        self.assertEqual(container.left(v4), v2)
        self.assertEqual(container.right(v4), v6)

    def test_iter(self):
        container = VehicleContainer(3)
        v1 = container.spawn(Vehicle(0, position=4))
        v2 = container.spawn(Vehicle(0, position=3))
        v3 = container.spawn(Vehicle(0, position=0))
        v4 = container.spawn(Vehicle(1, position=2))
        v5 = container.spawn(Vehicle(2, position=1))

        for v, w in zip([v1, v2, v4, v5, v3], iter(container)):
            self.assertEqual(v, w)

    def test_first_last(self):
        container = VehicleContainer(1)
        v1 = container.spawn(Vehicle(0, position=5.0))
        v2 = container.spawn(Vehicle(0))

        self.assertEqual(container.first(0), v1)
        self.assertEqual(container.last(0), v2)

    def test_despawn(self):
        container = VehicleContainer(1)
        v1 = container.spawn(Vehicle(0, position=5.0))
        v2 = container.spawn(Vehicle(0))

        container.despawn(v1)

        self.assertEqual(container.first(0), v2)
        self.assertEqual(container.last(0), v2)

    def test_notify_lane_change(self):
        container = VehicleContainer(2)
        v1 = container.spawn(Vehicle(0, position=5.0))
        v2 = container.spawn(Vehicle(1, position=7.0))

        self.assertEqual(container.first(0), v1)
        self.assertEqual(container.first(1), v2)
        self.assertEqual(container.left(v2), v1)
        self.assertEqual(container.right(v1), v2)
        self.assertIsNone(container.front(v1))
        self.assertIsNone(container.front(v2))
        self.assertIsNone(container.back(v1))
        self.assertIsNone(container.back(v2))

        v1.lane = 1
        container.notify_lane_change(v1, 0)

        self.assertEqual(container.first(1), v2)
        self.assertEqual(container.last(1), v1)
        self.assertEqual(container.front(v1), v2)
        self.assertEqual(container.back(v2), v1)
        self.assertIsNone(container.first(0))

if __name__ == '__main__':
    unittest.main()
