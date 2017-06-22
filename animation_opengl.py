import numpy as np

import pygame
from pygame.locals import *

from OpenGL.GL import *
OpenGL.ERROR_CHECKING = False

from animation_base import AnimationBase

LANE_WIDTH   = 4.0
ROAD_SPACING = 2.5

class Animation(AnimationBase):

    def __init__(self, sim, conf):
        super().__init__(sim, conf)

        pygame.init()
        pygame.display.set_caption('Highway simulation (OpenGL)')
        song = pygame.mixer.Sound('highway-1.wav')
        song.play(loops = -1)

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
        
        self.asphalt = self.TexFromIMG("asphalt.jpg")

        self.textures = {
            'car': self.TexFromIMG("car.png"),
            'yellow_car': self.TexFromIMG("yellow_car.png"),
            'black_car': self.TexFromIMG("black_car.png"),
            'police_car': self.TexFromIMG("police_car.png"),
            'ambulance': self.TexFromIMG("ambulance.png"),
            'red_truck': self.TexFromIMG("red_truck.png")
        }
        
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
        super().draw_frame()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # Draw asphalt
        self._draw_asphalt()

        # Draw road lines
        self._draw_road()

        # Draw cars
        for v in self._sim:
            self._draw_vehicle(v)
        pygame.display.flip()
        self._clock.tick(self._conf.fps)

    def _draw_asphalt(self):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBindTexture(GL_TEXTURE_2D, self.asphalt)

        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0);
        glVertex2f(0, 0)
        glTexCoord2f(1.0*8, 0.0);
        glVertex2f(200, 0)
        glTexCoord2f(1.0*8, 1.0*8);
        glVertex2f(200, 200)
        glTexCoord2f(0.0, 1.0*8);
        glVertex2f(0, 200)
        glEnd()


    def _draw_road(self):
        glPushAttrib(GL_ENABLE_BIT)
        glLineWidth(1.0)
        glLineStipple(1, 0xF00F)
        glEnable(GL_LINE_STIPPLE)
        glBegin(GL_LINES)
        for row in range(self._conf.rows):
            for lane in range(1, self._conf.nb_lanes):
                y = self._y_offset(row, lane)
                glColor3f(1.0, 1.0, 1.0)
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
        
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBindTexture(GL_TEXTURE_2D, self.textures[v.type])

        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_ADD)

        glBegin(GL_QUADS)
        self._draw_rect(xc, yc, 4, 2)
        glEnd()
        glDisable(GL_TEXTURE_2D)

        glBegin(GL_QUADS)
        if v.emergency > 0:
            glColor3f(0.7, 0.1, 0.1)
        elif v.acceleration < 0:
            a = min(1.0, -v.acceleration/9)
            glColor3f(a, a, 0.1)
        elif v.acceleration > 0:
            a = min(1.0, 0.3 + v.acceleration/3)
            glColor3f(0.1, a, 0.1)
        elif v.desired_velocity-v.velocity < 1:
            glColor3f(0.05, 0.4, 0.4)
        self._draw_rect(xc-0.5, yc, 0.5, 0.5)
        glColor3f(0.0, 0.0, 0.0)            
        glEnd()

    def _draw_rect(self, xc, yc, w, h):
        w2 = w/2; h2 = h/2
        x0 = xc-w2; y0 = yc-h2
        x1 = xc+w2; y1 = yc+h2

        glTexCoord2f(0.0, 0.0);
        glVertex2f(x0, y0)
        glTexCoord2f(1.0, 0.0);
        glVertex2f(x1, y0)
        glTexCoord2f(1.0, 1.0);
        glVertex2f(x1, y1)
        glTexCoord2f(0.0, 1.0);
        glVertex2f(x0, y1)

    def _handle_event(self, event):
        super()._handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos, lane = self._pixel_pox_to_pos_lane(event.pos[0], event.pos[1])
                self._slow_down_cars(pos)

    def _y_offset(self, row, lane):
        return row*self._road_width + ROAD_SPACING + lane*LANE_WIDTH

    def _pixel_pox_to_pos_lane(self, x, y):
        xm = x / self._pixels_per_meter
        ym = y / self._pixels_per_meter

        row = ym // self._road_width
        pos = row*self._row_length + xm
        lane = int((ym - row*self._road_width - ROAD_SPACING) // LANE_WIDTH)

        return (pos, lane)

    def _slow_down_cars(self, pos):
        for i in range(self._conf.nb_lanes):
            v = self._sim.find_vehicle(pos, i)
            if v:
                v.velocity = 0
                v.acceleration = 0

    def TexFromIMG(self, filename):
        img = pygame.image.load(filename)
        img_data = pygame.image.tostring(img, "RGBA", 1)

        texture = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glBindTexture(GL_TEXTURE_2D, texture)

        # glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        # glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        # glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.get_width(), img.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        return texture
