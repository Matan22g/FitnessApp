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
            self.app.change_title("Dashboard")
        except:
            pass

    def on_enter(self, *args):
        self.app.title = "Home"
        if "None" not in self.app.exc_pie_dic[0]:
            self.app.update_chart()

    def addworkout(self, *args):
        self.app.change_screen1("workoutsscreen")

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