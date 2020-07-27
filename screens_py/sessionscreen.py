import json

import certifi
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, ThreeLineListItem
from kivymd.uix.snackbar import Snackbar


class SwipeToDeleteItem(MDCardSwipe):
    text = StringProperty()


class SessionScreen(Screen):
    workout = []
    ex_reference_by_id = {}
    ex_reference_by_exc = {}
    session_rec = {}
    workout_key = 0
    num_of_split = 0 # problem between sessions
    dialog = 0  # for presenting dialog to user.

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"

    def on_pre_enter(self, *args):
        self.app.title = "Home"
        # First visit:
        if self.app.new_session == 1:
            for exc in self.workout:
                self.ids["container"].add_widget(
                    ThreeLineListItem(
                        text=exc,
                        secondary_text="Personal Best: ",
                        tertiary_text="Done: ",
                        on_release=self.start_exc
                    ))
                # saving dic with the widget id to be able to ref to them later
                ex_widget_id = self.ids["container"].children[0]
                self.ex_reference_by_id[ex_widget_id] = exc
                self.ex_reference_by_exc[exc] = ex_widget_id
            self.app.new_session = 0
            print(self.num_of_split)

    def start_exc(self, *args):
        ExerciseScreen.exercise = self.ex_reference_by_id[args[0]]
        self.app.change_screen1("exercisescreen")

    def save_session(self):
        date = 5
        num_of_exc = 0
        unfinished_exc = 0
        msg = "Save your workout?"

        for session in self.session_rec:
            num_of_exc += 1
            if not self.session_rec[session]:
                unfinished_exc += 1
        if unfinished_exc:
            msg = "only " + str(num_of_exc - unfinished_exc) + "/" + str(num_of_exc) + " Completed, " + msg

        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.6, None),
                               text=msg,
                               buttons=[
                                   MDFlatButton(
                                       text="Save", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.upload_session
                                   ),
                                   MDFlatButton(
                                       text="Cancel", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.cancel_save
                                   )
                               ],
                               )
        self.dialog.open()

    def upload_session(self, *args):

        link = "https://gymbuddy2.firebaseio.com/%s/sessions.json?auth=%s" % (self.app.local_id, self.app.id_token)
        Workout = "{%s: %s: %s}" % (
            '"' + str(self.workout_key) + '"', '"' + str(self.num_of_split) + '"', '"' + str(self.session_rec) + '"')
        data = json.dumps(Workout)
        req = UrlRequest(link, req_body=data,
                         ca_file=certifi.where(), verify=True)
        self.dialog.dismiss()
        self.app.change_screen1("homescreen")
        Snackbar(text="workout saved!").show()

    def cancel_save(self, *args):
        self.dialog.dismiss()
    ###### FIX NEW SESSION


class ExerciseScreen(Screen):
    exercise = "TEST EXC"
    repScale = 1
    weightScale = 5

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"

    def changeInput(self, toScale, increase):
        currWeight = int(self.ids["weight"].text)
        currReps = int(self.ids["reps"].text)

        if toScale == 'w':
            if increase == 1:
                self.ids["weight"].text = str(currWeight + self.weightScale)
            else:
                if (currWeight - self.weightScale) > 0:
                    self.ids["weight"].text = str(currWeight - self.weightScale)
                else:
                    self.ids["weight"].text = "0"

        if toScale == 'r':
            if increase == 1:
                self.ids["reps"].text = str(currReps + self.repScale)
            else:
                if (currReps - self.repScale) > 0:
                    self.ids["reps"].text = str(currReps - self.repScale)
                else:
                    self.ids["reps"].text = "0"

    def on_pre_enter(self, *args):
        self.app.title = "Home"
        exc = self.exercise
        self.ids["ex_name"].text = exc

        if exc in SessionScreen.session_rec:
            sets = SessionScreen.session_rec[exc]
            for set in sets:
                self.ids["md_list"].add_widget(
                    SwipeToDeleteItem(text=f"{set}")
                )
            if sets:
                set = set.split()
                self.ids["reps"].text = set[0]
                self.ids["weight"].text = set[2]

        else:
            SessionScreen.session_rec[exc] = []

    def on_leave(self, *args):
        self.clear_screen()

    def add_set(self):
        currWeight = int(self.ids["weight"].text)
        currReps = int(self.ids["reps"].text)
        self.ids["md_list"].add_widget(
            SwipeToDeleteItem(text=f"{currWeight} X {currReps}")
        )

    def save_exc(self):
        exc = self.ids["ex_name"].text
        sets_list = []
        SessionScreen.session_rec[exc] = sets_list
        for child in self.ids["md_list"].children:
            set = child.text
            sets_list.append(set)
        SessionScreen.session_rec[exc] = sets_list
        print(SessionScreen.session_rec[exc])
        print(SessionScreen.session_rec)
        self.app.change_screen1("sessionscreen", -1, "right")
        sets_list_str = ', '.join(sets_list)
        SessionScreen.ex_reference_by_exc[exc].tertiary_text = "Done: " + sets_list_str

    def clear_screen(self):
        self.ids["md_list"].clear_widgets()
        self.ids["weight"].text = "0"
        self.ids["reps"].text = "0"

    def remove_set(self, instance):
        self.ids["md_list"].remove_widget(instance)
