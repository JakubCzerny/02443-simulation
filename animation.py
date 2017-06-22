import pygame
from draw_dashed_line import draw_dashed_line

from animation_base import AnimationBase
from vehicle import Vehicle

WHITE = (255, 255, 255)
BLACK = (0,   0,   0   )
GREY  = (150, 150, 150)
ROAD  = (220, 220, 220)
RED   = (255, 0,   0)
GRASS = (230, 230, 240)

LANE_WIDTH = 4   # meter
LANE_SPACING = 3 # meter

class Animation(AnimationBase):

    def __init__(self, sim, conf):
        super().__init__(sim, conf)

        if conf.road_len == -1:
            conf.road_len = max_road_len(conf)
            print("set road_len to", conf.road_len)

        pygame.init()
        pygame.display.set_caption('Highway simulation')
        self._clock = pygame.time.Clock()


        song = pygame.mixer.Sound('highway-1.wav')

        song.play(loops = -1)

        self._screen = pygame.display.set_mode((conf.window_width, conf.window_height))

        # Load vehicle types
        car_type_image = pygame.transform.scale(pygame.image.load('car_side.png'),
                (int(4*conf.scale), int(2*conf.scale)))
        self._vtypes = {'car': car_type_image}

    def draw_frame(self):
        super().draw_frame()

        self._handle_events()
        self._screen.fill(WHITE)
        self._draw_road()

        for v in self._sim:
            self._draw_vehicle(v)

        pygame.display.flip()
        self._clock.tick(self._conf.fps)

    def _draw_road(self):
        sc = self._conf.scale
        sw = self._screen.get_width()

        for row in range(self._conf.rows):
            y = self._y_offset(row, 0)
            pygame.draw.rect(self._screen, WHITE, (0, y, sw, sc*self._conf.nb_lanes*LANE_WIDTH))
            
            pygame.draw.line(self._screen, BLACK, (0, y), (sw, y), 3)
            
            for lane in range(1, self._conf.nb_lanes):
                y += LANE_WIDTH*sc
                pygame.draw.line(self._screen, GREY, (0, y), (sw, y), 1)

            y += LANE_WIDTH*sc
            pygame.draw.line(self._screen, BLACK, (0, y), (sw, y), 3)

    def _draw_vehicle(self, v):
        if not v.type in self._vtypes:
            raise Exception('ERROR: animation can\'t deal with vehicle type {}'.format(v.type))

        image = self._vtypes[v.type]
        rect = image.get_rect()

        sc = self._conf.scale
        xmax = self._screen.get_width()     # number of pixels on screen (width)

        x0 = v.position*sc - rect.width/2   # position is center of vehicle
        x1 = x0 % xmax

        y1 = self._y_offset(x0 // xmax, v.animlane)
        y1 += rect.height/2                 #  position is center of vehicle

        rect.x = x1
        rect.y = y1

        if v.emergency > 0:
            self._screen.fill(RED, rect=rect)
        else:
            self._screen.blit(image, rect)

    def _y_offset(self, row, lane):
        sc = self._conf.scale
        return sc*(row*(self._conf.nb_lanes*LANE_WIDTH+LANE_SPACING) + LANE_SPACING + lane*LANE_WIDTH)

def max_road_len(conf):
    """ Max road_len that fits on the screen given the configuration. """
    meters_per_row = conf.window_width/conf.scale
    total_meters = conf.rows * meters_per_row
    return total_meters
