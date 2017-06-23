import numpy as np
import time

import random
import pygame

class Vehicle:
    VEHICLE_TYPES = ["tesla", "car", "black_car", "yellow_car", "police_car", "red_truck", "ambulance"]
    VEHICLE_TYPES = ["car", "black_car", "yellow_car", "police_car", "red_truck", "ambulance"]

    def __init__(self, lane, position=0.0):
        self.lane = lane
        self.position = position # meter
        self.velocity = 0.0      # meter/sec
        self.acceleration = 0.0  # meter/sec²
        self.extremely_safe_distance = 2.0  # meter

        self.type = random.choice(self.VEHICLE_TYPES)
        self.emergency = 0

    def __lt__(self, other):
        return self.position < other.position

    def __str__(self):
        return "Vehicle[type={:s}, lane={:2n}, pos={:06.2f}, vel={:06.2f}, acc={:06.2f}]" \
            .format(self.type, self.lane, self.position, self.velocity, self.acceleration)

    def _enough_room(self, container, location, switch_distance):
        """
        Helper function that returns true/false if vehicle at location is further away than

        INPUT:
            location: two-element list of front/back, left/right, e.g. ['font', 'right']
            switch_distance: the minimum distance to the car at 'location' for "enough room"

        """
        distance = 0 # distance to other vehicle at location

        # Get distance to other vehicle at 'location'
        if location[0] == 'front' and location[1] == 'left':
            other_vehicle = container.left_front(self)
            distance = other_vehicle.position - self.position if other_vehicle else None
        elif location[0] == 'front' and location[1] == 'right':
            other_vehicle = container.right_front(self)
            distance = other_vehicle.position - self.position if other_vehicle else None
        elif location[0] == 'back'  and location[1] == 'left':
            other_vehicle = container.left_back(self)
            distance = self.position - other_vehicle.position if other_vehicle else None
        elif location[0] == 'back'  and location[1] == 'right':
            other_vehicle = container.right_back(self)
            distance = self.position - other_vehicle.position if other_vehicle else None

        if distance is None:
            return True
        elif distance > max(vehicle.length, switch_distance):
            return True
        else:
            return False


    def update(self, conf, container, dt):
        # Update position/velocity using velocity/acceleartion from previous timestep
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

            if conf.sound:
                scream = pygame.mixer.Sound('data/wilhem.wav')
                scream.play()
        else:
            self.position = new_position
            self.velocity = new_velocity
            self.emergency = max(0, self.emergency-1)

        # Cap velocity by desired_velocity
        self.velocity = min(self.desired_velocity, self.velocity)

        # Update safe distance
        self.safe_distance = max(self.extremely_safe_distance, self.velocity * self.safe_time)
        # self.safe_distance = 7

        # Update acceleration/velocity of sorrounding vehicles
        vehicle_front = container.front(self)
        af = vehicle_front.acceleration if vehicle_front else None
        vf = vehicle_front.velocity if vehicle_front else None
        df = vehicle_front.position  - self.position if vehicle_front else None

        vehicle_back = container.back(self)
        db = self.position - vehicle_back.position if vehicle_back else None

        vehicle_left = container.left_front(self)
        vlf = vehicle_left.velocity if vehicle_left else None
        dlf = vehicle_left.position - self.position if vehicle_left else None

        vehicle_leftback = container.left_back(self)
        vlb = vehicle_leftback.velocity if vehicle_leftback else None
        dlb = self.position - vehicle_leftback.position if vehicle_leftback else None

        vehicle_rightfront = container.right_front(self)
        vrf = vehicle_rightfront.velocity if vehicle_rightfront else None
        drf = vehicle_rightfront.position - self.position if vehicle_rightfront else None

        vehicle_rightback = container.right_back(self)
        drb = self.position - vehicle_rightback.position if vehicle_rightback else None
        vrb = vehicle_rightback.velocity if vehicle_rightback else None



###############################################################################
#                        VEHICLE DRIVEN BY A HUMAN                            #
###############################################################################

# More names
#    [X]f  - front           [X]b  - back
#    [X]rf - right front     [X]rb - right back
#    [X]lf - left front      [X]lb - left back

# where:
#    [X] = d (distance)
#    [X] = v (velocity)
#    [X] = a (acceleration)

class HumanVehicle(Vehicle):

    # NOT NEEDED???
    def __init__(self, lane, position=0.0):
        super().__init__(lane, position)


    def update(self, conf, container, dt):
        super().update(conf, container, dt)

        # REDUNDANT START
        # Update acceleration/velocity of sorrounding vehicles
        vehicle_front = container.front(self)
        af = vehicle_front.acceleration if vehicle_front else None
        vf = vehicle_front.velocity if vehicle_front else None
        df = vehicle_front.position  - self.position if vehicle_front else None

        vehicle_back = container.back(self)
        db = self.position - vehicle_back.position if vehicle_back else None

        vehicle_left = container.left_front(self)
        vlf = vehicle_left.velocity if vehicle_left else None
        dlf = vehicle_left.position - self.position if vehicle_left else None

        vehicle_leftback = container.left_back(self)
        vlb = vehicle_leftback.velocity if vehicle_leftback else None
        dlb = self.position - vehicle_leftback.position if vehicle_leftback else None

        vehicle_rightfront = container.right_front(self)
        vrf = vehicle_rightfront.velocity if vehicle_rightfront else None
        drf = vehicle_rightfront.position - self.position if vehicle_rightfront else None

        vehicle_rightback = container.right_back(self)
        drb = self.position - vehicle_rightback.position if vehicle_rightback else None
        vrb = vehicle_rightback.velocity if vehicle_rightback else None
        # REDUNDANT END

        def lane_switching(self, switch_distance):

            # Decide if switch to left/right lane
            p = np.random.rand()

            p_right = self.prob_right(container, conf, df, vf, db, vrf, drf, vrb, drb,)
            p_left = self.prob_left(container, conf, af, vf, df, dlf, vlf, dlb, vlb)

            # Switch lane only if no switch recently and sorroundings are above 3 * safe_distance
            laneswitch_timeout = 5.0
            if (time.time() - self.last_lane_change) > (laneswitch_timeout/conf.speedup) and self.velocity > 3:
                if (p < p_right) \
                    and (self.lane + 1 < conf.nb_lanes) \
                    and (self.position > (3 * self.safe_distance)) \
                    and (drf is None or drf > self.safe_distance) \
                    and (drb is None or drb > vehicle_rightback.safe_distance):
                    self.lane += 1
                    container.notify_lane_change(self, self.lane - 1)
                    self.last_lane_change = time.time()
                elif (p < p_left) \
                    and (self.lane > 0) \
                    and (self.position > (3 * self.safe_distance)) \
                    and (dlf is None or dlf > self.safe_distance) \
                    and (dlb is None or dlb > vehicle_leftback.safe_distance):
                    self.lane -= 1
                    container.notify_lane_change(self, self.lane + 1)
                    self.last_lane_change = time.time()

            ### Animation for lane changing
            if abs(self.animlane - self.lane) > 0.1:
                if self.animlane < self.lane:
                    self.animlane = round(self.animlane + 0.1, 1)
                else:
                    self.animlane = round(self.animlane - 0.1, 1)
            else:
                self.animlane = self.lane

            acc = self.calc_acceleration(conf, af, vf, df)
            acc = min(self.HV_AMAX, acc)
            self.acceleration = acc

    def prob_left(self, container, conf, af, vf, df, dlf, vlf, dlb, vlb):
        p = 0
        if (df and df < self.HV_K1*self.safe_distance \
            and (self.desired_velocity - self.velocity > self.epsilon or self.desired_velocity - vf > self.epsilon) \
            and self._enough_room(container, ('front','left')) \
            and self._enough_room(container, ('back','left')) \
            and (vlf is None or (self.velocity <= vlf or dlf >= self.HV_K1*self.safe_distance))
            and (vlb is None or (self.velocity >= vlb or dlb >= self.HV_K1*self.safe_distance))):
            p = (self.safe_distance/df)**(3/4)  # P(left|state)
        return p

    def prob_right(self, container, conf, df, vf, db, vrf, drf, vrb, drb, switch_distance):
        p = 0

        if (vrf is None or self.velocity < self.epsilon) \
            and self._enough_room(container, ('front','right'), switch_distance) \
            and self._enough_room(container, ('back','right'), switch_distance) \
            and (vrf is None or (self.velocity <= vrf or drf > self.HV_K1*self.safe_distance)):

            if df:
                p = 1-np.sqrt(self.safe_distance/df)
            else:
                p = 0.8

        return p

    def calc_acceleration(self, conf, af, vf, df):

        # acceleration zone
        if (df is None or (df >= self.HV_K1*self.safe_distance)):
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
            if df < self.HV_K*self.safe_distance and (af and af < self.acceleration):
                a = -self.HV_BRAKING
            elif self.velocity > vf:
                a = max(-self.HV_BRAKING, -(self.HV_BRAKING / self.safe_distance * df - self.HV_BRAKING)) # always negative
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
        super().__init__(lane, position)

        self.HV_K    = 1.4  # distance factor
        self.HV_K1   = 3.0  # scaling factors on safety distance ds to separate space to...
        self.HV_K2   = 1.8  # ... car in front into behavioral zones.
        self.HV_A0   = 1.0  # small constant acceleration to reach desired velocity
        self.HV_L    = np.random.uniform(1, 20)  # no idea what this is
        self.HV_AMAX = np.random.uniform(2.5, 4)  # maximum acceleration (0-100 in about 7 seconds)
        self.HV_BRAKING = 9.0
        self.length = 4.0
        self.extremely_safe_distance = np.random.uniform(2.5, 4)   # meter
        self.safe_distance = self.extremely_safe_distance

        self.desired_velocity = np.random.uniform(30.0, 35.0)
        self.safe_time = 0.9 # seconds, 7m/(30m/s) = 0.23333... s
        self.epsilon = np.random.uniform(2.0, 10.0) # sensitivity to speed up
        self.animlane = self.lane
        self.last_lane_change = time.time()
        self.switch_distance = 5.0 # number of safe distances to sorrounding cars for lane switching

    def update(self, conf, container, dt):
        super().update(conf, container, dt)

    def prob_left(self, container, conf, af, vf, df, dlf, vlf, dlb, vlb):
        return super().prob_left(container, conf, af, vf, df, dlf, vlf, dlb, vlb)

    def prob_right(self, container, conf, df, vf, db, vrf, drf, vrb, drb):
        return super().prob_right(container, conf, df, vf, db, vrf, drf, vrb, drb)

    super.lane_switching(switch_distance)

    def calc_acceleration(self, conf, af, vf, df):
        return super().calc_acceleration(conf, af, vf, df)


class Truck(HumanVehicle):

    def __init__(self, lane, position=0.0):
        super().__init__(lane, position)

        self.HV_K    = 2.0  # distance factor
        self.HV_K1   = 2.6  # scaling factors on safety distance ds to separate space to...
        self.HV_K2   = 2.2  # ... car in front into behavioral zones.
        self.HV_A0   = 1.0  # small constant acceleration to reach desired velocity
        self.HV_L    = 1.0  # no idea what this is
        self.HV_AMAX = np.random.uniform(1, 2)  # maximum acceleration (0-100 in about 7 seconds)
        self.HV_BRAKING = 5.0
        self.length = 15.0
        self.extremely_safe_distance = np.random.uniform(8, 9)
        self.safe_distance = self.extremely_safe_distance

        self.desired_velocity = np.random.uniform(18.0, 22.0)
        self.safe_time = 2.2 # seconds, 7m/(30m/s) = 0.23333... s
        self.epsilon = np.random.uniform(1.0, 3.0) # sensitivity to speed up
        self.animlane = self.lane
        self.last_lane_change = time.time()
        self.type = 'long_truck'

    def update(self, conf, container, dt):
        super().update(conf, container, dt)

    def prob_left(self, container, conf, af, vf, df, dlf, vlf, dlb, vlb, switch_distance):
        return super().prob_left(container, conf, af, vf, df, dlf, vlf, dlb, vlb)

    def prob_right(self, container, conf, df, vf, db, vrf, drf, vrb, drb, switch_distance):
        return super().prob_right(container, conf, df, vf, db, vrf, drf, vrb, drb)

    def calc_acceleration(self, conf, af, vf, df):
        return super().calc_acceleration(conf, af, vf, df)



class AutomaticCar(HumanVehicle):

    def __init__(self, lane, position=0.0):
        super().__init__(lane, position)

        self.HV_K    = 1.4  # distance factor
        self.HV_K1   = 3.0  # scaling factors on safety distance ds to separate space to...
        self.HV_K2   = 1.8  # ... car in front into behavioral zones.
        self.HV_A0   = 1.0  # small constant acceleration to reach desired velocity
        self.HV_L    = np.random.uniform(1, 20)  # no idea what this is
        self.HV_AMAX = np.random.uniform(2.5, 4)  # maximum acceleration (0-100 in about 7 seconds)
        self.HV_BRAKING = 9.0
        self.length = 4.0
        self.extremely_safe_distance = np.random.uniform(2.5, 4)   # meter
        self.safe_distance = self.extremely_safe_distance

        self.desired_velocity = np.random.uniform(30.0, 35.0)
        self.safe_time = 0.9 # seconds, 7m/(30m/s) = 0.23333... s
        self.epsilon = np.random.uniform(2.0, 10.0) # sensitivity to speed up
        self.animlane = self.lane
        self.last_lane_change = time.time()
        self.switch_distance = 5.0

    def update(self, conf, container, dt):
        super().update(conf, container, dt)

    def prob_left(self, container, conf, af, vf, df, dlf, vlf, dlb, vlb, switch_distance):
        return super().prob_left(container, conf, af, vf, df, dlf, vlf, dlb, vlb)

    def prob_right(self, container, conf, df, vf, db, vrf, drf, vrb, drb, switch_distance):
        return super().prob_right(container, conf, df, vf, db, vrf, drf, vrb, drb)

    def calc_acceleration(self, conf, af, vf, df):
        return super().calc_acceleration(conf, af, vf, df)









# class AutomaticCar(HumanVehicle):

#     def __init__(self, lane, position=0.0):
#         self.HV_K    = 1.4  # AUTOMATIC CAR!
#         self.HV_K1   = 3.0  # scaling factors on safety distance ds to separate space to...
#         self.HV_K2   = 1.8  # ... car in front into behavioral zones.
#         self.HV_K3   = 1.1  # AUTOMATIC CAR
#         self.HV_A0   = 1.0  # small constant acceleration to reach desired velocity
#         self.HV_L    = 10  # no idea what this is
#         self.HV_L2    = 50  # no idea what this is
#         self.HV_AMAX = np.random.uniform(2.5, 4)  # maximum acceleration (0-100 in about 7 seconds)
#         self.HV_BRAKING = 119.0
#         self.length = 4.0
#         self.extremely_safe_distance = 4.0     # meter
#         self.safe_distance = self.extremely_safe_distance
#         self.type = 'tesla'

#         super().__init__(lane, position)

#         self.desired_velocity = np.random.uniform(30.0, 35.0)
#         self.safe_time = 0.9 # seconds, 7m/(30m/s) = 0.23333... s
#         self.epsilon = np.random.uniform(2.0, 10.0) # sensitivity to speed up
#         self.animlane = self.lane
#         self.last_lane_change = time.time()

#     def update(self, conf, container, dt):
#         super().update(conf, container, dt)

#     def prob_left(self, container, conf, af, vf, df, dlf, vlf, dlb, vlb):
#         return super().prob_left(container, conf, af, vf, df, dlf, vlf, dlb, vlb)

#     def prob_right(self, container, conf, df, vf, db, vrf, drf, vrb, drb):
#         return super().prob_right(container, conf, df, vf, db, vrf, drf, vrb, drb)

#     def calc_acceleration(self, conf, af, vf, df):

#         # acceleration zone
#         if (df is None or (df >= self.HV_K1*self.safe_distance)):
#             if self.desired_velocity - self.velocity == 0:
#                 a = 0
#             elif self.desired_velocity - self.velocity < self.epsilon:
#                 a = self.HV_A0
#             else:
#                 a = min(self.HV_AMAX, (self.desired_velocity - self.velocity) / (self.velocity+0.01) * self.HV_L * self.HV_AMAX)
        
#         # OLD HUMAN BEHAVIOR
#         # adaptive zone
#         elif (df < self.HV_K1*self.safe_distance) and (df > self.HV_K2*self.safe_distance):
#             if self.velocity > vf:
#                 a = max(-self.HV_BRAKING, (vf - self.velocity) / (vf+0.01) * self.HV_L * self.HV_BRAKING)
#             else:
#                 if self.desired_velocity - self.velocity == 0:
#                     a = 0
#                 elif self.desired_velocity - self.velocity < self.epsilon:
#                     a = self.HV_A0
#                 else:
#                     a = min(self.HV_AMAX, (vf - self.velocity) / (vf+0.01) * self.HV_L * self.HV_AMAX)
#         # lock-in zone
#         elif (df < self.HV_K2*self.safe_distance) and (df > self.HV_K3*self.safe_distance) and (np.absolute(vf - self.desired_velocity) < 2):
#             print ("interesting1")
#             if np.absolute(self.velocity - vf < 1):
#                 print ("interesting1")
#                 self.velocity = vf
#                 a = 0
#                 if self.safe_distance > 2:
#                     self.safe_distance -= 1
#             else:
#                 a = min(self.HV_AMAX, (vf - self.velocity) / (self.velocity+0.001) * self.HV_L2 * self.HV_AMAX)
#                 print ("interesting2")
#             print(self.safe_distance)
#         # braking zone
#         else:
#             if df < self.HV_K*self.safe_distance and af:
#                 a = -self.HV_BRAKING
#             # elif self.velocity > vf:
#                 a = max(-self.HV_BRAKING, -(self.HV_BRAKING / self.safe_distance * df - self.HV_BRAKING)) # always negative
#             # else: # try these one at a time and see what works best!
#                 # a = -0.1
#         print(self.safe_distance)
#         return a