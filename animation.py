import pygame
from draw_dashed_line import draw_dashed_line 

from vehicle import Vehicle

WHITE = (255,255,255)
BLACK = (0,  0,  0   )
GREY  = (100, 100, 100)

CAR_WIDTH = 2   # meters
CAR_LENGTH = 4  # meters

LANE_WIDTH = 4  # meters
CONST = 15 #For lanes

class AnimationInterrupt(BaseException):
    pass

class Animation:

    def __init__(self, simulation, conf):
        self._simulation = simulation
        self._conf = conf

        pygame.init()

        self.screen_width = 1800
        self.screen_height = 100

        self._scale = self.screen_width / simulation._conf.road_len   # pixers per meter

        self._screen = pygame.display.set_mode([self.screen_width, self.screen_height])
        self._clock = pygame.time.Clock()

        l = CAR_LENGTH*self._scale
        w = CAR_WIDTH*self._scale
        self.image = pygame.image.load('car_side.png')
        self.image = pygame.transform.scale(self.image, (int(l),int(w)))

    def destroy(self):
        pygame.quit()

    def draw_frame(self):
        self._handle_events()
        self._screen.fill(WHITE)
        pygame.draw.line(self._screen, GREY, (0, LANE_WIDTH*self._scale-5), (self.screen_width, LANE_WIDTH*self._scale-5), 3)
        pygame.draw.line(self._screen, GREY, (0, LANE_WIDTH*self._scale*3+CONST), (self.screen_width, LANE_WIDTH*self._scale*3+CONST), 3)
        draw_dashed_line(self._screen, BLACK, (0, LANE_WIDTH*self._scale+CONST), (self.screen_width, LANE_WIDTH*self._scale+CONST), dash_length = 3)
        draw_dashed_line(self._screen, BLACK, (0, LANE_WIDTH*2*self._scale+CONST), (self.screen_width, LANE_WIDTH*2*self._scale+CONST), dash_length = 3)
        for v in self._simulation:
            x1 = (v.position-CAR_LENGTH/2.0)*self._scale
            y1 = (v.animlane*LANE_WIDTH+LANE_WIDTH)*self._scale
            self.rect = self.image.get_rect()
            self.rect.x = x1
            self.rect.y = y1
            self._screen.blit(self.image, self.rect)
            #self._screen.fill(BLACK, rect=(x1, y1, l, w))

        pygame.display.flip()
        self._clock.tick(self._conf.fps)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise AnimationInterrupt
