""" This should not depend on anything else. This is a simple value type. """

class Vehicle:

    def __init__(self, time_offset=0):
        self.position = 0
        self.lane = 0
        self.speed = 0
        self.acceleration = 0
        self.time_offset = time_offset

    def time_step(self, container, time):
        # after modifying state of vehicle, make sure the data structure is
        # updated according to the changes
        container.notify_update(self)
