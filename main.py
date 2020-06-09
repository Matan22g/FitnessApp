import ast
from time import sleep

import certifi
from kivy.network.urlrequest import UrlRequest
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, NoTransition
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDTextButton, MDFloatingActionButton, MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard, MDSeparator
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from FirebaseLoginScreen.firebaseloginscreen import FirebaseLoginScreen
import kivy.utils as utils
import requests
import json
from kivymd.uix.picker import MDTimePicker, MDThemePicker

Window.size = (360, 639)


class HomeScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"

    def on_enter(self, *args):
        self.app.title = "Home"

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

    def on_pre_enter(self, *args):
        self.app.title = "Workouts"


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
            max_height=(Window.size[1] / 3)
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


class FriendsScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_enter(self, *args):
        self.app.title = "Friends"


class MainApp(MDApp):
    id_token = ""
    local_id = ""
    user_data = []
    workouts = {}  # straight from database
    workoutsANLAYZE = {}  # analyze to list
    friends_list = {}  # will have all usernames of the users friends.
    dialog = ""  # for presenting dialog to user.
    workout_to_delete = 0  # saving the workout obj between function.

    def __init__(self, **kwargs):
        self.title = "FitnessApp"
        self.theme_cls.primary_palette = "Indigo"
        super().__init__(**kwargs)

    def on_start(self):
        self.root.ids['nav_drawer'].swipe_edge_width = -2  # before login, denies access to navigation drawer

    def on_login(self):
        # loads data
        self.get_user_data()
        self.load_workout_data()
        # TEST OF USER NAME
        user_name = "Matan22G"
        self.root.ids['toolbar'].title = "Hello " + user_name
        self.get_user_name_data("Matan22g")

    # for login screens
    def change_screen(self, screen_name, *args):
        # Get the screen manager from the kv file
        screen_manager = self.root.ids['screen_manager']
        if args:
            if args[0]:  # optional transition direction
                screen_manager.transition.direction = args[0]
            else:
                screen_manager.transition.direction = "left"
            # if args[1]:  # optional no transition
            #     screen_manager.transition = NoTransition()
        screen_manager.current = screen_name
        screen_manager = self.root.ids

    # for app screens
    def change_screen1(self, screen_name, *args):
        # Get the screen manager from the kv file
        # args is an optional input of which direction the change will occur
        screen_manager = self.root.ids['screen_manager1']
        if args:
            if args[0]:  # optional transition direction
                screen_manager.transition.direction = args[0]
        else:
            screen_manager.transition.direction = "left"
            # if args[1]:  # optional no transition
            #     screen_manager.transition = NoTransition()
        screen_manager.current = screen_name
        screen_manager = self.root.ids

    def load_workout_data(self):
        # try:
        self.get_user_data()
        workoutdic = self.user_data["workouts"]  # gets workout data
        keysToAdd = []
        self.workouts = {}  # solution in case of deleted workout. reloads all database workouts
        for workoutkey in workoutdic:
            workout = workoutdic[workoutkey]
            workout = json.loads(workout)  # turning str to dic
            self.workouts[workoutkey] = workout  # creating an object of list of keys and workouts

        self.workoutsANLAYZE = self.parse_workout(
            self.workouts)  # Need to reconsider this depending, on workout anylysis.
        self.add_workouts(self.workoutsANLAYZE)

        # except Exception:
        # print("no workouts")

    def parse_workout(self, workoutIdDic):
        # turning json data into iterable list, retrun dic of workout dics {key: {workout name :[[split 1],[split2]]}}
        workoutdicReadAble = {}
        for workoutkey in workoutIdDic:
            workoutTemp = {}
            workoutdic = workoutIdDic[workoutkey]  # argument 0 is the workout id, and 1 is the dict
            for workoutName in workoutdic:
                exercises = workoutdic[workoutName]  # getting the the exercises of the workout
                exercises = ast.literal_eval(exercises)  # turning the str to list
                workoutTemp[workoutName] = exercises
            workoutdicReadAble[workoutkey] = workoutTemp
        return workoutdicReadAble

    def add_workouts(self, workoutDic):
        self.delete_workout_grid()
        workoutgrid = self.root.ids['workoutsscreen'].ids[
            'banner_grid']  # getting the id of where the widgets are coming in
        for workoutkey in workoutDic:
            workoutdic = workoutDic[workoutkey]  # argument 0 is the workout id, and 1 is the dict
            for workoutname in workoutdic:
                exercises = workoutdic[workoutname]  # getting the the exercises of the workout
                splits = ""
                totalsplits = ""
                lines = 0
                for numofsplit, split in enumerate(exercises):
                    splits = "Split " + str(numofsplit + 1) + ": "
                    separator = ', '
                    exercisesstr = separator.join(split)
                    splits = splits + exercisesstr + "."
                    splitsleng = len(splits)
                    if splitsleng > 37:
                        lines += int(splitsleng / 38)
                    totalsplits += splits + "\n"
                    lines += 1

                cardsizey = 170
                if lines > 1:  # adjusting card size according to splitsnum
                    cardsizey = str(cardsizey + (12.8 * lines))
                cardsizex = str(Window.size[0] - 20) + "dp"

                newlayout = MDFloatLayout()  # for centering
                workoutcard = MDCard(
                    radius=[14],
                    orientation="vertical",
                    size_hint=(None, None),
                    size=(cardsizex, cardsizey),
                    padding="7dp",
                    pos_hint={"center_y": 0.5, "center_x": 0.5}
                )
                workoutcard.add_widget(MDLabel(
                    text=workoutname,
                    size_hint=(None, 0.5),
                    theme_text_color="Secondary",
                    size=("280dp", "120dp")))
                workoutcard.add_widget(MDSeparator(
                    height="1dp"))
                workoutcard.add_widget(MDLabel(
                    theme_text_color="Primary",
                    text=totalsplits
                ))
                startButton = MDFloatingActionButton(
                    icon="play",
                    md_bg_color=[1, 0, 0, 1],
                    background_palette="Indigo",
                    elevation_normal=4,
                    on_release=self.workoutbuttons
                )
                editButton = MDFloatingActionButton(
                    icon="file-edit",
                    background_palette="BlueGray",
                    elevation_normal=4,
                )
                deleteButton = MDFloatingActionButton(
                    icon="trash-can",
                    background_palette="Indigo",
                    elevation_normal=4,
                    pos_hint={'right': 0},
                    on_release=self.delete_workout_msg
                )
                buttonlayout = MDBoxLayout(
                    adaptive_height=True,
                    orientation='horizontal',
                    spacing=20
                )

                keybutton = MDRaisedButton(
                    opacity=0,
                    size_hint=(.01, .2 / 3),
                    text=workoutkey
                )
                buttonlayout.add_widget(keybutton)
                buttonlayout.add_widget(startButton)
                buttonlayout.add_widget(editButton)
                buttonlayout.add_widget(deleteButton)
                workoutcard.add_widget(buttonlayout)
                newlayout.add_widget(workoutcard)
                workoutgrid.add_widget(newlayout)

    def workoutbuttons(self, *args):
        # parent-buttons layout, has a hidden button[the fourth one] with the workout key.
        print(args[0].icon)
        workoutkey = args[0].parent.children[3].text

    def delete_workout_msg(self, *args):
        self.workout_to_delete = args[0]  # saving the object we want to delete
        workoutname = args[0].parent.parent.children[3].text
        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.7, None),
                               text="Delete " + workoutname + "?",
                               buttons=[
                                   MDFlatButton(
                                       text="DELETE", text_color=self.theme_cls.primary_color,
                                       on_release=self.del_workout
                                   ),
                                   MDFlatButton(
                                       text="CANCEL", text_color=self.theme_cls.primary_color,
                                       on_release=self.cancel_del_workout
                                   )
                               ],
                               )
        self.dialog.open()

    def cancel_del_workout(self, *args):
        self.workout_to_delete = 0
        self.dialog.dismiss()

    def del_workout(self, caller):
        if self.workout_to_delete:
            workoutkey = self.workout_to_delete.parent.children[3].text
            workoutlink = "https://gymbuddy2.firebaseio.com/%s/workouts/%s.json?auth=%s" % (
                self.local_id, workoutkey, self.id_token)
            del_req = UrlRequest(workoutlink, on_success=self.success_del_workout, on_error=self.error_del_workout,
                                 on_failure=self.error_del_workout,
                                 ca_file=certifi.where(), method='DELETE', verify=True)
            self.workoutsANLAYZE.pop(workoutkey)
        else:
            print("error no workout to delete")
            self.dialog.dismiss()

    def success_del_workout(self, req, result):
        # self.load_workout_data()
        self.add_workouts(self.workoutsANLAYZE)
        self.dialog.dismiss()
        self.workout_to_delete = 0

    def error_del_workout(self, *args):
        # show proper msg
        print('failed')

    def delete_workout_grid(self):
        workoutgrid = self.root.ids['workoutsscreen'].ids[
            'banner_grid']  # getting the id of where the widgets are coming in
        if workoutgrid.children:
            for child in workoutgrid.children[:]:
                workoutgrid.remove_widget(child)

    # test username methods
    #######################
    def get_user_data(self):
        try:
            result = requests.get("https://gymbuddy2.firebaseio.com/" + self.local_id + ".json?auth=" + self.id_token)
            data = json.loads(result.content.decode())
            self.user_data = data
            # getting the user data upon login and
            # print("https://gymbuddy2.firebaseio.com/" + self.local_id + ".json?auth=" + self.id_token)
            # print(result.content.decode())
            # print("id token is", self.id_token)
            # print(result.ok)
            # print("DATA IS", data)
            # print(data["workouts"])
            # print(data["workouts"].keys())

        except Exception:
            print("no data")

    def openR(self, req, result):
        pass
        # print("FUQ YEA", result)

    def on_error(self, *args):
        print('failed')

    def get_user_name_data(self, user_name):
        # Query database and make sure friend_id exists
        user_name = '"' + user_name + '"'
        link = 'https://gymbuddy2.firebaseio.com/.json?orderBy="user_name"&equalTo=' + user_name
        check_req = requests.get(link)
        req = UrlRequest(link, on_success=self.openR, on_error=self.on_error, on_failure=self.on_error,
                         ca_file=certifi.where(), verify=True)
        data = check_req.json()
        # if data:
        #     print(True)
        # else:
        #     print(False)
        # print(user_name[1:-1] + " data is: ", data)

    def is_user_exist(self, user_name):
        user_name = '"' + user_name + '"'
        check_req = requests.get(
            'https://gymbuddy2.firebaseio.com/.json?orderBy="user_name"&equalTo=' + user_name)
        data = check_req.json()
        if data:
            return True
        else:
            return False

    #######################


MainApp().run()
