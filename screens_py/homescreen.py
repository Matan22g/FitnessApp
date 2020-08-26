from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from akivymd.uix.datepicker import AKDatePicker


class HomeScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"

    def on_enter(self, *args):
        self.app.title = "Home"

    def addworkout(self, *args):
        self.app.change_screen1("workoutsscreen")

    def choose_date(self):
        new_date = AKDatePicker(callback=self.new_date)
        new_date.open()
        print(new_date)

    def new_date(self, date):
        if not date:
            return
        new_date = '%d / %d / %d' % (date.day, date.month, date.year)
        print(new_date)
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