from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from FirebaseLoginScreen.firebaseloginscreen import FirebaseLoginScreen
import kivy.utils as utils
import requests
import json
from kivymd.uix.picker import MDTimePicker, MDThemePicker

Window.size = (420, 630)


class HomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"

    def on_enter(self, *args):
        self.app.title = "Home"

    def addworkout(self, *args):
        self.app.change_screen1("workoutsscreen")

    # def is_binary(self, binary_number):
    #     try:
    #         decimal = int(binary_number, 2)
    #         self.ids["solution"].text = f'Your Number in Binary: {decimal}'
    #         self.ids["solution"].theme_text_color = "Primary"
    #     except ValueError:
    #         self.ids["solution"].text = "This is not Binary"
    #         self.ids["solution"].theme_text_color = "Error"


# class LoginScreen(Screen):
#     def __init__(self, **kw):
#         super().__init__(**kw)
#         self.app = MDApp.get_running_app()
#         self.sub_title = "Welcome! \nPlease Log in"
#         self.hint_username = "User Name"
#         self.hint_password = "Password"
#
#     def on_enter(self, *args):
#         self.app.title = "Login"
#
#     def is_binary(self, binary_number):
#         try:
#             decimal = int(binary_number, 2)
#             self.ids["solution"].text = f'Your Number in Binary: {decimal}'
#             self.ids["solution"].theme_text_color = "Primary"
#         except ValueError:
#             self.ids["solution"].text = "This is not Binary"
#             self.ids["solution"].theme_text_color = "Error"

class SettingsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_enter(self, *args):
        self.app.title = "Settings"

    def change_mode(self, checkbox, value):
        if value:
            self.app.theme_cls.theme_style = "Dark"
        else:
            self.app.theme_cls.theme_style = "Light"

    def show_theme_picker(self):
        theme_dialog = MDThemePicker()
        theme_dialog.open()


class WorkoutsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.limit = 12
        self.exercise = 0

    def on_enter(self, *args):
        self.app.title = "Workouts"

    def addexercise(self):
        # Add Another exercise

        limit = self.limit
        if self.exercise < limit:
            self.exercise += 1
            exid = "ex" + str(self.exercise)
            self.ids[exid].opacity = 1
        else:
            msg = "Cannot add more than\n" + str(limit) + " exercises at the moment."
            self.app.dialog = MDDialog(text=msg, radius=[10, 7, 10, 7], size_hint=(0.5, None))
            self.app.dialog.open()

    def deleteworkout(self):
        limit = self.limit
        if self.exercise > 0:
            exid = "ex" + str(self.exercise)
            self.exercise -= 1
            self.ids[exid].opacity = 0

    def workoutvalid(self):
        msg = ""
        if len(self.ids["ex0"].text) == 0:
            msg = "Choose name for the workout"
        elif self.exercise == 0:
            msg = "Enter at least one exercise"
        else:
            for i in range(self.exercise):
                exid = "ex" + str(i + 1)
                if len(self.ids[exid].text) == 0:
                    msg = "Name all the exercises"
                    break
        return msg

    def clearworkout(self):
        pass

    def saveworkout(self):
        msg = self.workoutvalid()
        if len(msg) == 0:
            exercises = []
            workout_name = self.ids["ex0"].text
            for i in range(self.exercise):
                exid = "ex" + str(i + 1)
                exercises.append(self.ids[exid].text)
            for i in range(self.exercise + 1):
                exid = "ex" + str(i)
                self.ids[exid].text = ""
                self.ids[exid].focus = False
                if i > 0:
                    self.ids[exid].opacity = 0
            self.exercise = 0
            Workout = "{%s: %s}" % (workout_name, exercises)
            self.uploadWorkout(Workout)
            print(Workout)
            self.app.change_screen1("homescreen")
            return True
        else:
            self.app.dialog = MDDialog(text=msg, radius=[10, 7, 10, 7], size_hint=(0.5, None))
            self.app.dialog.open()
            return False

    def uploadWorkout(self, workout):
        workout_request = requests.post("https://gymbuddy2.firebaseio.com/%s/workouts.json?auth=%s"
                                        % (self.app.local_id, self.app.id_token), data=json.dumps(workout))


class FriendsScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_enter(self, *args):
        self.app.title = "Friends"


class MainApp(MDApp):
    my_friend_id = ""
    friends_list = ""
    id_token = ""
    local_id = ""

    def __init__(self, **kwargs):
        self.title = "KivyMD Example - Backdrop"
        self.theme_cls.primary_palette = "Indigo"
        super().__init__(**kwargs)

    def set_friend_id(self, my_friend_id):
        self.my_friend_id = my_friend_id
        # friend_id_label = self.root.ids['settings_screen'].ids['friend_id_label']
        # friend_id_label.text = "Friend ID: " + str(self.my_friend_id)

    def change_screen(self, screen_name):
        # Get the screen manager from the kv file
        screen_manager = self.root.ids['screen_manager']
        screen_manager.transition.direction = 'left'
        screen_manager.current = screen_name
        screen_manager = self.root.ids

    def change_screen1(self, screen_name):
        # Get the screen manager from the kv file
        screen_manager = self.root.ids['screen_manager1']
        screen_manager.transition.direction = 'left'
        screen_manager.current = screen_name
        screen_manager = self.root.ids

    def on_start(self):
        self.root.ids['nav_drawer'].swipe_edge_width = -2
        # try:
        #     # Try to read the persisten signin credentials (refresh token)
        #     with open("refresh_token.txt", 'r') as f:
        #         refresh_token = f.read()
        #     # Use refresh token to get a new idToken
        #     id_token, local_id = self.my_firebase.exchange_refresh_token(refresh_token)
        #     self.local_id = local_id
        #     self.id_token = id_token
        # except Exception as e:
        #     print(e)
        #     pass
        # Get database data
        # result = requests.get("https://gymbuddy2.firebaseio.com/" + str(self.my_friend_id) + ".json")
        # print(json.loads(result.content.decode()))
        # data = json.loads(result.content.decode())  # loads string into dic
        # print(data['workouts'])
        # workouts = data['workouts']
        # for workout in workouts.split(", "):
        #     print(workout)


MainApp().run()
