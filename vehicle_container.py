
class VehicleContainer:

    def __init__(self, nb_lanes):
        pass

    def get_front(self, vehicle):
        pass

    def get_behind(self, vehicle):
        pass

    def get_left(self, vehicle):
        pass

    def get_rigth(self, vehicle):
        pass

    def insert(self, vehicle):
        print("vehicle added")

    def notify_update(self, vehicle):
        # lane change -> update data structure
        # if vehicle off the road -> remove from data structure
        pass

    def __iter__(self):
        return VehicleContainerIter(self)

class VehicleContainerIter:
    def __init__(self, container):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration
