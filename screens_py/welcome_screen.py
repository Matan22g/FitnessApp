from kivy import utils
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton, MDRoundFlatButton

from customKv.toggle_behavior import MDToggleButton


class MyToggleButton2(MDRoundFlatButton, MDToggleButton):
    def __init__(self, **kwargs):
        self.background_down = MDApp.get_running_app().theme_cls.primary_dark
        super().__init__(**kwargs)
        self.font_color_normal = 0, 0, 0, 0
        self.font_color_down = 0, 0, 0, 0
        self.text_color = 0, 0, 0, 0
        self.allow_no_selection = False
        self._radius = NumericProperty("36dp")

class WelcomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"

    def on_pre_enter(self, *args):
        self.ids.kg_button.md_bg_color = utils.get_color_from_hex("#90AEFF")
        self.ids.lbs_button.md_bg_color = (0, 0, 1, 0)
