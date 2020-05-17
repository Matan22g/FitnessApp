from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from FirebaseLoginScreen.firebaseloginscreen import FirebaseLoginScreen
import kivy.utils as utils
import requests
import json

Window.size = (420, 630)


class HomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"

    def on_enter(self, *args):
        self.app.title = "Home"

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


class WorkoutsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.limit = 5
        self.Exercise = 0

    def on_enter(self, *args):
        self.app.title = "Workouts"

    def addworkout(self):
        limit = self.limit
        if self.Exercise < limit:
            self.Exercise += 1
            exid = "ex" + str(self.Exercise)
            self.ids[exid].opacity = 1

            # pos = {"x": .35, "y": heig}
            # b1 = MDTextField(id=str(self.Exercise), text="name of workout", pos_hint=pos, size_hint= (.3, .1))
            # print (b1)
            # self.add_widget(b1)
        else:
            msg = "Cannot add more than\n" + str(limit) + " exercises at the moment."
            self.app.dialog = MDDialog(text=msg, radius=[10, 7, 10, 7], size_hint=(0.5, None))
            self.app.dialog.open()

    def deleteworkout(self):
        limit = self.limit
        if self.Exercise > 0:
            exid = "ex" + str(self.Exercise)
            self.Exercise -= 1
            self.ids[exid].opacity = 0

    def workoutvalid(self):
        msg = ""
        if len(self.ids["ex0"].text) == 0:
            msg = "Choose a name for the workout"
        elif self.Exercise == 0:
            msg = "Enter at least one exercise"
        else:
            for i in range(self.Exercise):
                exid = "ex" + str(i + 1)
                if len(self.ids[exid].text) == 0:
                    msg = "Name all the exercises"
                    break
        return msg

    def saveworkout(self):
        msg = self.workoutvalid()
        if len(msg) == 0:
            self.app.change_screen1("homescreen")
            exercises = []
            workout_name = self.ids["ex0"].text
            for i in range(self.Exercise):
                exid = "ex" + str(i + 1)
                exercises.append(self.ids[exid].text)
            for i in range(self.Exercise + 1):
                exid = "ex" + str(i)
                self.ids[exid].text = ""
                self.ids[exid].focus = False
                if i > 0:
                    self.ids[exid].opacity = 0
            self.Exercise = 0
            print(exercises)
            self.app.change_screen1("homescreen")
            return True
        else:
            self.app.dialog = MDDialog(text=msg, radius=[10, 7, 10, 7], size_hint=(0.5, None))
            self.app.dialog.open()
            return False


class FriendsScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_enter(self, *args):
        self.app.title = "Friends"


class MainApp(MDApp):
    my_friend_id = ""
    friends_list = ""

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
        pass
        # Get database data
        # result = requests.get("https://gymbuddy2.firebaseio.com/" + str(self.my_friend_id) + ".json")
        # print(json.loads(result.content.decode()))
        # data = json.loads(result.content.decode())  # loads string into dic
        # print(data['workouts'])
        # workouts = data['workouts']
        # for workout in workouts.split(", "):
        #     print(workout)


MainApp().run()
