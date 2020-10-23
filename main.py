from kivy.config import Config
from kivymd.color_definitions import colors

Config.set('graphics', 'resizable', 1)

from kivy.metrics import dp
import ast
import calendar
import os
import smtplib
from datetime import datetime, date, timedelta
import certifi
from kivy.graphics.vertex_instructions import Rectangle, RoundedRectangle
from kivy.network.urlrequest import UrlRequest
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, NoTransition, SlideTransition
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.picker import MDDatePicker
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from customKv.toolbar import CustomMDToolbar
from kivymd.uix.card import MDCard, MDSeparator
from kivy.factory import Factory
import copy
import math
from kivy.utils import platform
import kivy.utils as utils
import requests
import json
from kivy.clock import Clock
import time

""" Screens classes import """

from FirebaseLoginScreen.firebaseloginscreen import FirebaseLoginScreen
from screens_py.homescreen import HomeScreen
from screens_py.settingsscreen import SettingsScreen
from screens_py.workoutsscreen import WorkoutsScreen
from screens_py.workoutscreen import WorkoutScreen
from screens_py.exercise_sessions import ExerciseSessionsScreen
from screens_py.previous_workouts import PreviousWorkoutsScreen
from screens_py.welcome_screen import WelcomeScreen
from screens_py.exercise_stats_screen import ExerciseStatsScreen
from screens_py.sessionscreen import SessionScreen, ExerciseScreen

from kivy.core.window import Window

# Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
# Window.softinput_mode = "below_target"


if platform != 'android':
    Window.size = (330, 650)


    def run_on_ui_thread(*args):
        return
else:  # For managing android JAVA classes
    from jnius import autoclass, cast
    from android import mActivity
    from android.runnable import run_on_ui_thread
    import sentry_sdk

    sentry_sdk.init(
        "https://2a7928d9ecc4464286cc2def110e4d7d@o460345.ingest.sentry.io/5460360",
        traces_sample_rate=1.0
    )


## msg for new workout name
class AddWorkoutContent(BoxLayout):
    pass


class SendMailContent(BoxLayout):
    pass


class UpdateWeightContent(BoxLayout):
    pass


class ChangeUserNameContent(BoxLayout):
    pass


class BlankScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_enter(self, *args):
        self.app.title = "Friends"


# Class for handling sessions data.
class Workout_Session:

    def __init__(self, session_key, date, duration, workout_key, workout_name, workout_split, exercises, session_num):
        self.session_key = session_key
        self.date = date
        self.duration = duration
        self.workout_key = workout_key
        self.workout_name = workout_name
        self.workout_split = workout_split
        self.exercises = exercises
        self.session_num = session_num


class MainApp(MDApp):
    mainscreens = ["homescreen", "workoutsscreen", "previous_workouts_screen", "settingsscreen"]
    bottom_nav = 0
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
    last_session_date = 0  # for dashboard quick view
    text_color = (0, 0, 1, 1)
    workout_edit_mode = 0
    exc_pie_dic = {"None": 100}
    total_exc_sets = 0
    monthly_session_amount = 0
    weekly_session_amount = 0
    workouts_trained_amount = {}
    today_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    units = "metric"  # kg to lbs 1 to 2.20462262
    kg_to_pounds = 2.2
    user_name = ''
    weights = {}  # dict of dates and weight measures
    weight_date = '0'
    temp_num_filter = ''
    app_mail = ''
    app_pass = ''
    bottom_buttons_inc = 0.018
    weight_history_by_month_year = {}
    recent_sessions = []
    session_counter = 0
    exercises_bank = ["Bench Press", "Squats", "Push Ups", "Pull Ups", "Leg Press", "Bent Over Row", "Flies",
                      "Bicep Curl", "Military Press"]
    resize_event = 0
    tabs_text_color_normal = (1, 1, 1, 0.5)
    tabs_text_color_active = (1, 1, 1, 1)
    tabs_color_indicator = (1, 1, 1, 1)

    """ App Main Functions """

    def __init__(self, **kwargs):
        self.title = "FitnessApp"
        super().__init__(**kwargs)

        menu_items = [{"text": f"{exc}"} for exc in self.exercises_bank]
        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=4,
        )
        self.menu.bind(on_release=self.menu_callback)

        # workout_menu_items = [{"text": f"{option}"} for option in ["Edit","Delete"]]
        workout_menu_items = [{"icon": "pencil", "text": "Edit"}, {"icon": "trash-can-outline", "text": "Delete"}]
        self.workout_menu = MDDropdownMenu(
            items=workout_menu_items,
            width_mult=3.2,
        )
        self.workout_menu.bind(on_release=self.workout_menu_callback)

    def workout_menu_callback(self, instance_menu, instance_menu_item):
        method = instance_menu_item.text
        if method == "Edit":
            self.root.ids['workoutscreen'].show_view_buttons(False)
            self.root.ids['workoutscreen'].show_edit_buttons(True)
            self.root.ids['workoutscreen'].edit_mode = 1
        else:
            self.delete_workout_msg(self.root.ids['workoutscreen'].workout_key)

        instance_menu.dismiss()

    def on_start(self):
        if platform == "android":
            color_s = '#' + colors[self.theme_cls.primary_palette]['700']
            color_n = '#' + colors[self.theme_cls.primary_palette]['500']
            self.statusbar(color_s, color_n)
            self.clear_statusbar()
            self.set_Full_Screen_Flags()
        self.weight_date = self.today_date[:10]
        # Window.on_resize = self.show_size
        # Window.size = self.window_size
        # Window.fullscreen= 1
        # Window.allow_stretch = True
        # Window.minimum_width = self.window_size[0]
        # Window.minimum_height = self.window_size[1]

        self.root.ids.firebase_login_screen.ids.login_screen.ids.backdrop.open()  # start login screen with closed backdrop
        # before login, denies access to navigation drawer
        # bind android back button to back function
        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        try:
            file1 = open("resources/appmail.txt", "r")
            account = file1.read().splitlines()
            self.app_mail = account[0]
            self.app_mail_pass = account[1]
        except:
            print("couldnt load mail and pass")

    def on_pause(self):
        self.clear_statusbar()
        self.set_Full_Screen_Flags()
        return True

    def on_resume(self):
        pass
    def on_stop(self):
        if self.running_session:
            self.upload_temp_session()
        else:
            self.clean_temp_session_data()

    def on_login(self):
        self.text_color = utils.get_color_from_hex("#283592")
        # loads data
        if self.root.ids.firebase_login_screen.login_success == False:
            return
        if not self.sign_up:
            self.change_screen("main_app_screen", "left")
            Snackbar(text="Logged in!").show()

            self.root.ids['bottom_nav'].on_resize()
            self.add_top_canvas()
            self.root.ids['bottom_nav'].switch_tab('1')
            self.get_user_data()

            try:
                self.load_session_data()
                self.update_chart()

            except:
                print("failed load session")
                self.sessions = {}
            self.load_workout_data()
            self.load_settings_data()
            self.load_weight_data()
        else:
            self.clear_user_app_data()
            self.update_dashboard_stats()
            self.update_last_date_card()
            self.change_screen("welcome_screen", 'left')

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

        ## for home screen first load
        if self.units == "metric":
            self.root.ids['homescreen'].ids["weight_units"].text = "Kg"
        else:
            self.root.ids['homescreen'].ids["weight_units"].text = "Lbs"
        # self.change_screen1("exercise_sessions_screen")

    def on_logout(self):
        self.clear_user_app_data()

        self.root.ids.firebase_login_screen.login_success = False
        self.root.ids.firebase_login_screen.save_refresh_token("")

        Snackbar(text="Logged out!").show()

        self.change_screen("loginscreen", 'right')
        self.change_screen1("homescreen")

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

    def clear_user_app_data(self):
        self.root.ids['previous_workouts_screen'].curr_month = 0
        self.root.ids['previous_workouts_screen'].curr_year = 0
        self.set_current_weight(0, 0)
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
        self.recent_sessions = []
        self.reload_for_running_session = ""
        self.delete_mode = 0
        self.last_session_date = 0
        self.sign_up = 0
        self.workout_edit_mode = 0
        self.exc_pie_dic = {"None": 100}
        self.total_exc_sets = 0
        self.delete_workout_grid()
        self.update_chart()
        self.update_last_date_card()
        self.monthly_session_amount = 0
        self.weekly_session_amount = 0
        self.workouts_trained_amount = {}
        self.weights = {}
        self.weight_date = self.today_date[:10]
        self.temp_num_filter = ''
        self.weight_history_by_month_year = {}
        self.units = "metric"

    def change_title(self, text):
        self.root.ids['toolbar'].title = text

    """ Refresh Auth token if expired """

    def refresh_auth_token(self):
        self.root.ids.firebase_login_screen.load_saved_account()

    """ Bind back button of android to back function. """

    def hook_keyboard(self, window, key, *largs):

        if key == 27:
            try:
                self.root.ids.firebase_login_screen.hide_loading_screen()
                self.hide_loading_screen()
            except:
                print("couldnt hide loading screen")
            try:
                if self.root.ids['screen_manager1'].current == "homescreen":
                    from jnius import autoclass
                    activity = autoclass('org.kivy.android.PythonActivity')
                    activity.moveTaskToBack(True)
                    return True
            except:
                pass
            self.back_to_last_screen()
        return True

    """ Fixing on resume bug where screen resize """

    @run_on_ui_thread
    def clear_statusbar(self):
        LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
        window = mActivity.getWindow()
        window.setFlags(
            LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            LayoutParams.FLAG_LAYOUT_NO_LIMITS)

    @run_on_ui_thread
    def statusbar(self, color_s, color_n):
        LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
        window = mActivity.getWindow()
        window.clearFlags(LayoutParams.FLAG_LAYOUT_NO_LIMITS)
        window.clearFlags(LayoutParams.FLAG_TRANSLUCENT_STATUS)
        window.addFlags(LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
        window.setStatusBarColor(Color.parseColor(color_s))
        window.setNavigationBarColor(Color.parseColor(color_n))
        window.getDecorView().setSystemUiVisibility(0)

    @run_on_ui_thread
    def set_Full_Screen_Flags(self):
        LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
        window = mActivity.getWindow()
        window.clearFlags(LayoutParams.FLAG_FORCE_NOT_FULLSCREEN)
        window.addFlags(LayoutParams.FLAG_FULLSCREEN)

    """ Home screen methods  """
    """ Update exercise pie chart stats on homescreen. """

    def update_chart(self):
        piechart = self.root.ids['homescreen'].ids[
            'piechart']  # getting the id of where the widgets are coming in

        items = [self.calc_exc_pie()]

        self.root.ids['homescreen'].ids[
            'piechart']._clear_canvas()

        self.root.ids['homescreen'].ids[
            'piechart']._make_chart(items)

        self.root.ids['homescreen'].ids[
            'piechart'].items = items

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

    def open_pie_dialog(self):
        text = ""
        for exc in self.exc_pie_dic:
            text += exc + ": " + str(self.exc_pie_dic[exc]) + "\n"
        if text:
            text = text[:-1]
        if text.find("None") != -1:
            text = "Here will be your exercises set list"
        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.1),
                               title="Exercise Statistics - Set Amount", text=text)
        self.dialog.open()

    def update_last_date_card(self):
        if self.recent_sessions:

            last_session_date = self.recent_sessions[0]

            last_session = self.sessions[last_session_date]
            last_session_name = last_session.workout_name
            last_session_num = last_session.session_num
            last_session_exc_completed = str(len(last_session.exercises)) + " exercises completed"
            last_session_date = last_session_date.ctime()[0:10]
            last_session_date = last_session_date[0:3] + "," + last_session_date[3:]

            if len(last_session_name) > 11:
                self.root.ids['homescreen'].ids['last_space'].size_hint_y = 6.5
                self.root.ids['homescreen'].ids['last_session_name'].size_hint_y = 4

            else:
                self.root.ids['homescreen'].ids['last_space'].size_hint_y = 8.4
                self.root.ids['homescreen'].ids['last_session_name'].size_hint_y = 2.5
            last_session_pic_num = (last_session_num % 7) + 1
            self.root.ids['homescreen'].ids['last_session_card'].background = "resources/session_back/" + str(
                (last_session_num % 7) + 1) + ".png"
            self.root.ids['homescreen'].ids['last_session_date'].text = last_session_date
            self.root.ids['homescreen'].ids['last_session_name'].text = last_session_name
            # self.root.ids['homescreen'].ids['session_exc_completed'].text = session_exc_completed
            if len(self.recent_sessions) > 1:
                prev_last_session_date = self.recent_sessions[1]

                prev_last_session = self.sessions[prev_last_session_date]
                prev_last_session_name = prev_last_session.workout_name
                prev_last_session_num = prev_last_session.session_num

                prev_last_session_exc_completed = str(len(prev_last_session.exercises)) + " exercises completed"
                prev_last_session_date = prev_last_session_date.ctime()[0:10]
                prev_last_session_date = prev_last_session_date[0:3] + "," + prev_last_session_date[3:]
                if len(prev_last_session_name) > 11:
                    self.root.ids['homescreen'].ids['prev_last_space'].size_hint_y = 6.5
                    self.root.ids['homescreen'].ids['prev_last_session_name'].size_hint_y = 4

                else:
                    self.root.ids['homescreen'].ids['prev_last_space'].size_hint_y = 8.4
                    self.root.ids['homescreen'].ids['prev_last_session_name'].size_hint_y = 2.5

                prev_session_pic_num = (prev_last_session_num % 7) + 1
                if last_session_pic_num == prev_session_pic_num:
                    prev_session_pic_num = (prev_session_pic_num % 7) + 1
                self.root.ids['homescreen'].ids['prev_last_session_card'].background = "resources/session_back/" + str(
                    prev_session_pic_num) + ".png"
                self.root.ids['homescreen'].ids['prev_last_session_date'].text = prev_last_session_date
                self.root.ids['homescreen'].ids['prev_last_session_name'].text = prev_last_session_name
                self.show_two_recent_msg()
            else:
                self.show_one_recent()
        else:
            self.show_no_recent_msg()

    def show_two_recent_msg(self):
        self.root.ids['homescreen'].ids["no_workout_label"].opacity = 0
        self.root.ids['homescreen'].ids["one_workout_label"].opacity = 0
        self.root.ids['homescreen'].ids["last_session_card"].opacity = 1
        self.root.ids['homescreen'].ids["prev_last_session_card"].opacity = 1

    def show_no_recent_msg(self):
        self.root.ids['homescreen'].ids["no_workout_label"].opacity = 1
        self.root.ids['homescreen'].ids["last_session_card"].opacity = 0
        self.root.ids['homescreen'].ids["prev_last_session_card"].opacity = 0
        self.root.ids['homescreen'].ids["one_workout_label"].opacity = 0

    def show_one_recent(self):
        self.root.ids['homescreen'].ids["no_workout_label"].opacity = 0
        self.root.ids['homescreen'].ids["last_session_card"].opacity = 1
        self.root.ids['homescreen'].ids["prev_last_session_card"].opacity = 0
        self.root.ids['homescreen'].ids["one_workout_label"].opacity = 1

    def update_dashboard_stats(self):

        self.root.ids['homescreen'].ids['monthly_sessions'].text = str(self.monthly_session_amount)
        self.root.ids['homescreen'].ids['weekly_sessions'].text = str(self.weekly_session_amount)

    """ Method for displaying dialog with custom content """

    def show_content_msg(self, *args):
        """ Args can be: 0 for OK action. 1 for Cancel action, 2 for title, 3 content - 1 means SendMailContent 2 - UpdateWeight
        """
        try:
            ok_action = args[0]
            cancel_action = args[1]
            title = args[2]
            content = args[3]
            ok_title = args[4]
        except:
            pass
        if content == 1:
            dialog_content = SendMailContent()
            size_y = 0.4
        if content == 2:
            dialog_content = UpdateWeightContent()
            size_y = 0.2

        if content == 3:
            dialog_content = AddWorkoutContent()
            size_y = 0.2

        self.dialog = MDDialog(
            radius=[10, 7, 10, 7],
            size_hint=(0.9, size_y),
            title=title,
            type="custom",
            content_cls=dialog_content,
            buttons=[

                MDFlatButton(
                    text="CANCEL",
                    text_color=self.theme_cls.primary_color,
                    on_release=cancel_action
                ),
                MDFlatButton(
                    text=ok_title,
                    text_color=self.theme_cls.primary_color,
                    on_release=ok_action
                ),
            ],
        )
        self.dialog.open()
        if content == 2:
            self.dialog.content_cls.remove_widget(self.dialog.content_cls.children[1])
            self.dialog.content_cls.height = dp(80)

    def show_ok_cancel_msg(self, *args):
        """ Args can be: 0 for OK action. 1 for Cancel action, 2 for title, 3 for msg
        """
        try:
            ok_action = args[0]
            cancel_action = args[1]
            title = args[2]
            msg = args[3]
        except:
            pass

        self.dialog = MDDialog(
            radius=[10, 7, 10, 7],
            size_hint=(0.9, 0.2),
            title=title,
            text=msg,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    text_color=self.theme_cls.primary_color,
                    on_release=cancel_action
                ),
                MDFlatButton(
                    text="OK",
                    text_color=self.theme_cls.primary_color,
                    on_release=ok_action
                )
            ],
        )
        self.dialog.open()

    def show_ok_msg(self, *args):
        """ Args can be: 0 for OK action. 1 for title, 2 for msg
        """
        try:
            ok_action = args[0]
            title = args[1]
            msg = args[2]
        except:
            pass

        self.dialog = MDDialog(
            radius=[10, 7, 10, 7],
            size_hint=(0.9, 0.2),
            title=title,
            text=msg,
            buttons=[
                MDFlatButton(
                    text="OK",
                    text_color=self.theme_cls.primary_color,
                    on_release=ok_action
                )
            ],
        )
        self.dialog.open()

    """ Feedback or bug reporting method"""

    def send_email(self, *args):
        self.dismiss_dialog()
        self.display_loading_screen()

        if self.debug:
            print("trying to send feedback")
            print("subject:", self.dialog.title)
            print("content:", self.dialog.content_cls.children[0].text)

        subject = self.dialog.title.split()
        try:
            subject = subject[2]
        except:
            subject = subject[1]

        msg = self.dialog.content_cls.children[0].text
        if not msg:
            self.hide_loading_screen()
            self.show_ok_msg(self.dismiss_dialog, "Try Again", "Can't send empty message")
            return
        fromaddr = self.app_mail
        toaddrs = self.app_mail

        user_email = self.user_data["email"]

        TEXT = "From " + user_email + "\n" + msg
        SUBJECT = subject
        msg = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

        username = self.app_mail

        password = self.app_mail_pass
        try:
            server = smtplib.SMTP('smtp.gmail.com:587')

            server.starttls()

            server.login(username, password)

            server.sendmail(fromaddr, toaddrs, msg)

            server.quit()
            self.hide_loading_screen()

            Snackbar(text="Message Sent! Thanks for the report").show()

        except:
            self.hide_loading_screen()
            print("couldnt send msg")
            Snackbar(text="Something went wrong, try again later").show()

    """ Find for given Exercise the best Set of all sessions"""

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

    """ Find the best set of a given Session - weight wise"""

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

    """ Session Methods"""

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
        self.sessions = {}
        today_date = datetime.today()
        curr_month = today_date.month
        curr_year = today_date.year

        # TODO seperate monday as the first day of the week

        curr_week = today_date.strftime("%U")

        session_counter = 0
        for session_key in session_dic:
            session_counter += 1

            session = ast.literal_eval(session_dic[session_key][1:-1])  # turning the str to list

            date = datetime.strptime(session[0], "%d/%m/%Y %H:%M:%S")

            if date.month == curr_month and date.year == curr_year:
                self.monthly_session_amount += 1
                session_week = date.strftime("%U")

                # date_plus_one_day = date + timedelta(days=1)

                if session_week == curr_week:
                    self.weekly_session_amount += 1
            if date in self.sessions:
                date = date + timedelta(seconds=60)
            duration = session[1]
            workout_key = session[2]
            workout_name = session[3]
            workout_split = session[4]
            exercises = session[5]

            self.add_session_to_excs_stats(exercises, date, workout_name)
            new_session = Workout_Session(session_key, date, duration, workout_key, workout_name, workout_split,
                                          exercises, session_counter)
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
            last_session_date = session_dates[0]
            self.last_session_date = session_dates[0]
            try:
                prev_last_session_date = session_dates[1]
                self.recent_sessions = [last_session_date, prev_last_session_date]
            except:
                print("only one recent workout")
                self.recent_sessions = [last_session_date]
                # only one session
        else:
            self.recent_sessions = []
        self.update_last_date_card()

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
                    text="CANCEL",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.dismiss_dialog
                ),
                MDFlatButton(
                    text="OK",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.resume_session
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
            exc_session = 0
            if exc in self.exc_sessions:
                if date in self.exc_sessions[exc]:
                    exc_session = self.exc_sessions[exc].pop(date)
            if not exc_session:
                if self.debug:
                    print("skipped on ", exc)
                return
            if self.is_in_past_month(date):
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

    def del_session(self, session_date_key):
        # self.display_loading_screen()
        if self.debug:
            print("deleting session")
            print("session_date_key", session_date_key)
            print("session_before_del", self.sessions)
        session = self.sessions.pop(session_date_key)

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
        # TODO delete session from sessions dict

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

    """ Workout Methods. """

    def show_workout_help(self):
        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
                               title="Create Workout - Help",
                               padding=10,
                               text="[size=" + str(
                                   int(
                                       self.headline_text_size * 0.75)) + "][color=0,0,0,1]Add Splits[/color][/size]\nSplit system training is a program of weight training that divides training sessions by body regions - usually upper and lower body training.\nYou can add up to 7 different splits.\n\n[size=" + str(
                                   int(
                                       self.headline_text_size * 0.75)) + "][color=0,0,0,1]Add Exercise[/color][/size]\nPress the plus icon located at the bottom of the screen to add a new exercise.\nYou can type the name of the exercise or choose from list of exercises with the bank button."
                               )
        self.dialog.open()

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
        num_of_pic = -1
        for workoutkey in workoutDic:
            num_of_pic += 1

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
                    background="resources/workout_back/" + str((num_of_pic % 5) + 1) + ".jpg",
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
                    theme_text_color="Custom",
                    # text_color=self.theme_cls.primary_color
                    text_color=(1, 1, 1, 1)
                ))

                card_layout.add_widget(MDLabel(
                    text="Created: " + workout_date,
                    font_style="Subtitle1",
                    pos_hint={"center_y": 0.06, "center_x": 0.5},
                    theme_text_color="Custom",
                    # text_color=self.theme_cls.primary_color
                    text_color=(1, 1, 1, 0.7)
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
                    theme_text_color="Custom",
                    # text_color=self.theme_cls.primary_color
                    text_color=(1, 1, 1, 0.7)
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

    def first_new_workout(self, *args):

        workout_name = self.dialog.content_cls.children[0].text
        if not workout_name:
            return
        self.dialog.dismiss()
        self.root.ids['workoutscreen'].workout = []
        self.root.ids['workoutscreen'].temp_workout = []
        self.root.ids['workoutscreen'].workout_name = workout_name
        self.root.ids['workoutscreen'].create_mode = 1
        self.root.ids['workoutscreen'].num_of_splits = 1
        screen_manager = self.root.ids['screen_manager1']
        screen_manager.current = 'workoutscreen'
        self.change_screen("main_app_screen")
        self.root.ids['bottom_nav'].on_resize()

        self.remove_bottom_nav()
        self.add_top_canvas()
        self.add_bottom_canvas()
        self.root.ids['toolbar'].left_action_items = [["chevron-left", lambda x: self.back_to_last_screen()]]

    def create_new_workout(self, *args):
        new_workout = args[0].parent.parent.parent.children[2].children[0].children[0].text
        # If the user hasnt written any name, do nothing.
        if new_workout and not new_workout.isspace():
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
                    text="CANCEL",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.dismiss_dialog
                ),
                MDFlatButton(
                    text="OK",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.create_new_workout
                ),
            ],
        )
        self.dialog.open()

    def dismiss_dialog(self, *args):
        self.dialog.dismiss()

    def show_change_user_name_dialog(self):
        self.dialog = MDDialog(
            radius=[10, 7, 10, 7],
            size_hint=(0.9, 0.3),
            title="Enter new username",
            type="custom",
            content_cls=ChangeUserNameContent(),
            buttons=[

                MDFlatButton(
                    text="CANCEL",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.dismiss_dialog
                ),
                MDFlatButton(
                    text="OK",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.change_user_name_callback
                ),
            ],
        )
        self.dialog.open()

    def change_user_name_callback(self, *args):
        text_field = args[0].parent.parent.parent.children[2].children[0].children[1]
        error_label = args[0].parent.parent.parent.children[2].children[0].children[0]
        new_user_name = text_field.text
        if not new_user_name or new_user_name.find(" ") != -1:
            error_label.text = "English letters and numbers, without spaces"
            return
        check_is_exist = self.root.ids.firebase_login_screen.is_user_exist(new_user_name)
        if check_is_exist == 2:  # no internet
            self.dismiss_dialog()
            self.root.ids.firebase_login_screen.show_no_internet_msg()
            return
        if not check_is_exist:
            self.dismiss_dialog()
            self.change_user_name(new_user_name)
        else:
            error_label.text = new_user_name + " already taken"

    def start_workout(self, *args):
        # start new session of workout

        # workoutkey = args[0].parent.children[3].text
        workoutkey = args[0]

        # workout_split = self.split_Choice_dict[workoutkey]
        workout_split = args[1]
        try:
            workout_list = list(self.workoutsParsed[workoutkey][0].values())
        except KeyError:
            print("no such workout key", workoutkey)
            self.show_ok_msg(self.dismiss_dialog, "Error", "This workout is no longer available")
            return
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

    def delete_workout_msg(self, *args):
        self.workout_to_delete = args[0]  # saving the object we want to delete
        workoutkey = args[0]
        workout_name = list(self.workoutsParsed[workoutkey][0].keys())[0]

        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
                               title="Delete " + workout_name + "?",
                               text="Warning: Deleting " + workout_name + " cannot be undone\nYour workout history however wont be deleted",
                               buttons=[

                                   MDFlatButton(
                                       text="CANCEL", text_color=self.theme_cls.primary_color,
                                       on_release=self.cancel_del_workout
                                   ),
                                   MDFlatButton(
                                       text="DELETE", text_color=self.theme_cls.primary_color,
                                       on_release=self.del_workout
                                   ),
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
        self.lastscreens = ["homescreen"]
        self.change_screen1("workoutsscreen", -1)
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

    """ Switching Screens Methods """

    def direction_to_switch(self, new_screen):
        screen_manager = self.root.ids['screen_manager1']
        current_screen = screen_manager.current

        if current_screen in self.mainscreens:
            ind_of_current = self.mainscreens.index(current_screen)
            if new_screen in self.mainscreens:
                ind_of_new = self.mainscreens.index(new_screen)
                dif = ind_of_current - ind_of_new
                if dif > 0:
                    return "right"
                else:
                    return "left"
            else:
                return "up"
        elif new_screen in self.mainscreens:
            return "down"
        return "left"

    def back_to_last_screen(self, *args):
        if self.debug:
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
                    self.root.ids['previous_workouts_screen'].curr_year = 0
                    self.root.ids['previous_workouts_screen'].curr_month = 0
                    self.lastscreens = ["homescreen", "workoutsscreen", "workoutscreen"]
                    self.change_screen1("sessionscreen", -1, "right")
                    return

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
                if last_screen in self.mainscreens and current_screen not in self.mainscreens:
                    self.change_screen1(last_screen, -1, "down")
                else:
                    self.change_screen1(last_screen, -1, "right")
            else:
                self.change_screen1("homescreen", "right")

    """ Login Screens Manager """

    def change_screen(self, screen_name, *args):
        # Get the screen manager from the kv file
        screen_manager = self.root.ids['screen_manager']
        if args:
            if args[0]:  # optional transition direction
                screen_manager.transition.direction = args[0]
            else:
                screen_manager.transition.direction = "left"
            try:
                if args[1]:  # optional no transition
                    screen_manager.transition = NoTransition()
            except:
                pass
        screen_manager.current = screen_name
        screen_manager = self.root.ids

    """ Main App Screens Manager """

    def change_screen1(self, screen_name, *args):
        # Get the screen manager from the kv file
        # args is an optional input of which direction the change will occur

        if screen_name != "sessionscreen" and screen_name != "workoutscreen":
            self.clear_canvas()
            self.add_top_canvas()
        if screen_name in self.mainscreens:
            if self.debug:
                print("self.reload_for_running_session", self.reload_for_running_session)
            if self.reload_for_running_session and screen_name == "previous_workouts_screen":
                pass
            else:
                self.add_bottom_nav()
        else:
            self.remove_bottom_nav()

        screen_manager = self.root.ids['screen_manager1']
        current_screen = screen_manager.current

        if self.debug:
            print("Before change screen, curr screen: ", current_screen)
            print("trying to switch to: ", screen_name)

        if self.lastscreens:
            self.lastscreens.append(current_screen)
        else:
            self.lastscreens.append(current_screen)
        # screen_manager.transition = NoTransition()

        if args:
            for item in args:
                if item == -1:
                    last_screen = self.lastscreens.pop(-1)
                    while self.lastscreens and self.lastscreens[-1] == last_screen:
                        last_screen = self.lastscreens.pop(-1)

                    if screen_name in self.mainscreens:
                        try:
                            ind = self.mainscreens.index(screen_name)
                            temp = copy.deepcopy(self.lastscreens)
                            self.root.ids['bottom_nav'].switch_tab(str(ind + 1))
                            self.lastscreens = temp


                        except:
                            print("wasnt able to switch tabs")

                if item == -2:  # optional no transition
                    screen_manager.transition = NoTransition()
                if isinstance(item, str):  # optional transition direction
                    screen_manager.transition.direction = item

        else:
            screen_manager.transition.direction = self.direction_to_switch(screen_name)
            # if args[1]:  # optional no transition
            #     screen_manager.transition = NoTransition()

        if screen_name == "homescreen":
            self.root.ids['toolbar'].left_action_items = [['', lambda x: None]]
            self.lastscreens = []
        else:
            if screen_name in self.mainscreens and not self.reload_for_running_session:
                self.root.ids['toolbar'].left_action_items = [['', lambda x: None]]
            else:
                self.root.ids['toolbar'].left_action_items = [["chevron-left", lambda x: self.back_to_last_screen()]]

        # if screen_name != "sessionscreen":
        #     self.root.ids['toolbar'].right_action_items = [
        #         ['menu', lambda x: self.root.ids['nav_drawer'].set_state()]]

        if -3 in args:  # recovering transition
            screen_manager.current = screen_name
            screen_manager.transition = SlideTransition()
        else:
            screen_manager.current = screen_name

        if self.debug:
            print("self.lastscreens", self.lastscreens, )
            print("currscreen = ", screen_name)

    """ Bottom Nav handler """

    def remove_bottom_nav(self):
        try:
            self.bottom_nav = self.root.ids['bottom_nav']
            self.root.ids['main_layout'].remove_widget(self.bottom_nav)
        except:
            pass

    def add_bottom_nav(self):
        try:
            self.root.ids['main_layout'].add_widget(self.bottom_nav)
        except:
            pass

    """ Top and bottom background for main app screens"""

    def add_top_canvas(self):
        self.window_size = Window.size
        with self.root.ids.main_layout.canvas.before:
            Rectangle(source='resources/canvas.png', pos=(0, self.window_size[1] / 1.23), size=(
                self.root.ids.main_layout.parent.parent.size[0], self.root.ids.main_layout.parent.parent.size[1] / 5))

    def add_bottom_canvas(self):
        with self.root.ids.main_layout.canvas.before:
            Rectangle(source='resources/canvas.png', pos=(0, 0), size=(
                self.root.ids.main_layout.parent.parent.size[0], self.root.ids.main_layout.parent.parent.size[1] / 10))

    def clear_canvas(self):
        self.root.ids.main_layout.canvas.before.clear()

    """ Input Filters """

    def proper_input_filter(self, input_to_check, indicator):

        if self.debug:
            print("input_to_check", input_to_check)
            print("indicator", indicator)
        asci_val = ord(input_to_check)
        if asci_val > 64 and asci_val < 90:
            return input_to_check
        if asci_val > 96 and asci_val < 123:
            return input_to_check
        if asci_val > 47 and asci_val < 58:
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

    def text_input_length_filter(self, widget, text, leng):
        if len(text) > leng:
            widget.text = text[:leng]

    """ Filter for number inputs, checking length and if negative, and decimal precision """

    def input_number_check(self, widget, text):
        new_text = text
        if new_text and new_text != '.' and new_text != '-':

            try:
                number = int(new_text)
            except ValueError:
                number = float(new_text)

            if number < 0:
                new_text = str(number * -1)
                if self.debug:
                    print("isnegative now is:", new_text)

            if len(new_text) > 6:
                new_text = new_text[:6]
                widget.text = new_text[:6]
                if self.debug:
                    print("longer than 6 now:", new_text)

                return

            if '.' in new_text:
                new_text = self.check_after_float_point(new_text)
                if self.debug:
                    print("was . now :", new_text)

        if new_text == '.' or new_text == '-':
            new_text = ''
        widget.text = new_text

    """ Help method for input_number_check, allows only 2 numbers after float point """

    def check_after_float_point(self, text):
        text_len = len(text)
        dot_ind = text.find('.')
        if text_len - dot_ind > 2:
            return text[:dot_ind + 3]
        return text

    """ Uploading to Firebase methods """

    def upload_data(self, *args):
        """  target can be: 1 - upload new workout ,
             2 - update an existing workout, 3 - upload new session, 4 - upload settings, 5 - delete account
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

        if target == 1 or target == 3 or target == 5:
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
        self.hide_loading_screen()
        """  target can be: 1 - upload new workout ,
             2 - update an existing workout, 3 - upload new session, 4 - upload settings, 5 - delete account
        """
        target = self.upload_backup[2]
        if target == 4 or target == 5:
            return
        else:
            self.running_session = 0
            self.get_user_data()
            self.load_session_data()
            self.load_workout_data()
            self.root.ids['previous_workouts_screen'].curr_month = 0
            self.root.ids['previous_workouts_screen'].curr_year = 0
            if target == 1 or target == 2:
                self.root.ids['bottom_nav'].switch_tab('2')
                self.lastscreens = ["homescreen"]
                self.change_screen1("workoutsscreen", -1, "down")

            else:
                self.root.ids['bottom_nav'].switch_tab('1')
                self.change_screen1("homescreen")

            # self.root.ids['toolbar'].right_action_items = [
            #     ['menu', lambda x: self.root.ids['nav_drawer'].set_state()]]
            Snackbar(text="Workout saved!").show()
            self.upload_backup = 0

    def error_upload(self, *args):
        self.refresh_auth_token()
        self.on_upload_error()
        # Snackbar(text="Something went wrong!", padding="20dp", button_text="TRY AGAIN", button_color=(1, 0, 1, 1),
        #          duration=15,
        #          button_callback=self.on_upload_error).show()

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

    def upload_temp_session(self, *args):

        date = self.root.ids['sessionscreen'].ids["date_picker_label"].text
        session_rec = self.root.ids['sessionscreen'].session_rec
        for exc in list(session_rec):
            if not session_rec[exc]:  # if exc is empty (after deletion)
                session_rec.pop(exc, None)
        link = "https://gymbuddy2.firebaseio.com/%s/temp_session.json?auth=%s" % (self.local_id, self.id_token)
        if self.debug:
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

    """ Spinner for loading """

    def display_loading_screen(self, *args):
        self.popup.open()

    def hide_loading_screen(self, *args):
        self.popup.dismiss()

    """ Settings Methods """

    def upload_settings(self):
        units = self.units
        link = "https://gymbuddy2.firebaseio.com/%s/settings.json?auth=%s" % (self.local_id, self.id_token)
        settings_data = {"units": units}
        data = json.dumps(settings_data)
        self.upload_data(data, link, 4)

    def load_settings_data(self):
        settings_dict = self.user_data['settings']
        if "units" in settings_dict:
            units = settings_dict["units"]
            self.units = units
            # if units == 'metric':
            #     self.root.ids['settingsscreen'].ids.metric.active = True
            # else:
            #     self.root.ids['settingsscreen'].ids.imperial.active = True

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

    def success_del_account_data(self, *args):
        delete_account_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/deleteAccount?key=" + self.root.ids.firebase_login_screen.web_api_key
        delete_account_payload = json.dumps({"localId": self.local_id, "idToken": self.id_token})
        UrlRequest(delete_account_url, req_body=delete_account_payload,
                   on_success=self.successful_delete_account,
                   on_failure=self.delete_account_failure,
                   on_error=self.delete_account_failure, ca_file=certifi.where())

    def error_del_account_data(self, *args):
        print(args)
        print("error deleting account data")
        self.dismiss_dialog()
        self.show_ok_msg(self.dismiss_dialog, "Error Deleting Account", "Please try again later")

    def delete_account(self, *args):
        try:
            account_data_link = "https://gymbuddy2.firebaseio.com/%s.json?auth=%s" % (
                self.local_id, self.id_token)
            del_req = UrlRequest(account_data_link, on_success=self.success_del_account_data,
                                 on_error=self.error_del_account_data,
                                 on_failure=self.error_del_account_data,
                                 ca_file=certifi.where(), method='DELETE', verify=True)
        except:
            print("error requesting to delete account data")

    def successful_delete_account(self, *args):
        self.dismiss_dialog()
        self.on_logout()

    def delete_account_failure(self, *args):
        self.show_ok_msg(self.dismiss_dialog, "Error Deleting Account", "Try login again and than delete your account")

    """ Personal weight methods """

    def upload_weight_data(self):
        link = "https://gymbuddy2.firebaseio.com/%s/weights.json?auth=%s" % (self.local_id, self.id_token)
        data_str = '{'
        for key in self.weights:
            data_str += '"' + key.strftime("%d/%m/%Y") + '"'
            data_str += ':'
            data_str += '"' + str(self.weights[key]) + '"'
            data_str += ','
        data_str = data_str[:-1]
        data_str += '}'

        data = json.dumps(data_str)

        # max_date = datetime.strptime(self.app.today_date[:10], '%d/%m/%Y').date()

        self.upload_data(data, link, 4)

    def del_weight_by_key(self, weight_key):
        weight = self.weights.pop(weight_key)
        weight_history_ref = self.weight_history_by_month_year[weight_key.year][weight_key.month]
        ind_to_pop = weight_history_ref.index(weight_key)
        weight_history_ref.pop(ind_to_pop)
        self.upload_weight_data()
        self.sort_weights()

    def load_weight_data(self):
        if self.debug:
            print("trying to load weight")
        if 'weights' in self.user_data:
            weights = self.user_data['weights']
            if weights != '}':
                weights = json.loads(weights)
                for key in weights:
                    date_key = datetime.strptime(key, '%d/%m/%Y').date()
                    self.weights[date_key] = weights[key]
                self.sort_weights()

            if self.debug:
                print("self.weights", self.weights)

    def show_update_weight_dialog(self):
        self.weight_date = self.today_date[:10]
        self.dialog = MDDialog(
            radius=[10, 7, 10, 7],
            size_hint=(0.9, 0.2),
            type="custom",
            content_cls=UpdateWeightContent(),
            buttons=[
                MDFlatButton(
                    text="Show Stats",
                    text_color=(0.5, 0.5, 0.5, 1),
                    on_release=self.show_weight_stats

                ),

                MDFlatButton(
                    text="CANCEL",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.dismiss_dialog
                ),
                MDFlatButton(
                    text="SAVE",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.add_weight_meas
                ),
            ],
        )
        self.dialog.children[0].padding = [dp(24), dp(5), dp(8), dp(8)]
        self.dialog.open()

    def show_date_picker_for_weight(self, *args):
        self.dialog.dismiss()
        max_date = datetime.strptime(self.today_date[:10], '%d/%m/%Y').date()

        MDDatePicker(self.set_previous_date, max_date=max_date).open()

    def set_previous_date(self, date_obj):
        new_date = date_obj.strftime("%d/%m/%Y")
        self.weight_date = new_date
        self.dialog.content_cls.children[1].children[0].text = new_date
        self.dialog.open()

    def add_weight_meas(self, *args):
        # TODO add internet check
        self.dialog.dismiss()

        if self.root.ids['screen_manager'].current != "welcome_screen":
            Snackbar(text="Weight Saved").show()
        try:
            date_to_save = self.dialog.content_cls.children[1].children[0].text
            date_to_save = datetime.strptime(date_to_save, '%d/%m/%Y').date()
        except IndexError:
            date_to_save = datetime.strptime((self.weight_date), '%d/%m/%Y').date()

        try:
            weight_to_save = self.dialog.content_cls.children[0].text
        except IndexError:
            weight_to_save = self.dialog.content_cls.children[0].text

        self.root.ids['welcome_screen'].ids['initial_weight_button'].text = weight_to_save

        if self.units != 'metric':
            weight_to_save = str(round(float(weight_to_save) / self.kg_to_pounds, 2))
            self.root.ids['welcome_screen'].ids['initial_weight_button'].text += " Lbs"
        else:
            self.root.ids['welcome_screen'].ids['initial_weight_button'].text += " Kg"
        self.weights[date_to_save] = weight_to_save
        self.sort_weights()
        self.upload_weight_data()

        if self.root.ids['previous_workouts_screen'].weight_history:
            self.root.ids['previous_workouts_screen'].on_pre_enter()

    def set_current_weight(self, weight, date):

        if weight:
            self.root.ids['exercise_stats_screen'].ids["record"].text = "Current Weight"
            month_abb = calendar.month_abbr[date.month]
            date = str(date.day) + " " + month_abb + ", " + str(date.year)

            # self.root.ids['exercise_stats_screen'].ids["record_date"].text = date
            self.root.ids['exercise_stats_screen'].ids["current_weight_date"].text = date
            unit = " Kg"
            if self.units == "metric":
                self.root.ids['exercise_stats_screen'].ids["current_weight_unit"].text = " Kg"
                self.root.ids['homescreen'].ids["weight_units"].text = "Kg"
                weight = str(round(float(weight), 2))

            else:
                self.root.ids['exercise_stats_screen'].ids["current_weight_unit"].text = " Lbs"
                self.root.ids['homescreen'].ids["weight_units"].text = "Lbs"
                unit = " Lbs"
                weight = str(round(float(weight) * self.kg_to_pounds, 2))

            self.root.ids['exercise_stats_screen'].ids["current_weight"].text = weight

            self.root.ids['homescreen'].ids["personal_weight"].text = weight

            self.root.ids['settingsscreen'].ids["settings_weight_label"].text = weight + unit


        else:
            self.root.ids['homescreen'].ids["personal_weight"].text = "0"
            self.root.ids['exercise_stats_screen'].ids["current_weight"].text = "0"
            self.root.ids['exercise_stats_screen'].ids["current_weight_date"].text = ""

    def show_weight_stats(self, *args):
        self.dialog.dismiss()

        today = datetime.today()

        self.stats_to_weight_mode()
        self.sort_weights()

        self.change_screen1("exercise_stats_screen")

    def sort_weights(self):
        dates = [date for date in self.weights if date != "record"]
        dates.sort(reverse=True)
        if dates:
            self.set_current_weight(self.weights[dates[0]], dates[0])
        else:
            self.set_current_weight(0, 0)
        dates_dict = {}
        for date in dates:
            year = int(date.year)
            month = int(date.month)

            if year not in dates_dict:
                dates_dict[year] = {}

            if month not in dates_dict[year]:
                dates_dict[year][month] = [date]

            else:
                dates_dict[year][month].append(date)
        self.weight_history_by_month_year = dates_dict
        self.root.ids['exercise_stats_screen'].session_date = dates_dict

    def show_weight_history(self):
        self.root.ids['previous_workouts_screen'].weight_history = 1
        self.change_screen1("previous_workouts_screen", 'left')

    def stats_to_weight_mode(self):
        self.root.ids['exercise_stats_screen'].ids["records_scroll"].opacity = 0
        self.root.ids['exercise_stats_screen'].ids["current_weight_card"].opacity = 1
        self.root.ids['exercise_stats_screen'].ids["avg_weight_card"].opacity = 1

        self.root.ids['exercise_stats_screen'].sessions = self.weights
        self.root.ids['exercise_stats_screen'].exericse_name = "Personal Weight"
        self.root.ids['exercise_stats_screen'].exericse_mode = 0

    def stats_to_exercise_mode(self):
        self.root.ids['exercise_stats_screen'].ids["records_scroll"].opacity = 1
        self.root.ids['exercise_stats_screen'].ids["current_weight_card"].opacity = 0
        self.root.ids['exercise_stats_screen'].ids["avg_weight_card"].opacity = 0

        self.root.ids['exercise_stats_screen'].exericse_mode = 1

    """ Converts given str weight to right unit, and returns float """

    def fix_weight_by_unit(self, weight):
        weight = float(weight)
        if self.units != 'metric':
            weight = round(weight * self.kg_to_pounds, 2)
            if weight / round(weight) >= 0.99:
                weight = float(round(weight))
            return weight, "Lbs"
        else:
            weight = round(weight, 2)
            return weight, "Kg"

    """ Exercise Bank Menu handle functions """

    def menu_callback(self, instance_menu, instance_menu_item):
        instance_menu.parent.children[1].children[0].children[2].children[0].children[0].text = instance_menu_item.text
        instance_menu.dismiss()

    def open_exercise_bank_menu(self, *args):
        button = args[0]
        self.menu.caller = button
        self.menu.open()

    def open_workout_menu(self, *args):
        print(self.root.ids['toolbar'].children[0].children)
        print(self.root.ids['toolbar'].children[0].children[0].children[0])

        button = self.root.ids['toolbar'].children[0].children[0].children[0]
        self.workout_menu.caller = button
        self.workout_menu.open()

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

    # def is_user_exist(self, user_name):
    #     user_name = '"' + user_name + '"'
    #     check_req = requests.get(
    #         'https://gymbuddy2.firebaseio.com/.json?orderBy="user_name"&equalTo=' + user_name)
    #     print(check_req)
    #     data = check_req.json()
    #     if data:
    #         return True
    #     else:
    #         return False

    # filter for names input, allows numbers and english letters only

    # allow for 6 digits top as input
    # def proper_number_filter(self, input_to_check, indicator):
    #     self.temp_num_filter = self.dialog.content_cls.children[1].text
    #     if len(self.temp_num_filter) < 6:
    #         if input_to_check.isnumeric() or input_to_check== '.':
    #             if input_to_check== '.':
    #                 if self.temp_num_filter and '.' not in self.temp_num_filter:
    #                     self.temp_num_filter += '.'
    #                     if self.temp_num_filter[0] =='.':
    #                         return ''
    #                     else:
    #                         self.dialog.content_cls.children[1].text = self.temp_num_filter
    #                         return ''
    #                 else:
    #                     return ''
    #             self.temp_num_filter += input_to_check
    #             return input_to_check
    #     return ''

    # Uploads all kind of Data Methods - Session / Workout

    # input floating number and returns 6 digits only 2 decimal point accuracy
    # def length_filter(self, number_input):
    #
    #     number_input = round(number_input, 2)
    #     number_input = str(number_input)
    #
    #     if len(number_input) > 5:
    #         number_input = number_input[:6]
    #         if number_input[-1] == '.':
    #             number_input = number_input[:-1]
    #
    #     return float(number_input)


MainApp().run()
