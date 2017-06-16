""" This should not depend on anything else. This is a simple value type. """

class Vehicle:

    def __init__(self, lane):
        self.lane = lane
        self.position = 0
        self.velocity = 0
        self.acceleration = 0

    def __lt__(self, other):
        return isinstance(other, Vehicle) and self.position < other.position

    def __str__(self):
        return "Vehicle[lane={}, pos={}, vel={}, acc={}]" \
            .format(self.lane, self.position, self.velocity, self.acceleration)
