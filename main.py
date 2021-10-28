from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout

from glob import glob
from math import sin, cos, pi
from random import choice, randint

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
    
    def new_game(self):
        self.root.new_game()
        self.step += 1
        if not self.step % 5:
            self.pictures_rel_size *= 0.8
    
    def build(self):
        root = RootLayout(size=Window.size, pos=(-0.2*Window.size[0], -0.2*Window.size[1]))
        quantity = 6
        for i in range(quantity):
            x = root.center[0] + root.size[0]*cos(2*pi*i/quantity) * 0.3
            y = root.center[1] + root.size[1]*sin(2*pi*i/quantity) * 0.3
            root.add_widget(Petal(index=i, size_hint=(.25, .25), pos=(x, y)))
        root.add_widget(Petal(size_hint=(.25, .25), pos=root.center))
        return root


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
    def new_game(self):
        app = App.get_running_app()
        size = (app.pictures_rel_size*self.width, app.pictures_rel_size*self.height)
        print(size)
        self.canvas.clear()
        with self.canvas:
            if App.get_running_app().key_petal == self.parent.index or self.parent.index == -1:
                self.bg = Rectangle(source=ANIMALS[app.key],
                                    pos=self.center, size=size)
            else:
                self.bg = Rectangle(source=choice(list(app.decoys)),
                                    pos=self.center, size=size)
    
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
