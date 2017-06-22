import pygame

class AnimationInterrupt(BaseException):
    pass

class AnimationBase:

    def __init__(self, sim, conf):
        self._sim = sim
        self._conf = conf

    def destroy(self):
        pygame.quit()

    def draw_frame(self):
        self._handle_events()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise AnimationInterrupt
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    raise AnimationInterrupt
            else:
                self._handle_event(event)

    def _handle_event(self, event):
        pass

