import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

class AnimationInterrupt(BaseException):
    pass

V = (
        ( 1, -1, -1),
        ( 1,  1, -1),
        (-1,  1, -1),
        (-1, -1, -1),
        ( 1, -1,  1),
        ( 1,  1,  1),
        (-1, -1,  1),
        (-1,  1,  1)
)

E = (
        (0, 1),
        (0, 3),
        (0, 4),
        (2, 1),
        (2, 3),
        (2, 7),
        (5, 3),
        (5, 4),
        (5, 7),
        (5, 1),
        (5, 4),
        (5, 7)
)

def cube():
    glBegin(GL_LINES)
    for e in E:
        for v in e:
            glVertex3fv(V[v])
    glEnd()

class Animation:

    def __init__(self, sim, conf):
        self._sim = sim
        self._conf = conf

        display = (800, 600)

        pygame.init()

        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

        gluPerspective(45, (display[0]/display[1]), .1, 50)
        glTranslatef(0.0, 0.0, -5.0)
        glRotatef(0, 0, 0, 0)

    def destroy(self):
        pygame.quit()

    def draw_frame(self):
        self._handle_events()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glRotatef(3, 4, 1, 0)
        cube()

        pygame.display.flip()
        self._clock.tick(self._conf.fps)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise AnimationInterrupt
