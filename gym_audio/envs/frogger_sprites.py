from pygame import *
import random
from os import path

class Sprite(sprite.Sprite):
    def __init__(self, x_pos, y_pos, filename, alt_filename):
        self.screen = display.set_mode((640, 480))
        sprite.Sprite.__init__(self)
        self.x, self.y = x_pos, y_pos
        self.bitmap = image.load(filename)
        if alt_filename:
            self.alt_bitmap = image.load(alt_filename)
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