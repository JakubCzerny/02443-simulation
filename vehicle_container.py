from vehicle import Vehicle

class _Node:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.front = None
        self.back = None

class _LList:
    def __init__(self):
        self.head = _Node(None)
        self.tail = _Node(None)
        self.map = {}

        self.head.front = self.tail
        self.tail.back = self.head

    def __iter__(self):
        return _LListBackIter(self)

    def insert_front(self, vehicle):
        node = _Node(vehicle)
        node.back = self.head
        node.front = self.head.front
        self.head.front.back = node
        self.head.front = node

        self.map[vehicle] = node

    def remove_back(self):
        node = self.tail.back

        node.back.front = self.tail
        self.tail.back = node.back
        node.back = None
        node.front = None

        del self.map[node.vehicle]

        return node.vehicle

    def get_node(self, vehicle):
        if not vehicle in self.map:
            raise Exception("vehicle not in list")

        return self.map[vehicle]

class _LListBackIter:

    def __init__(self, l):
        self.node = l.tail

    def __iter__(self):
        return self

    def __next__(self):
        if self.node.back.vehicle is not None:
            self.node = self.node.back
            return self.node.vehicle
        else:
            raise StopIteration

    def peek(self):
        return self.node.vehicle

class VehicleContainer:
    def __init__(self, nb_lanes):
        self._map = {}
        self._lists = [_LList()] * nb_lanes

    def __iter__(self):
        return VehicleContainerIter(self)

    def get_front(self, vehicle):
        return self._lists[vehicle.lane].get_node(vehicle).front.vehicle

    def get_back(self, vehicle):
        return self._lists[vehicle.lane].get_node(vehicle).back.vehicle

    def get_left(self, vehicle):
        raise NotImplementedError

    def get_rigth(self, vehicle):
        raise NotImplementedError

    def insert(self, vehicle):
        self._lists[vehicle.lane].insert_front(vehicle)

    def notify_update(self, vehicle):
        # lane change -> update data structure
        # if vehicle off the road -> remove from data structure
        pass

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

    def test_LList(self):
        l = _LList()
        n = 10

        for i in range(n):
            l.insert_front(i)

        it = iter(l)
        for (i,j) in zip(range(n), it):
            assert i == it.peek()
            assert i == j

        for i in range(n):
            assert l.remove_back() == i

    def test_front_behind(self):
        container = VehicleContainer(1)
        v1 = Vehicle()
        v2 = Vehicle()

        container.insert(v1)
        container.insert(v2)

        assert container.get_front(v2) is v1
        assert container.get_back(v1) is v2

if __name__ == '__main__':
    unittest.main()
