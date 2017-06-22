import matplotlib.pyplot as plt
class SimEventHandler:
    """
    A simulation handler allows you to add additional behavior to the base
    simulation, e.g. to collect statistics or modify car behavior.

    It contains a bunch of methods that are called by the simulation at
    specific moments in the simulation. These methods should be overwritten by
    sub-classes.
    """

    _sim = None
    enabled = True

    def before_time_step(self, dt):
        pass

    def after_time_step(self, dt, sim_time):
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
        if self.enabled and vehicle.position > self._start and vehicle.position < self._stop:
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

class AverageSpeedHandler(SimEventHandler):

    def __init__(self):
        self.averageSpeed = 0
        self.numberOfVehicles = 0
        self.averageSpeedList = []
        self.simTimeList = []
        self.updatecount = 0

    def after_vehicle_update(self, dt, vehicle):
        self.averageSpeed += vehicle.velocity
        self.numberOfVehicles += 1

    def after_time_step(self, dt, sim_time):
        self.updatecount += 1
        if self.updatecount > 3: #Only update ever 3. timestep 
            if self.numberOfVehicles > 0:
                self.averageSpeedList.append(self.averageSpeed / self.numberOfVehicles)
                self.averageSpeed = 0
                self.numberOfVehicles = 0
                self.simTimeList.append(sim_time)
            self.updatecount = 0

    def plot(self):
        plt.figure()
        plt.plot(self.simTimeList, self.averageSpeedList)
        plt.xlabel("Time [s]")
        plt.ylabel("Average speed of cars [m/s]")
        plt.show()
        print(len(self.simTimeList))
