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
    
    def new_game(self):
        self.root.new_game()
    
    def build(self):
        root = RootLayout(size=Window.size, pos=(-0.2*Window.size[0], -0.2*Window.size[1]))
        quantity = 6
        for i in range(quantity):
            x = root.center[0] + root.size[0]*cos(2*pi*i/quantity) * 0.3
            y = root.center[1] + root.size[1]*sin(2*pi*i/quantity) * 0.3
            root.add_widget(Petal(index=i, text="Petal #{}".format(i), size_hint=(.25, .25), pos=(x, y)))
        root.add_widget(Petal(text="Center", size_hint=(.25, .25), pos=root.center))
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
        App.get_running_app().key = randint(0, len(ANIMALS)-1)
        App.get_running_app().key_petal = randint(0, len(self.children)-2)
        App.get_running_app().decoys = set(ANIMALS).difference([ANIMALS[App.get_running_app().key]])
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
        self.canvas.clear()
        with self.canvas:
            if App.get_running_app().key_petal == self.parent.index or self.parent.index == -1:
                self.bg = Rectangle(source=ANIMALS[App.get_running_app().key],
                                    pos=self.center, size_hint=(0.5, 0.5))
            else:
                self.bg = Rectangle(source=choice(list(App.get_running_app().decoys)),
                                    pos=self.center, size_hint=(0.5, 0.5))
    
    def on_press(self):
        if self.parent.index < 0:
            self.parent.parent.new_game()
        else:
            if App.get_running_app().key_petal == self.parent.index:
                choice(SOUNDS).play()
                self.parent.parent.new_game()


if __name__ == "__main__":
    Flower().run()
