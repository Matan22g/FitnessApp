from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp



class WorkoutsScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self, *args):
        self.app.change_title("Workouts")
        if self.app.running_session == 0:
            # self.app.root.ids['workoutsscreen'].ids["running_session_label"].text = ""
            self.app.root.ids['workoutsscreen'].ids["running_session_label"].opacity = 0
            self.app.root.ids['workoutsscreen'].ids["running_session"].opacity = 0
            self.app.root.ids['workoutsscreen'].ids["running_session"].disabled = True
        else:
            self.app.root.ids['workoutsscreen'].ids["running_session"].opacity = 1
            self.app.root.ids['workoutsscreen'].ids["running_session_label"].opacity = 1
            self.app.root.ids['workoutsscreen'].ids["running_session"].disabled = False
            self.app.root.ids['workoutsscreen'].ids["running_session"].disabled = False
            self.app.root.ids['workoutsscreen'].ids["running_session"].text_color = (1, 1, 1, 1)
        self.app.root.ids['toolbar'].right_action_items = [['', lambda x: None]]

        self.app.title = "Workouts"
