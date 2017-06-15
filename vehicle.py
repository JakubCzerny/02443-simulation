""" This should not depend on anything else. This is a simple value type. """

class Vehicle:

    def __init__(self):
        self._position = 0
        self._lane = 0
        self._speed = 0
        self._acceleration = 0
        self._time_offset = 0

    def time_step(self, container, time):
        # after modifying state of vehicle, make sure the data structure is
        # updated according to the changes
        container.notify_update(self)
