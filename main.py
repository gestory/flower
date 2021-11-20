from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle, Triangle
from kivy.properties import ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, CardTransition
from kivy.uix.widget import Widget

import csv
from glob import glob
from math import sin, cos, pi
from random import choice, randint, shuffle
from time import time

from shapes import Shapes
from statistics import Statistics


CORRECT_SOUNDS = [SoundLoader.load(sound) for sound in glob('./sounds/*') if 'correct' in sound]
WRONG_SOUNDS = [SoundLoader.load(sound) for sound in glob('./sounds/*') if 'wrong' in sound]


class Flower(App):
    use_kivy_settings = False
    score = NumericProperty(0)
    username = StringProperty('')
    condition = StringProperty('')
    texture = ObjectProperty()
    
    def __init__(self, **kwargs):
        super(Flower, self).__init__(**kwargs)
        self.key = None
        self.key_petal = None
        self.decoys = set()
        self.pictures_rel_size = 0.5
        self.step = 0
        self.size = 1
        self.sizes = []
        self.timings = []
        self.start_level = 1
        self.level = 1
        self.max_times = [0, 5, 10, 15, 20]
        self.max_time = self.max_times[self.level]
        self.current_time = self.max_time
        self.errors = 0
        self.results = []
        self.load_top_results()
        
        self.statistics = Statistics(0)
        self.start_time = time()
        
        self.themes = []
        self.shapes = Shapes().shapes
        self.update_colors = True
        
        self.sound = 1
        
        self.hexagonal = 1

    @property
    def top_results(self):
        return [[i+1, *result] for i, result in
                enumerate(sorted(self.results, key=lambda e: e[1], reverse=True)[:10])]

    def _populate_shapes(self):
        self.themes = []
        for theme in Shapes().get_themes():
            if self.config.getint('pictures', theme):
                self.themes.append(theme)
        self.shapes = Shapes(self.themes).shapes

    def _populate_sizes(self):
        self.sizes = []
        for size in range(1, 6):
            if self.config.getint('sizes', str(size)):
                self.sizes.append(size)
        self.size = min(self.sizes) if self.sizes else 1
        self.pictures_rel_size = 0.5 * (0.86 ** (self.size - 1))

    def load_top_results(self):
        try:
            with open('top_scores', 'r') as top_scores:
                for name, score in csv.reader(top_scores):
                    self.results.append([name, int(score)])
        except FileNotFoundError:
            pass
        if not self.results:
            self.results = [['root', 100], ['admin', 10], ['Cheburashka', 1000]]

    def save_top_results(self):
        with open('top_scores', 'w', newline='') as top_scores:
            csv.writer(top_scores).writerows(self.results)

    def error(self):
        self.errors += 1
        if self.sound:
            choice(WRONG_SOUNDS).play()

    def update_statistics(self, data):
        self.timings.append(data)

    def new_game(self):
        self.root.current_screen.clock_event.cancel()
        self.max_time = self.max_times[self.level]
        if self.step and not self.step % 5:
            self.update_colors = True
            self.statistics.update(self.level, self.size, self.timings, self.errors)
            self.timings = []
            self.errors = 0
            self.size += 1
            while self.size not in self.sizes and self.size < 6:
                self.size += 1
            self.pictures_rel_size = 0.5 * (0.86 ** (self.size - 1))
        if self.size == 6:
            self.step = 0
            self.size = min(self.sizes) if self.sizes else 1
            self.pictures_rel_size = 0.5 * (0.86 ** (self.size - 1))
            self.level += 1
            if self.level == 5:
                self.results.append([self.username, self.score])
                self.save_top_results()
                self.level = self.start_level
                self.root.current = 'results'
                self.root.current_screen.update_results(*self.statistics.get_results())
                return
            self.root.current = 'congrats'
            return
        self.root.current_screen.clock_event = Clock.schedule_interval(self.root.current_screen.update_clock, 1)
        self.root.current_screen.root.new_game(self.update_colors)
        self.step += 1
        self.update_colors = False

    def build_config(self, config):
        config.setdefaults('main', {
            'start_level': '1'})
        config.setdefaults('timer', {
            '1': 5, '2': 10, '3': 15, '4': 20})
        config.setdefaults('sizes', {
            '1': 1, '2': 1, '3': 1, '4': 1, '5': 1})
        config.setdefaults('pictures', {
            'monsters': 1, 'animals': 1, 'numbers': 1, 'letters': 1})
        config.setdefaults('audio', {
            'sound': 1})
        config.setdefaults('flower', {
            'fullscreen': 1, 'hexagonal': 1})

    def build_settings(self, settings):
        settings.add_json_panel('Settings', self.config, 'settings.json')
        settings.add_json_panel('Audio', self.config, 'audio.json')
        settings.add_json_panel('Other', self.config, 'flower.json')

    def on_config_change(self, config, section, key, value):
        if config is self.config:
            if key == 'start_level':
                self.start_level = self.config.getint('main', 'start_level')
                self.level = self.start_level
            if section == 'timer':
                self.max_times[int(key)] = self.config.getint('timer', key)
            if section == 'pictures':
                self._populate_shapes()
            if section == 'sizes':
                self._populate_sizes()
            if section == 'audio':
                self.sound = self.config.getint('audio', 'sound')
            if key == 'fullscreen':
                pass
            if key == 'hexagonal':
                self.hexagonal = self.config.getint(section, key)
                
    def on_score(self, instance, value):
        self.root.current_screen.score.text = str(value)

    def on_start(self):
        self._populate_shapes()
        self._populate_sizes()
        self.sound = self.config.getint('audio', 'sound')
    
    def build(self):
        self.start_level = self.config.getint('main', 'start_level')
        self.max_time = self.config.getint('timer', str(self.start_level))
        
        self.texture = Image(source='images/green_tile.png').texture
        self.texture.wrap = 'repeat'
        self.texture.uvsize = (8, 6)
        
        sm = ScreenManager(transition=CardTransition())
        
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(AboutScreen(name='about'))
        sm.add_widget(HallOfFameScreen(name='hall_of_fame'))
        sm.add_widget(FlowerScreen(name='flower'))
        sm.add_widget(CongratsScreen(name='congrats'))
        sm.add_widget(ResultsScreen(name='results'))

        return sm


class BackgroundScreen(Screen):
    pass


class MenuScreen(BackgroundScreen):
    pass


class StartScreen(BackgroundScreen):
    pass


class AboutScreen(BackgroundScreen):
    pass


class HallOfFameScreen(BackgroundScreen):
    def on_enter(self):
        grid = self.ids.hall_of_fame
        grid.clear_widgets()
        
        app = App.get_running_app()
        for result in app.top_results:
            for e in result:
                grid.add_widget(Button(text=str(e)))


class CongratsScreen(BackgroundScreen):
    pass


class ResultsScreen(BackgroundScreen):
    def update_results(self, results, k):
        grid = self.ids.results
        grid.clear_widgets()
        for row in results:
            for e in row:
                grid.add_widget(Button(text=e))
        k1 = self.ids.k1
        k1.text = "K1: " + k[0]
        k2 = self.ids.k2
        k2.text = "K2: " + k[1]
        k3 = self.ids.k3
        k3.text = "K3: " + k[2]


class FlowerScreen(BackgroundScreen):
    def __init__(self, **kwargs):
        super(FlowerScreen, self).__init__(**kwargs)
        self.clock_event = None
        self.root = RootLayout(size=(640, 640), pos=(64, -64))
        self.root.add_widget(Petal(size_hint=(.16, .24), pos=self.root.center))
        quantity = 6
        for i in range(quantity):
            x = self.root.center[0] + self.root.width*cos(2*pi*i/quantity) * 0.4
            y = self.root.center[1] + self.root.height*sin(2*pi*i/quantity) * 0.4
            self.root.add_widget(Petal(index=i, size_hint=(.16, .24), pos=(x, y)))
        self.add_widget(self.root)

        self.timer = Timer()
        self.add_widget(self.timer)
        
        self.score = Score(text="0")
        self.add_widget(self.score)
        
    def on_enter(self):
        self.clock_event = Clock.schedule_interval(self.update_clock, 1)
        app = App.get_running_app()
        if app.level > app.start_level:
            app.new_game()
            return
        app.level = app.start_level
        app.score = 0
        app.statistics.clear_results()
        app.new_game()
    
    def update_clock(self, dt):
        app = App.get_running_app()
        app.current_time -= 1
        self.timer.value = app.current_time / app.max_time
        if app.current_time <= 0:
            app.error()
            app.new_game()


class Timer(Widget):
    value = NumericProperty(1.0)
    
    def on_value(self, instance, value):
        self.canvas.clear()
        with self.canvas:
            if value > .3:
                Color(0, 1, 0)
            else:
                Color(1, 1, 0)
            Rectangle(pos=self.pos, size=(self.size[0]*value, self.size[1]*value))


class Score(Label):
    pass


class RootLayout(FloatLayout):
    def new_game(self, update_colors=False):
        app = App.get_running_app()
        app.current_time = app.max_time
        self.parent.timer.value = 1.0
        app.key = randint(0, len(app.shapes)-1)
        app.key_petal = randint(0, len(self.children)-2)
        app.decoys = set(app.shapes).difference([app.shapes[app.key]])
        app.start_time = time()
        for children in self.children:
            children.new_game(update_colors)


class Petal(FloatLayout):
    def __init__(self, index=-1, **kwargs):
        super(Petal, self).__init__()
        self.index = index
        self.button = PetalButton(**kwargs)
        self.pos = self.button.pos
        self.add_widget(self.button)

    def new_game(self, update_colors=False):
        self.button.new_game(update_colors)
    
    
class PetalButton(Button):
    colors = ListProperty([(0, 1, 1),
                           (1, 1, 0),
                           (1, 0, 1)])
    
    @staticmethod
    def get_pictures(decoys, quantity):
        pictures = []
        for i in range(quantity):
            pictures.append(choice(decoys))
        return pictures
    
    def update_background_color(self):
        app = App.get_running_app()
        self.canvas.before.clear()
        if app.hexagonal:
            hex_vertexes = []
            for i in range(6):
                angle_deg = 60 * i - 30
                angle_rad = pi / 180 * angle_deg
                hex_vertexes += [self.center[0] + 32 + self.size[0] * 0.9 * cos(angle_rad),
                                 self.center[1] + 32 + self.size[1] * 0.8 * sin(angle_rad)]
            with self.canvas.before:
                Color(*choice(self.colors))
                for i in range(-2, 4):
                    Triangle(points=[*self.center, hex_vertexes[2*i], hex_vertexes[2*i + 1],
                                     hex_vertexes[2*i + 2], hex_vertexes[2*i + 3]])
                Color(0, 0, 0)
                Line(points=hex_vertexes, close=True, width=2)
        else:
            with self.canvas.before:
                Color(*choice(self.colors))
                Ellipse(pos=self.parent.pos, size=(self.size[0] * 1.4, self.size[1] * 1.4))
    
    def draw_several_pictures(self, app, size, quantity, radius=1):
        if app.key_petal == self.parent.index:
            pictures = [app.shapes[app.key]]
            pictures += self.get_pictures(list(app.decoys), quantity-1)
        else:
            pictures = self.get_pictures(list(app.decoys), quantity)
        shuffle(pictures)
        with self.canvas:
            self.bg = Rectangle(source=pictures.pop(), pos=(32-size[0]/2 + self.center[0],
                                                            32-size[1]/2 + self.center[1]), size=size)
            for i in range(quantity-1):
                pos = (32 - size[0]/2 + self.center[0] + self.size[0] * cos(2 * pi * i / (quantity-1)) * radius,
                       32 - size[1]/2 + self.center[1] + self.size[1] * sin(2 * pi * i / (quantity-1)) * radius)
                self.bg = Rectangle(source=pictures.pop(), pos=pos, size=size)

    def draw_one_picture(self, app, size):
        self.draw_several_pictures(app, size, 1)
    
    def draw_four_pictures(self, app, size):
        size = [d * .9 for d in size]
        self.draw_several_pictures(app, size, 4, app.pictures_rel_size)
        
    def draw_seven_pictures(self, app, size):
        size = [d * .8 for d in size]
        self.draw_several_pictures(app, size, 7, app.pictures_rel_size)
        
    def draw_ten_pictures(self, app, size):
        size = [d * .75 for d in size]
        self.draw_several_pictures(app, size, 10, app.pictures_rel_size)
    
    def new_game(self, update_colors=False):
        app = App.get_running_app()
        size = (app.pictures_rel_size*self.width, app.pictures_rel_size*self.height)
        self.canvas.clear()
        if update_colors:
            self.update_background_color()
        if self.parent.index == -1:
            with self.canvas:
                self.bg = Rectangle(source=app.shapes[app.key], pos=(32-size[0]/2 + self.center[0],
                                                                     32-size[1]/2 + self.center[1]), size=size)
        else:
            if app.level == 1:
                self.draw_one_picture(app, size)
            elif app.level == 2:
                self.draw_four_pictures(app, size)
            elif app.level == 3:
                self.draw_seven_pictures(app, size)
            elif app.level == 4:
                self.draw_ten_pictures(app, size)
    
    def on_press(self):
        app = App.get_running_app()
        if app.key_petal == self.parent.index:
            exercise_time = time() - app.start_time
            app.update_statistics(exercise_time)
            app.score += (app.max_time - int(exercise_time)) * 2
            if app.sound:
                choice(CORRECT_SOUNDS).play()
        else:
            app.error()
        app.new_game()


if __name__ == "__main__":
    Window.size = (1024, 768)
    Window.fullscreen = True
    Flower().run()
