""" This should not depend on anything else. This is a simple value type. """

class Vehicle:

    def __init__(self, lane, position=0.0):
        self.lane = lane
        self.position = position # meter
        self.velocity = 33.0     # meter/sec
        self.acceleration = 0.0  # meter/sec²

    def __lt__(self, other):
        return isinstance(other, Vehicle) and self.position < other.position

    def __str__(self):
        return "Vehicle[lane={:2n}, pos={:06.2f}, vel={:06.2f}, acc={:06.2f}]" \
            .format(self.lane, self.position, self.velocity, self.acceleration)
