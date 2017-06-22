import pygame

class AnimationInterrupt(BaseException):
    pass

class AnimationBase:

    def __init__(self, sim, conf):
        self._sim = sim
        self._conf = conf
        self._handler_dict = {}

    def destroy(self):
        pygame.quit()

    def draw_frame(self):
        self._handle_events()

    def register_interactive_sim_handler(self, handler, key):
        """
        Allow enabling and disabling a handler by the press of a button.
        Buttons re-imagined, re-invented. © Apple Inc.
        """
        self._handler_dict[key] = handler

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise AnimationInterrupt
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    raise AnimationInterrupt

            self._handle_event(event)

    def _handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self._handler_dict:
                h = self._handler_dict[event.key]
                h.enabled = not h.enabled
                if h.enabled:
                    print("Enabled handler", h)
                else:
                    print("Disabled handler", h)
            elif event.key == pygame.K_s:
                if event.mod & pygame.KMOD_SHIFT:
                    if self._conf.speedup > 0:
                        self._conf.speedup -= 1
                else:
                    self._conf.speedup += 1
                print('speedup =', self._conf.speedup)
            elif event.key == pygame.K_r:
                if event.mod & pygame.KMOD_SHIFT:
                    if self._conf.spawn_rate > 0.5:
                        self._conf.spawn_rate -= 0.5
                else:
                    self._conf.spawn_rate += 0.5
                print('spawn_rate =', self._conf.spawn_rate)
