from glob import glob
import os


class Shapes(object):
    def __init__(self, themes=None):
        if not themes:
            themes = self.get_themes()
        self.shapes = []
        for theme in themes:
            self.shapes += [shape for shape in glob(f'./images/shapes/{theme}/*') if '.png' in shape]

    @staticmethod
    def get_themes():
        return [theme.name for theme in os.scandir('./images/shapes/') if theme.is_dir()]
