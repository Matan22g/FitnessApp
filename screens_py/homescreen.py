from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp

from customKv.piechart import AKPieChart


class HomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"

    def on_pre_enter(self, *args):

        try:
            self.app.root.ids['bottom_nav'].on_resize()

            self.app.change_title("Dashboard")
            self.app.sort_weights()
            self.app.root.ids['toolbar'].right_action_items = [['', lambda x: None]]
        except:
            pass
        try:

            if self.app.units == "metric":
                self.ids["weight_units"].text = "Kg"
            else:
                self.ids["weight_units"].text = "Lbs"
        except:
            pass

    # def on_quick_menu(self, *args):
    #     print(args[0].icon
    #           )

    def on_enter(self, *args):
        self.app.title = "Home"
        try:
            self.app.update_chart()
        except:
            print("error in self.app.exc_pie_dic:", self.app.exc_pie_dic)
    # data = {
    #     'weight-lifter': 'Create Workout',
    #     'weight': 'Workouts'
    # }
    # screendata = {
    #     'weight-lifter': 'create_workout_screen',
    #     'weight': 'workoutsscreen',
    # }
    #
    # def callback(self, instance):
    #     menu=self.ids["menu"]
    #     menu.close_stack()
    #     screenname=self.screendata[instance.icon]
    #
    #     self.app.change_screen1(screenname,"right")
    #

    def start_recent_session(self, num_of_card):
        num_of_recents = len(self.app.recent_sessions)
        if not num_of_recents:
            return
        if num_of_card == 1:
            session_date = self.app.recent_sessions[0]
            session = self.app.sessions[session_date]
            session_workout_key = session.workout_key
            session_split = session.workout_split

            self.app.start_workout(session_workout_key, session_split)
        elif num_of_card == 2:
            if num_of_recents == 1:
                return
            else:
                session_date = self.app.recent_sessions[1]
                session = self.app.sessions[session_date]
                session_workout_key = session.workout_key
                session_split = session.workout_split
                self.app.start_workout(session_workout_key, session_split)

    def view_recent_session(self, num_of_card):
        num_of_recents = len(self.app.recent_sessions)
        if not num_of_recents:
            return
        if num_of_card == 1:
            session_date = self.app.recent_sessions[0]
            self.app.view_session(session_date)
        elif num_of_card == 2:
            if num_of_recents == 1:
                return
            else:
                session_date = self.app.recent_sessions[1]
                self.app.view_session(session_date)
