import json

from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
import requests
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

Window.size = (360, 639)


class Create_Workout_Screen(Screen):
    workoutName = []
    splits = 0
    newWorkout = 1
    exercises = []

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.exercise = 0
        self.MaxSplits = 3

    def on_pre_enter(self, *args):
        self.app.title = "Workouts"

        if not self.workoutName:
            self.ids["ex0"].text = ""
        if not self.splits:
            self.ids.dropdown_item.set_item("How many splits?")

    def on_enter(self, *args):
        self.app.title = "Workouts"
        menu_items = [{"icon": "arm-flex", "text": f"{i}"} for i in range(1, self.MaxSplits + 1)]
        self.menu = MDDropdownMenu(
            caller=self.ids.dropdown_item,
            items=menu_items,
            position="bottom",
            callback=self.set_item,
            width_mult=3,
            max_height=(self.app.root.height / 3)
        )

    def set_item(self, instance):
        self.ids.dropdown_item.set_item(instance.text)
        self.menu.dismiss()
        msg = instance.text.split(" ")[0]
        if Create_Workout_Screen.splits > 0:  # if user change split, reseting the exercises
            Create_Workout_Screen.exercises = []
        else:
            Create_Workout_Screen.newWorkout = int(msg)  # else its a new workout input, saving how many pages to clear.
        Create_Workout_Screen.splits = int(msg)

    def isValid(self):
        msg = ""
        if len(self.ids["ex0"].text) == 0:
            msg = "Choose name for the workout"

        elif self.splits == 0:
            msg = "Choose how many splits"

        if len(msg) == 0:
            if not Create_Workout_Screen.workoutName:  # First visit in this creating workout session
                Create_Workout_Screen.workoutName.append(self.ids["ex0"].text)
                Create_Workout_Screen.newWorkout = Create_Workout_Screen.splits
            self.app.change_screen1("splitscreen")
        else:
            self.app.dialog = MDDialog(text=msg, radius=[10, 7, 10, 7], size_hint=(0.5, None))
            self.app.dialog.open()


class SplitScreensMain(Screen):
    split = 0
    nextPressed = False

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.limit = 12
        self.exercise = 0

    def on_pre_enter(self, *args):
        self.app.title = "Workouts"
        if Create_Workout_Screen.splits > self.split:  # switching between next and save button.
            self.ids.savebutton.opacity = 0
            self.ids.nextbutton.opacity = 1
            self.ids.savebutton.disabled = True
            self.ids.nextbutton.disabled = False
        else:
            self.ids.savebutton.opacity = 1
            self.ids.nextbutton.opacity = 0
            self.ids.savebutton.disabled = False
            self.ids.nextbutton.disabled = True
        if Create_Workout_Screen.newWorkout:  # in case of save pressed on the next split, and this page in not clean
            self.nextPressed = False
            self.cleanScreen()
            Create_Workout_Screen.newWorkout -= 1  # for knowing when not to clean when switching between pages
        if not Create_Workout_Screen.exercises:  # if the user changed splits exercises got reset
            self.nextPressed = False  # on the next button click saving will save the new exercises

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
        if Create_Workout_Screen.splits > self.split:
            if self.nextPressed:
                return True
        msg = self.workoutvalid()
        if len(msg) == 0:
            exercises = []
            workout_name = Create_Workout_Screen.workoutName[0]
            for i in range(self.exercise):
                exid = "ex" + str(i + 1)
                exercises.append(self.ids[exid].text)
            Create_Workout_Screen.exercises.append(exercises)
            if Create_Workout_Screen.splits > self.split:
                self.nextPressed = True
                return True
            Workout = "{%s: %s}" % ('"' + workout_name + '"', '"' + str(Create_Workout_Screen.exercises) + '"')
            self.cleanScreen()
            self.uploadWorkout(workout_name, Create_Workout_Screen.exercises)
            Create_Workout_Screen.exercises = []
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

    def uploadWorkout(self, workout_name, exercises):
        Workout = "{%s: %s}" % ('"' + workout_name + '"', '"' + str(Create_Workout_Screen.exercises) + '"')
        workout_request = requests.post("https://gymbuddy2.firebaseio.com/%s/workouts.json?auth=%s"
                                        % (self.app.local_id, self.app.id_token), data=json.dumps(Workout))


class SplitScreen(SplitScreensMain):
    split = 1
    nextPressed = False


class SplitScreen2(SplitScreensMain):
    split = 2
    nextPressed = False


class SplitScreen3(SplitScreensMain):
    split = 3
    nextPressed = False
