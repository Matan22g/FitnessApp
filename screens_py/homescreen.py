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
        try:
            if self.app.units == "metric":
                self.ids["weight_units"].text = "Kg"
            else:
                self.ids["weight_units"].text = "Lbs"
        except:
            pass

    def on_quick_menu(self, *args):
        print(args[0].icon
              )

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