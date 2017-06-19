""" This should not depend on anything else. This is a simple value type. """

class Vehicle:

    def __init__(self, lane, position=0.0):
        self.lane = lane
        self.position = position # meter
        self.velocity = 33.0     # meter/sec
        self.acceleration = 0.0  # meter/sec²

        self.vd = 110
        self.ds = 3
        self.epsilon = 10
        self.k  = 1
        self.k1 = 1
        self.k2 = 1
        self.a0 = 1
        self.l  = 1
        self.a_max = 1

    def __lt__(self, other):
        return isinstance(other, Vehicle) and self.position < other.position

    def __str__(self):
        return "Vehicle[lane={:2n}, pos={:06.2f}, vel={:06.2f}, acc={:06.2f}]" \
            .format(self.lane, self.position, self.velocity, self.acceleration)

    def prob_left(self, af, vf, df, dlf, vlf, dlb):
        p = 0
        if (self.vd - self.velocity > self.epsilon):
            if not af:
                p = 0
            elif (af <= 0) \
                and (not dlf or not (dlf < self.ds)) \
                and (not dlb or not (dlb < self.ds)) \
                and (not vlf or (not vlf > vf)):
                p = (self.ds/df)**(3/4)  # P(left|state)

        return p

    def prob_right(self, db, vrf, drf, drb):
        p = 0
        if (self.vd - self.velocity < self.epsilon) \
            and (not drf or not (drf < self.k*self.ds)) \
            and (not drb or not (drb < self.ds)) \
            and (not vrf or (self.velocity <= vrf)):

            if db:
                p = np.sqrt(self.ds/db)  # P(right|state)
            else:
                p = 1

        return p

    def calc_acceleration(self, vf, df):
        # NOTE: k2 = 1

        # acceleration zone
        if (not df or (df > self.k1*self.ds)):
            if max(0, (self.vd - self.velocity)) == 0:
                a = 0
            elif (self.vd - self.velocity) < self.epsilon:
                a = self.a0
            else:
                a = (self.vd - self.velocity) * self.l
        # adaptive zone
        elif (self.df < self.k1*self.ds) and (self.df > self.k2*self.ds):
            if self.velocity > vf:
                a = (vf - self.velocity) * self.l
            else:
                if max(0, (self.vd - self.velocity)) == 0:
                    a = 0
                elif (self.vd - self.velocity) < self.epsilon:
                    a = self.a0
                else:
                    a = (self.vd - self.velocity) * self.l
        # braking zone
        else:
            if self.velocity > vf:
                a = -(-self.a_max / self.ds * df + self.a_max ) # always negative
            else: # try these one at a time and see what works best!
                a = 0 # option 1
                # a = small number # option 2
                # a = -(-a_max / ds * df + a_max ) * (ds-df)/ds   # option 3
        return a
