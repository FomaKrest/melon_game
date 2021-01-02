import pygame
import os


def resize(image, coefficient):
    return pygame.transform.scale(image, (image.get_width() * coefficient, image.get_height() * coefficient))


def mirror(image):
    return pygame.transform.flip(image, True, False)


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class Animation:
    def __init__(self, images, delay, color_key=None, cycle=True, is_mirror=False, size=0):
        self.images = [load_image(i, color_key) for i in images]
        if is_mirror:
            for i in range(len(self.images)):
                self.images[i] = mirror(self.images[i])
        if size:
            for i in range(len(self.images)):
                self.images[i] = resize(self.images[i], size)

        self.cycle = cycle
        self.delay = delay
        self.current_frame = 0
        self.start_ticks = pygame.time.get_ticks()

    def get_frame(self):
        seconds = (pygame.time.get_ticks() - self.start_ticks) / 200
        if seconds > self.delay:
            self.current_frame = self.current_frame + 1
            if not self.cycle and self.current_frame + 1 > len(self.images):
                return None
            self.current_frame %= len(self.images)
            self.start_ticks = pygame.time.get_ticks()
        return self.images[self.current_frame - 1]

    def restart(self):
        self.current_frame = 0