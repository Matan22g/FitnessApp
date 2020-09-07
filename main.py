import ast
import os
from datetime import datetime

import certifi
from kivy.network.urlrequest import UrlRequest
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, NoTransition, SlideTransition
from kivy.core.window import Window
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard
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


from screens_py.homescreen import HomeScreen
from screens_py.settingsscreen import SettingsScreen
from screens_py.workoutsscreen import WorkoutsScreen
from screens_py.workoutscreen import WorkoutScreen
from screens_py.exercise_sessions import ExerciseSessionsScreen
from screens_py.previous_workouts import PreviousWorkoutsScreen

from kivy.factory import Factory
from screens_py.sessionscreen import SessionScreen, ExerciseScreen
import copy

Window.size = (375,750)


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





class MainApp(MDApp):
    mainscreens = ["homescreen", "workoutscreen", "friendsscreen", "settingsscreen"]
    id_token = ""
    local_id = ""
    user_data = []  # on login loads all user data
    workouts = {}  # straight from database
    workoutsParsed = {}  # analyze to list  'workout_key': {'name': "[['exc1'], ['exc2']]"} ----> '-workout_key': {'name': [['exc1'], ['exc2']]}
    sessions = {}  # dic of sessions obj by dates
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
    sessions_by_month_year = {}  # dict of session dates by month by year.
    sessions = {}  # dic of sessions obj by dates
    running_session_workout = []
    reload_for_running_session = ""
    delete_mode = 0  # help for knowing when checkbox are showed.

    def __init__(self, **kwargs):
        self.title = "FitnessApp"
        super().__init__(**kwargs)

    def on_start(self):
        # before login, denies access to navigation drawer
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Indigo"
        self.root.ids['nav_drawer'].swipe_edge_width = -2
        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def hook_keyboard(self, window, key, *largs):
        if key == 27:
            self.back_to_last_screen()
        return True

    def change_title(self, text):
        self.root.ids['toolbar'].title = text

    def on_stop(self):
        if self.running_session:
            self.upload_temp_session()
        else:
            self.clean_temp_session_data()

    def on_login(self):
        # loads data
        self.get_user_data()
        self.change_screen1("homescreen")
        self.load_workout_data()
        self.load_session_data()
        # Initial left menu obj to settings
        self.root.ids['toolbar'].left_action_items = [["cog", lambda x: self.change_screen1("settingsscreen")]]
        # TEST OF USER NAME
        user_name = self.user_data["real_user_name"]
        self.change_title("Hello " + user_name)

        if len(self.user_data["temp_session"]) > 4:  # not empty list {[]}
            self.retrieve_paused_session()
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
    def retrieve_paused_session(self):
        print('self.user_data["temp_session"]', self.user_data["temp_session"])
        print(type(self.user_data["temp_session"]))
        session = ast.literal_eval(self.user_data["temp_session"][1:-1])
        print(type(session))
        print(session)
        self.show_resume_session_dialog(session)

    def show_resume_session_dialog(self, session):
        self.dialog = MDDialog(
            radius=[10, 7, 10, 7],
            size_hint=(0.9, 0.3),
            title="Do you wish to resume " + session[3],
            buttons=[

                MDFlatButton(
                    text="OK",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.resume_session
                ),
                MDFlatButton(
                    text="CANCEL",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.dismiss_dialog
                )
            ],
        )
        self.dialog.open()

    def resume_session(self, *args):
        session = ast.literal_eval(self.user_data["temp_session"][1:-1])
        print(type(session))
        print(session)
        print(type(session[4]), "session[4]")
        self.root.ids['sessionscreen'].ids["date_picker_label"].text = session[0]
        self.root.ids['sessionscreen'].session_date = session[0] + " 00:00:00"
        timer = session[1]
        self.root.ids['sessionscreen'].workout_key = session[2]
        self.root.ids['sessionscreen'].workout_name = session[3]
        self.root.ids['sessionscreen'].num_of_split = session[4]
        self.root.ids['sessionscreen'].session_rec = session[5]
        self.running_session = 1

        workout_list = list(self.workoutsParsed[session[2]].values())

        chosen_workout = workout_list[0]  # List of exercise to train

        self.root.ids['sessionscreen'].workout = copy.deepcopy(
            chosen_workout[session[4] - 1])  # Sets the exercise list
        self.running_session_workout = self.root.ids['sessionscreen'].workout

        if self.debug:
            print("trying to start old session")
            print("SessionScreen.workout", SessionScreen.workout)
            print("SessionScreen.workout_key", SessionScreen.workout_key)
            print("SessionScreen.num_of_split", SessionScreen.num_of_split)

        self.new_session = 0
        self.running_session = 1
        self.root.ids['sessionscreen'].view_mode = 0

        self.root.ids['workoutsscreen'].ids["running_session"].text = session[3]

        # Start workout timer.
        self.start_session_timer(timer)
        self.dialog.dismiss()
        self.change_screen1("sessionscreen")

    def show_exc_history(self, exc_name):
        self.root.ids['exercise_sessions_screen'].exercise = exc_name
        self.change_screen1("exercise_sessions_screen")

    def get_user_data(self):
        try:
            result = requests.get("https://gymbuddy2.firebaseio.com/" + self.local_id + ".json?auth=" + self.id_token)
            data = json.loads(result.content.decode())
            self.user_data = data
            if self.debug:
                print(data)
                print("user email:", self.user_data["email"])
                print("user friends:", self.user_data["friends"])
                print("user real_user_name:", self.user_data["real_user_name"])
                print("user user_name:", self.user_data["user_name"])
                print("user sessions:", self.user_data["sessions"])
                print("user workouts:", self.user_data["workouts"])
                print("user streak:", self.user_data["streak"])

        except Exception:
            print("no data")

    def load_session_data(self):
        # Creates a sessions obj list sorted by dates
        try:
            session_dic = self.user_data["sessions"]
        except KeyError:
            session_dic = {}

        if self.debug:
            print("session dic: ", session_dic)
        temp_session_list = []
        for session_key in session_dic:
            session = ast.literal_eval(session_dic[session_key][1:-1])  # turning the str to list
            date = datetime.strptime(session[0], "%d/%m/%Y %H:%M:%S")
            duration = session[1]
            workout_key = session[2]
            workout_name = session[3]
            workout_split = session[4]
            exercises = session[5]
            self.add_session_to_excs_stats(exercises, date, workout_name)
            new_session = Workout_Session(session_key, date, duration, workout_key, workout_name, workout_split,
                                          exercises)
            self.sessions[date] = new_session
        self.sort_workouts_sessions()

        if self.debug:
            print("sessions: ", self.sessions)

    def sort_workouts_sessions(self):
        session_dates = [session_date for session_date in self.sessions]
        print(session_dates)
        session_dates.sort(reverse=True)
        print(session_dates)
        self.sessions_by_month_year = {}
        for date in session_dates:
            year = int(date.year)
            month = int(date.month)
            if year not in self.sessions_by_month_year:
                self.sessions_by_month_year[year] = {}

            if month not in self.sessions_by_month_year[year]:
                self.sessions_by_month_year[year][month] = [date]
            else:
                self.sessions_by_month_year[year][month].append(date)

        if self.debug:
            print("sessions_by_month_year: ", self.sessions_by_month_year)

    def add_session_to_excs_stats(self, exercises, date, workout_name):
        # gets a session exc list, and add it to a dict: {exc_name:{ record:.. , date: [workout_name ,[session]]
        for exc in exercises:
            exercises_list = exercises[exc]
            print(exc)
            if exc not in self.exc_sessions:
                self.exc_sessions[exc] = {date: [workout_name, exercises_list], "record": ["", 0]}
                record = self.find_best_set(exercises_list)
                self.exc_sessions[exc]["record"][0] = record
                self.exc_sessions[exc]["record"][1] = date

            else:

                record = self.exc_sessions[exc]["record"][0]
                record_weight = record.split()
                record_weight = float(record_weight[2])
                maybe_record = self.find_best_set(exercises_list)
                maybe_record_weight = maybe_record.split()
                maybe_record_weight = float(maybe_record_weight[2])

                if maybe_record_weight > record_weight:
                    self.exc_sessions[exc]["record"][0] = maybe_record
                    self.exc_sessions[exc]["record"][1] = date

                self.exc_sessions[exc][date] = [workout_name, exercises_list]

    def del_session_from_exc_dict(self, date, exc_list):
        if self.debug:
            print("trying to del", date)
            print("session_exc_list", exc_list)
            print("self.exc_sessions", self.exc_sessions)

        for exc in exc_list:
            self.exc_sessions[exc].pop(date)
            if "record" in self.exc_sessions[exc]:
                record_date = self.exc_sessions[exc]["record"][1]
                if record_date == date:
                    self.exc_sessions[exc]["record"][1] = 0
                    self.exc_sessions[exc]["record"][0] = ""
                if len(self.exc_sessions[exc]) > 1:
                    self.exc_sessions[exc]["record"][0],self.exc_sessions[exc]["record"][1] = self.find_new_record(exc)


            if len(self.exc_sessions[exc]) == 1:
                self.exc_sessions.pop(exc)
        if self.debug:
            print("self.exc_sessions", self.exc_sessions)

    def find_new_record(self, exc):
        # in case of deleteing sessions with record, finding a new record
        # self.exc_sessions[exc] = {date: [workout_name, exercises_list], "record": ["", 0]}
        record = ""
        record_weight = 0
        maybe_record =""
        maybe_record_weight=0
        record_date = ""
        for date in self.exc_sessions[exc]:
            if date != "record":

                session_list = self.exc_sessions[exc][date][1]

                maybe_record = self.find_best_set(session_list)
                maybe_record_weight = maybe_record.split()
                maybe_record_weight = float(maybe_record_weight[2])

                if maybe_record_weight > record_weight:
                    record_weight = maybe_record_weight
                    record = maybe_record
                    record_date = date
        return record, record_date


    def find_best_set(self, exc_session):
        # by weight:
        best_weight = 0
        best_weight_ind = 0
        for i, set in enumerate(exc_session):
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
        # If the user hasnt written any name, do nothing.
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
            size_hint=(0.9, 0.3),
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
                    text="CANCEL",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.dismiss_dialog
                )
            ],
        )
        self.dialog.open()

    def dismiss_dialog(self, *args):
        self.dialog.dismiss()

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
                    background="resources/card_1.jpeg",
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
                    text_color=(0, 0, 1, 1)
                ))

                card_layout.add_widget(MDLabel(
                    text="12/08/20",
                    font_style="Subtitle1",
                    pos_hint={"center_y": 0.07, "center_x": 0.5},
                    # theme_text_color="Custom",
                    # text_color=self.theme_cls.primary_color
                    text_color=(0, 0, 1, 1)
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
                    text_color=(0, 0, 1, 1)
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

        # self.root.ids['sessionscreen'].new_workout = 1  # Sets the enitre workout
        self.root.ids['sessionscreen'].workout = copy.deepcopy(
            chosen_workout[workout_split - 1])  # Sets the exercise list
        self.root.ids['sessionscreen'].workout_key = workoutkey  # Sets the workout key list
        self.root.ids['sessionscreen'].num_of_split = workout_split  # Sets which split was chosen
        self.running_session_workout = copy.deepcopy(chosen_workout[workout_split - 1])

        if self.debug:
            print("trying to start new session")
            print("SessionScreen.workout", SessionScreen.workout)
            print("SessionScreen.workout_key", SessionScreen.workout_key)
            print("SessionScreen.num_of_split", SessionScreen.num_of_split)

        # Reset all dicts from previous workouts
        SessionScreen.ex_reference_by_id = {}
        SessionScreen.ex_reference_by_exc = {}
        SessionScreen.session_rec = {}
        SessionScreen.ex_reference_by_checkBox = {}

        SessionScreen.workout_name = workout_name
        self.new_session = 1
        self.running_session = 1
        self.root.ids['sessionscreen'].view_mode = 0

        self.root.ids['workoutsscreen'].ids["running_session"].text = workout_name

        # Start workout timer.
        self.start_session_timer()

        self.change_screen1("sessionscreen")


    def view_session(self, session_key):
        session_grid = self.root.ids['sessionscreen'].ids[
            'exc_cards']
        session_grid.clear_widgets()

        SessionScreen.session_key = session_key
        self.root.ids['sessionscreen'].view_mode = 1

        self.change_screen1("sessionscreen")

    def back_to_running_session(self):
        self.root.ids['sessionscreen'].view_mode = 0
        self.root.ids['sessionscreen'].workout = self.running_session_workout
        self.change_screen1("sessionscreen")



    def delete_workout_msg(self, *args):
        self.workout_to_delete = args[0]  # saving the object we want to delete
        workoutkey = args[0]
        workout_name = list(self.workoutsParsed[workoutkey].keys())[0]

        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
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

    def del_session(self, session_date_key):
        # self.display_loading_screen()
        session = self.sessions.pop(session_date_key)
        print("session_date_key", session_date_key)
        session_link = "https://gymbuddy2.firebaseio.com/%s/sessions/%s.json?auth=%s" % (
            self.local_id, session.session_key, self.id_token)
        del_req = UrlRequest(session_link, on_success=self.success_del_session, on_error=self.error_del_session,
                             on_failure=self.error_del_session,
                             ca_file=certifi.where(), method='DELETE', verify=True)

        sessions_list_ref = self.sessions_by_month_year[session_date_key.year][session_date_key.month]
        ind_to_pop = sessions_list_ref.index(session_date_key)
        sessions_list_ref.pop(ind_to_pop)
        self.del_session_from_exc_dict(session_date_key, session.exercises)
        ########################### delete data from exc_sessions!!!

    def success_del_session(self, req, result):
        pass
        # self.hide_loading_screen()
        # self.root.ids['previous_workouts_screen'].on_pre_enter()
        # Snackbar(text="Session Deleted!").show()
        # self.load_workout_data()

    def error_del_session(self, *args):
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
    def start_session_timer(self, *args):
        self.timer = time.time()

        if args:
            # in case of old session, restatring timer:
            timer = args[0]
            self.timer -= timer

        Clock.schedule_interval(self.increment_time, .1)
        self.increment_time(0)
        self.start_timer()

    def increment_time(self, interval):
        timer = time.time()-self.timer
        self.timer_format = str(time.strftime('%H:%M:%S', time.gmtime(round(timer))))
        self.root.ids['sessionscreen'].ids["timer"].text = self.timer_format

    def start_timer(self):
        Clock.unschedule(self.increment_time)
        Clock.schedule_interval(self.increment_time, .1)

        # To stop the count / time

    def stop_timer(self):
        Clock.unschedule(self.increment_time)

    # Back button
    def back_to_last_screen(self, *args):
        print("back func")
        print("current_screen", self.root.ids['screen_manager1'].current)
        print("self.lastscreens", self.lastscreens)

        if self.root.ids['screen_manager1'].current == "homescreen":
            return
        if self.root.ids['workoutscreen'].edit_mode:
            self.root.ids['workoutscreen'].leave_in_middle_edit_workout()
        else:
            current_screen = self.root.ids['screen_manager1'].current

            # exiting loading previous session
            if current_screen == "previous_workouts_screen":
                if self.reload_for_running_session:
                    self.reload_for_running_session = ""
                if self.root.ids['previous_workouts_screen'].delete_mode:
                    self.root.ids['previous_workouts_screen'].show_checkbox(False)
                    return

            if current_screen == "sessionscreen":
                if self.delete_mode:
                    self.root.ids['sessionscreen'].show_checkbox(False)
                    return

            if self.lastscreens:
                last_screen = self.lastscreens.pop(-1)
                if last_screen == "blankscreen":
                    last_screen = self.lastscreens.pop(-1)
                    while self.lastscreens and self.lastscreens[-1] == current_screen:
                        last_screen = self.lastscreens.pop(-1)
                    last_screen = self.lastscreens.pop(-1)
                while self.lastscreens and last_screen == self.lastscreens[-1] or last_screen == current_screen:
                    last_screen = self.lastscreens.pop(-1)

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
        # Get the screen manager from the kv file
        # args is an optional input of which direction the change will occur

        screen_manager = self.root.ids['screen_manager1']
        current_screen = screen_manager.current
        if self.debug:
            print("Before change screen, curr screen: ", current_screen)
            print("trying to switch to: ", screen_name)

        if self.lastscreens:
            self.lastscreens.append(current_screen)
        else:
            self.lastscreens.append(current_screen)

        if args:
            for item in args:
                if item == -1:
                    last_screen = self.lastscreens.pop(-1)
                    while self.lastscreens and self.lastscreens[-1] == last_screen:
                        last_screen = self.lastscreens.pop(-1)
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
                ["cog", lambda x: self.change_screen1("settingsscreen")]]
            self.lastscreens = []
        else:
            self.root.ids['toolbar'].left_action_items = [["chevron-left", lambda x: self.back_to_last_screen()]]

        # screen_manager.current = screen_name
        if screen_name != "sessionscreen":
            self.root.ids['toolbar'].right_action_items = [
                ['menu', lambda x: self.root.ids['nav_drawer'].set_state()]]

        if -3 in args:  # recovering transition
            screen_manager.current = screen_name
            screen_manager.transition = SlideTransition()
        else:
            screen_manager.current = screen_name

        if self.debug:
            print("self.lastscreens", self.lastscreens, )
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

        self.change_screen1("workoutsscreen")
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

    def proper_input_filter(self, input_to_check, indicator):
        if self.debug:
            print("input_to_check", input_to_check)
            print("indicator", indicator)
        if input_to_check.isalpha() or input_to_check.isdigit() or input_to_check == ' ':
            return input_to_check
        else:
            return ""

    def upload_temp_session(self, *args):
        date = self.root.ids['sessionscreen'].ids["date_picker_label"].text
        session_rec = self.root.ids['sessionscreen'].session_rec
        for exc in list(session_rec):
            if not session_rec[exc]:  # if exc is empty (after deletion)
                session_rec.pop(exc, None)
        link = "https://gymbuddy2.firebaseio.com/%s/temp_session.json?auth=%s" % (self.local_id, self.id_token)
        session_data = [date, time.time() - self.timer, self.root.ids['sessionscreen'].workout_key,
                        self.root.ids['sessionscreen'].workout_name, self.root.ids['sessionscreen'].num_of_split,
                        session_rec]
        session = "{%s}" % (str(session_data))
        data = json.dumps(session)
        # req = UrlRequest(link, req_body=data, on_success=self.on_upload_temp_session_success, on_error=self.on_upload_temp_session_error,
        #                  on_failure=self.on_upload_temp_session_error, method='POST',ca_file=certifi.where(), verify=True)
        requests.put(link, data=data)

    def clean_temp_session_data(self, *args):
        session = "{%s}" % (str([]))
        data = json.dumps(session)
        link = "https://gymbuddy2.firebaseio.com/%s/temp_session.json?auth=%s" % (self.local_id, self.id_token)
        requests.put(link, data=data)


MainApp().run()
