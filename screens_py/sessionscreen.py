import json

import certifi
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.behaviors import TouchBehavior
from kivymd.uix.button import MDFlatButton, MDRoundFlatIconButton
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, ThreeLineListItem, OneLineAvatarIconListItem, IRightBodyTouch, \
    ThreeLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.picker import MDDatePicker


class SwipeToDeleteItem(MDCardSwipe):
    text = StringProperty()


class ListItemWithCheckbox(ThreeLineAvatarIconListItem, TouchBehavior):
    '''Custom list item.'''
    # override the left icon attribute, adjust text dist from left border.
    _txt_left_pad = NumericProperty("16dp")
    icon = StringProperty("android")

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    # def on_long_touch(self, *args):
    #     self.app.root.ids['sessionscreen'].show_checkbox(True)
    #     self.app.root.ids['sessionscreen'].long_press=1

    def choose_mode(self):
        # On checkbox press, switch can and shows num of rows selected

        self.app.root.ids['sessionscreen'].switch_delete_can("delete_selected")

        if self.app.root.ids['sessionscreen'].ids["num_to_delete"].text:
            num_to_del = int(self.app.root.ids['sessionscreen'].ids["num_to_delete"].text)
        else:
            num_to_del = 0
        checkbox = self.children[0].children[0]
        if checkbox.active:
            self.app.root.ids['sessionscreen'].ids["num_to_delete"].text = str(num_to_del + 1)
        else:
            self.app.root.ids['sessionscreen'].ids["num_to_delete"].text = str(num_to_del - 1)
        SessionScreen.num_to_del = self.app.root.ids['sessionscreen'].ids["num_to_delete"].text


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''Custom right container.'''


class AddExerciseContent(BoxLayout):
    pass


class SessionScreen(Screen):
    workout = []
    ex_reference_by_id = {}
    ex_reference_by_exc = {}
    session_rec = {}  # dic: key is exc, value, list of sets
    workout_key = 0
    num_of_split = 0  # problem between sessions
    dialog = None  # for presenting dialog to user.
    num_to_del = 0

    # long_press = 0

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"

    def switch_delete_can(self, to_active):
        if to_active == "show_checkbox":
            self.show_checkbox(False)
            self.app.root.ids['sessionscreen'].ids["num_to_delete"].text = ""
            self.ids["delete_selected"].opacity = 0
            self.ids["delete_selected"].disabled = True
            self.ids["show_checkbox"].opacity = 1
            self.ids["show_checkbox"].disabled = False

        if to_active == "delete_selected":
            self.ids["delete_selected"].opacity = 1
            self.ids["delete_selected"].disabled = False
            self.ids["show_checkbox"].opacity = 0
            self.ids["show_checkbox"].disabled = True

    def on_pre_enter(self, *args):
        self.app.title = "Session"

        # First visit: setting date to todays date, and loading all exc to the list.
        self.switch_delete_can("show_checkbox")
        if self.app.new_session == 1:
            self.app.new_session = 0
            self.ids["date_picker_label"].text = "Date: " + str(MDDatePicker.today)
            for exc in self.workout:
                self.add_exc_to_list(exc)  # Loads the screen with the exc
        for exc_id in self.ex_reference_by_id:
            exc_id.children[0].children[0].opacity = 0

    def on_leave(self, *args):
        self.show_checkbox(False)

    def add_exc_to_list(self, exc):
        self.ids["container"].add_widget(
            ListItemWithCheckbox(
                text=exc,
                secondary_text="Personal Best: ",
                tertiary_text="Done: ",
                on_press=self.start_exc
            ))
        # saving dic with the widget id to be able to ref to them later
        ex_widget_id = self.ids["container"].children[0]
        self.ex_reference_by_id[ex_widget_id] = exc
        self.ex_reference_by_exc[exc] = ex_widget_id

    def start_exc(self, *args):
        print (self.ex_reference_by_id)
        print (self.ex_reference_by_exc)

        ExerciseScreen.exercise = self.ex_reference_by_id[args[0]]
        self.app.change_screen1("exercisescreen")

    def save_session(self):

        unfinished_exc = 0
        msg = "Save your workout?"

        # Find if the user hasn't completed his workout
        for exc in self.workout:

            if exc not in self.session_rec:
                unfinished_exc += 1
            elif not self.session_rec[exc]:
                unfinished_exc += 1

        if unfinished_exc:
            msg = str(unfinished_exc) + " Unfinished exercise, " + msg

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
        date = self.ids["date_picker_label"].text
        date = date[6:]
        for exc in list(self.session_rec):
            if not self.session_rec[exc]:  # if exc is empty (after deletion)
                self.session_rec.pop(exc, None)
        link = "https://gymbuddy2.firebaseio.com/%s/sessions.json?auth=%s" % (self.app.local_id, self.app.id_token)
        Workout = "{%s: %s: %s: %s}" % (
            '"' + date + '"', '"' + str(self.workout_key) + '"', '"' + str(self.num_of_split) + '"',
            '"' + str(self.session_rec) + '"')
        data = json.dumps(Workout)
        req = UrlRequest(link, req_body=data, on_success=self.on_save_success, on_error=self.on_save_error,
                         on_failure=self.on_save_error, ca_file=certifi.where(), verify=True)

    def on_save_success(self, *args):
        self.dialog.dismiss()
        self.app.change_screen1("homescreen")
        Snackbar(text="Session saved!").show()

    def on_save_error(self, *args):
        self.dialog.dismiss()
        print("error session save")

    def cancel_save(self, *args):
        self.dialog.dismiss()

    def show_checkbox(self, to_Show):
        for exc_id in self.ex_reference_by_id:
            exc_id.children[0].children[0].active = 0
            if to_Show:
                exc_id.children[0].children[0].opacity = 1
            else:
                exc_id.children[0].children[0].opacity = 0

            # self.ids["show_checkbox"].opacity = 0
            # self.ids["delete_selected"].opacity = 1
            # turn on checkbox

    def delete_selected(self):
        self.show_del_exercise_dialog()

    def show_del_exercise_dialog(self):
        num_to_del = self.app.root.ids['sessionscreen'].ids["num_to_delete"].text
        if int(num_to_del):
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.7, None),
                                   title="Delete " + num_to_del + " Exercise?",
                                   buttons=[
                                       MDFlatButton(
                                           text="DELETE", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.del_exc
                                       ),
                                       MDFlatButton(
                                           text="CANCEL", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.cancel_del_exc
                                       )
                                   ],
                                   )
        else:
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.7, None),
                                   text="Select exercise to delete",
                                   buttons=[
                                       MDFlatButton(
                                           text="Ok", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.cancel_del_exc
                                       )
                                   ],
                                   )
        self.dialog.open()

    def del_exc(self, *args):
        self.dialog.dismiss()
        exc_to_del = []
        for exc_id in list(self.ex_reference_by_id):  # force a copy to avoid "dict changed size during iteration"
            if exc_id.children[0].children[0].active == True:
                self.ids["container"].remove_widget(exc_id)

                exc = self.ex_reference_by_id.pop(exc_id, None)
                self.ex_reference_by_exc.pop(exc, None)
                self.session_rec.pop(exc, None)
                self.workout.remove(exc)
        self.switch_delete_can("show_checkbox")

    def cancel_del_exc(self, caller):
        self.dialog.dismiss()

    def show_add_exercise_dialog(self):
        self.dialog = MDDialog(
            radius=[10, 7, 10, 7],
            size_hint=(0.8, None),
            title="New Exercise:",
            type="custom",
            content_cls=AddExerciseContent(),
            buttons=[

                MDFlatButton(
                    text="OK",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=self.add_exercise
                ),
            ],
        )
        self.dialog.open()

    def add_exercise(self, *args):
        new_exercise = args[0].parent.parent.parent.children[2].children[0].children[0].text
        if new_exercise:
            self.add_exc_to_list(new_exercise)
            self.workout.append(new_exercise)
            self.dialog.dismiss()

    def show_example_date_picker(self, *args):
        MDDatePicker(self.set_previous_date).open()

    def set_previous_date(self, date_obj):
        self.ids["date_picker_label"].text = "Date: " + str(date_obj)
        print(self.ids["date_picker_label"].text)


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

        # if already completed a few sets in this session:
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

        self.app.change_screen1("sessionscreen", -1, "right")
        sets_list_str = ', '.join(sets_list)
        SessionScreen.ex_reference_by_exc[exc].tertiary_text = "Done: " + sets_list_str

    def clear_screen(self):
        self.ids["md_list"].clear_widgets()
        self.ids["weight"].text = "0"
        self.ids["reps"].text = "0"

    def remove_set(self, instance):
        self.ids["md_list"].remove_widget(instance)
