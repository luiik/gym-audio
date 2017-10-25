"""Base class for representing audio games."""
import pygame
import os
from pygame.locals import RLEACCEL
import numpy as np
import gym

class AudioGame(gym.Env):
    def __init__(self, width, height, render):
        pygame.mixer.pre_init(44100, channels=1)
        pygame.init()
        pygame.mixer.init(44100, channels=1)
        self.width = width
        self.height = height
        self.rendering = render
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.load_sprites()

    def update_audio_stream(self, sound):
        return np.fft.fft(pygame.sndarray.samples(sound)).real

    def load_sprites(self):
        raise NotImplementedError("Subclasses should implement this.")

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print('Cannot load image:', name)
        raise SystemExit

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()