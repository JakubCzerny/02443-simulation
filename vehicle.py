import numpy as np
import time
class Vehicle:

    def __init__(self, lane, position=0.0):
        self.lane = lane
        self.position = position # meter
        self.velocity = 0.0      # meter/sec
        self.acceleration = 0.0  # meter/sec²

        self.type = 'car'

        self.emergency = 0

    def __lt__(self, other):
        return self.position < other.position

    def __str__(self):
        return "Vehicle[lane={:2n}, pos={:06.2f}, vel={:06.2f}, acc={:06.2f}]" \
            .format(self.lane, self.position, self.velocity, self.acceleration)

    def update(self, conf, container, dt):
        new_position = self.position + dt*self.velocity + .5*dt*dt*self.acceleration
        new_velocity = max(0, self.velocity + self.acceleration*dt)

        # Emergency speed change: this should never occur, it should be
        # prevented by the proper acceleration/de-acceleration behavior.
        front = container.front(self)
        if front and abs(front.position-new_position) < .99*self.extremely_safe_distance:
            self.velocity = front.velocity
            self.acceleration = front.acceleration
            self.position = front.position - self.extremely_safe_distance

            self.emergency = conf.fps

            print('WARNING: Emergency speed change -- fix driver behavior in', \
                    self.__class__.__name__)
        else:
            self.position = new_position
            self.velocity = new_velocity
            self.emergency = max(0, self.emergency-1)



###############################################################################
#                        VEHICLE DRIVEN BY A HUMAN                            #
###############################################################################

# More names
#    [X]f  - front           [X]b  - back
#    [X]rf - right front     [X]rb - right back
#    [X]lf - left front      [X]lb - left back

class HumanVehicle(Vehicle):

    def __init__(self, lane, position=0.0):
        super().__init__(lane, position)

    def update(self, conf, container, dt):
        # First update position and velocity using previous acc/vel...
        super().update(conf, container, dt)

        # ... cap velocity by desired_velocity and...
        self.velocity = min(self.desired_velocity, self.velocity)

        # ... then update safe distance
        self.safe_distance = max(self.extremely_safe_distance, self.velocity * self.safe_time)
        # self.safe_distance = 7

        # ... then update acc/vel itself
        veh_f = container.front(self)
        af = veh_f.acceleration if veh_f else None
        vf = veh_f.velocity if veh_f else None
        df = veh_f.position  - self.position if veh_f else None

        veh_b = container.back(self)
        db = self.position - veh_b.position if veh_b else None

        veh_lf = container.left_front(self)
        vlf = veh_lf.velocity if veh_lf else None
        dlf = veh_lf.position - self.position if veh_lf else None

        veh_lb = container.left_back(self)
        vlb = veh_lb.velocity if veh_lb else None
        dlb = self.position - veh_lb.position if veh_lb else None

        veh_rf = container.right_front(self)
        vrf = veh_rf.velocity if veh_rf else None
        drf = veh_rf.position - self.position if veh_rf else None

        veh_rb = container.right_back(self)
        drb = self.position - veh_rb.position if veh_rb else None
        vrb = veh_rb.velocity if veh_rb else None

        p = np.random.rand()
        p_right = self.prob_right(conf, df, vf, db, vrf, drf, vrb, drb)
        p_left = self.prob_left(conf, af, vf, df, dlf, vlf, dlb, vlb)

        #NEW ONLY SWITCH IF THEY ARE ABOVE 3 SAFE_DISTANCES #####
        if time.time() - self.last_lane_change > (2.0/conf.speedup):
            if (p < p_right) and (self.lane+1 < conf.nb_lanes) and (self.position > (3 * self.safe_distance)):
                self.lane += 1
                container.notify_lane_change(self, self.lane-1)
                self.last_lane_change = time.time()
            elif (p < p_left) and (self.lane > 0) and (self.position > (3 * self.safe_distance)):
                self.lane -= 1
                container.notify_lane_change(self, self.lane+1)
                self.last_lane_change = time.time()
        #########################################################

        ### ANIMATION FOR LANE CHANGING
        if abs(self.animlane - self.lane) > 0.1:
            if self.animlane < self.lane:
                self.animlane = round(self.animlane + 0.1, 1)
            else:
                self.animlane = round(self.animlane - 0.1, 1)
        else:
            self.animlane = self.lane

        acc = self.calc_acceleration(conf, af, vf, df)
        self.acceleration = min(self.HV_AMAX, acc)

    def prob_left(self, conf, af, vf, df, dlf, vlf, dlb, vlb):
        p = 0

        if (df and df < self.HV_K1*self.safe_distance \
            and (self.desired_velocity - self.velocity > self.epsilon or self.desired_velocity - vf > self.epsilon) \
            and (not dlf or (dlf > self.HV_K*self.safe_distance)) \
            and (not dlb or (dlb > self.HV_K*self.safe_distance)) \
            and (not vlf or (self.velocity <= vlf or dlf >= self.HV_K2*self.safe_distance))
            and (not vlb or (self.velocity >= vlb or dlb >= self.HV_K2*self.safe_distance))):
            p = (self.safe_distance/df)**(3/4)  # P(left|state)
            # p = np.sqrt(self.safe_distance/df)  # P(left|state)
        return p

    def prob_right(self, conf, df, vf, db, vrf, drf, vrb, drb):
        p = 0

        # if (self.desired_velocity - self.velocity < self.epsilon) \
        if (not vrf or vrf - self.velocity < self.epsilon) \
            and (not drf or (drf > self.HV_K*self.safe_distance)) \
            and (not drb or (drb > self.HV_K*self.safe_distance)) \
            and (not vrf or (self.velocity <= vrf or drf > self.HV_K2*self.safe_distance)):

            if df:
                p = 1-np.sqrt(self.safe_distance/df)
            else:
                p = 0.8

        return p

    def calc_acceleration(self, conf, af, vf, df):

        # acceleration zone
        if (not df or (df >= self.HV_K1*self.safe_distance)):
            if self.desired_velocity - self.velocity == 0:
                a = 0
            elif self.desired_velocity - self.velocity < self.epsilon:
                a = self.HV_A0
            else:
                a = min(self.HV_AMAX, (self.desired_velocity - self.velocity) / (self.velocity+0.01) * self.HV_L * self.HV_AMAX)
        # adaptive zone
        elif (df < self.HV_K1*self.safe_distance) and (df > self.HV_K2*self.safe_distance):
            if self.velocity > vf:
                a = max(-self.HV_BRAKING, (vf - self.velocity) / (vf+0.01) * self.HV_L * self.HV_BRAKING)
            else:
                if self.desired_velocity - self.velocity == 0:
                    a = 0
                elif self.desired_velocity - self.velocity < self.epsilon:
                    a = self.HV_A0
                else:
                    a = min(self.HV_AMAX, (vf - self.velocity) / (vf+0.01) * self.HV_L * self.HV_AMAX)
        # braking zone
        else:
            if self.velocity > vf:
                a = max(-self.HV_BRAKING, -(self.HV_BRAKING / self.safe_distance * df - self.HV_BRAKING)) # always negative
            elif df < self.HV_K*self.safe_distance:
                a = -self.HV_BRAKING

            else: # try these one at a time and see what works best!
                # a = 0 # option 1
                # a = small number # option 2
                a = -0.1
                # a = -(-self.HV_AMAX / self.safe_distance * df + self.HV_AMAX) * (self.safe_distance-df)/self.HV_Dself.HV_D   # option 3
        # print("self.velocity: {}".format(self.velocity))
        # print("self.safe_time: {}".format(self.safe_time))
        # print("self.safe_distance: {}".format(self.safe_distance))
        # print("self.velocity * self.safe_time: {}".format(self.velocity * self.safe_time))

        return a



class Car(HumanVehicle):

    def __init__(self, lane, position=0.0):
        self.HV_K    = 1.4  # distance factor
        self.HV_K1   = 2.5  # scaling factors on safety distance ds to separate space to...
        self.HV_K2   = 1.8  # ... car in front into behavioral zones.
        self.HV_A0   = 1.0  # small constant acceleration to reach desired velocity
        self.HV_L    = np.random.uniform(1, 20)  # no idea what this is
        self.HV_AMAX = np.random.uniform(2.5, 4)  # maximum acceleration (0-100 in about 7 seconds)
        self.HV_BRAKING = 9.0
        self.extremely_safe_distance = 3     # meter

        super().__init__(lane, position)

        self.desired_velocity = np.random.uniform(25.0, 35.0)
        self.safe_time = 0.8 # seconds, 7m/(30m/s) = 0.23333... s
        self.epsilon = np.random.uniform(2.0, 10.0) # sensitivity to speed up
        self.animlane = self.lane
        self.last_lane_change = time.time()

    def update(self, conf, container, dt):
        super().update(conf, container, dt)

    def prob_left(self, conf, af, vf, df, dlf, vlf, dlb, vlb):
        return super().prob_left(conf, af, vf, df, dlf, vlf, dlb, vlb)

    def prob_right(self, conf, df, vf, db, vrf, drf, vrb, drb):
        return super().prob_right(conf, df, vf, db, vrf, drf, vrb, drb)

    def calc_acceleration(self, conf, af, vf, df):
        return super().calc_acceleration(conf, af, vf, df)


class Truck(HumanVehicle):

    def __init__(self, lane, position=0.0):
        self.HV_K    = 1.4  # distance factor
        self.HV_K1   = 2.5  # scaling factors on safety distance ds to separate space to...
        self.HV_K2   = 1.8  # ... car in front into behavioral zones.
        self.HV_A0   = 1.0  # small constant acceleration to reach desired velocity
        self.HV_L    = 1.0  # no idea what this is
        self.HV_AMAX = np.random.uniform(1, 2)  # maximum acceleration (0-100 in about 7 seconds)
        self.HV_BRAKING = 5.0
        self.extremely_safe_distance = 8.0     # meter


        super().__init__(lane, position)

        self.desired_velocity = np.random.uniform(18.0, 22.0)
        self.safe_time = 1.2 # seconds, 7m/(30m/s) = 0.23333... s
        self.epsilon = np.random.uniform(1.0, 3.0) # sensitivity to speed up
        self.animlane = self.lane
        self.last_lane_change = time.time()

    def update(self, conf, container, dt):
        super().update(conf, container, dt)

    def prob_left(self, conf, af, vf, df, dlf, vlf, dlb, vlb):
        return super().prob_left(conf, af, vf, df, dlf, vlf, dlb, vlb)

    def prob_right(self, conf, df, vf, db, vrf, drf, vrb, drb):
        return super().prob_right(conf, df, vf, db, vrf, drf, vrb, drb)

    def calc_acceleration(self, conf, af, vf, df):
        return super().calc_acceleration(conf, af, vf, df)
