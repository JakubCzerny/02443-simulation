import pygame

from vehicle import Vehicle

WHITE = (255,255,255)
BLACK = (0,  0,  0   )

CAR_WIDTH = 2   # meters
CAR_LENGTH = 4  # meters

LANE_WIDTH = 6  # meters

class AnimationInterrupt(BaseException):
    pass

class Animation:

    def __init__(self, simulation, fps=30):
        self._simulation = simulation
        self.fps = fps

        pygame.init()

        screen_width = 1200
        screen_height = 300

        self._scale = screen_width / simulation.road_len   # pixers per meter

        self._screen = pygame.display.set_mode([screen_width, screen_height])
        self._clock = pygame.time.Clock()

    def destroy(self):
        pygame.quit()

    def draw_frame(self):
        self._handle_events()
        self._screen.fill(WHITE)

        for v in self._simulation:
            x1 = (v.position-CAR_LENGTH/2.0)*self._scale
            y1 = (v.lane*LANE_WIDTH+LANE_WIDTH)*self._scale
            l = CAR_LENGTH*self._scale
            w = CAR_WIDTH*self._scale

            self._screen.fill(BLACK, rect=(x1, y1, l, w))

        pygame.display.flip()
        self._clock.tick(self.fps)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise AnimationInterrupt

    def delta_time(self):
        return 1/self.fps
