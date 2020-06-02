import ast
from kivy.uix.floatlayout import FloatLayout
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivymd.uix.button import MDTextButton, MDFloatingActionButton
from kivymd.uix.card import MDCard, MDSeparator
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
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


class Create_Workout_Screen(Screen):
    workoutName = []
    splits = 0
    newWorkout = 1

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.exercise = 0
        self.MaxSplits = 2

    def on_pre_enter(self, *args):
        if not self.workoutName:
            self.ids["ex0"].text = ""
        if not self.splits:
            self.ids.dropdown_item.set_item("How many splits?")

    def on_enter(self, *args):
        self.app.title = "Workouts"
        menu_items = [{"icon": "arm-flex", "text": f"{i} split"} for i in range(1, self.MaxSplits + 1)]
        self.menu = MDDropdownMenu(
            caller=self.ids.dropdown_item,
            items=menu_items,
            position="bottom",
            callback=self.set_item,
            width_mult=3,
        )

    def set_item(self, instance):
        self.ids.dropdown_item.set_item(instance.text)
        self.menu.dismiss()
        msg = instance.text.split(" ")[0]
        Create_Workout_Screen.splits = int(msg)

    def isValid(self):
        msg = ""
        if len(self.ids["ex0"].text) == 0:
            msg = "Choose name for the workout"

        elif Create_Workout_Screen.splits == 0:
            msg = "Choose how many splits"

        if len(msg) == 0:
            if not self.workoutName:  # First visit in this creating workout session
                self.workoutName.append(self.ids["ex0"].text)
                Create_Workout_Screen.newWorkout = 1
            print(self.workoutName)
            self.app.change_screen1("splitscreen")
        else:
            self.app.dialog = MDDialog(text=msg, radius=[10, 7, 10, 7], size_hint=(0.5, None))
            self.app.dialog.open()


class WorkoutsScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self, *args):
        pass

    def on_enter(self, *args):
        pass

    def isValid(self):
        msg = ""
        if len(self.ids["ex0"].text) == 0:
            msg = "Choose name for the workout"

        elif Create_Workout_Screen.splits == 0:
            msg = "Choose how many splits"

        if len(msg) == 0:
            if not self.workoutName:  # First visit in this creating workout session
                self.workoutName.append(self.ids["ex0"].text)
                Create_Workout_Screen.newWorkout = 1
            print(self.workoutName)
            self.app.change_screen1("splitscreen")
        else:
            self.app.dialog = MDDialog(text=msg, radius=[10, 7, 10, 7], size_hint=(0.5, None))
            self.app.dialog.open()


class SplitScreen(Screen):
    exercises = []

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.limit = 12
        self.exercise = 0

    def on_pre_enter(self, *args):
        self.app.title = "Workouts"
        if Create_Workout_Screen.splits > 1:  # switching between next and save button.
            self.ids.savebutton.opacity = 0
            self.ids.nextbutton.opacity = 1
            self.ids.savebutton.disabled = True
            self.ids.nextbutton.disabled = False
        else:
            self.ids.savebutton.opacity = 1
            self.ids.nextbutton.opacity = 0
            self.ids.savebutton.disabled = False
            self.ids.nextbutton.disabled = True
        if Create_Workout_Screen.newWorkout:  # incase of save pressed on the next split, and this page in not clean
            self.cleanScreen()
        Create_Workout_Screen.newWorkout = 0  # know not to clean when switching between pages

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
        if self.exercise == 0:
            msg = "Enter at least one exercise"
        else:
            for i in range(self.exercise):
                exid = "ex" + str(i + 1)
                if len(self.ids[exid].text) == 0:
                    msg = "Name all the exercises"
                    break
        return msg

    def cleanScreen(self):
        for i in range(1, self.exercise + 1):
            exid = "ex" + str(i)
            self.ids[exid].text = ""
            self.ids[exid].focus = False
            self.ids[exid].opacity = 0
        self.exercise = 0

    def saveworkout(self):
        msg = self.workoutvalid()
        if len(msg) == 0:
            exercises = []
            workout_name = Create_Workout_Screen.workoutName[0]
            for i in range(self.exercise):
                exid = "ex" + str(i + 1)
                exercises.append(self.ids[exid].text)
            if Create_Workout_Screen.splits > 1:
                self.exercises.extend(exercises)
                return True
            Workout = "{%s: %s}" % ('"' + workout_name + '"', '"' + str(exercises) + '"')
            self.cleanScreen()
            self.uploadWorkout(Workout)
            Create_Workout_Screen.workoutName = []
            Create_Workout_Screen.splits = 0
            Create_Workout_Screen.newWorkout = 1
            self.app.change_screen1("homescreen")
            self.app.load_workout_data()
            return True
        else:
            self.app.dialog = MDDialog(text=msg, radius=[10, 7, 10, 7], size_hint=(0.5, None))
            self.app.dialog.open()
            return False

    def uploadWorkout(self, workout):
        workout_request = requests.post("https://gymbuddy2.firebaseio.com/%s/workouts.json?auth=%s"
                                        % (self.app.local_id, self.app.id_token), data=json.dumps(workout))


# try ineheritence for not duplicate code
class SplitScreen2(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.limit = 12
        self.exercise = 0

    def on_pre_enter(self, *args):
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
        if self.exercise == 0:
            msg = "Enter at least one exercise"
        else:
            for i in range(self.exercise):
                exid = "ex" + str(i + 1)
                if len(self.ids[exid].text) == 0:
                    msg = "Name all the exercises"
                    break
        return msg

    def cleanScreen(self):
        for i in range(1, self.exercise + 1):
            exid = "ex" + str(i)
            self.ids[exid].text = ""
            self.ids[exid].focus = False
            self.ids[exid].opacity = 0
        # after save, needs restart values
        self.exercise = 0

    def saveworkout(self):
        msg = self.workoutvalid()
        if len(msg) == 0:
            exercises = []
            workout_name = Create_Workout_Screen.workoutName[0]
            print(Create_Workout_Screen.workoutName)
            for i in range(self.exercise):
                exid = "ex" + str(i + 1)
                exercises.append(self.ids[exid].text)
            self.cleanScreen()
            self.exercise = 0
            split1 = SplitScreen.exercises
            totalWorkout = [split1, exercises]
            Workout = "{%s: %s}" % ('"' + workout_name + '"', '"' + str(totalWorkout) + '"')
            self.uploadWorkout(Workout)
            Create_Workout_Screen.workoutName = []
            Create_Workout_Screen.splits = 0
            Create_Workout_Screen.newWorkout = 1
            self.app.change_screen1("homescreen")
            self.app.load_workout_data()
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
    workouts = {}

    def __init__(self, **kwargs):
        self.title = "FitnessApp"
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

    def change_screen1(self, screen_name, *args):
        # Get the screen manager from the kv file
        # args is an optional input of which direction the change will occur
        screen_manager = self.root.ids['screen_manager1']
        if args:
            screen_manager.transition.direction = args[0]
        else:
            screen_manager.transition.direction = "left"
        screen_manager.current = screen_name
        screen_manager = self.root.ids

    def on_start(self):
        self.root.ids['nav_drawer'].swipe_edge_width = -2

    def on_login(self):
        # loads data
        self.load_workout_data()

    def load_workout_data(self):
        try:
            # print("https://gymbuddy2.firebaseio.com/" + self.local_id + ".json?auth=" + self.id_token)
            result = requests.get("https://gymbuddy2.firebaseio.com/" + self.local_id + ".json?auth=" + self.id_token)
            # print(result.content.decode())
            data = json.loads(result.content.decode())
            # print("id token is", self.id_token)
            # print(result.ok)
            # print("DATA IS", data)
            # print(data["workouts"])

            # print(data["workouts"].keys())
            workoutdic = data["workouts"]  # gets workout data
            keysToAdd = []
            self.workouts = {}  # soultion in case of deleted workout. reloads all database workouts
            for workoutkey in workoutdic:
                workout = workoutdic[workoutkey]
                workout = json.loads(workout)  # turning str to dic
                if workoutkey not in self.workouts:
                    self.workouts[workoutkey] = workout  # creating an object of list of keys and workouts
                    keysToAdd.append(workoutkey)
            print(keysToAdd)
            self.addWorkouts(keysToAdd)
        except Exception:
            print("no data")

    def addWorkouts(self, keys):
        workoutgrid = self.root.ids['workoutsscreen'].ids[
            'banner_grid']  # getting the id of where the widgets are coming in
        for workoutkey in keys:
            workoutdic = self.workouts[workoutkey]  # argument 0 is the workout id, and 1 is the dict
            print(workoutdic)
            for workoutname in workoutdic:
                exercises = workoutdic[workoutname]  # getting the the exercises of the workout
                exercises = ast.literal_eval(exercises)  # turning the str to list
                splits = ""
                totalsplits = ""
                Splitted = any(isinstance(i, list) for i in exercises)  # checks if theres nested lists for spilts.
                for numofsplit, split in enumerate(exercises):
                    splits = "Split " + str(numofsplit + 1) + ": "
                    separator = ', '
                    if not Splitted:
                        exercisesstr = separator.join(exercises)
                        splits = splits + exercisesstr
                        totalsplits += splits + "\n"
                        break
                    exercisesstr = separator.join(split)
                    splits = splits + exercisesstr
                    totalsplits += splits + "\n"

                newlayout = FloatLayout()  # for centering
                workoutcard = MDCard(
                    orientation="vertical",
                    size_hint=(None, None),
                    size=("400dp", "160dp"),
                    padding="8dp",
                    pos_hint={"top": 1, "center_x": 0.5}
                )
                workoutcard.add_widget(MDLabel(
                    text="%s" % workoutname,
                    size_hint=(None, 0.5),
                    theme_text_color="Secondary",
                    size=("280dp", "120dp")))
                workoutcard.add_widget(MDSeparator(
                    height="1dp"))
                workoutcard.add_widget(MDLabel(
                    text="%s" % totalsplits
                ))
                md = MDFloatingActionButton(
                    icon="play",
                    md_bg_color=[1, 0, 0, .3],
                    elevation_normal=4,
                    pos_hint={"top": 1, "center_x": 0.9}
                )
                workoutcard.add_widget(md)
                newlayout.add_widget(workoutcard)
                workoutgrid.add_widget(newlayout)

    def deleteworkoutgrid(self):
        workoutgrid = self.root.ids['workoutsscreen'].ids[
            'banner_grid']  # getting the id of where the widgets are coming in
        if workoutgrid.children:
            for child in workoutgrid.children[:]:
                workoutgrid.remove_widget(child)


MainApp().run()
