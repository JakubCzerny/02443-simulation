
class SimEventHandler:
    """
    A simulation handler allows you to add additional behavior to the base
    simulation, e.g. to collect statistics or modify car behavior.

    It contains a bunch of methods that are called by the simulation at
    specific moments in the simulation. These methods should be overwritten by
    sub-classes.
    """

    _sim = None

    def before_time_step(self, dt):
        pass

    def after_time_step(self, dt):
        pass

    def before_vehicle_update(self, dt, vehicle):
        pass

    def after_vehicle_update(self, dt, vehicle):
        pass

    def before_vehicle_despawn(self, vehicle):
        pass

class SlowZoneEvHandler(SimEventHandler):
    """
    Simulation handler that forces cars to go slow down in a certain section of
    the road.
    """

    def __init__(self, start, stop, max_velocity=10):
        """ Section of road defined by [start, stop], in meters. """
        self._start = start
        self._stop = stop
        self._max_velocity = max_velocity

    def after_vehicle_update(self, dt, vehicle):
        if vehicle.position > self._start and vehicle.position < self._stop:
            if vehicle.velocity > self._max_velocity:
                vehicle.acceleration = -3

class StatsEvHandler(SimEventHandler):
    """
    Simulation handler that collects statistics.
    """

    def __init__(self):
        self.unspawned_count = 0

    def before_vehicle_despawn(self, vehicle):
        self.unspawned_count += 1

    def __str__(self):
        return """
        Statistics summary:
         - unspawned_count: {}
        """.format(self.unspawned_count)
