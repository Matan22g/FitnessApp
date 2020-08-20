import json
from datetime import datetime

import certifi
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.behaviors import TouchBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRoundFlatIconButton, MDIconButton
from kivymd.uix.card import MDCardSwipe, MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
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


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''Custom right container.'''


class AddExerciseContent(BoxLayout):
    pass


class MDCard_Custom(MDCard, TouchBehavior):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_long_touch(self, *args):
        print(3)
        self.app.root.ids['sessionscreen'].show_checkbox(True)


class MDLabel_custom(MDLabel, ButtonBehavior):
    def on_release(self):
        self.app.root.ids['sessionscreen'].show_example_date_picker()


class SessionScreen(Screen):
    workout = []
    ex_reference_by_id = {}
    ex_reference_by_exc = {}
    session_rec = {}  # dic: key is exc, value, list of sets
    workout_name = ""
    workout_key = 0
    num_of_split = 0  # problem between sessions
    dialog = None  # for presenting dialog to user.
    num_to_del = 0
    session_date = 0
    ex_reference_by_checkBox = {}

    # long_press = 0

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"

    # def on_pre_enter(self, *args):
    #     self.app.title = "Session"
    #     print(self.workout_name)
    #     # First visit: setting date to today's date, and loading all exc to the list.
    #     self.switch_delete_can("show_checkbox")
    #     if self.app.new_session == 1:
    #         self.app.new_session = 0
    #         now = datetime.now()
    #         now = now.strftime("%d/%m/%Y %H:%M:%S")
    #         self.ids["date_picker_label"].text = now[0:10]
    #         self.ids["workout_name"].text = self.workout_name
    #         self.session_date = now
    #         for exc in self.workout:
    #             self.add_exc_to_list(exc)  # Loads the screen with the exc
    #     for exc_id in self.ex_reference_by_id:
    #         exc_id.children[0].children[0].opacity = 0

    def on_pre_enter(self, *args):
        self.app.root.ids['toolbar'].right_action_items = [['content-save', lambda x: self.save_session()]]

        self.app.title = "Session"
        print(self.session_rec)
        # First visit: setting date to today's date, and loading all exc to the list.
        self.show_checkbox(False)
        if self.app.new_session == 1:
            self.app.new_session = 0
            now = datetime.now()
            now = now.strftime("%d/%m/%Y %H:%M:%S")
            self.ids["date_picker_label"].text = now[0:10]
            self.ids["date_picker_label"].line_color = [0, 0, 0, 0]
            self.ids["workout_name"].text = self.workout_name
            self.session_date = now
        # for exc_id in self.ex_reference_by_id:
        #     exc_id.children[0].children[0].opacity = 0
        self.load_session()

    def load_session(self):
        num_of_exc_total = len(self.workout)
        dict_of_row_height = {}
        layout = self.ids.exc_cards
        layout.clear_widgets()
        for i, exc in enumerate(self.workout):
            dict_of_row_height[i] = 175
            if exc in self.session_rec:
                row_enlarger = 50 * len(self.session_rec[exc])
                dict_of_row_height[i] += row_enlarger
        self.ids.exc_cards.rows_minimum = dict_of_row_height
        print(dict_of_row_height)
        for num_of_exc, exc in enumerate(self.workout):
            name_layout = MDGridLayout(size_hint_y=0.1, rows=1, cols=2)
            newlayout = MDFloatLayout()  # for centering
            if exc in self.session_rec:
                set_amount = len(self.session_rec[exc])
            else:
                set_amount = 0
            # card_y_size = 200
            # card_y_size = str(card_y_size + set_amount * 50) + "dp"
            self.ids.exc_cards.row_default_height += set_amount * 50

            excCard = MDCard_Custom(
                spacing=5,
                radius=[14],
                orientation="vertical",
                size_hint=(0.9, 0.9),
                padding="12dp",
                pos_hint={"center_y": 0.5, "center_x": 0.5}
            )
            help_layout = MDFloatLayout(size_hint_y=0.05)
            excnum = str(num_of_exc + 1) + " of " + str(num_of_exc_total)
            exc_num = MDLabel(
                text=excnum,
                font_style="Caption",
                size_hint=(None, 0.1),
                theme_text_color="Secondary",
                pos_hint={"center_y": 0.85, "center_x": 0.17}
            )
            deleteBox = MDCheckbox(
                pos_hint={"center_y": 0.85, "center_x": 0.9275},
                on_release=self.choose_mode

            )
            self.ex_reference_by_checkBox[deleteBox] = exc
            help_layout.add_widget(exc_num)
            help_layout.add_widget(deleteBox)
            excCard.add_widget(help_layout)
            exc_name = MDLabel(
                text=exc,
                font_style="H5",
                size_hint=(1, 0.1),
                theme_text_color="Custom",
                text_color=self.app.theme_cls.primary_color
            )

            sButton = MDIconButton(
                icon="history",
                user_font_size="25sp",
                theme_text_color="Custom",
                text_color=self.app.theme_cls.primary_color,
                on_release=self.test
            )
            name_layout.add_widget(exc_name)
            name_layout.add_widget(sButton)

            excCard.add_widget(name_layout)

            # session = ["3   X   8", "3   X   8", "3   X   8", "3   X   8"]
            session = []
            if exc in self.session_rec:
                session = self.session_rec[exc]
            for num_of_set, set in enumerate(reversed(session)):
                exc_layout = MDGridLayout(rows=1, cols=2, size_hint_y=0.08)
                units_layout = MDGridLayout(rows=1, cols=1, size_hint_y=0.1)
                num_of_set = "SET " + str(num_of_set + 1)
                units_pos = 1
                set = self.str_to_set(set)
                # units_pos -= space_to_add/10
                reps = set.split()
                reps = reps[0]
                if len(reps) > 1:
                    units_pos = 0.9
                set_label = MDLabel(
                    text=num_of_set,
                    font_style="H6",
                    size_hint=(units_pos, None),
                    theme_text_color="Custom",
                    text_color=self.app.theme_cls.primary_color
                )
                set_number = MDLabel(
                    text=set,
                    font_style="H5",
                    size_hint=(1, None),
                    theme_text_color="Custom",
                    text_color=self.app.theme_cls.primary_color
                )
                reps_label = MDLabel(
                    text="                                                Reps                  Kg",
                    font_style="Caption",
                    size_hint=(1, None),
                    theme_text_color="Secondary"
                )

                exc_layout.add_widget(set_label)
                exc_layout.add_widget(set_number)
                units_layout.add_widget(reps_label)

                excCard.add_widget(exc_layout)
                excCard.add_widget(units_layout)

            startButton = MDIconButton(
                icon="arrow-right-drop-circle-outline",
                user_font_size="45sp",
                theme_text_color="Custom",
                text_color=self.app.theme_cls.primary_color,
                on_release=self.start_exc
            )
            buttonlayout = MDBoxLayout(
                size_hint_y=0.4,
                orientation='horizontal',
                spacing=20
            )
            buttonlayout.add_widget(startButton)
            self.ex_reference_by_id[startButton] = exc

            excCard.add_widget(buttonlayout)
            # For fast deletion
            self.ex_reference_by_exc[exc] = excCard

            newlayout.add_widget(excCard)
            layout.add_widget(newlayout)
        self.show_checkbox(False)

    def choose_mode(self, *args):
        # shows num of rows selected
        num_to_del = 0
        for checkbox in SessionScreen.ex_reference_by_checkBox:
            if checkbox.active:
                num_to_del += 1
        self.app.root.ids['sessionscreen'].ids["num_to_delete"].text = str(num_to_del)
        self.num_to_del = self.app.root.ids['sessionscreen'].ids["num_to_delete"].text

    def str_to_set(self, set):
        # space_before_x = 4
        # space_after_x = 4
        print(set)

        set = set.split()
        reps_leng = len(set[0])
        weight_leng = len(set[2])

        new_space_before_x = "    "
        if reps_leng - 1 > 0:
            new_space_before_x = new_space_before_x[:-(reps_leng - 1)]

        new_space_after_x = "    "
        if weight_leng - 1 > 0:
            new_space_after_x = new_space_after_x[:-(weight_leng - 1)]

        fixed_set = set[0] + new_space_before_x + "X" + new_space_after_x + set[2]

        print(fixed_set)
        return fixed_set

    def on_enter(self, *args):
        self.fix_grid_heights()

    def fix_grid_heights(self):
        grid = self.ids.exc_cards
        self.ids.exc_cards.height = sum(x.height for x in grid.children)

    def on_leave(self, *args):
        self.show_checkbox(False)

    def test(self, *args):
        print(3)

    def start_exc(self, *args):
        # print(args[0])
        # print(self.ex_reference_by_id)
        # print(self.ex_reference_by_exc)
        # print(self.ex_reference_by_id[args[0]])
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
        num_of_exc = len(self.workout)

        if unfinished_exc == num_of_exc:
            msg = "Come on at least complete one exercise"
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.6, None),
                                   title=msg,
                                   buttons=[
                                       MDFlatButton(
                                           text="OK", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.cancel_save
                                       )
                                   ],
                                   )
        else:
            if unfinished_exc:
                msg = str(unfinished_exc) + " Unfinished exercise, " + msg
                self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.6, None),
                                       title=msg,
                                       buttons=[
                                           MDFlatButton(
                                               text="SAVE", text_color=self.app.theme_cls.primary_color,
                                               on_release=self.upload_session
                                           ),
                                           MDFlatButton(
                                               text="CANCEL", text_color=self.app.theme_cls.primary_color,
                                               on_release=self.cancel_save
                                           )
                                       ],
                                       )
        self.dialog.open()

    def upload_session(self, *args):
        self.app.display_loading_screen()



        date = self.ids["date_picker_label"].text
        date = self.session_date
        for exc in list(self.session_rec):
            if not self.session_rec[exc]:  # if exc is empty (after deletion)
                self.session_rec.pop(exc, None)
        link = "https://gymbuddy2.firebaseio.com/%s/sessions.json?auth=%s" % (self.app.local_id, self.app.id_token)
        session_data = [date, self.app.timer_format, self.workout_key, self.workout_name, self.num_of_split,
                        self.session_rec]
        Workout = "{%s}" % (str(session_data))
        data = json.dumps(Workout)
        req = UrlRequest(link, req_body=data, on_success=self.on_save_success, on_error=self.on_save_error,
                         on_failure=self.on_save_error, ca_file=certifi.where(), verify=True)
        self.app.running_session = 0

    def on_save_success(self, *args):
        self.dialog.dismiss()
        self.app.change_screen1("homescreen")
        Snackbar(text="Session saved!").show()
        self.app.hide_loading_screen()
    def on_save_error(self, *args):
        self.dialog.dismiss()
        print("error session save")
        self.app.hide_loading_screen()
    def cancel_save(self, *args):
        self.dialog.dismiss()

    def show_checkbox(self, to_show):
        self.app.root.ids['sessionscreen'].ids["num_to_delete"].text = ""
        if to_show == "False" or not to_show:
            to_show = 0
        else:
            to_show = 1

        if to_show:
            self.ids["show_checkbox"].opacity = 1
            self.ids["show_checkbox"].disabled = False
        else:
            self.ids["show_checkbox"].opacity = 0
            self.ids["show_checkbox"].disabled = True

        for checkbox_id in self.ex_reference_by_checkBox:
            checkbox_id.active = 0
            if to_show:
                checkbox_id.opacity = 1
            else:
                checkbox_id.opacity = 0

    def delete_selected(self):
        self.show_del_exercise_dialog()

    def show_del_exercise_dialog(self):
        num_to_del = self.app.root.ids['sessionscreen'].ids["num_to_delete"].text
        if num_to_del:
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
        print(self.ex_reference_by_exc)
        for checkbox in list(
                self.ex_reference_by_checkBox):  # force a copy to avoid "dict changed size during iteration"
            if checkbox.active:
                exc = self.ex_reference_by_checkBox[checkbox]
                exc_card_id = self.ex_reference_by_exc[exc]

                self.ids["exc_cards"].remove_widget(exc_card_id)

                # exc = self.ex_reference_by_id.pop(exc_card_id, None)

                self.ex_reference_by_exc.pop(exc, None)
                self.session_rec.pop(exc, None)
                self.workout.remove(exc)
        self.show_checkbox(False)
        self.fix_resize()

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

        # If the user hasnt written any name, dont do nothing.
        if new_exercise:
            self.workout.append(new_exercise)
            self.load_session()
            self.on_enter()
            self.dialog.dismiss()
            self.fix_resize()

            # animation for scrolling to the new exercise
            new_card = self.ex_reference_by_exc[new_exercise]
            self.ids.scroll.scroll_to(new_card, padding=10, animate=True)

    def fix_resize(self):
        # after delete or add exercise, needs to adjust scroll view size
        # current fix is by rentering the page, so the original fix will work
        self.app.change_screen1("workoutsscreen", -2)
        self.app.change_screen1("sessionscreen", -3)

    def show_example_date_picker(self, *args):
        MDDatePicker(self.set_previous_date).open()

    def set_previous_date(self, date_obj):
        new_date = date_obj.strftime("%d/%m/%Y")
        self.ids["date_picker_label"].text = new_date
        self.session_date = new_date + " 00:00:00"
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

        if self.ids["weight"].text:
            currWeight = int(self.ids["weight"].text)
        else:
            currWeight = 0

        if self.ids["reps"].text:
            currReps = int(self.ids["reps"].text)
        else:
            currReps = 0

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
            for set in reversed(sets):
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
            SwipeToDeleteItem(text=f"{currReps}    X    {currWeight}")
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
        # sets_list_str = ', '.join(sets_list)
        # SessionScreen.ex_reference_by_exc[exc].tertiary_text = "Done: " + sets_list_str

    def clear_screen(self):
        self.ids["md_list"].clear_widgets()
        self.ids["weight"].text = "0"
        self.ids["reps"].text = "0"

    def remove_set(self, instance):
        self.ids["md_list"].remove_widget(instance)
