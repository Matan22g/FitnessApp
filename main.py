import ast
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

Window.size = (360, 639)

### screens classes import

from screens_py.create_workout_screen import Create_Workout_Screen, SplitScreensMain, SplitScreen, SplitScreen2, \
    SplitScreen3
from screens_py.homescreen import HomeScreen
from screens_py.settingsscreen import SettingsScreen
from screens_py.workoutsscreen import WorkoutsScreen
from screens_py.sessionscreen import SessionScreen, ExerciseScreen


class FriendsScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_enter(self, *args):
        self.app.title = "Friends"


class MainApp(MDApp):
    mainscreens = ["homescreen", "workoutscreen", "friendsscreen", "settingsscreen"]
    id_token = ""
    local_id = ""
    user_data = []
    workouts = {}  # straight from database
    workoutsParsed = {}  # analyze to list
    friends_list = {}  # will have all usernames of the users friends.
    dialog = ""  # for presenting dialog to user.
    workout_to_delete = 0  # saving the workout obj between function.
    toTrainWorkout = 0
    lastscreens = []
    new_session = 0
    debug = 1

    def __init__(self, **kwargs):
        self.title = "FitnessApp"
        self.theme_cls.primary_palette = "Indigo"
        super().__init__(**kwargs)

    def on_start(self):
        # before login, denies access to navigation drawer
        self.root.ids['nav_drawer'].swipe_edge_width = -2

    def on_login(self):
        # loads data
        self.change_screen1("homescreen")
        self.load_workout_data()  # ALSO LOADS USER DATA
        self.root.ids['toolbar'].left_action_items = [["settings", lambda x: self.change_screen1("settingsscreen")]]
        # TEST OF USER NAME
        user_name = self.user_data["real_user_name"]
        self.root.ids['toolbar'].title = "Hello " + user_name
        # self.get_user_name_data(user_name)
        ### debug:
        if self.debug == 1:
            self.toTrainWorkout = "-M9NjJ45dRBIxqEQ40LC"
            self.chose_split(1)

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

    # back button
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
        if self.debug:
            print(self.lastscreens)
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

        self.workoutsParsed = self.parse_workout(
            self.workouts)  # Need to reconsider this depending, on workout anylysis.
        self.add_workouts(self.workoutsParsed)

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

                cardsizey = self.root.height / 3.75
                if lines > 1:  # adjusting card size according to splitsnum - how many splits there are
                    cardsizey = str(cardsizey + (12.8 * lines))
                cardsizex = str(self.root.width - 20) + "dp"
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
                    on_release=self.start_workout
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

    def start_workout(self, *args):
        # start new session of workout

        workoutkey = args[0].parent.children[3].text
        workoutlist = list(self.workoutsParsed[workoutkey].values())
        num_splits = len(workoutlist[0])

        # saving the workout key to be use as identifier.
        self.toTrainWorkout = workoutkey

        if num_splits == 1:
            self.chose_split(-1)
            return
        if num_splits == 2:
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.6, None),
                                   title="Choose Split",
                                   buttons=[
                                       MDFlatButton(
                                           text="Split 1", text_color=self.theme_cls.primary_color,
                                           on_release=self.chose_one_split
                                       ),
                                       MDFlatButton(
                                           text="Split 2", text_color=self.theme_cls.primary_color,
                                           on_release=self.chose_second_split
                                       )
                                   ],
                                   )
        if num_splits == 3:
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.8, None),
                                   text="Choose Split",
                                   buttons=[
                                       MDFlatButton(
                                           text="Split 1", text_color=self.theme_cls.primary_color,
                                           on_release=self.chose_one_split
                                       ),
                                       MDFlatButton(
                                           text="Split 2", text_color=self.theme_cls.primary_color,
                                           on_release=self.chose_second_split
                                       ),
                                       MDFlatButton(
                                           text="Split 3", text_color=self.theme_cls.primary_color,
                                           on_release=self.chose_third_split
                                       )
                                   ],
                                   )
        if num_splits == 4:
            pass
        self.dialog.open()

    def chose_split(self, split_chosen):
        #loading workout from the workout dic using saved key

        workout_list = list(self.workoutsParsed[self.toTrainWorkout].values())
        chosen_workout = workout_list[0]
        # getting the id of where the widgets are coming in
        session_grid = self.root.ids['sessionscreen'].ids[
            'container']
        session_grid.clear_widgets()

        # in case of only one split program no need for popup screen
        if split_chosen != -1:
            if self.debug == 0:
                self.dialog.dismiss()
        else:
            split_chosen = 1

        SessionScreen.workout = chosen_workout[split_chosen - 1]
        SessionScreen.workout_key = self.toTrainWorkout
        SessionScreen.num_of_split = split_chosen
        SessionScreen.ex_reference_by_id = {}
        SessionScreen.ex_reference_by_exc = {}
        SessionScreen.session_rec = {}

        self.new_session = 1
        print("split_chosen", split_chosen)
        self.change_screen1("sessionscreen")

    def chose_one_split(self, *args):
        self.chose_split(1)

    def chose_second_split(self, *args):
        self.chose_split(2)

    def chose_third_split(self, *args):
        self.chose_split(2)

    def chose_fourth_split(self, *args):
        self.chose_split(3)

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
        print(args)
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

    def get_user_data(self):
        try:
            result = requests.get("https://gymbuddy2.firebaseio.com/" + self.local_id + ".json?auth=" + self.id_token)
            data = json.loads(result.content.decode())
            self.user_data = data
            if self.debug:
                print(data)
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
