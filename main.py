from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen

from glob import glob
from math import sin, cos, pi
from random import choice, randint, shuffle

ANIMALS = [animal for animal in glob('./images/*') if '.png' in animal]
SOUNDS = [SoundLoader.load(sound) for sound in glob('./sounds/*') if '.ogg' in sound]


class Flower(App):
    def __init__(self, **kwargs):
        super(Flower, self).__init__(**kwargs)
        self.key = None
        self.key_petal = None
        self.decoys = set()
        self.pictures_rel_size = 0.5
        self.step = 1
        self.level = 1
    
    def new_game(self):
        if self.step == 20:
            self.step = 0
            self.pictures_rel_size = 0.5
            self.level += 1
            if self.level == 4:
                self.step = 10
                self.pictures_rel_size = 0.25
            if self.level == 5:
                self.stop()
                return
        self.root.current_screen.root.new_game()
        self.step += 1
        if not self.step % 5:
            self.pictures_rel_size *= 0.8
    
    def build(self):
        sm = ScreenManager()
        
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(FlowerScreen(name='flower'))

        return sm


class MenuScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class FlowerScreen(Screen):
    def __init__(self, **kwargs):
        super(FlowerScreen, self).__init__(**kwargs)
        root = RootLayout(size=Window.size, pos=(-0.2*Window.size[0], -0.2*Window.size[1]))
        quantity = 6
        for i in range(quantity):
            x = root.center[0] + root.size[0]*cos(2*pi*i/quantity) * 0.3
            y = root.center[1] + root.size[1]*sin(2*pi*i/quantity) * 0.3
            root.add_widget(Petal(index=i, size_hint=(.25, .25), pos=(x, y)))
        root.add_widget(Petal(size_hint=(.25, .25), pos=root.center))
        self.add_widget(root)
        self.root = root
        
    def on_enter(self):
        self.root.new_game()


class RootLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(RootLayout, self).__init__(**kwargs)
        self.bind(pos=self.update)
        self.bind(size=self.update)
        
    def update(self, *args):
        self.pos = (-0.2*Window.size[0], -0.2*Window.size[1])
        self.size = Window.size
        
    def new_game(self):
        app = App.get_running_app()
        app.key = randint(0, len(ANIMALS)-1)
        app.key_petal = randint(0, len(self.children)-2)
        app.decoys = set(ANIMALS).difference([ANIMALS[app.key]])
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

        self.bind(pos=self.update)
        self.bind(size=self.update)

    def update(self, *args):
        if self.index >= 0:
            x = self.parent.center[0] + Window.size[0] * cos(2 * pi * self.index / 6) * .3
            y = self.parent.center[1] + Window.size[1] * sin(2 * pi * self.index / 6) * .3
        else:
            x = self.parent.center[0]
            y = self.parent.center[1]
        self.button.pos = x, y
        self.button.size = self.size
     
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
            self.bg = Rectangle(source=pictures.pop(), pos=self.center, size=size)
            for i in range(quantity-1):
                pos = (self.center[0] + self.size[0] * cos(2 * pi * i / (quantity-1)) * radius,
                       self.center[1] + self.size[1] * sin(2 * pi * i / (quantity-1)) * radius)
                self.bg = Rectangle(source=pictures.pop(), pos=pos, size=size)

    def draw_one_picture(self, app, size):
        self.draw_several_pictures(app, size, 1, None)
    
    def draw_four_pictures(self, app, size):
        self.draw_several_pictures(app, size, 4, .3)
        
    def draw_seven_pictures(self, app, size):
        self.draw_several_pictures(app, size, 7, .33)
        
    def draw_ten_pictures(self, app, size):
        self.draw_several_pictures(app, size, 10, .35)
    
    def new_game(self):
        app = App.get_running_app()
        size = (app.pictures_rel_size*self.width, app.pictures_rel_size*self.height)
        self.canvas.clear()
        if self.parent.index == -1:
            with self.canvas:
                self.bg = Rectangle(source=ANIMALS[app.key], pos=self.center, size=size)
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
        if self.parent.index < 0:
            self.parent.parent.new_game()
        else:
            if app.key_petal == self.parent.index:
                choice(SOUNDS).play()
                app.new_game()


if __name__ == "__main__":
    Flower().run()
