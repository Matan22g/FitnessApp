from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, ThreeLineListItem


class SessionScreen(Screen):
    workout = []
    ex_reference = {}

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"

    def on_pre_enter(self, *args):
        self.app.title = "Home"
        for exc in self.workout:
            self.ids["container"].add_widget(
                ThreeLineListItem(
                    text=exc,
                    secondary_text="Personal Best: ",
                    tertiary_text="Done: ",
                    on_release=self.start_exc
                ))
            # saving dic with the widget id to be able to ref to them later
            ex_widget_id = self.ids["container"].children[0]
            self.ex_reference[ex_widget_id] = exc

    def start_exc(self, *args):
        ExerciseScreen.exercise=self.ex_reference[args[0]]
        self.app.change_screen1("exercisescreen")



class ExerciseScreen(Screen):
    exercise=""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"


    def on_pre_enter(self, *args):
        self.app.title = "Home"
        self.ids["ex_name"].text=self.exercise


    def bla(self, *args):
        print(args)
