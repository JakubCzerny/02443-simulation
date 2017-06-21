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

        # Emergency speed change: this should never occur, it should be
        # prevented by the proper acceleration/de-acceleration behavior.
        front = container.front(self)
        if front and abs(front.position-new_position) < .75*conf.safe_distance:
            self.velocity = front.velocity
            self.acceleration = front.acceleration
            self.position = front.position - .8*conf.safe_distance

            self.emergency = conf.fps

            print('WARNING: Emergency speed change -- fix driver behavior in', \
                    self.__class__.__name__)
        else:
            self.position = new_position
            self.emergency = max(0, self.emergency-1)



###############################################################################
#                        VEHICLE DRIVEN BY A HUMAN                            #
###############################################################################

HV_K    = 1.5  # distance factor
HV_K1   = 5.0  # scaling factors on safety distance ds to separate space to...
HV_K2   = 2.5  # ... car in front into behavioral zones.
HV_A0   = 1.0  # small constant acceleration to reach desired velocity
HV_L    = 1.0  # no idea what this is
HV_AMAX = 3.0  # maximum acceleration (0-100 in about 7 seconds)
HV_BRAKING = 9.0

# More names
#    [X]f  - front           [X]b  - back
#    [X]rf - right front     [X]rb - right back
#    [X]lf - left front      [X]lb - left back

class HumanVehicle(Vehicle):

    def __init__(self, lane, position=0.0):
        super().__init__(lane, position)

        self.desired_velocity = np.random.uniform(25.0, 35.0)
        self.epsilon = np.random.uniform(2.0, 10.0) # sensitivity to speed up
        self.animlane = self.lane
        self.previous_time = time.time()

    def update(self, conf, container, dt):
        # First update position using previous acc/vel...
        super().update(conf, container, dt)

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

        p = np.random.rand()
        p_right = self.prob_right(conf, df, vf, db, vrf, drf, drb)
        p_left = self.prob_left(conf, af, vf, df, dlf, vlf, dlb, vlb)

        #NEW ONLY SWITCH IF THEY ARE ABOVE 3 SAFE_DISTANCES #####
        if time.time() - self.previous_time > (2.0/conf.speedup):
            if (p < p_right) and (self.lane+1 < conf.nb_lanes) and (self.position > (3 * conf.safe_distance)):
                self.lane += 1
                container.notify_lane_change(self, self.lane-1)
                self.previous_time = time.time()
            elif (p < p_left) and (self.lane > 0) and (self.position > (3 * conf.safe_distance)):
                self.lane -= 1
                container.notify_lane_change(self, self.lane+1)
                self.previous_time = time.time()
        #########################################################

        """
        if time.time() - self.previous_time > (2.0/conf.speedup):
            if p < p_right and self.lane+1 < conf.nb_lanes:
                self.lane += 1
                container.notify_lane_change(self, self.lane-1)
                self.previous_time = time.time()
            elif p < p_left and self.lane > 0:
                self.lane -= 1
                container.notify_lane_change(self, self.lane+1)
                self.previous_time = time.time()
        """
        ### ANIMATION FOR LANE CHANGING
        if abs(self.animlane - self.lane) > 0.1:
            if self.animlane < self.lane:
                self.animlane = round(self.animlane + 0.1, 1)
            else:
                self.animlane = round(self.animlane - 0.1, 1)
        else:
            self.animlane = self.lane

        acc = self.calc_acceleration(conf, vf, df)

        self.velocity = max(0, self.velocity + acc*dt)
        self.velocity = min(self.desired_velocity, self.velocity)
        self.acceleration = min(HV_AMAX, acc)

    def prob_left(self, conf, af, vf, df, dlf, vlf, dlb, vlb):
        p = 0

        if (df and df < 2*HV_K1*conf.safe_distance \
            and (self.desired_velocity - self.velocity > self.epsilon or self.desired_velocity - vf > self.epsilon) \
            and (not dlf or (dlf > HV_K2*conf.safe_distance)) \
            and (not dlb or (dlb > HV_K2*conf.safe_distance)) \
            and (not vlf or (self.velocity <= vlf or dlf >= HV_K2*conf.safe_distance))
            and (not vlb or (self.velocity >= vlb or dlb >= HV_K2*conf.safe_distance))):
            p = (conf.safe_distance/df)**(3/4)  # P(left|state)
            # p = np.sqrt(conf.safe_distance/df)  # P(left|state)
        return p

    def prob_right(self, conf, df, vf, db, vrf, drf, drb):
        p = 0

        if (self.desired_velocity - self.velocity < self.epsilon) \
            and (not drf or (drf > 2/3*HV_K2*conf.safe_distance)) \
            and (not drb or (drb > 2/3*HV_K2*conf.safe_distance)) \
            and (not vrf or (self.velocity <= vrf or drf > HV_K1*conf.safe_distance)):

            if df:
                p = 1-np.sqrt(conf.safe_distance/df)
            else:
                p = 0.8

        return p

    def calc_acceleration(self, conf, vf, df):
        # NOTE: k2 = 1

        # acceleration zone
        if (not df or (df > HV_K1*conf.safe_distance)):
            if max(0, (self.desired_velocity - self.velocity)) == 0:
                a = 0
            elif (self.desired_velocity - self.velocity) < self.epsilon:
                a = HV_A0
            else:
                a = (self.desired_velocity - self.velocity) * HV_L
        # adaptive zone
        elif (df < HV_K1*conf.safe_distance) and (df > HV_K2*conf.safe_distance):
            if self.velocity > vf:
                a = (vf - self.velocity) * HV_L
            else:
                if max(0, (self.desired_velocity - self.velocity)) < self.epsilon:
                    a = 0
                elif (self.desired_velocity - self.velocity) < self.epsilon:
                    a = HV_A0
                else:
                    a = (self.desired_velocity - self.velocity) * HV_L
        # braking zone
        else:
            if df < HV_K*conf.safe_distance:
                a = -HV_BRAKING
            elif self.velocity > vf:
                a = (-HV_BRAKING / conf.safe_distance * df + HV_BRAKING) # always negative
            else: # try these one at a time and see what works best!
                # a = 0 # option 1
                # a = small number # option 2
                a = -0.1
                # a = -(-HV_AMAX / conf.safe_distance * df + HV_AMAX) * (conf.safe_distance-df)/HV_DHV_D   # option 3
        return a
