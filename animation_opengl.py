import numpy as np

import pygame
from pygame.locals import *

from OpenGL.GL import *
OpenGL.ERROR_CHECKING = False

class AnimationInterrupt(BaseException):
    pass

LANE_WIDTH   = 4.0
ROAD_SPACING = 2.5

class Animation:

    def __init__(self, sim, conf):
        self._sim = sim
        self._conf = conf

        pygame.init()
        pygame.display.set_caption('Highway simulation (OpenGL)')

        self._row_length = conf.road_len / conf.rows                     # meter
        self._road_width = ROAD_SPACING + LANE_WIDTH * conf.nb_lanes     # meter
        self._world_height = self._road_width * conf.rows + ROAD_SPACING # meter
        self._pixels_per_meter = conf.window_width / self._row_length    # px/meter

        self._display = (conf.window_width, int(self._world_height*self._pixels_per_meter))
        self._confirm_display()
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(self._display, DOUBLEBUF|OPENGL)

        glScalef(1.0, -1.0, 1.0)
        glTranslatef(-1.0, -1.0, 0.0)
        glScalef(2.0, 2.0, 1.0)
        glScalef(1/self._row_length, 1/self._world_height, 1.0)
        glClearColor(1.0, 1.0, 1.0, 1.0)

    def _confirm_display(self):
        if self._display[1] > 1080:
            r = input('Confirm window height {}? '.format(self._display[1]))
            if r != 'y':
                print('Aborting...')
                self.destroy()
                exit(1)

    def destroy(self):
        pygame.quit()

    def draw_frame(self):
        self._handle_events()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # Draw road lines
        self._draw_road()

        # Draw cars
        glBegin(GL_QUADS)
        glColor3f(0.0, 0.0, 0.0)
        for v in self._sim:
            self._draw_vehicle(v)
        glEnd()

        pygame.display.flip()
        self._clock.tick(self._conf.fps)

    def _draw_road(self):
        glPushAttrib(GL_ENABLE_BIT)
        glLineWidth(1.0)
        glLineStipple(1, 0xF00F)
        glEnable(GL_LINE_STIPPLE)
        glBegin(GL_LINES)
        for row in range(self._conf.rows):
            for lane in range(1, self._conf.nb_lanes):
                y = self._y_offset(row, lane)
                glVertex2f(0, y)
                glVertex2f(self._row_length, y)
        glEnd()
        glPopAttrib()

        glLineWidth(2.0)
        glBegin(GL_LINES)
        for row in range(self._conf.rows):
            y = self._y_offset(row, 0)
            glVertex2f(0, y)
            glVertex2f(self._row_length, y)
            y += LANE_WIDTH * self._conf.nb_lanes
            glVertex2f(0, y)
            glVertex2f(self._row_length, y)
        glEnd()
        glLineWidth(1.0)

    def _draw_vehicle(self, v):
        row = v.position // self._row_length
        xc = v.position % self._row_length
        yc = self._y_offset(row, v.animlane) + LANE_WIDTH/2

        if v.emergency > 0:
            glColor3f(0.7, 0.1, 0.1)
        elif v.acceleration < 0:
            a = min(1.0, -v.acceleration/5)
            glColor3f(a, a, 0.1)
        elif v.acceleration > 0:
            a = min(1.0, 0.3 + v.acceleration/5)
            glColor3f(0.1, a, 0.1)
        elif v.desired_velocity-v.velocity < 1:
            glColor3f(0.05, 0.4, 0.4)

        self._draw_rect(xc, yc, 4, 2)

        glColor3f(0.0, 0.0, 0.0)

    def _draw_rect(self, xc, yc, w, h):
        w2 = w/2; h2 = h/2
        x0 = xc-w2; y0 = yc-h2
        x1 = xc+w2; y1 = yc+h2
        glVertex2f(x0, y0)
        glVertex2f(x1, y0)
        glVertex2f(x1, y1)
        glVertex2f(x0, y1)

    def _y_offset(self, row, lane):
        return row*self._road_width + ROAD_SPACING + lane*LANE_WIDTH

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise AnimationInterrupt
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    raise AnimationInterrupt
