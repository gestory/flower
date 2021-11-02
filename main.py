from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget

import json
from glob import glob
from math import sin, cos, pi
from random import choice, randint, shuffle
from time import time

from statistics import Statistics


ANIMALS = [animal for animal in glob('./images/*') if '.png' in animal]
CORRECT_SOUNDS = [SoundLoader.load(sound) for sound in glob('./sounds/*') if 'correct' in sound]
WRONG_SOUNDS = [SoundLoader.load(sound) for sound in glob('./sounds/*') if 'wrong' in sound]


class Flower(App):
    use_kivy_settings = False
    score = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(Flower, self).__init__(**kwargs)
        self.key = None
        self.key_petal = None
        self.decoys = set()
        self.pictures_rel_size = 0.5
        self.step = 0
        self.size = 1
        self.timings = []
        self.start_level = 1
        self.level = 1
        self.max_times = [0, 5, 10, 15, 20]
        self.max_time = self.max_times[self.level]
        self.current_time = self.max_time
        self.errors = 0
        
        self.statistics = Statistics(0)
        self.start_time = time()

    def error(self):
        self.errors += 1
        choice(WRONG_SOUNDS).play()

    def update_statistics(self, data):
        self.timings.append(data)

    def new_game(self):
        self.root.current_screen.clock_event.cancel()
        self.max_time = self.max_times[self.level]
        if self.step and not self.step % 5:
            self.statistics.update(self.level, self.size, self.timings, self.errors)
            self.timings = []
            self.errors = 0
            self.size += 1
            self.pictures_rel_size *= 0.8
        if self.size == 6:
            self.step = 0
            self.size = 1
            self.pictures_rel_size = 0.5
            self.level += 1
            if self.level == 5:
                self.level = self.start_level
                self.root.current = 'results'
                self.root.current_screen.update_results(*self.statistics.get_results())
                return
            self.root.current = 'congrats'
            return
        self.root.current_screen.clock_event = Clock.schedule_interval(self.root.current_screen.update_clock, 1)
        self.root.current_screen.root.new_game()
        self.step += 1

    def build_config(self, config):
        config.setdefaults('main', {
            'start_level': '1'})
        config.setdefaults('timer', {
            '1': 5, '2': 10, '3': 15, '4': 20
        })

    def build_settings(self, settings):
        with open("flower.json") as f:
            json_data = json.load(f)
        data = json.dumps(json_data)
        
        settings.add_json_panel('Flower settings', self.config, data=data)

    def on_config_change(self, config, section, key, value):
        if config is self.config:
            if key == 'start_level':
                self.start_level = self.config.getint('main', 'start_level')
                self.level = self.start_level
            if section == 'timer':
                self.max_times[int(key)] = self.config.getint('timer', key)
                
    def on_score(self, instance, value):
        self.root.current_screen.score.text = str(value)
    
    def build(self):
        self.start_level = self.config.getint('main', 'start_level')
        self.max_time = self.config.getint('timer', str(self.start_level))
        
        sm = ScreenManager()
        
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(FlowerScreen(name='flower'))
        sm.add_widget(CongratsScreen(name='congrats'))
        sm.add_widget(ResultsScreen(name='results'))

        return sm


class MenuScreen(Screen):
    pass


class CongratsScreen(Screen):
    pass


class ResultsScreen(Screen):
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


class FlowerScreen(Screen):
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
        app.new_game()
    
    def update_clock(self, dt):
        app = App.get_running_app()
        app.current_time -= 1
        self.timer.value = app.current_time / app.max_time
        if app.current_time <= 0:
            app.error()
            self.root.new_game()


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
    def new_game(self):
        app = App.get_running_app()
        app.current_time = app.max_time
        self.parent.timer.value = 1.0
        app.key = randint(0, len(ANIMALS)-1)
        app.key_petal = randint(0, len(self.children)-2)
        app.decoys = set(ANIMALS).difference([ANIMALS[app.key]])
        app.start_time = time()
        for children in self.children:
            children.new_game()


class Petal(FloatLayout):
    def __init__(self, index=-1, **kwargs):
        super(Petal, self).__init__()
        self.index = index
        self.canvas.before.clear()
        self.button = PetalButton(**kwargs)
        self.pos = self.button.pos
        self.add_widget(self.button)

    def new_game(self):
        self.button.new_game()
    
    
class PetalButton(Button):
    @staticmethod
    def get_pictures(decoys, quantity):
        pictures = []
        for i in range(quantity):
            pictures.append(choice(decoys))
        return pictures
    
    def draw_several_pictures(self, app, size, quantity, radius):
        if app.key_petal == self.parent.index:
            pictures = [ANIMALS[app.key]]
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
        self.draw_several_pictures(app, size, 1, None)
    
    def draw_four_pictures(self, app, size):
        size = [d * .9 for d in size]
        self.draw_several_pictures(app, size, 4, .4)
        
    def draw_seven_pictures(self, app, size):
        size = [d * .8 for d in size]
        self.draw_several_pictures(app, size, 7, .4)
        
    def draw_ten_pictures(self, app, size):
        size = [d * .7 for d in size]
        self.draw_several_pictures(app, size, 10, .4)
    
    def new_game(self):
        app = App.get_running_app()
        size = (app.pictures_rel_size*self.width, app.pictures_rel_size*self.height)
        self.canvas.clear()
        if self.parent.index == -1:
            with self.canvas:
                self.bg = Rectangle(source=ANIMALS[app.key], pos=(32-size[0]/2 + self.center[0],
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
            choice(CORRECT_SOUNDS).play()
        else:
            app.error()
        app.new_game()


if __name__ == "__main__":
    Window.clearcolor = (.4, .4, .3, 1)
    Window.size = (1024, 768)
    Window.fullscreen = True
    Flower().run()
