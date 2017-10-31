"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from pygame import *
import platform
import gym
# import audio_game
from gym import  spaces,utils,error
import os
import random
from os import path
import numpy as np
import signal
import gym_audio
import pygame
init()




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

class Frogger(AudioGame):
    metadata = {'render.modes': ['human']}
    croc_locations = ((50, 0), (200, 0), (350, 0), (500, 0))
    home_points = 100
    # Set up pygame window.
    def __init__(self,no_of_lives=1,width=500, height=500, render=True,visual=True):


        if platform.system() == "Windows":
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        mixer.pre_init(44100, -16, 2, 1024)
        # Start a new game
        background_image = path.join(path.dirname(__file__), "data/background.png")
        self.background = image.load(background_image)

        self.screen = display.set_mode((640, 480))
        icon_image = path.join(path.dirname(__file__), "data/icon.png")
        self.icon = image.load(icon_image)
        display.set_icon(self.icon)
        display.set_caption('Froggix')
        # Create font for text on screen
        self.scorefont = font.Font(None, 40)
        self.menufont = font.Font(None, 60)
        self.titlefont = font.Font(None, 150)
        self.frogs = []
        self.no_of_lives = no_of_lives
        self.frog = None
        self.vehicles = []
        self.homes = []
        self.crocs = []
        self.river_objects = []
        # Create sound effect objects
        self.splasheffect = mixer.Sound(path.join(path.dirname(__file__), "data/splash.wav"))
        self.cheereffect = mixer.Sound(path.join(path.dirname(__file__), "data/cheer.wav"))
        self.crasheffect = mixer.Sound(path.join(path.dirname(__file__), "data/crash.wav"))
        self.cruncheffect = mixer.Sound(path.join(path.dirname(__file__), "data/crunch.wav"))
        self.carhorn = mixer.Sound(path.join(path.dirname(__file__), "data/car_horn.wav"))
        self.car_from_right = mixer.Sound(path.join(path.dirname(__file__), "data/car_to_right.wav"))
        self.water = mixer.Sound(path.join(path.dirname(__file__), "data/made_it_to_water.wav"))
        self.lives = no_of_lives
        self.frogs_safe = 0
        self.load_sprites()
        self.score = self.game_data['score']
        self.in_game = False  # a flag set when in play
        self.titles = True  # a flag set when on Main title screen
        self.game_over = False  # a flag set when on game_over screen
        self.in_between_level = False  # a flag set when between levels
        self.game_over = False  # flag set when game is reset at start of a new level
        self.quit_screen = False  # flag set to go to quit_screen
        self.new_highscore = False  # flag set when new highscore set
        self.level_counter = 1
        self.highscores = None
        self.letter_list_index = 0
        self.name = "_"
        self.quit = 0
        self.viewer = None
        self.game_data = self.load_sprites()


        screen_width, screen_height = 640,480


        self.observation_space = spaces.Box(low=0, high=255, shape=(screen_height, screen_width, 3))

        #     RL VARIABLES
        self.action_space = spaces.Discrete(4)
        super(Frogger, self).__init__(width, height, render)


    def _render(self, mode='human', close=False):

        if close:
            if self.viewer is not None:
                os.kill(self.viewer.pid, signal.SIGKILL)
        else:
            if self.viewer is None:
                self._start_viewer()


    def _step(self, action):
        # Begin main game loop
        # if self.render:
        #     self._render()
        background_image = path.join(path.dirname(__file__), "data/background.png")
        self.background = image.load(background_image)
        self.screen.blit(self.background, (0, 0))

        display.update()


        if action == 0 and self.frog:
            self.score += 1
            self.frog.step(action)
        elif action == 1 and self.frog:
            self.frog.step(action)
        elif action == 2 and self.frog:
            self.frog.step(action)
        elif action == 3 and self.frog:
            self.frog.step(action)

        # Move all objects
        to_move = ['vehicles', 'river_objects', 'crocs', 'frogs']

        for li in to_move:
            for obj in self.game_data[li]:
                obj.move(self.level_counter)
                if li == 'vehicles' and self.frog:
                    self.frog.vehicleDetected(obj)

        # Collision detection
        self.riverCollisions()
        self.vehicleCollision()
        self.crocCollision()
        self.madeItToGoal()

        # Draw all objects.  The order is important. frogs need to be on top of all but vehicles
        to_draw = ['river_objects', 'crocs', 'frogs', 'vehicles']
        for li in to_draw:
            [obj.render() for obj in self.game_data[li]]

        scoretext = self.scorefont.render("Score: " + str(self.score), True, (220, 0, 0))
        self.screen.blit(scoretext, (5, 400))

        display.update()

        reward = self.score

        done = False if self.frog else True


        obs = self.game_data

        info = {}

        return obs, reward, done, info

    def vehicleCollision(self):

        if self.frog is None:
            self.in_game = False
            self.game_over = True
            return

        for vehicle in self.vehicles:
            if vehicle.intersect(self.frog):
                mixer.Sound.play(self.crasheffect)
                self.lives -= 1
                self.score -= 10
                self.frog = self.nextFrog(self.lives, self.no_of_lives, False, True)

    def riverCollisions(self):
        if self.frog == None:
            self.in_game = False
            self.game_over = True
            return

        safe = [l.intersect(self.frog) for l in self.river_objects if l.draw]

        river_obj = [s for s in safe if s != None]
        if river_obj:  # if a river object is landed on.
            self.frog.speed = river_obj[0].speed
            self.score +=5

            if river_obj[0].sinkable:  # Determines if obj can sink
                river_obj[0].sink()
        else:
            self.frog.speed = 0
            # Frog in river section: so dies if not on an object.
        if (50 < self.frog.y < 200) and self.frog.speed == 0:
            mixer.Sound.play(self.splasheffect)
            self.lives -= 1
            self.score -= 10
            self.frog = self.nextFrog(self.lives, self.no_of_lives, True, False)

    def crocCollision(self):
        if self.frog is None:
            self.game_over = True
            return

        croc_lunch = [self.intersect(self.frog, c) for c in self.game_data['crocs']]

        if [cl for cl in croc_lunch if cl != None]:  # if a croc is hit
            mixer.Sound.play(self.cruncheffect)
            self.lives -= 1
            self.score -= 10
            self.frog = self.nextFrog(self.lives, self.no_of_lives, False, True)

    def madeItToGoal(self):
        if self.frog is None:
            self.game_over = True
            return

        home = [self.intersect(self.frog, h) for h in self.game_data['homes']]
        home_occupied = [(index, value) for (index, value) in enumerate(home) if value != None]
        if self.frog and self.frog.y < 50 and not home_occupied:  # frog on the bank but not in a home
            self.lives -= 1
            self.score += self.home_points
            self.frog = self.nextFrog(self.lives, self.no_of_lives, True, False)


        elif self.frog and self.frog.y < 50:  # Frog safe at home, so next frog in play.
            mixer.Sound.play(self.cheereffect)
            self.score += self.home_points
            # del self.game_data['homes'][home_occupied[0][0]] #remove home
            self.lives -= 1
            self.frogs_safe += 1
            self.frog = self.nextFrog(self.lives, self.no_of_lives)

    def generateFrogs(self,no_of_lives):
            frog_x_positions = [x * 50 for x in range(no_of_lives)]
            frogs = [Frog(x, 430, 'data/frog.png', 'data/splat.png', 0) for x in frog_x_positions]
            return frogs

    def generateVehicles(self):
        cars = [Car(x, 300) for x in range(0, 640, 213)]
        lorries = [Lorry(x, 350) for x in [200, 520]]
        bikes = [Bike(x, 250) for x in [300, 620]]

        vehicles = []
        vehicles.extend(cars)
        vehicles.extend(lorries)
        vehicles.extend(bikes)

        return vehicles

    def generateRiverObjects(self):
        logs1 = [Log(x, 50, 'data/log.png', None, -4) for x in [0, 128, 256, 384, 512]]
        turtles = [Turtle(x, 100, 'data/turtle.png', 'data/sink_turtle.png', 2, 0.75) \
                   for x in [50, 178, 306, 434, 562]]
        logs2 = [Log(x, 150, 'data/log.png', None, -4) for x in [0, 128, 256, 384, 512]]

        river_objects = []
        river_objects.extend(logs1)
        river_objects.extend(turtles)
        river_objects.extend(logs2)

        return river_objects


    def load_sprites(self, score=0):
        # Create frogs and other objects, package them in lists and return a dictionary of the lists.
        self.frogs = self.generateFrogs(self.no_of_lives)
        self.frog = self.frogs[0]
        self.frog.x, self.frog.y = 305, 405

        self.vehicles = self.generateVehicles()

        self.river_objects = self.generateRiverObjects()

        homes = [Frogger.Home(x, 0) for x in [50, 200, 350, 500]]

        crocs = [TimedMoveable(50, 0, 'data/croc.png', None, None, 3, Frogger.croc_locations)]

        self.game_data = {'frog': self.frog, 'frogs': self.frogs,
                          'vehicles': self.vehicles,'river_objects': self.river_objects, \
                     'homes': homes, 'crocs': crocs, 'score': score}

    def _reset(self):
        self.load_sprites(0)
        self.lives =  self.no_of_lives = len(self.frogs)
        self.score  = 0
        self.frogs_safe = 0
        self.in_game = True
        self.in_between_level = False
        self.quit_screen = False
        self.highscores = None
        self.new_highscore = False
        self.game_over = False

    #Global Function definitions are defined here.

    def intersect(self,frogger, mover):
        if ((frogger.x + frogger.width - 5) > mover.x - 15) and (frogger.x + 5 < mover.x + mover.width -15 ) \
        and (frogger.y > mover.y - frogger.height) and (frogger.y < mover.y + mover.height  ):
            return mover
        else:
            return None

    def nextFrog(self,lives,  init_lives,  drowned = False, crushed = False):
        if self.lives > 0:
             if crushed:
                self.frog.bitmap = self.frog.alt_bitmap
             if drowned:
                 drowned_frog = [(index, value) for (index, value) in enumerate(self.frogs)\
                                                                                           if  value == self.frog]
                 self.frogs[drowned_frog[0][0]].draw = False

             frog = self.frogs[init_lives-lives]
             frog.x, frog.y = 305,405

        else:
            frog = None
            self.game_over = True
        return frog


    class Home:
        def __init__(self, x_pos,  y_pos):
            self.x,  self.y = x_pos, y_pos
            self.width,  self.height = 60,  60

class Sprite(sprite.Sprite):


    def __init__(self, x_pos, y_pos, filename, alt_filename):
        self.screen = display.set_mode((640, 480))
        sprite.Sprite.__init__(self)
        self.x, self.y = x_pos, y_pos
        self.bitmap = image.load(path.join(path.dirname(__file__),filename))
        if alt_filename:
            self.alt_bitmap = image.load(path.join(path.dirname(__file__),alt_filename))
        else:
            self.alt_bitmap = None
        self.draw = True

    def render(self):
        if self.draw:
            self.screen.blit(self.bitmap, (self.x, self.y))


class Moveable(Sprite):
    def __init__(self, x_pos, y_pos, filename, alt_filename, speed):
        Sprite.__init__(self, x_pos, y_pos, filename, alt_filename)
        self.speed = speed
        self.width = self.bitmap.get_width()
        self.height = self.bitmap.get_height()

    def move(self, level):
        if self.x < (0 - self.width):  # Moved off left edge of screen.
            self.x = 640
        elif self.x > 640:  # Moved off right edge of screen.
            self.x = (0 - self.width)
        else:
            self.x -= self.speed + (level * 0.5 * self.speed)

    def intersect(self, frogger):
        if frogger is None:
            return None
        if ((frogger.x + frogger.width - 5) > self.x - 15) and (frogger.x + 5 < self.x + self.width - 15) \
                and (frogger.y > self.y - frogger.height) and (frogger.y < self.y + self.height):
            return self
        else:
            return None

class Vehicle(Moveable):
    def __init__(self, x_pos, y_pos, filename, alt_filename, speed=0):

        Moveable.__init__(self, x_pos, y_pos, filename, alt_filename,speed)

        self.x = x_pos
        self.y = y_pos
        self.filename = filename
        self.speed = speed

class Car(Vehicle):
    car_image =  path.join(path.dirname(__file__), "data/car.png")

    def __init__(self, x_pos, y_pos, filename=car_image, alt_filename=None, speed=3):
        Vehicle.__init__(self, x_pos, y_pos, filename, alt_filename,speed)




class Lorry(Vehicle):
    lorry_image  = path.join(path.dirname(__file__), "data/blue-lorry.png")
    def __init__(self, x_pos, y_pos, filename=lorry_image, alt_filename=None, speed=2):
        Vehicle.__init__(self, x_pos, y_pos, filename, alt_filename,speed)

class Bike(Vehicle):
    bike_icon = path.join(path.dirname(__file__), "data/bike.png")
    def __init__(self, x_pos, y_pos, filename=bike_icon, alt_filename=None, speed=7):
        Vehicle.__init__(self, x_pos, y_pos, filename, alt_filename,speed)


class Frog(Moveable):
    frog_icon = path.join(path.dirname(__file__), "data/frog.png")
    def __init__(self, x_pos, y_pos, filename=frog_icon, alt_filename='data/splat.png', speed=0):
        Moveable.__init__(self, x_pos, y_pos, filename, alt_filename,speed)
        self.speed = speed
        self.width = self.bitmap.get_width()
        self.height = self.bitmap.get_height()
        self.x = x_pos
        self.y = y_pos
        self.carhorn = mixer.Sound(path.join(path.dirname(__file__),"data/car_horn.wav"))
        self.car_from_right = mixer.Sound(path.join(path.dirname(__file__),"data/car_to_right.wav"))
        self.boing = mixer.Sound( path.join(path.dirname(__file__),"data/boing.wav"))
        self._sensor = self.sensors()

    def movement(self,e):
        if e.key == K_UP and self.y > 20:
            self.y -= 50
            mixer.Sound.play(self.boing)
        if e.key == K_DOWN and self.y < 405:
            self.y += 50
            mixer.Sound.play(self.boing)
        if e.key == K_LEFT and self.x > 10:
            self.x -= 50
            mixer.Sound.play(self.boing)
        if e.key == K_RIGHT and self.x < 600:
            self.x += 50
            mixer.Sound.play(self.boing)

    def action(self,key):
        mixer.Sound.play(self.boing)

        if key == K_UP and self.y > 20:
            self.y -= 50
        if key == K_DOWN and self.y < 405:
            self.y += 50
        if key == K_LEFT and self.x > 10:
            self.x -= 50
        if key == K_RIGHT and self.x < 600:
            self.x += 50

    def step(self,action):
        mixer.Sound.play(self.boing)

        if action == 0 and self.y > 20:
            self.y -= 50
        if action == 1 and self.y < 405:
            self.y += 50
        if action == 2 and self.x > 10:
            self.x -= 50
        if action == 3 and self.x < 600:
            self.x += 50


    def sensors(self):
            moves = {
                'forward': (self.x,
                            self.y - 50),
                'up_right_diagnol': (self.x + 50,
                                     self.y - 50),
                'car_to_right': (self.x + 50, self.y)

            }

            return moves

    def vehicleDetected(self, vehicle):

        for key, value in self.sensors().items():
            frog_x = value[0]
            frog_y = value[1]
            if key == 'forward' or key == 'up_right_diagnol':
                if frog_x - 10 < vehicle.x <= frog_x and \
                                                frog_y - 10 < vehicle.y <= frog_y:
                    mixer.Sound.play(self.carhorn)

            elif key == 'car_to_right':
                if vehicle.x - 50 < frog_x <= vehicle.x + 50 and \
                                                vehicle.y - 10 < frog_y <= vehicle.y + 10:
                    mixer.Sound.play(self.car_from_right)

class TimedMoveable(Moveable):
    def __init__(self, x_pos, y_pos, filename, alt_filename, speed, delay, locs):
        Moveable.__init__(self, x_pos, y_pos, filename, alt_filename, speed)
        if delay:
            self.delay = delay * 1000  # delay is in seconds, while self.delay needs to be msecs
            self.timer = time.get_ticks()
        self.locations = locs

    def move(self, level):
        # determine if a change in location is needed (level is not used at present)
        if (self.timer + self.delay) < time.get_ticks():
            new_loc = random.choice(self.locations)
            self.x = new_loc[0]
            self.y = new_loc[1]
            self.timer = time.get_ticks()

            # TODO add ability of crocs and flies to be on other moveables.


class RiverMoveable(TimedMoveable):
    def __init__(self, x_pos, y_pos, filename, alt_filename, speed, delay=None, locs=None):
        TimedMoveable.__init__(self, x_pos, y_pos, filename, alt_filename, speed, delay, locs)
        if delay:
            self.sinkable = True
        else:
            self.sinkable = False
        self.temp_bitmap = None
        self.timer = None
        self.sinking = False

    def move(self, level):
        Moveable.move(self, level)  # Recall the move function from Moveable
        if self.sinking == True and (self.timer + 4 * self.delay) < time.get_ticks():  # Have sunk so need to surface
            self.timer = None
            self.bitmap = self.temp_bitmap
            self.temp_bitmap = None
            self.sinking = False
            self.draw = True

    def sink(self):
        if self.timer == None:
            self.timer = time.get_ticks()
        if self.temp_bitmap == None:  # ensures this only happens once
            self.temp_bitmap = self.bitmap
            self.sinking = True
        if (self.timer + self.delay) < time.get_ticks():  # start to sink
            if self.bitmap != self.alt_bitmap:
                self.bitmap = self.alt_bitmap
        if (self.timer + 2 * self.delay) < time.get_ticks():  # Sunk
            self.draw = False

class Log(RiverMoveable):
    log_icon = path.join(path.dirname(__file__), "data/log.png")
    def __init__(self, x_pos, y_pos, filename=log_icon, alt_filename=None, speed=0, delay=None, locs=None):
        RiverMoveable.__init__(self, x_pos, y_pos, filename, alt_filename, speed, delay, locs)

class Turtle(RiverMoveable):
    turtle_icon = path.join(path.dirname(__file__), "data/turtle.png")
    sink_turtle_icon = path.join(path.dirname(__file__), "data/sink_turtle.png")
    def __init__(self, x_pos, y_pos, filename=turtle_icon, alt_filename=sink_turtle_icon, speed=0, delay=None, locs=None):
        RiverMoveable.__init__(self, x_pos, y_pos, filename, alt_filename, speed, delay, locs)

