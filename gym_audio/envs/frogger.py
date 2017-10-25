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

import platform

from gym import spaces

import audio_game
from frogger_sprites import *

init()
class Frogger(audio_game.AudioGame):
    metadata = {'render.modes': ['human']}
    croc_locations = ((50, 0), (200, 0), (350, 0), (500, 0))
    home_points = 100
    # Set up pygame window.
    def __init__(self,no_of_lives=5,width=500, height=500, render=True):
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
        self.game_data = self.load_sprites()
    #     RL VARIABLES
        self.action_space = spaces.Discrete(4)
        super(Frogger, self).__init__(width, height, render)

    def _render(self, mode='human', close=False):
        self.screen.blit(self.background, (0, 0))

    def moveObjects(self):
        # Move all objects
        to_move = ['vehicles', 'river_objects', 'crocs', 'frogs']

        for li in to_move:
            for obj in self.game_data[li]:
                obj.move(self.level_counter)
                if li == 'vehicles' and self.frog:
                    self.frog.vehicleDetected(obj)

    def drawObjects(self):
        # Draw all objects.  The order is important. frogs need to be on top of all but vehicles
        to_draw = ['river_objects', 'crocs', 'frogs', 'vehicles']
        for li in to_draw:
            [obj.render() for obj in self.game_data[li]]
        scoretext = self.scorefont.render("Score: " + str(self.score), True, (220, 0, 0))
        self.screen.blit(scoretext, (5, 400))
        display.update()

    def _step(self, action):
        # Begin main game loop
       

        if action == 0 and self.frog:
            self.score += 1
            self.frog.step(action)
        elif action == 1 and self.frog:
            self.frog.step(action)
        elif action == 2 and self.frog:
            self.frog.step(action)
        elif action == 3 and self.frog:
            self.frog.step(action)

        # Move objects
        self.moveObjects()
        # Collision detection
        self.riverCollisions()
        self.vehicleCollision()
        self.crocCollision()
        self.madeItToGoal()

        # draw objects
        self.drawObjects()

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
            frogs = [Frog(x, 430, path.join(path.dirname(__file__), "data/frog.png"), path.join(path.dirname(__file__), "data/splat.png"), 0) for x in frog_x_positions]
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

        logs1 = [Log(x, 50, path.join(path.dirname(__file__), "data/log.png"), None, -4) for x in [0, 128, 256, 384, 512]]
        turtles = [Turtle(x, 100, path.join(path.dirname(__file__), "data/turtle.png"), path.join(path.dirname(__file__), "data/sink_turtle.png"), 2, 0.75) \
                   for x in [50, 178, 306, 434, 562]]
        logs2 = [Log(x, 150, path.join(path.dirname(__file__), "data/log.png"), None, -4) for x in [0, 128, 256, 384, 512]]

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


        crocs = [TimedMoveable(50, 0, path.join(path.dirname(__file__), "data/croc.png"), None, None, 3, Frogger.croc_locations)]

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

def main():
    import pygame, sys

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # quit the screen
                running = False
                sys.exit()

if __name__ == '__main__':
    main()
