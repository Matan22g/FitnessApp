from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp


class WorkoutsScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self, *args):
        self.app.title = "Workouts"