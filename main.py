import ast
import calendar
import os
from datetime import datetime, date

import certifi
from kivy.graphics.vertex_instructions import Rectangle, RoundedRectangle
from kivy.network.urlrequest import UrlRequest
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, NoTransition, SlideTransition
from kivy.core.window import Window
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineListItem, OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from customKv.toolbar import CustomMDToolbar
from kivymd.uix.card import MDCard, MDSeparator

# from customKv.card import MDCard

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

from screens_py.exercise_stats_screen import ExerciseStatsScreen

from kivy.factory import Factory
from screens_py.sessionscreen import SessionScreen, ExerciseScreen
import copy
import math

from kivy.utils import platform

if platform != 'android':
    Window.size = (330, 650)


## msg for new workout name
class AddWorkoutContent(BoxLayout):
    pass


class Change_User_Name_Content(BoxLayout):
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
    debug = 0
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
    upload_backup = 0  # help for backing up, uploading attempts - format: [data, link, target, workout_key]
    sign_up = 0
    window_size = Window.size
    headline_text_size = int(math.sqrt(Window.size[0] * Window.size[0] + Window.size[1] * Window.size[
        1]) / 32)  # text_size adapted to window size - used for tabs title, and info title
    last_session_date = 0
    text_color = (1, 1, 1, 1)
    workout_edit_mode = 0
    exc_pie_dic = {"None": 100}
    total_exc_sets = 0
    monthly_session_amount = 0
    weekly_session_amount = 0
    workouts_trained_amount = {}
    today_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    units = "Imperial"  # kg to lbs 1 to 2.20462262
    kg_to_pounds = 2.20462262
    user_name = ''

    def __init__(self, **kwargs):
        self.title = "FitnessApp"
        super().__init__(**kwargs)

    # refresh Auth token if expired:
    def refresh_auth_token(self):
        self.root.ids.firebase_login_screen.load_saved_account()

    # update exercise pie chart stats on homescreen.
    def update_chart(self):
        piechart = self.root.ids['homescreen'].ids[
            'piechart']  # getting the id of where the widgets are coming in

        items = [self.calc_exc_pie()]
        print(items)

        self.root.ids['homescreen'].ids[
            'piechart']._clear_canvas()

        self.root.ids['homescreen'].ids[
            'piechart']._make_chart(items)

        self.root.ids['homescreen'].ids[
            'piechart'].items = items
        print(self.root.ids['homescreen'].ids[
                  'piechart'].items)

    # bind back button of android to back function.
    def hook_keyboard(self, window, key, *largs):

        if key == 27:
            try:
                if self.root.ids['screen_manager1'].current == "homescreen":
                    self.stop()
                    return True
            except:
                pass
            self.back_to_last_screen()
        return True

    # App Main Functions
    def on_start(self):
        self.root.ids.firebase_login_screen.ids.login_screen.ids.backdrop.open()  # start login screen with closed backdrop
        # before login, denies access to navigation drawer
        self.root.ids['nav_drawer'].swipe_edge_width = -2
        print(self.headline_text_size)
        # bind android back button to back function
        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def on_stop(self):
        if self.running_session:
            self.upload_temp_session()
        else:
            self.clean_temp_session_data()

    def on_login(self):
        # loads data
        self.add_top_canvas()

        if not self.sign_up:
            self.get_user_data()
            self.change_screen1("homescreen")
            try:
                self.load_session_data()
                self.update_chart()

            except:
                self.sessions = {}
            self.load_workout_data()
            self.load_settings_data()
        else:
            self.clear_user_app_data()
            self.update_dashboard_stats()
            self.update_last_date_card(0)
        # Initial left menu obj to settings
        # self.root.ids['toolbar'].left_action_items = [["cog", lambda x: self.change_screen1("settingsscreen")]]
        self.root.ids['toolbar'].left_action_items = [['', lambda x: None]]

        # TEST OF USER NAME
        try:
            self.user_name = self.user_data["real_user_name"]
        except:
            print("cant load username")
        # self.change_title("Hello " + user_name)
        self.change_title("Dashboard")
        try:
            if len(self.user_data["temp_session"]) > 4:  # not empty list {[]}
                self.retrieve_paused_session()
        except:
            print("key error: temp_session")
        self.change_screen1("exercisescreen")

        ## for home screen first load
        if self.units == "metric":
            self.root.ids['homescreen'].ids["weight_units"].text = "Kg"
        else:
            self.root.ids['homescreen'].ids["weight_units"].text = "Lbs"

    def load_settings_data(self):
        settings_dict = self.user_data['settings']
        if "units" in settings_dict:
            units = settings_dict["units"]
            self.units = units
            # if units == 'metric':
            #     self.root.ids['settingsscreen'].ids.metric.active = True
            # else:
            #     self.root.ids['settingsscreen'].ids.imperial.active = True

    def on_logout(self):
        self.clear_user_app_data()
        self.root.ids['nav_drawer'].swipe_edge_width = -2
        self.root.ids['nav_drawer'].set_state()

        self.root.ids.firebase_login_screen.login_success = False
        self.root.ids.firebase_login_screen.save_refresh_token("")

        Snackbar(text="Logged out!").show()
        self.change_screen("loginscreen", 'right')
        self.root.ids['nav_drawer'].swipe_edge_width = -2

    def clear_user_app_data(self):
        self.workouts = {}
        self.workoutsParsed = {}
        self.sessions = {}
        self.sessions_by_key = {}
        self.friends_list = {}
        self.dialog = 0
        self.workout_to_delete = 0
        self.new_session = 0
        self.running_session = 0
        self.toTrainWorkout = {}
        self.workout_key_to_view = 0
        self.exc_sessions = {}
        self.sessions_by_month_year = {}
        self.sessions = {}
        self.running_session_workout = []
        self.reload_for_running_session = ""
        self.delete_mode = 0
        self.upload_backup = 0
        self.last_session_date = 0
        self.sign_up = 0
        self.workout_edit_mode = 0
        self.exc_pie_dic = {"None": 100}
        self.total_exc_sets = 0
        self.delete_workout_grid()
        self.update_chart()
        self.update_last_date_card(0)
        self.monthly_session_amount = 0
        self.weekly_session_amount = 0
        self.workouts_trained_amount = {}

    def change_title(self, text):
        self.root.ids['toolbar'].title = text

    # top and bottom background for the app methods
    def add_top_canvas(self):
        with self.root.ids.main_layout.canvas.before:
            Rectangle(source='resources/loginback1.png', pos=(0, self.window_size[1] / 1.23), size=(
                self.root.ids.main_layout.parent.parent.size[0], self.root.ids.main_layout.parent.parent.size[1] / 5))

    def clear_canvas(self):
        self.root.ids.main_layout.canvas.before.clear()

    def add_bottom_canvas(self):
        with self.root.ids.main_layout.canvas.before:
            Rectangle(source='resources/loginback1.png', pos=(0, 0), size=(
                self.root.ids.main_layout.parent.parent.size[0], self.root.ids.main_layout.parent.parent.size[1] / 8))

    #

    # Handling user data

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

    def calc_exc_pie(self):
        temp_tot = 0
        items = {}
        if self.debug:
            print("self.exc_pie_dic", self.exc_pie_dic)
        if not self.exc_pie_dic:
            self.exc_pie_dic = {"None": 100}
            items = {"None": 100}
        for exc in self.exc_pie_dic:
            if exc == "None":
                items = {"None": 100}
                return items
            new_per = int(round((self.exc_pie_dic[exc] / self.total_exc_sets) * 100))
            if new_per:
                items[exc] = new_per
                temp_tot += new_per
        if temp_tot < 100:
            to_add = 100 - temp_tot
            items[exc] += to_add
        elif temp_tot > 100:
            to_sub = 100 - temp_tot
            if items[exc] + to_sub > 0:
                items[exc] += to_sub
            else:
                for exc in items:
                    if items[exc] + to_sub > 0:
                        items[exc] += to_sub
                        break
        return items
        print("self.exc_pie_dic", self.exc_pie_dic)

    # Find for Exercise the best Set for all sessions

    def find_new_record(self, exc):
        # in case of deleteing sessions with record, finding a new record
        # self.exc_sessions[exc] = {date: [workout_name, exercises_list], "record": ["", 0]}
        record = ""
        record_weight = 0
        maybe_record = ""
        maybe_record_weight = 0
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

    # Returns the index of the best set in a given Session
    def find_best_set(self, exc_session):
        # by weight:
        best_weight = 0
        best_weight_ind = 0
        for i, set in enumerate(exc_session):
            if not set:
                continue
            set = set.split()
            weight = float(set[2])
            maybe_best_reps = int(set[0])
            if weight > best_weight:
                best_weight = weight
                best_weight_ind = i
            elif weight == best_weight:
                if maybe_best_reps > int(exc_session[best_weight_ind].split()[0]):
                    best_weight = weight
                    best_weight_ind = i

        return exc_session[best_weight_ind]


    # Initial workouts dicts, and workouts screen
    def load_workout_data(self):
        try:
            workoutdic = self.user_data["workouts"]  # gets workout data
        except:
            # fix case of empty workouts in database
            workoutdic = {}
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
        print(workoutIdDic)
        # json data to iterable list, return dict of workout dicts {key: {workout name :[[split 1],[split2]]}}
        workoutdicReadAble = {}
        for workoutkey in workoutIdDic:
            workoutTemp = {}

            workoutdic = workoutIdDic[workoutkey][0]
            workout_date = workoutIdDic[workoutkey][1]
            workout_date = workout_date[:10]

            for workoutName in workoutdic:
                exercises = workoutdic[workoutName]  # getting the the exercises of the workout
                exercises = ast.literal_eval(exercises)  # turning the str to list
                workoutTemp[workoutName] = exercises
            workoutdicReadAble[workoutkey] = [workoutTemp, workout_date]
        return workoutdicReadAble

    def add_workouts(self, workoutDic):
        self.delete_workout_grid()
        workoutgrid = self.root.ids['workoutsscreen'].ids[
            'banner_grid']  # getting the id of where the widgets are coming in
        for workoutkey in workoutDic:
            workoutdic = workoutDic[workoutkey][0]  # argument 0 is the dict, and 1 is the date
            workout_date = workoutDic[workoutkey][1]  # argument 0 is the dict, and 1 is the date

            for workoutname in workoutdic:
                exercises = workoutdic[workoutname]  # getting the the exercises of the workout

                newlayout = MDFloatLayout()  # for centering
                card_layout = MDFloatLayout()  # for centering

                workoutcard = MDCard(
                    radius=[80],
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
                    text="Created: " + workout_date,
                    font_style="Subtitle1",
                    pos_hint={"center_y": 0.06, "center_x": 0.5},
                    # theme_text_color="Custom",
                    # text_color=self.theme_cls.primary_color
                    text_color=(0, 0, 1, 1)
                ))
                # ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'Subtitle1', 'Subtitle2', 'Body1', 'Body2', 'Button',
                #  'Caption', 'Overline', 'Icon']
                # card_layout.add_widget(MDLabel(
                #     text="Times Completed:",
                #     font_style="Subtitle1",
                #     pos_hint={"center_y": 0.07, "x": 0.45},
                #     # theme_text_="Custom",
                #     # text_color=selfcolor.theme_cls.primary_color
                #     text_color=(0, 0, 1, 1)
                # ))
                amount_trained = 0
                if workoutname in self.workouts_trained_amount:
                    amount_trained = self.workouts_trained_amount[workoutname]
                card_layout.add_widget(MDLabel(
                    text="Times trained: " + str(amount_trained),
                    font_style="Subtitle1",
                    pos_hint={"center_y": 0.06, "x": 0.65},
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

    # Session Methods:
    def load_session_data(self):
        # Creates a sessions obj list sorted by dates
        try:
            session_dic = self.user_data["sessions"]
        except KeyError:
            session_dic = {}

        if self.debug:
            print("session dic: ", session_dic)
        temp_session_list = []

        self.total_exc_sets = 0
        self.exc_pie_dic = {}

        self.monthly_session_amount = 0
        self.weekly_session_amount = 0
        self.workouts_trained_amount = {}

        today_date = datetime.today()
        curr_month = today_date.month
        curr_year = today_date.year
        curr_week = today_date.isocalendar()[1]

        for session_key in session_dic:
            session = ast.literal_eval(session_dic[session_key][1:-1])  # turning the str to list
            date = datetime.strptime(session[0], "%d/%m/%Y %H:%M:%S")

            if date.month == curr_month and date.year == curr_year:
                self.monthly_session_amount += 1
                if date.isocalendar()[1] == curr_week:
                    self.weekly_session_amount += 1

            duration = session[1]
            workout_key = session[2]
            workout_name = session[3]
            workout_split = session[4]
            exercises = session[5]
            self.add_session_to_excs_stats(exercises, date, workout_name)
            new_session = Workout_Session(session_key, date, duration, workout_key, workout_name, workout_split,
                                          exercises)
            self.sessions[date] = new_session

            if workout_name in self.workouts_trained_amount:
                self.workouts_trained_amount[workout_name] += 1
            else:
                self.workouts_trained_amount[workout_name] = 1

        self.sort_workouts_sessions()
        self.update_dashboard_stats()

        if self.debug:
            print("sessions: ", self.sessions)

    def sort_workouts_sessions(self):
        session_dates = [session_date for session_date in self.sessions]
        session_dates.sort(reverse=True)

        if session_dates:
            self.last_session_date = session_dates[0]
            self.update_last_date_card(session_dates[0])

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

    def update_last_date_card(self, session_date):

        last_session_month = ""
        last_session_day = ""
        last_session_name = "N/A"
        session_exc_completed = "Go Train"

        if session_date:
            self.last_session_date = session_date
            last_session = self.sessions[session_date]
            last_session_month = calendar.month_abbr[last_session.date.month]
            last_session_day = str(last_session.date.day)
            last_session_name = last_session.workout_name
            session_exc_completed = str(len(last_session.exercises)) + " exercises completed"

        self.root.ids['homescreen'].ids['last_session_month'].text = last_session_month
        self.root.ids['homescreen'].ids['last_session_day'].text = last_session_day
        self.root.ids['homescreen'].ids['last_session_name'].text = last_session_name
        self.root.ids['homescreen'].ids['session_exc_completed'].text = session_exc_completed

    def update_dashboard_stats(self):

        self.root.ids['homescreen'].ids['monthly_sessions'].text = str(self.monthly_session_amount)
        self.root.ids['homescreen'].ids['weekly_sessions'].text = str(self.weekly_session_amount)

    def view_session(self, session_key):
        if session_key:
            session_grid = self.root.ids['sessionscreen'].ids[
                'exc_cards']
            session_grid.clear_widgets()

            SessionScreen.session_key = session_key
            self.root.ids['sessionscreen'].view_mode = 1

            self.change_screen1("sessionscreen")

    def retrieve_paused_session(self):
        session = ast.literal_eval(self.user_data["temp_session"][1:-1])
        session_date = session[0]
        session_date = datetime.strptime(session_date, "%d/%m/%Y").date()
        today_date = date.today()
        if session_date == today_date:
            self.show_resume_session_dialog(session)
        else:
            self.clean_temp_session_data()

    def show_resume_session_dialog(self, session):
        self.dialog = MDDialog(
            radius=[10, 7, 10, 7],
            size_hint=(0.9, 0.2),
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
        self.root.ids['sessionscreen'].ids["date_picker_label"].text = session[0]
        self.root.ids['sessionscreen'].session_date = session[0] + " 00:00:00"
        timer = session[1]
        self.root.ids['sessionscreen'].workout_key = session[2]
        self.root.ids['sessionscreen'].workout_name = session[3]
        self.root.ids['sessionscreen'].num_of_split = session[4]
        self.root.ids['sessionscreen'].session_rec = session[5]
        self.running_session = 1

        workout_list = list(self.workoutsParsed[session[2]][0].values())

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

    def back_to_running_session(self):
        self.root.ids['sessionscreen'].view_mode = 0
        self.root.ids['sessionscreen'].workout = self.running_session_workout
        self.change_screen1("sessionscreen")

    def show_exc_history(self, exc_name):
        self.root.ids['exercise_sessions_screen'].exercise = exc_name
        self.change_screen1("exercise_sessions_screen")

    def add_session_to_excs_stats(self, exercises, date, workout_name):
        # gets a session exc list, and add it to a dict: {exc_name:{ record:.. , date: [workout_name ,[session]]
        for exc in exercises:
            exercises_list = exercises[exc]

            if self.is_in_past_month(date):
                if exc in self.exc_pie_dic:
                    self.exc_pie_dic[exc] += len(exercises_list)
                else:
                    self.exc_pie_dic[exc] = len(exercises_list)
                self.total_exc_sets += len(exercises_list)

            if exc not in self.exc_sessions:
                self.exc_sessions[exc] = {date: [workout_name, exercises_list], "record": ["", 0]}
                record = self.find_best_set(exercises_list)
                self.exc_sessions[exc]["record"][0] = record
                self.exc_sessions[exc]["record"][1] = date

            else:

                record = self.exc_sessions[exc]["record"][0]
                record_weight = record.split()
                record_list = record.split()
                record_weight = float(record_list[2])
                record_reps = int(record_list[0])

                maybe_record = self.find_best_set(exercises_list)
                maybe_record_list = maybe_record.split()
                maybe_record_weight = float(maybe_record_list[2])
                maybe_record_reps = float(maybe_record_list[0])

                if maybe_record_weight > record_weight:
                    self.exc_sessions[exc]["record"][0] = maybe_record
                    self.exc_sessions[exc]["record"][1] = date
                elif maybe_record_weight == record_weight:
                    if maybe_record_reps > record_reps:
                        self.exc_sessions[exc]["record"][0] = maybe_record
                        self.exc_sessions[exc]["record"][1] = date

                self.exc_sessions[exc][date] = [workout_name, exercises_list]

    def is_in_past_month(self, date):
        today = date.today()
        if (today - date).days <= 30:
            return True
        return False

    def del_session_from_exc_dict(self, date, exc_list):
        if self.debug:
            print("trying to del", date)
            print("session_exc_list", exc_list)
            print("self.exc_sessions", self.exc_sessions)

        for exc in exc_list:

            exc_session = self.exc_sessions[exc].pop(date)
            exc_session_len = len(exc_session[1])
            self.exc_pie_dic[exc] -= exc_session_len
            self.total_exc_sets -= exc_session_len
            if "record" in self.exc_sessions[exc]:
                record_date = self.exc_sessions[exc]["record"][1]
                if record_date == date:
                    self.exc_sessions[exc]["record"][1] = 0
                    self.exc_sessions[exc]["record"][0] = ""
                if len(self.exc_sessions[exc]) > 1:
                    self.exc_sessions[exc]["record"][0], self.exc_sessions[exc]["record"][1] = self.find_new_record(exc)

            if len(self.exc_sessions[exc]) == 1:
                self.exc_sessions.pop(exc)
        if self.debug:
            print("self.exc_sessions", self.exc_sessions)
        self.sort_workouts_sessions()

        today_date = datetime.today()
        curr_month = today_date.month
        curr_year = today_date.year
        curr_week = today_date.isocalendar()[1]

        if date.month == curr_month and date.year == curr_year:
            self.monthly_session_amount -= 1
            if date.isocalendar()[1] == curr_week:
                self.weekly_session_amount -= 1
            self.update_dashboard_stats()

    # Session deletion Methods
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

        workout_name = session.workout_name
        if workout_name in self.workouts_trained_amount:
            if self.workouts_trained_amount[workout_name] > 0:
                self.workouts_trained_amount[workout_name] -= 1
                self.add_workouts(self.workoutsParsed)

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

    ###

    # Timer methods.
    def start_session_timer(self, *args):
        self.timer = time.time()

        if args:
            # in case of old session, resetting timer to previous time:
            timer = args[0]
            self.timer = timer

        Clock.schedule_interval(self.increment_time, .1)
        self.increment_time(0)
        self.start_timer()

    def increment_time(self, interval):
        timer = time.time() - self.timer
        self.timer_format = str(time.strftime('%H:%M:%S', time.gmtime(round(timer))))
        self.root.ids['sessionscreen'].ids["timer"].text = self.timer_format

    def start_timer(self):
        Clock.unschedule(self.increment_time)
        Clock.schedule_interval(self.increment_time, .1)

        # To stop the count / time

    def stop_timer(self):
        Clock.unschedule(self.increment_time)

    # Workout Methods:
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

    def show_change_user_name_dialog(self):
        self.dialog = MDDialog(
            radius=[10, 7, 10, 7],
            size_hint=(0.9, 0.3),
            title="Enter new user name",
            type="custom",
            content_cls=Change_User_Name_Content(),
            buttons=[

                MDFlatButton(
                    text="OK",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.change_user_name_callback
                ),
                MDFlatButton(
                    text="CANCEL",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.dismiss_dialog
                )
            ],
        )
        self.dialog.open()

    def change_user_name_callback(self, *args):
        text_field = args[0].parent.parent.parent.children[2].children[0].children[1]
        error_label = args[0].parent.parent.parent.children[2].children[0].children[0]
        new_user_name = text_field.text
        if self.root.ids.firebase_login_screen.is_user_exist(new_user_name):
            error_label.text = new_user_name + " Already taken"
        else:
            self.dismiss_dialog()
            self.change_user_name(new_user_name)

    def start_workout(self, *args):
        # start new session of workout

        # workoutkey = args[0].parent.children[3].text
        workoutkey = args[0]

        # workout_split = self.split_Choice_dict[workoutkey]
        workout_split = args[1]
        workout_list = list(self.workoutsParsed[workoutkey][0].values())
        workout_name = list(self.workoutsParsed[workoutkey][0].keys())[0]
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

    def view_workout(self, *args):
        workout_key = args[0].children[0].children[0].text
        self.workout_key_to_view = workout_key
        self.change_screen1("workoutscreen")

    # Workout deletion Methods
    def delete_workout_msg(self, *args):
        self.workout_to_delete = args[0]  # saving the object we want to delete
        workoutkey = args[0]
        workout_name = list(self.workoutsParsed[workoutkey][0].keys())[0]

        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
                               title="Delete " + workout_name + "?",
                               text="Warning: Deleting " + workout_name + " cannot be undone\nYour workout history however wont be deleted",
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
        if screen_name != "sessionscreen" and screen_name != "workoutscreen":
            self.clear_canvas()
            self.add_top_canvas()

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
            # self.root.ids['toolbar'].left_action_items = [
            #     ["cog", lambda x: self.change_screen1("settingsscreen")]]
            self.root.ids['toolbar'].left_action_items = [['', lambda x: None]]

            self.lastscreens = []
        else:
            self.root.ids['toolbar'].left_action_items = [["chevron-left", lambda x: self.back_to_last_screen()]]

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

    def on_request_error(self, *args):
        print('failed')

    def get_user_name_data_success(self, req, result):
        pass

    def is_user_exist(self, user_name):
        user_name = '"' + user_name + '"'
        check_req = requests.get(
            'https://gymbuddy2.firebaseio.com/.json?orderBy="user_name"&equalTo=' + user_name)
        data = check_req.json()
        if data:
            return True
        else:
            return False

    def proper_input_filter(self, input_to_check, indicator):

        if self.debug:
            print("input_to_check", input_to_check)
            print("indicator", indicator)
        asci_val = ord(input_to_check)
        if asci_val > 64 and asci_val < 90:
            return input_to_check
        if asci_val > 96 and asci_val < 123:
            return input_to_check
        if asci_val > 47 and asci_val < 57:
            return input_to_check
        if input_to_check == ' ':
            return input_to_check

        else:
            return ""

    def proper_email_filter(self, input_to_check, indicator):

        if self.debug:
            print("input_to_check", input_to_check)
            print("indicator", indicator)
        asci_val = ord(input_to_check)
        if asci_val > 20 and asci_val < 177:
            return input_to_check
            return ""

    # Uploads all kind of Data Methods - Session / Workout
    def upload_data(self, *args):
        """  target can be: 1 - upload new workout ,
             2 - update an existing workout, 3 - upload new session, 4 - upload settings
        """
        data = args[0]
        link = args[1]
        target = args[2]
        try:
            workout_key = args[3]
        except:
            workout_key = 0

        if target != 4:
            self.display_loading_screen()

        self.upload_backup = [data, link, target, workout_key]

        if target == 1 or target == 3:
            method = 'POST'
        elif target == 2 or target == 4:
            method = 'PUT'

        post_workout_req = UrlRequest(link, req_body=data, on_success=self.success_upload,
                                      on_error=self.error_upload,
                                      on_failure=self.error_upload,
                                      ca_file=certifi.where(), method=method, verify=True)

    def success_upload(self, *args):
        if self.debug:
            print("upload successful, args:", args)

        req_data = args[1]
        if 'units' in req_data:
            pass
        elif req_data.lower() == self.user_name.lower():
            pass
        else:
            self.running_session = 0
            self.change_screen1("workoutsscreen")
            self.get_user_data()
            self.load_session_data()
            self.load_workout_data()
            self.root.ids['toolbar'].right_action_items = [
                ['menu', lambda x: self.root.ids['nav_drawer'].set_state()]]
            Snackbar(text="Workout saved!").show()
            self.upload_backup = 0
        self.hide_loading_screen()

    def error_upload(self, *args):
        self.refresh_auth_token()
        self.hide_loading_screen()
        Snackbar(text="Something went wrong!", padding="20dp", button_text="TRY AGAIN", button_color=(1, 0, 1, 1),
                 duration=15,
                 button_callback=self.on_upload_error).show()
        if self.debug:
            print(args)
            print("error session save")

    def on_upload_error(self, *args):
        self.refresh_auth_token()
        if self.upload_backup:
            upload_backup = self.upload_backup
            data = upload_backup[0]
            link = upload_backup[1]
            target = upload_backup[2]
            workout_key = upload_backup[3]
            if target == 1:
                link = "https://gymbuddy2.firebaseio.com/%s/workouts.json?auth=%s" % (self.local_id, self.id_token)
            if target == 2:
                link = "https://gymbuddy2.firebaseio.com/%s/workouts/%s.json?auth=%s" % (
                    self.local_id, workout_key, self.id_token)
            if target == 3:
                link = "https://gymbuddy2.firebaseio.com/%s/sessions.json?auth=%s" % (self.local_id, self.id_token)

            self.upload_data(data, link, target)

    # def upload_new_workout(self, data, link):
    #
    #     self.display_loading_screen()
    #     self.upload_backup = ["upload_new_workout", data, link]
    #     post_workout_req = UrlRequest(link, req_body=data, on_success=self.success_upload_workout,
    #                                   on_error=self.error_upload_workout,
    #                                   on_failure=self.error_upload_workout,
    #                                   ca_file=certifi.where(), method='POST', verify=True)
    #
    #
    # def success_upload_workout(self, *args):
    #     self.hide_loading_screen()
    #
    #     self.change_screen1("workoutsscreen")
    #     self.get_user_data()
    #     self.load_workout_data()
    #     Snackbar(text="Workout saved!").show()
    #     self.root.ids['toolbar'].right_action_items = [
    #         ['menu', lambda x: self.root.ids['nav_drawer'].set_state()]]
    #
    # def error_upload_workout(self, *args):
    #     self.hide_loading_screen()
    #     print(args)
    #     print(args[0])
    #     print("error uploading")
    #
    # def update_existing_workout(self, workout_key, workout_name, workout_exc):
    #     if self.debug:
    #         print("workout_key to update:", workout_key)
    #         print("workout_name to update:", workout_name)
    #         print("workout_exc to update:", workout_exc)
    #         print("real workout details:", self.workoutsParsed[workout_key])
    #
    #     self.display_loading_screen()
    #
    #     workout_link = "https://gymbuddy2.firebaseio.com/%s/workouts/%s.json?auth=%s" % (
    #         self.local_id, workout_key, self.id_token)
    #     print(workout_link)
    #     Workout = "{%s: %s}" % ('"' + workout_name + '"', '"' + str(workout_exc) + '"')
    #     data = json.dumps(Workout)
    #     post_workout_req = UrlRequest(workout_link, req_body=data, on_success=self.success_upload_workout,
    #                                   on_error=self.error_upload_workout,
    #                                   on_failure=self.error_upload_workout,
    #                                   ca_file=certifi.where(), method='PUT', verify=True)
    #
    # def upload_session(self, data, link):
    #     self.display_loading_screen()
    #     self.upload_backup = ["session_upload", data, link]
    #     req = UrlRequest(link, req_body=data, on_success=self.on_session_save_success,
    #                      on_error=self.on_session_save_error,
    #                      on_failure=self.on_session_save_error, ca_file=certifi.where(), verify=True)
    #
    # def on_session_save_success(self, *args):
    #     self.root.ids['sessionscreen'].dialog.dismiss()
    #     self.change_screen1("homescreen")
    #     self.get_user_data()
    #     self.load_session_data()
    #     self.running_session = 0
    #     Snackbar(text="Session saved!").show()
    #     self.upload_backup = 0
    #     self.hide_loading_screen()
    #
    # def on_session_save_error(self, *args):
    #     self.root.ids['sessionscreen'].dialog.dismiss()
    #     self.refresh_auth_token()
    #     self.hide_loading_screen()
    #     Snackbar(text="Something went wrong!", padding="20dp", button_text="TRY AGAIN", button_color=(1, 0, 1, 1),
    #              duration=10,
    #              button_callback=self.on_upload_error).show()
    #     if self.debug:
    #         print(args)
    #         print("error session save")
    #
    # def on_upload_error(self, *args):
    #     if self.upload_backup:
    #         upload_backup = self.upload_backup
    #         method = upload_backup[0]
    #         data = upload_backup[1]
    #         link = upload_backup[2]
    #         if method == "session_upload":
    #             self.upload_session(data, link)

    # Backup in case of app being closed on running session
    def upload_temp_session(self, *args):

        date = self.root.ids['sessionscreen'].ids["date_picker_label"].text
        session_rec = self.root.ids['sessionscreen'].session_rec
        for exc in list(session_rec):
            if not session_rec[exc]:  # if exc is empty (after deletion)
                session_rec.pop(exc, None)
        link = "https://gymbuddy2.firebaseio.com/%s/temp_session.json?auth=%s" % (self.local_id, self.id_token)
        print("timer to upload", self.timer)
        session_data = [date, self.timer, self.root.ids['sessionscreen'].workout_key,
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

    # Loading Spinner Methods
    def display_loading_screen(self, *args):
        self.popup.open()

    def hide_loading_screen(self, *args):
        self.popup.dismiss()

    def upload_settings(self):
        units = self.units
        link = "https://gymbuddy2.firebaseio.com/%s/settings.json?auth=%s" % (self.local_id, self.id_token)
        settings_data = {"units": units}
        data = json.dumps(settings_data)
        self.upload_data(data, link, 4)

    def change_user_name(self, user_name):
        self.user_name = user_name

        self.root.ids['settingsscreen'].ids.user_name_label.text = user_name

        user_name_lower = user_name.lower()

        link_lower = "https://gymbuddy2.firebaseio.com/%s/user_name.json?auth=%s" % (self.local_id, self.id_token)
        link = "https://gymbuddy2.firebaseio.com/%s/real_user_name.json?auth=%s" % (self.local_id, self.id_token)

        data = json.dumps(user_name)
        data_lower = json.dumps(user_name_lower)

        self.upload_data(data_lower, link_lower, 4)
        self.upload_data(data, link, 4)


MainApp().run()
