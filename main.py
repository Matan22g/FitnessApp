import ast
from datetime import datetime

import certifi
from kivy.network.urlrequest import UrlRequest
from kivy.properties import NumericProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, NoTransition, SlideTransition
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDTextButton, MDFloatingActionButton, MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard, MDSeparator
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from FirebaseLoginScreen.firebaseloginscreen import FirebaseLoginScreen
import kivy.utils as utils
import requests
import json
from kivy.clock import Clock
import time

Window.size = (360, 639)

### screens classes import

from screens_py.create_workout_screen import Create_Workout_Screen, SplitScreensMain, SplitScreen, SplitScreen2, \
    SplitScreen3
from screens_py.homescreen import HomeScreen
from screens_py.settingsscreen import SettingsScreen
from screens_py.workoutsscreen import WorkoutsScreen
from screens_py.sessionscreen import SessionScreen, ExerciseScreen
from customKv.tab import MDTabs, MDTabsBase


class FriendsScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_enter(self, *args):
        self.app.title = "Friends"


# Class for handling sessions data.
class Workout_Session:

    def __init__(self, session_key, date, duration, workout_key, workout_name, workout_split, exercises):
        self.session_key = session_key
        self.date = date
        self.duration = duration
        self.workout_key = workout_key
        self.workout_name = workout_name
        self.workout_split = workout_split
        self.exercises = exercises


class Tab(FloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''


class MainApp(MDApp):
    mainscreens = ["homescreen", "workoutscreen", "friendsscreen", "settingsscreen"]
    id_token = ""
    local_id = ""
    user_data = []  # on login loads all user data
    workouts = {}  # straight from database
    workoutsParsed = {}  # analyze to list  'workout_key': {'name': "[['exc1'], ['exc2']]"} ----> '-workout_key': {'name': [['exc1'], ['exc2']]}
    sessions = []  # list of sessions obj
    sessions_by_key = {}  # dic of all sessions -- may be not needed ***
    friends_list = {}  # will have all user names of the users friends.
    dialog = ""  # for presenting dialog to user.
    workout_to_delete = 0  # saving the workout obj between function.
    toTrainWorkout = 0  # saving workout key to train.
    lastscreens = []  # saving pages for back button.
    new_session = 0  # indicator for starting a new session.
    debug = 0
    running_session = 0  # indicator for running session - shows a button that helps the user return to the session
    timer = NumericProperty()  # timer that increment in seconds
    timer_format = ""  # for storing seconds in %H:%M:%S format
    split_Choice_dict = {}  # workout key with split choice

    def __init__(self, **kwargs):
        self.title = "FitnessApp"
        super().__init__(**kwargs)

    def on_start(self):
        # before login, denies access to navigation drawer
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Indigo"
        self.root.ids['nav_drawer'].swipe_edge_width = -2

    def on_login(self):
        # loads data
        self.get_user_data()
        self.change_screen1("homescreen")
        self.load_workout_data()
        self.load_session_data()

        # Initial left menu obj to settings
        self.root.ids['toolbar'].left_action_items = [["cog-outline", lambda x: self.change_screen1("settingsscreen")]]
        # TEST OF USER NAME
        user_name = self.user_data["real_user_name"]
        self.root.ids['toolbar'].title = "Hello " + user_name
        # self.get_user_name_data(user_name)
        ### debug:
        if self.debug == 1:
            self.toTrainWorkout = "-M9NjJ45dRBIxqEQ40LC"
            self.chose_split(1)
            # self.change_screen1("sessionscreen")

        #
        # date = "date"
        # workout_key = "workout_key"
        # num_of_split = 4
        # session_rec = {"exc1": "4 X 8", "exc2": "5*9"}
        # link = "https://gymbuddy2.firebaseio.com/%s/sessions.json?auth=%s" % (self.local_id, self.id_token)
        # Workout = "{%s: %s: %s}" % (
        #     '"' + workout_key + '"', '"' + str(num_of_split) + '"', '"' + str(session_rec) + '"')
        # data = json.dumps(Workout)
        # req = UrlRequest(link, req_body=data,
        #                  ca_file=certifi.where(), verify=True)

    # Handling user data
    def get_user_data(self):
        try:
            result = requests.get("https://gymbuddy2.firebaseio.com/" + self.local_id + ".json?auth=" + self.id_token)
            data = json.loads(result.content.decode())
            self.user_data = data
            if self.debug:
                print(data)

        except Exception:
            print("no data")

    def load_session_data(self):
        # Creates a sessions obj list sorted by dates

        session_dic = self.user_data["sessions"]
        if self.debug:
            print("session dic: ", session_dic)

        for session_key in session_dic:
            session = ast.literal_eval(session_dic[session_key][1:-1])  # turning the str to list
            date = datetime.strptime(session[0], "%d/%m/%Y %H:%M:%S")
            duration = session[1]
            workout_key = session[2]
            workout_name = session[3]
            workout_split = session[4]
            exercises = session[5]
            new_session = Workout_Session(session_key, date, duration, workout_key, workout_name, workout_split,
                                          exercises)
            self.sessions.append(new_session)

        self.sessions.sort(key=lambda r: r.date, reverse=True)

    # Initial workouts dicts, and workouts screen
    def load_workout_data(self):
        # try:
        workoutdic = self.user_data["workouts"]  # gets workout data
        keysToAdd = []
        self.workouts = {}  # solve case of deleted workout. reloads all database workouts
        for workoutkey in workoutdic:
            workout = workoutdic[workoutkey]
            workout = json.loads(workout)  # turning str to dic
            self.workouts[workoutkey] = workout  # creating an object of list of keys and workouts

        self.workoutsParsed = self.parse_workout(
            self.workouts)  # Need to reconsider this depending on workout analysis.
        self.add_workouts(self.workoutsParsed)

        # except Exception:
        # print("no workouts")

    def parse_workout(self, workoutIdDic):
        # json data to iterable list, return dict of workout dicts {key: {workout name :[[split 1],[split2]]}}
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

                newlayout = MDFloatLayout()  # for centering

                workoutcard = MDCard(
                    radius=[14],
                    orientation="vertical",
                    size_hint=(0.9, 0.9),
                    padding="8dp",
                    pos_hint={"center_y": 0.5, "center_x": 0.5}
                )
                workoutcard.add_widget(MDLabel(
                    text=workoutname,
                    font_style="H4",
                    size_hint=(None, 0.1),
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color
                ))
                splits_tabs = MDTabs(
                    on_tab_switch=self.on_split_switch
                )
                splits_tabs.background_color=(1, 1, 1, 1)
                splits_tabs.text_color_normal=(0, 0, 0, 1)
                splits_tabs.text_color_active=(0, 0, 1, 1)
                splits_tabs.color_indicator=(0, 0, 1, 1)

                for numofsplit, split in enumerate(exercises):
                    splits = "Split " + str(numofsplit + 1)
                    tab = Tab(text=splits)
                    layout = MDBoxLayout(orientation='vertical')
                    view = ScrollView()
                    layout.add_widget(view)
                    lst = MDList()
                    for exc in split:
                        lst.add_widget(OneLineListItem(text=exc))
                    view.add_widget(lst)
                    tab.add_widget(layout)
                    splits_tabs.add_widget(tab)
                workoutcard.add_widget(splits_tabs)

                startButton = MDIconButton(
                    icon="play",
                    pos_hint={'right': 0},
                    user_font_size="45sp",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.start_workout
                )
                editButton = MDIconButton(
                    icon="file-edit",
                    user_font_size="40sp",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.delete_workout_msg
                )
                deleteButton = MDIconButton(
                    icon="trash-can-outline",
                    pos_hint={'right': 0},
                    user_font_size="40sp",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
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

    def on_split_switch(self, *args):
        split_chosen = args[2]
        split_chosen = int(split_chosen[6])
        tab = args[0]
        workout_key = tab.parent.parent.parent.parent.parent.children[0].children[3].text
        self.split_Choice_dict[workout_key] = split_chosen

    # Methods for when User want to start a new workout session:
    def start_workout(self, *args):
        # start new session of workout

        workoutkey = args[0].parent.children[3].text
        workout_split = self.split_Choice_dict[workoutkey]

        workout_list = list(self.workoutsParsed[workoutkey].values())
        workout_name = list(self.workoutsParsed[workoutkey].keys())[0]
        num_splits = len(workout_list[0])
        chosen_workout = workout_list[0]  # List of exercise to train

        # getting the id of where the widgets are coming in, and clear exercise list
        session_grid = self.root.ids['sessionscreen'].ids[
            'exc_cards']
        session_grid.clear_widgets()

        SessionScreen.workout = chosen_workout[workout_split - 1]  # Sets the exercise list
        SessionScreen.workout_key = workoutkey  # Sets the workout key list
        SessionScreen.num_of_split = workout_split  # Sets which split was chosen

        # Reset all dicts from previous workouts
        SessionScreen.ex_reference_by_id = {}
        SessionScreen.ex_reference_by_exc = {}
        SessionScreen.session_rec = {}
        SessionScreen.ex_reference_by_checkBox = {}

        SessionScreen.workout_name = workout_name
        self.new_session = 1
        self.running_session = 1
        self.root.ids['workoutsscreen'].ids["running_session"].text = workout_name

        # Start workout timer.
        self.timer = 0
        Clock.schedule_interval(self.increment_time, .1)
        self.increment_time(0)
        self.start_timer()

        self.change_screen1("sessionscreen")

    def delete_workout_msg(self, *args):
        self.workout_to_delete = args[0]  # saving the object we want to delete
        workoutkey = args[0].parent.children[3].text
        workout_name = list(self.workoutsParsed[workoutkey].keys())[0]

        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.7, None),
                               text="Delete " + workout_name + "?",
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
            self.workoutsParsed.pop(workoutkey)
        else:
            print("error no workout to delete")
            self.dialog.dismiss()

    def success_del_workout(self, req, result):
        # self.load_workout_data()
        self.add_workouts(self.workoutsParsed)
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

    # Timer methods.
    def increment_time(self, interval):
        self.timer += .1
        self.timer_format = str(time.strftime('%H:%M:%S', time.gmtime(round(self.timer))))
        self.root.ids['sessionscreen'].ids["timer"].text = self.timer_format

    def start_timer(self):
        Clock.unschedule(self.increment_time)
        Clock.schedule_interval(self.increment_time, .1)

        # To stop the count / time

    def stop_timer(self):
        Clock.unschedule(self.increment_time)

    # Back button
    def back_to_last_screen(self, *args):
        # if current screen is mainscreen and last screen is main screen. go back to homescreen
        # if current screen is mainscreen and last screen isnt main screen. go back to lastpage
        # if current screen isnt main screen go back to lastpage

        # screen_manager = self.root.ids['screen_manager1']
        # current_screen = screen_manager.current
        # if self.lastscreens:
        #     if current_screen in self.mainscreens:
        #         if self.lastscreens[-1] in self.mainscreens:
        #             self.change_screen1("homescreen", "right")
        #         else:
        #             lastscreen = self.lastscreens.pop(-1)
        #             # -1 is 'back' indicator for change screen method
        #             self.change_screen1(lastscreen, -1, "right")
        # else:
        #     self.change_screen1("homescreen", "right")
        if self.lastscreens:
            lastscreen = self.lastscreens.pop(-1)
            # -1 is 'back' indicator for change screen method
            self.change_screen1(lastscreen, -1, "right")
        else:
            self.change_screen1("homescreen", "right")

    # For login screens
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

    # For app screens
    def change_screen1(self, screen_name, *args):
        # Get the screen manager from the kv file
        # args is an optional input of which direction the change will occur
        screen_manager = self.root.ids['screen_manager1']
        current_screen = screen_manager.current
        if self.lastscreens:
            if current_screen != self.lastscreens[-1]:
                self.lastscreens.append(current_screen)
        else:
            self.lastscreens.append(current_screen)

        if args:
            for item in args:
                if item == -1:
                    self.lastscreens.pop(-1)
                if item == -2:  # optional no transition
                    screen_manager.transition = NoTransition()
                if isinstance(item, str):  # optional transition direction
                    screen_manager.transition.direction = item

        else:
            screen_manager.transition.direction = "left"
            # if args[1]:  # optional no transition
            #     screen_manager.transition = NoTransition()

        if screen_name == "homescreen":
            self.root.ids['toolbar'].left_action_items = [["settings", lambda x: self.change_screen1("settingsscreen")]]
            self.lastscreens = []
        else:
            self.root.ids['toolbar'].left_action_items = [["chevron-left", lambda x: self.back_to_last_screen()]]

        screen_manager.current = screen_name

        if -3 in args:  # recovering transition
            screen_manager.transition = SlideTransition()

        if self.debug:
            print(self.lastscreens)
            print("currscreen = ", screen_name)

    # test username methods
    #######################
    def get_user_name_data_success(self, req, result):
        pass
        # print("FUQ YEA", result)

    def on_request_error(self, *args):
        print('failed')

    def get_user_name_data(self, user_name):
        # Query database and make sure friend_id exists
        user_name = '"' + user_name + '"'
        link = 'https://gymbuddy2.firebaseio.com/.json?orderBy="user_name"&equalTo=' + user_name
        check_req = requests.get(link)
        req = UrlRequest(link, on_success=self.get_user_name_data_success, on_error=self.on_request_error,
                         on_failure=self.on_request_error,
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
