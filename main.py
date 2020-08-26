import ast
import os
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
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog

from FirebaseLoginScreen.firebaseloginscreen import FirebaseLoginScreen
import kivy.utils as utils
import requests
import json
from kivy.clock import Clock
import time


### screens classes import

from screens_py.create_workout_screen import Create_Workout_Screen, SplitScreensMain, SplitScreen, SplitScreen2, \
    SplitScreen3
from screens_py.homescreen import HomeScreen
from screens_py.settingsscreen import SettingsScreen
from screens_py.workoutsscreen import WorkoutsScreen
from screens_py.workoutscreen import WorkoutScreen
from screens_py.exercise_sessions_screen import ExerciseSessionsScreen
from kivy.factory import Factory
from screens_py.sessionscreen import SessionScreen, ExerciseScreen
from customKv.tab import MDTabs, MDTabsBase
import copy

Window.size = (320, 650)


## msg for new workout name
class AddWorkoutContent(BoxLayout):
    pass


class BlankScreen(Screen):

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
    debug = 1
    running_session = 0  # indicator for running session - shows a button that helps the user return to the session
    timer = NumericProperty()  # timer that increment in seconds
    timer_format = ""  # for storing seconds in %H:%M:%S format
    split_Choice_dict = {}  # workout key with split choice
    workout_key_to_view = '-MF5efE9OJk4fKyB9LpK'
    folder = os.path.dirname(os.path.realpath(__file__))
    popup = Factory.LoadingPopup()
    popup.background = folder + "/FirebaseLoginScreen/transparent_image.png"
    exc_sessions = {}

    def __init__(self, **kwargs):
        self.title = "FitnessApp"
        super().__init__(**kwargs)

    def on_start(self):
        # before login, denies access to navigation drawer
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Indigo"
        self.root.ids['nav_drawer'].swipe_edge_width = -2

    def change_title(self, text):
        self.root.ids['toolbar'].title = text

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
        self.change_title("Hello " + user_name)

        # self.get_user_name_data(user_name)
        ### debug:
        # if self.debug == 0:
        #     self.workout_key_to_view = '-MF5efE9OJk4fKyB9LpK'
        #     self.change_screen1("workoutscreen")

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

    # Handling user data'
    def show_exc_history(self , exc_name):
        self.root.ids['exercise_sessions_screen'].exercise = exc_name
        self.change_screen1("exercise_sessions_screen")

    def get_user_data(self):
        try:
            result = requests.get("https://gymbuddy2.firebaseio.com/" + self.local_id + ".json?auth=" + self.id_token)
            data = json.loads(result.content.decode())
            self.user_data = data
            if self.debug:
                print(data)
                print("user email:",self.user_data["email"])
                print("user friends:",self.user_data["friends"])
                print("user real_user_name:",self.user_data["real_user_name"])
                print("user user_name:",self.user_data["user_name"])
                print("user sessions:",self.user_data["sessions"])
                print("user workouts:",self.user_data["workouts"])
                print("user streak:",self.user_data["streak"])

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
            self.add_session_to_excs_stats(exercises, date , workout_name)
            new_session = Workout_Session(session_key, date, duration, workout_key, workout_name, workout_split,
                                          exercises)
            self.sessions.append(new_session)

        self.sessions.sort(key=lambda r: r.date, reverse=True)
        if self.debug:
            print("sessions: ", self.sessions)
            print("exc_sessions: ", self.exc_sessions)

    def add_session_to_excs_stats(self, exercises , date , workout_name):
        # gets a session exc list, and add it to a dict: {exc_name:{ record:.. , date: [workout_name ,[session]]

        for exc in exercises:
            exercises_list = list(exercises.values())[0]

            if exc not in self.exc_sessions:
                self.exc_sessions[exc] = {date: [workout_name, exercises_list]}
                record = self.find_best_set(exercises_list)
                self.exc_sessions[exc]["record"] = record
            else:

                record = self.exc_sessions[exc]["record"]
                record_weight = record.split()
                record_weight = float(record_weight[2])
                maybe_record = self.find_best_set(exercises_list)
                maybe_record_weight = maybe_record.split()
                maybe_record_weight = float(maybe_record_weight[2])

                if maybe_record_weight > record_weight:
                    self.exc_sessions[exc]["record"] = maybe_record
                self.exc_sessions[exc][date] = [workout_name, exercises_list]

    def find_best_set(self, exc_session):
        # by weight:
        best_weight = 0
        best_weight_ind = 0
        for i , set in enumerate(exc_session):
            set = set.split()
            weight = float(set[2])
            if weight > best_weight:
                best_weight = weight
                best_weight_ind = i
        return exc_session[best_weight_ind]

    # Initial workouts dicts, and workouts screen
    def load_workout_data(self):
        # try:
        workoutdic = self.user_data["workouts"]  # gets workout data
        keysToAdd = []
        self.workouts = {}  # solve case of deleted workout. reloads all database workouts
        for workoutkey in workoutdic:
            workout = workoutdic[workoutkey]
            if self.debug:
                print("workout:", workout)
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

    def create_new_workout(self, *args):
        new_workout = args[0].parent.parent.parent.children[2].children[0].children[0].text
        # If the user hasnt written any name, dont do nothing.
        if new_workout:
            self.dialog.dismiss()
            self.root.ids['workoutscreen'].workout = []
            self.root.ids['workoutscreen'].temp_workout = []
            self.root.ids['workoutscreen'].workout_name = new_workout
            self.root.ids['workoutscreen'].create_mode = 1
            self.root.ids['workoutscreen'].num_of_splits = 1
            self.change_screen1("workoutscreen")

    def show_create_workout_dialog(self):
        self.dialog = MDDialog(
            radius=[10, 7, 10, 7],
            size_hint=(0.9, 0.2),
            title="Enter workout name:",
            type="custom",
            content_cls=AddWorkoutContent(),
            buttons=[

                MDFlatButton(
                    text="OK",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.create_new_workout
                ),
                MDFlatButton(
                    text="Cancel",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.dismiss_dialog
                )
            ],
        )
        self.dialog.open()

    def dismiss_dialog(self, *args):
        self.dialog.dismiss()

    # def add_workouts(self, workoutDic):
    #     self.delete_workout_grid()
    #     workoutgrid = self.root.ids['workoutsscreen'].ids[
    #         'banner_grid']  # getting the id of where the widgets are coming in
    #     for workoutkey in workoutDic:
    #         workoutdic = workoutDic[workoutkey]  # argument 0 its the workout key, and 1 is the dict
    #         for workoutname in workoutdic:
    #             exercises = workoutdic[workoutname]  # getting the the exercises of the workout
    #
    #             newlayout = MDFloatLayout()  # for centering
    #
    #             workoutcard = MDCard(
    #                 radius=[14],
    #                 orientation="vertical",
    #                 size_hint=(0.9, 0.9),
    #                 padding="8dp",
    #                 pos_hint={"center_y": 0.5, "center_x": 0.5}
    #             )
    #             workoutcard.add_widget(MDLabel(
    #                 text=workoutname,
    #                 font_style="H4",
    #                 size_hint=(None, 0.1),
    #                 theme_text_color="Custom",
    #                 text_color=self.theme_cls.primary_color
    #             ))
    #             splits_tabs = MDTabs()
    #             splits_tabs.background_color = (1, 1, 1, 1)
    #             splits_tabs.text_color_normal = (0, 0, 0, 1)
    #             splits_tabs.text_color_active = (0, 0, 1, 1)
    #             splits_tabs.color_indicator = (0, 0, 1, 1)
    #             splits_tabs.on_tab_switch = self.on_split_switch
    #
    #             for numofsplit, split in enumerate(exercises):
    #                 splits = "Split " + str(numofsplit + 1)
    #                 tab = Tab(text=splits)
    #                 layout = MDBoxLayout(orientation='vertical')
    #                 view = ScrollView()
    #                 layout.add_widget(view)
    #                 lst = MDList()
    #                 for exc in split:
    #                     lst.add_widget(OneLineListItem(text=exc))
    #                 view.add_widget(lst)
    #                 tab.add_widget(layout)
    #                 splits_tabs.add_widget(tab)
    #             workoutcard.add_widget(splits_tabs)
    #
    #             startButton = MDIconButton(
    #                 icon="play",
    #                 pos_hint={'right': 0},
    #                 user_font_size="45sp",
    #                 theme_text_color="Custom",
    #                 text_color=self.theme_cls.primary_color,
    #                 on_release=self.start_workout
    #             )
    #             editButton = MDIconButton(
    #                 icon="file-edit",
    #                 user_font_size="40sp",
    #                 theme_text_color="Custom",
    #                 text_color=self.theme_cls.primary_color,
    #                 on_release=self.view_workout
    #             )
    #             deleteButton = MDIconButton(
    #                 icon="trash-can-outline",
    #                 pos_hint={'right': 0},
    #                 user_font_size="40sp",
    #                 theme_text_color="Custom",
    #                 text_color=self.theme_cls.primary_color,
    #                 on_release=self.delete_workout_msg
    #             )
    #             buttonlayout = MDBoxLayout(
    #                 adaptive_height=True,
    #                 orientation='horizontal',
    #                 spacing=20
    #             )
    #
    #             keybutton = MDRaisedButton(
    #                 opacity=0,
    #                 size_hint=(.01, .2 / 3),
    #                 text=workoutkey
    #             )
    #             self.split_Choice_dict[workoutkey] = 1
    #
    #             buttonlayout.add_widget(keybutton)
    #             buttonlayout.add_widget(startButton)
    #             buttonlayout.add_widget(editButton)
    #             buttonlayout.add_widget(deleteButton)
    #             workoutcard.add_widget(buttonlayout)
    #             newlayout.add_widget(workoutcard)
    #             workoutgrid.add_widget(newlayout)

    def add_workouts(self, workoutDic):
        self.delete_workout_grid()
        workoutgrid = self.root.ids['workoutsscreen'].ids[
            'banner_grid']  # getting the id of where the widgets are coming in
        for workoutkey in workoutDic:
            workoutdic = workoutDic[workoutkey]  # argument 0 its the workout key, and 1 is the dict
            for workoutname in workoutdic:
                exercises = workoutdic[workoutname]  # getting the the exercises of the workout

                newlayout = MDFloatLayout()  # for centering
                card_layout = MDFloatLayout()  # for centering

                workoutcard = MDCard(
                    radius=[14],
                    orientation="vertical",
                    size_hint=(0.9, 0.9),
                    padding="8dp",
                    pos_hint={"center_y": 0.5, "center_x": 0.5},
                    background = "resources/card_1.jpeg",
                    on_release=self.view_workout
                )
                # workoutcard.add_widget(MDLabel(
                #     text=workoutname,
                #     font_style="H4",
                #     size_hint=(None, 0.1),
                #     theme_text_color="Custom",
                #     text_color=self.theme_cls.primary_color
                # ))
                card_layout.add_widget(MDLabel(
                    text=workoutname,
                    font_style="H4",
                    pos_hint={"center_y": 0.195, "center_x": 0.5},
                    # theme_text_color="Custom",
                    # text_color=self.theme_cls.primary_color
                    text_color = (0, 0, 1, 1)
                ))

                card_layout.add_widget(MDLabel(
                    text="12/08/20",
                    font_style="Subtitle1",
                        pos_hint={"center_y": 0.07, "center_x": 0.5},
                    # theme_text_color="Custom",
                    # text_color=self.theme_cls.primary_color
                    text_color = (0, 0, 1, 1)
                ))
                # ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'Subtitle1', 'Subtitle2', 'Body1', 'Body2', 'Button',
                #  'Caption', 'Overline', 'Icon']
                card_layout.add_widget(MDLabel(
                    text="Times Completed:",
                    font_style="Subtitle1",
                    pos_hint={"center_y": 0.07, "x": 0.45},
                    # theme_text_="Custom",
                    # text_color=selfcolor.theme_cls.primary_color
                    text_color=(0, 0, 1, 1)
                ))
                card_layout.add_widget(MDLabel(
                    text="7",
                    font_style="Subtitle1",
                    pos_hint={"center_y": 0.07, "x": 0.95},
                    # theme_text_color="Custom",
                    # text_color=self.theme_cls.primary_color
                    text_color = (0, 0, 1, 1)
                ))
                keybutton = MDRaisedButton(
                    opacity=0,
                    size_hint=(.01, .2 / 3),
                    text=workoutkey
                )
                self.split_Choice_dict[workoutkey] = 1

                card_layout.add_widget(keybutton)
                workoutcard.add_widget(card_layout)
                newlayout.add_widget(workoutcard)
                workoutgrid.add_widget(newlayout)

    def on_split_switch(self, *args):
        split_chosen = args[2]
        split_chosen = int(split_chosen[6])
        tab = args[1]
        workout_key = tab.parent.parent.parent.parent.parent.children[0].children[3].text
        self.split_Choice_dict[workout_key] = split_chosen
        print("here", self.split_Choice_dict)

    # Methods for when User want to start a new workout session:
    def view_workout(self, *args):
        workout_key = args[0].children[0].children[0].text
        self.workout_key_to_view = workout_key
        self.change_screen1("workoutscreen")

    def start_workout(self, *args):
        # start new session of workout

        # workoutkey = args[0].parent.children[3].text
        workoutkey = args[0]

        # workout_split = self.split_Choice_dict[workoutkey]
        workout_split = args[1]
        workout_list = list(self.workoutsParsed[workoutkey].values())
        workout_name = list(self.workoutsParsed[workoutkey].keys())[0]
        num_splits = len(workout_list[0])
        chosen_workout = workout_list[0]  # List of exercise to train

        # getting the id of where the widgets are coming in, and clear exercise list
        session_grid = self.root.ids['sessionscreen'].ids[
            'exc_cards']
        session_grid.clear_widgets()

        SessionScreen.new_workout = 1  # Sets the enitre workout
        SessionScreen.workout_splits = chosen_workout  # Sets the enitre workout
        SessionScreen.workout = copy.deepcopy(chosen_workout[workout_split - 1]) # Sets the exercise list
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
        self.start_session_timer()

        self.change_screen1("sessionscreen")

    def start_session_timer(self):
        self.timer = 0
        Clock.schedule_interval(self.increment_time, .1)
        self.increment_time(0)
        self.start_timer()

    def delete_workout_msg(self, *args):
        self.workout_to_delete = args[0]  # saving the object we want to delete
        workoutkey = args[0]
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
        self.display_loading_screen()
        if self.workout_to_delete:
            workoutkey = self.workout_to_delete
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
        self.hide_loading_screen()
        self.change_screen1("workoutsscreen")
        Snackbar(text="Workout Deleted!").show()
        # self.load_workout_data()
        self.add_workouts(self.workoutsParsed)
        self.dialog.dismiss()
        self.workout_to_delete = 0

    def error_del_workout(self, *args):
        self.hide_loading_screen()
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
        if self.root.ids['workoutscreen'].edit_mode:
            self.root.ids['workoutscreen'].leave_in_middle_edit_workout()
        else:
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
                current_screen = self.root.ids['screen_manager1'].current
                last_screen = self.lastscreens.pop(-1)
                if last_screen == "blankscreen":
                    last_screen = self.lastscreens.pop(-1)
                    while self.lastscreens and self.lastscreens[-1] == current_screen:
                        last_screen = self.lastscreens.pop(-1)
                    last_screen = self.lastscreens.pop(-1)
                while self.lastscreens and last_screen == self.lastscreens[-1]:
                    last_screen = self.lastscreens.pop(-1)
                # lastscreen = self.root.ids['screen_manager1'].previous()
                # -1 is 'back' indicator for change screen method
                self.change_screen1(last_screen, -1, "right")
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
        # if screen_name == "workoutscreen":
        #     self.test_workout()
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
            self.root.ids['toolbar'].left_action_items = [
                ["cog-outline", lambda x: self.change_screen1("settingsscreen")]]
            self.lastscreens = []
        else:
            self.root.ids['toolbar'].left_action_items = [["chevron-left", lambda x: self.back_to_last_screen()]]

        # screen_manager.current = screen_name

        if -3 in args:  # recovering transition
            screen_manager.current = screen_name
            screen_manager.transition = SlideTransition()
        else:
            screen_manager.current = screen_name

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

    def upload_new_workout(self, workout_name, workout_exc):
        self.display_loading_screen()

        Workout = "{%s: %s}" % ('"' + workout_name + '"', '"' + str(workout_exc) + '"')
        workout_link = "https://gymbuddy2.firebaseio.com/%s/workouts.json?auth=%s" % (self.local_id, self.id_token)
        data = json.dumps(Workout)
        post_workout_req = UrlRequest(workout_link, req_body=data, on_success=self.success_upload_workout,
                                      on_error=self.error_upload_workout,
                                      on_failure=self.error_upload_workout,
                                      ca_file=certifi.where(), method='POST', verify=True)

    def success_upload_workout(self, *args):
        self.hide_loading_screen()

        self.change_screen1("homescreen")
        self.get_user_data()
        self.load_workout_data()
        Snackbar(text="Workout saved!").show()
        self.root.ids['toolbar'].right_action_items = [
            ['menu', lambda x: self.root.ids['nav_drawer'].set_state()]]

    def error_upload_workout(self, *args):
        self.hide_loading_screen()
        print(args)
        print("error uploading")

    def update_existing_workout(self, workout_key, workout_name, workout_exc):
        if self.debug:
            print("workout_key to update:", workout_key)
            print("workout_name to update:", workout_name)
            print("workout_exc to update:", workout_exc)
            print("real workout details:", self.workoutsParsed[workout_key])

        self.display_loading_screen()

        workout_link = "https://gymbuddy2.firebaseio.com/%s/workouts/%s.json?auth=%s" % (
            self.local_id, workout_key, self.id_token)
        print(workout_link)
        Workout = "{%s: %s}" % ('"' + workout_name + '"', '"' + str(workout_exc) + '"')
        data = json.dumps(Workout)
        post_workout_req = UrlRequest(workout_link, req_body=data, on_success=self.success_upload_workout,
                                      on_error=self.error_upload_workout,
                                      on_failure=self.error_upload_workout,
                                      ca_file=certifi.where(), method='PUT', verify=True)

    def display_loading_screen(self, *args):
        self.popup.open()

    def hide_loading_screen(self, *args):
        self.popup.dismiss()


MainApp().run()
