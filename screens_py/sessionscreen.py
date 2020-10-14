import json
from datetime import datetime

import certifi
from kivy.core.window import Window
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.behaviors import TouchBehavior
# from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.textfield import MDTextField

from customKv.toggle_behavior import MDToggleButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRoundFlatIconButton, MDIconButton, MDRectangleFlatButton, \
    MDFloatingActionButton
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
        self.app.root.ids['sessionscreen'].show_checkbox(True)


class SessionScreen(Screen):
    inc = 0.05
    workout = []
    ex_reference_by_id = {}
    ex_reference_by_exc = {}
    session_rec = {}  # dic: key is exc, value, list of sets
    session_rec_to_view = {}
    workout_name = ""
    workout_key = 0
    num_of_split = 0  # problem between sessions
    dialog = None  # for presenting dialog to user.
    num_to_del = 0
    session_date = 0
    ex_reference_by_checkBox = {}
    view_mode = 0
    # long_press = 0
    session_key = 0
    check_box_by_card = {}
    exc_limit = 15

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
    # def on_pre_leave(self, *args):
    #     self.app.clear_canvas()
    #     self.app.add_top_canvas()

    def on_pre_enter(self, *args):

        if self.app.debug:
            print("entering session page")
            print("session screen, view mode:", self.view_mode)
            print("session workout", self.workout)
        self.app.title = "Session"
        self.app.root.ids['toolbar'].right_action_items = [['', lambda x: None]]

        if not self.view_mode:
            self.app.add_bottom_canvas()

            # self.app.root.ids['toolbar'].right_action_items = [['content-save', lambda x: self.save_session()]]

            # First visit: setting date to today's date, and loading all exc to the list.
            self.show_checkbox(False)
            if self.app.new_session == 1:
                self.app.new_session = 0
                now = datetime.now()
                now = now.strftime("%d/%m/%Y %H:%M:%S")
                self.ids["date_picker_label"].text = now[0:10]
                self.ids["date_picker_label"].line_color = [0, 0, 0, 0]
                self.ids["workout_name"].text = self.workout_name
                inc = (len(self.workout_name.split()) - 1) * 0.025
                self.ids["workout_name"].pos_hint = {"center_x": 0.3, "top": .935 + self.inc + inc}
                if len(self.workout_name) < 5:
                    self.ids["workout_name"].font_size = "40sp"
                else:
                    self.ids["workout_name"].font_size = "35sp"
                self.session_date = now
                self.session_rec = {}
            # for exc_id in self.ex_reference_by_id:
            #     exc_id.children[0].children[0].opacity = 0
            self.load_session()
            self.hide_edit_buttons(False)
            # self.app.change_title(session.workout_name)
            self.app.change_title("Running Session")

        else:
            print(self.app.sessions)
            print(self.session_key)

            session = self.app.sessions[self.session_key]
            session_workout = list(session.exercises.keys())
            session_sets_dict = session.exercises

            self.workout = session_workout
            self.session_rec_to_view = session_sets_dict
            session_duration = session.duration
            session_date = session.date
            if self.app.debug:
                print("session workout", self.workout)
                print("session.exercises", session.exercises)
                print("self.session_key", self.session_key)
                print(" self.app.sessions[self.session_key]", self.app.sessions[self.session_key])

            self.ids["timer_view"].text = session_duration

            # self.ids["date_view"].text = str(session_date)[0:10]
            self.ids["date_view"].text = session_date.strftime("%d/%m/%Y")
            self.load_session()
            self.hide_edit_buttons(True)
            # self.app.change_title(session.workout_name)
            self.app.change_title("Recent Workout")
            self.ids["workout_name"].text = session.workout_name
            inc = (len(session.workout_name.split()) - 1) * 0.025
            self.ids["workout_name"].pos_hint = {"center_x": 0.3, "top": .935 + self.inc + inc}
            if len(session.workout_name) < 5:
                self.ids["workout_name"].font_size = "40sp"
            else:
                self.ids["workout_name"].font_size = "35sp"

            self.show_checkbox(False)
            if self.app.reload_for_running_session:
                self.app.root.ids['toolbar'].right_action_items = [
                    ['', lambda x: None]]

    def hide_edit_buttons(self, to_hide):
        if to_hide:
            self.ids["control_grid"].opacity = 0
            self.ids["control_grid"].disabled = True

            self.ids["timer"].opacity = 0
            self.ids["timer_view"].opacity = 1

            self.ids["scroll"].size_hint_y = 0.87

            self.ids["date_view"].opacity = 1
            self.ids["date_icon"].opacity = 1

        else:
            self.ids["control_grid"].opacity = 1
            self.ids["control_grid"].disabled = False

            self.ids["timer"].opacity = 1
            self.ids["timer_view"].opacity = 0
            self.ids["scroll"].size_hint_y = 0.745 + self.app.bottom_buttons_inc

            self.ids["date_view"].opacity = 0
            self.ids["date_icon"].opacity = 0

    def load_session(self):
        if self.app.debug:
            print("loading session:")
        if self.view_mode:
            session_rec = self.session_rec_to_view
        else:
            session_rec = self.session_rec

        num_of_exc_total = len(self.workout)
        dict_of_row_height = {}
        layout = self.ids.exc_cards
        layout.clear_widgets()
        print("Window.size", Window.size)
        window_height = Window.size[1]
        row_height = Window.size[1] / 4
        row_height_view = Window.size[1] / 7
        row_enlarger_inc = Window.size[1] / 15
        for i, exc in enumerate(self.workout):
            if not self.view_mode:
                dict_of_row_height[i] = row_height
            else:
                dict_of_row_height[i] = row_height_view

            if exc in session_rec:
                row_enlarger = row_enlarger_inc * len(session_rec[exc])
                dict_of_row_height[i] += row_enlarger
        self.ids.exc_cards.rows_minimum = dict_of_row_height
        self.check_box_by_card = {}

        # print(dict_of_row_height)
        for num_of_exc, exc in enumerate(self.workout):
            new_card_layout = self.create_card(num_of_exc, exc, num_of_exc_total)
            layout.add_widget(new_card_layout)

        self.show_checkbox(False)

    def active_card_check_box(self, *args):
        try:
            check_box = self.check_box_by_card[args[0]]
            check_box_state = check_box.active
            check_box.active = not check_box_state
        except KeyError:
            check_box = args[0]

        self.update_delete_num('sessionscreen', self.ex_reference_by_checkBox)

    def create_card(self, num_of_exc, exc, num_of_exc_total):
        if self.view_mode:
            session_rec = self.session_rec_to_view
        else:
            session_rec = self.session_rec

        newlayout = MDFloatLayout()  # for centering
        if exc in session_rec:
            set_amount = len(session_rec[exc])
        else:
            set_amount = 0
        # card_y_size = 200
        # card_y_size = str(card_y_size + set_amount * 50) + "dp"
        self.ids.exc_cards.row_default_height += set_amount * 175

        if not self.view_mode:
            excCard = MDCard_Custom(
                spacing=5,
                radius=[80],
                orientation="vertical",
                size_hint=(0.9, 0.85),
                padding=[25, 25, 0, 20],  # [padding_left, padding_top,padding_right, padding_bottom].
                pos_hint={"center_y": 0.5, "center_x": 0.5},
                background="resources/card_back.png",
                on_release=self.active_card_check_box,
                elevation=1,

            )
        else:
            excCard = MDCard(
                spacing=5,
                radius=[80],
                orientation="vertical",
                size_hint=(0.9, 0.85),
                padding=[25, 25, 0, 45],  # [padding_left, padding_top,padding_right, padding_bottom].
                pos_hint={"center_y": 0.5, "center_x": 0.5},
                background="resources/card_back.png",
                elevation=1,
            )

        help_layout, check_box = self.create_top_card_layout(num_of_exc, num_of_exc_total, exc)
        self.check_box_by_card[excCard] = check_box

        excCard.add_widget(help_layout)

        name_layout_y_size = 2.5
        if self.view_mode:
            name_layout_y_size = 2
        name_layout = MDGridLayout(size_hint_y=name_layout_y_size, rows=1, cols=1)

        exc_name = MDLabel(
            text=exc,
            font_style="H5",
            theme_text_color="Custom",
            text_color=self.app.text_color
        )
        name_layout.add_widget(exc_name)
        excCard.add_widget(name_layout)

        # session = ["3   X   8", "3   X   8", "3   X   8", "3   X   8"]
        session = []
        if exc in session_rec:
            session = session_rec[exc]
        for num_of_set, set in enumerate(session):
            exc_layout = MDGridLayout(rows=1, cols=2)
            units_layout = MDGridLayout(rows=1, cols=2)
            if self.view_mode:
                exc_layout = MDGridLayout(rows=1, cols=2)
                units_layout = MDGridLayout(rows=1, cols=2)

            set_label, set_number, reps_label = self.create_set_label(set, num_of_set)
            exc_layout.add_widget(set_label)
            exc_layout.add_widget(set_number)
            units_layout.add_widget(MDLabel(text="", size_hint_x=0.9))
            units_layout.add_widget(reps_label)
            excCard.add_widget(exc_layout)
            excCard.add_widget(units_layout)
            # new_exc_layout, new_units_layout = self.create_set_label(set, num_of_set)
            # excCard.add_widget(new_exc_layout)
            # excCard.add_widget(new_units_layout)
        if not self.view_mode:
            button_layout = self.create_button_layout(exc)
            excCard.add_widget(button_layout)
        # For fast deletion
        self.ex_reference_by_exc[exc] = excCard
        newlayout.add_widget(excCard)
        return newlayout

    def create_top_card_layout(self, num_of_exc, num_of_exc_total, exc):
        help_layout = MDGridLayout(rows=1, cols=2)
        excnum = str(num_of_exc + 1) + " of " + str(num_of_exc_total)
        exc_num = MDLabel(
            text=excnum,
            font_style="Caption",
            theme_text_color="Secondary",
            pos_hint={"center_y": 0.85, "center_x": 0.2}
        )
        deleteBox = MDCheckbox(
            pos_hint={"center_y": 0.85, "center_x": 0.9275},
            on_release=self.active_card_check_box
        )
        self.ex_reference_by_checkBox[deleteBox] = exc
        help_layout.add_widget(exc_num)
        help_layout.add_widget(deleteBox)

        return help_layout, deleteBox

    def create_button_layout(self, exc):
        startButton = MDIconButton(
            icon="arrow-right-drop-circle-outline",
            theme_text_color="Custom",
            text_color=self.app.theme_cls.primary_color,
            user_font_size="45sp",
            size_hint=(0.2, 3.5),
            pos_hint={"center_x": 0.5},
            on_release=self.start_exc,
        )
        # startButton = MDFloatingActionButton(
        #     icon="play",
        #     theme_text_color="Custom",
        #     text_color=(1,1,1,1),
        #     md_bg_color= self.app.theme_cls.primary_color,
        #     elevation= 0,
        #     size_hint=(0.15, 2),
        #     user_font_size="35sp",
        #     pos_hint={"center_x": 0.5},
        #     on_release=self.start_exc
        # )

        self.ex_reference_by_id[startButton] = exc
        return startButton

    def create_set_label(self, set, num_of_set):
        # create and return two rows, of set and units

        # exc_layout = MDGridLayout(rows=1, cols=2)
        # units_layout = MDGridLayout(rows=1, cols=1)
        num_of_set = "SET " + str(num_of_set + 1)
        units_pos = 1
        set = self.str_to_set(set)
        # units_pos -= space_to_add/10
        reps = set.split()
        weights = reps[2]

        weights, unit = self.app.fix_weight_by_unit(weights)

        reps = reps[0]
        if len(reps) > 1:
            units_pos = 0.9
        set_label = MDLabel(
            text=num_of_set,
            font_style="H6",
            size_hint=(0.9, None),
            theme_text_color="Custom",
            text_color=self.app.text_color,
        )
        set_number = MDLabel(
            text=set,
            font_style="H5",
            size_hint=(1.5, None),
            theme_text_color="Custom",
            text_color=self.app.text_color,
        )
        curr_screen = self.app.root.ids['screen_manager1'].current
        if curr_screen == "sessionscreen":
            units_space = 1.1
        else:
            units_space = 1.3
        reps_label = MDLabel(
            text="  Reps                        " + unit,
            font_style="Caption",
            size_hint=(1, units_space),
            theme_text_color="Custom",
            text_color=self.app.text_color,
        )
        set_layout = MDGridLayout(rows=1, cols=3)
        set_layout.add_widget(MDLabel(
            text=reps,
            font_style="H6",
            size_hint=(0.6, None),
            theme_text_color="Custom",
            text_color=self.app.text_color,
            halign='center'
        ))
        set_layout.add_widget(MDLabel(
            text="X",
            font_style="H6",
            size_hint=(0.7, None),
            theme_text_color="Custom",
            text_color=self.app.text_color,
            halign='center'
        ))

        # if self.app.units != 'metric':
        #     weights = str(round(float(weights) * self.app.kg_to_pounds, 2))
        # else:
        #     weights = str(round(float(weights), 2))

        set_layout.add_widget(MDLabel(
            text="  " + str(weights),
            font_style="H6",
            size_hint=(1.4, None),
            theme_text_color="Custom",
            text_color=self.app.text_color,
            halign='left'
        ))
        return set_label, set_layout, reps_label

        # exc_layout.add_widget(set_label)
        # exc_layout.add_widget(set_number)
        # units_layout.add_widget(reps_label)
        # return exc_layout, units_layout

    def update_delete_num(self, screen, check_box_list):
        # shows num of rows selected
        num_to_del = 0
        for checkbox in check_box_list:
            if checkbox.active:
                num_to_del += 1
        self.app.root.ids[screen].ids["num_to_delete"].text = str(num_to_del)
        self.num_to_del = self.app.root.ids[screen].ids["num_to_delete"].text

    def str_to_set(self, set):
        # space_before_x = 4
        # space_after_x = 4
        set = set.split()
        reps_leng = len(set[0])
        weight_leng = len(set[2])
        if weight_leng > 3:
            weight_leng = 3
        new_space_before_x = "      "
        if reps_leng - 1 > 0:
            new_space_before_x = new_space_before_x[:-(reps_leng - 1)]

        new_space_after_x = "     "
        if weight_leng - 1 > 0:
            new_space_after_x = new_space_after_x[:-(weight_leng - 1)]
        new_space_before_x = new_space_before_x[:-2]
        fixed_set = set[0] + new_space_before_x + "X" + new_space_after_x + set[2]

        return fixed_set

    def on_enter(self, *args):
        self.fix_grid_heights()

    def fix_grid_heights(self):
        grid = self.ids.exc_cards
        self.ids.exc_cards.height = sum(x.height for x in grid.children)

    def on_leave(self, *args):
        # self.app.root.ids['toolbar'].right_action_items = [
        #     ['menu', lambda x: self.app.root.ids['nav_drawer'].set_state()]]
        if self.app.root.ids['sessionscreen'].view_mode:
            self.app.root.ids['sessionscreen'].view_mode = 0
            if self.app.running_session:
                self.app.root.ids['sessionscreen'].workout = self.app.running_session_workout

    def start_exc(self, *args):
        # print(args[0])
        # print(self.ex_reference_by_id)
        # print(self.ex_reference_by_exc)
        # print(self.ex_reference_by_id[args[0]])
        ExerciseScreen.exercise = self.ex_reference_by_id[args[0]]
        self.app.change_screen1("exercisescreen")

    def valid_session(self):
        unfinished_exc = 0
        # Find if the user hasn't completed his workout
        for exc in self.workout:
            if exc not in self.session_rec:
                unfinished_exc += 1
            elif not self.session_rec[exc]:
                unfinished_exc += 1
        return unfinished_exc

    def save_session(self):
        msg = "Save your workout?"
        text = ""
        unfinished_exc = self.valid_session()
        num_of_exc = len(self.workout)

        if unfinished_exc == num_of_exc:
            msg = "Come on, at least complete one exercise"
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
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
                text = str(unfinished_exc) + " Unfinished exercise"
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
                                   title=msg,
                                   text=text,
                                   buttons=[

                                       MDFlatButton(
                                           text="CANCEL", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.cancel_save
                                       ),
                                       MDFlatButton(
                                           text="SAVE", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.upload_session
                                       ),
                                   ],
                                   )
        self.dialog.open()

    def upload_session(self, *args):
        self.app.display_loading_screen()

        date = self.session_date
        for exc in list(self.session_rec):
            if not self.session_rec[exc]:  # if exc is empty (after deletion)
                self.session_rec.pop(exc, None)
        link = "https://gymbuddy2.firebaseio.com/%s/sessions.json?auth=%s" % (self.app.local_id, self.app.id_token)
        session_data = [date, self.app.timer_format, self.workout_key, self.workout_name, self.num_of_split,
                        self.session_rec]
        Workout = "{%s}" % (str(session_data))
        data = json.dumps(Workout)

        self.app.upload_data(data, link, 3)
        self.dialog.dismiss()

    def cancel_save(self, *args):
        self.dialog.dismiss()

    def show_checkbox(self, to_show):

        # date_label_id = "date_picker_label"
        # date_icon_id = "date_picker_icon"
        self.app.root.ids['sessionscreen'].ids["num_to_delete"].text = ""
        if to_show == "False" or not to_show:
            to_show = 0
        else:
            to_show = 1

        if to_show:
            self.app.delete_mode = 1
            self.ids["num_to_delete"].opacity = 1
            # self.ids[date_label_id].opacity = 0
            # self.ids[date_icon_id].opacity = 0
            # self.ids[date_icon_id].disabled = True
            self.ids["show_checkbox"].opacity = 1
            self.ids["show_checkbox"].disabled = False
        else:
            self.app.delete_mode = 0

            self.ids["num_to_delete"].opacity = 0
            # self.ids[date_label_id].opacity = 1
            # if not self.view_mode:
            #     self.ids[date_icon_id].opacity = 1
            #     self.ids[date_icon_id].disabled = False
            self.ids["show_checkbox"].opacity = 0
            self.ids["show_checkbox"].disabled = True

        for checkbox_id in self.ex_reference_by_checkBox:
            checkbox_id.active = 0
            checkbox_id.selected_color = self.app.theme_cls.primary_color
            if to_show:
                checkbox_id.opacity = 1
            else:
                checkbox_id.opacity = 0

    def delete_selected(self):
        self.show_del_exercise_dialog()

    def show_del_exercise_dialog(self):
        num_to_del = self.app.root.ids['sessionscreen'].ids["num_to_delete"].text
        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
                               title="Select exercise to delete",
                               buttons=[
                                   MDFlatButton(
                                       text="Ok", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.cancel_del_exc
                                   )
                               ],
                               )
        if num_to_del:
            if int(num_to_del):
                msg = "Delete " + num_to_del + " Exercise?"
                warning = ""
                if self.view_mode:
                    warning = "Warning: deleting session record cannot be undone"

                self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
                                       title=msg,
                                       text=warning,
                                       buttons=[

                                           MDFlatButton(
                                               text="CANCEL", text_color=self.app.theme_cls.primary_color,
                                               on_release=self.cancel_del_exc
                                           ),
                                           MDFlatButton(
                                               text="DELETE", text_color=self.app.theme_cls.primary_color,
                                               on_release=self.del_exc
                                           ),
                                       ],
                                       )
        self.dialog.open()

    def del_exc(self, *args):
        self.dialog.dismiss()
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

        if self.view_mode:
            self.delete_exc_from_session(exc)

        self.show_checkbox(False)
        self.fix_resize()

    def delete_exc_from_session(self, exc):
        session = self.app.sessions[self.session_key]

    def cancel_del_exc(self, caller):
        self.dialog.dismiss()

    def show_add_exercise_dialog(self):
        exc_limit = self.exc_limit
        num_of_exc_in_split = len(self.workout)
        if num_of_exc_in_split > exc_limit - 1:
            self.app.show_ok_msg(self.app.dismiss_dialog, "Limit Reached",
                                 "Cant have more than " + str(exc_limit) + " exercises in one split")
            return

        self.dialog = MDDialog(
            radius=[10, 7, 10, 7],
            size_hint=(0.9, 0.2),
            title="New Exercise:",
            type="custom",
            content_cls=AddExerciseContent(),
            buttons=[
                MDFlatButton(
                    text="Exercises Bank",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=self.app.open_exercise_bank_menu
                ),
                MDFlatButton(
                    text="Cancel",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=self.dismiss_dialog
                ),
                MDFlatButton(
                    text="OK",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=self.add_exercise
                ),
            ],
        )
        self.dialog.open()

    def dismiss_dialog(self, *args):
        self.dialog.dismiss()

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
            if len(self.workout) > 5:
                self.ids.scroll.scroll_to(new_card, padding=10, animate=True)

    def fix_resize(self):
        # after delete or add exercise, needs to adjust scroll view size
        # current fix is by rentering the page, so the original fix will work
        self.app.change_screen1("blankscreen", -2)
        self.app.change_screen1("sessionscreen", -3)
        self.load_session()
        # self.app.root.ids['toolbar'].right_action_items = [['content-save', lambda x: self.save_session()]]

        self.app.root.ids['toolbar'].right_action_items = [['', lambda x: None]]

    def show_example_date_picker(self, *args):
        max_date = datetime.strptime(self.app.today_date[:10], '%d/%m/%Y').date()
        MDDatePicker(self.set_previous_date, max_date=max_date).open()

    def set_previous_date(self, date_obj):
        new_date = date_obj.strftime("%d/%m/%Y")
        self.ids["date_picker_label"].text = new_date
        self.session_date = new_date + " 00:00:00"
        if self.app.debug:
            print(self.ids["date_picker_label"].text)

    def reload_previous_session(self, *args):
        self.app.reload_for_running_session = self.workout_name
        self.app.change_screen1("previous_workouts_screen")


class MyToggleButton2(MDRectangleFlatButton, MDToggleButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_down = self.theme_cls.primary_light
        self.background_normal = (1, 1, 1, 0)
        self.text_color = (1, 1, 1, 1)
        self.allow_no_selection = False


class MDSetsLabel(MDGridLayout):
    cols = 1


class ExerciseScreen(Screen):
    exercise = "TEST EXC"
    repScale = 1
    weightScale = 1
    sets = []
    dialog = 0
    barbell = 0
    sets_limit = 15

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"

    def changeInput(self, toScale, increase):

        if self.ids["weight"].text:
            currWeight = float(self.ids["weight"].text)
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
        self.app.root.ids['toolbar'].right_action_items = [['', lambda x: None]]

        self.barbell = 0
        self.change_scale(1)

        self.sets = []
        self.app.title = "Home"
        self.app.root.ids['toolbar'].title = self.exercise
        self.app.add_bottom_canvas()

        if self.app.units == "metric":
            self.ids["weight"].helper_text = "Kg"
        else:
            self.ids["weight"].helper_text = "Lbs"

        exc = self.exercise
        self.ids["ex_name"].text = exc  # if already completed a few sets in this session:
        session_rec = self.app.root.ids['sessionscreen'].session_rec

        if exc in session_rec:
            sets = session_rec[exc]
            for set in sets:
                set = set.split()
                reps = set[0]
                weight = set[2]
                self.add_set_to_grid(int(reps), float(weight))
                weight_to_show = weight
                if self.app.units != 'metric':
                    weight_to_show = str(round(float(weight) * self.app.kg_to_pounds, 2))
                else:
                    weight_to_show = str(round(float(weight), 2))

                self.ids["reps"].text = reps
                self.ids["weight"].text = weight_to_show

        else:
            session_rec[exc] = []
        self.clear_focus_toggle()

    def clear_focus_toggle(self):
        for child in self.ids["group_scale"].children:
            if child.text == '+1':
                child.md_bg_color = self.app.theme_cls.primary_light
            else:
                child.md_bg_color = (1, 1, 1, 0)
        for child in self.ids["group_barbell"].children:
            if child.text == 'None':
                child.md_bg_color = self.app.theme_cls.primary_light
            else:
                child.md_bg_color = (1, 1, 1, 0)

    def on_leave(self, *args):
        self.clear_screen()

    def add_set(self):

        sets_limit = self.sets_limit
        num_of_exc_in_split = len(self.sets)
        if num_of_exc_in_split > sets_limit - 1:
            self.app.show_ok_msg(self.app.dismiss_dialog, "Limit Reached",
                                 "Cant have more than " + str(sets_limit) + " sets")
            return

        weight = self.ids["weight"].text
        currWeight = float(weight)

        if self.app.units != 'metric':
            currWeight = currWeight / self.app.kg_to_pounds

        currReps = int(self.ids["reps"].text)
        if not currReps:
            self.show_invalid_input_msg()
        else:
            if self.barbell:
                currWeight = currWeight * 2 + self.barbell

            weight_to_save = currWeight  # in kg as defualt

            self.add_set_to_grid(currReps, currWeight)

    def show_invalid_input_msg(self):
        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
                               title="Not a single Rep? Too lazy..",
                               buttons=[
                                   MDFlatButton(
                                       text="Ok, Ill try harder", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.invalid_input_dismiss
                                   )
                               ],
                               )
        self.dialog.open()

    def invalid_input_dismiss(self, *args):
        self.dialog.dismiss()

    def open_help_dialog(self):
        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
                               text="[size=" + str(
                                   self.app.headline_text_size) + "][color=0,0,0,1]Inc[/color][/size]\nCustom increase/decrease in reps and weight value.\n\n[size=" + str(
                                   self.app.headline_text_size) + "][color=0,0,0,1]Barbell[/color][/size]\nAuto calculate set weight for chosen barbell weight.\nChoose your barbell weight and how much weight has been added to one side."
                               )
        self.dialog.open()

    def add_set_to_grid(self, currReps, currWeight):
        rep_inc = 0
        weight_inc = 0
        if currReps > 9:
            rep_inc = -0.015

        self.sets.append([currReps, currWeight])

        currWeight, unit = self.app.fix_weight_by_unit(currWeight)

        if len(str(currWeight)) > 3:
            weight_inc = -0.004 * len(str(currWeight))

        num_of_set = len(self.sets)
        # self.ids["md_list"].add_widget(
        #     SwipeToDeleteItem(text=f"{currReps}    X    {currWeight}", size_hint=(1, 1))
        # )
        set_add = 0.05
        x_add = 0.23

        set_layout = MDFloatLayout()
        set_num = "SET " + str(num_of_set) + ":"
        set_layout.add_widget(
            MDLabel(text=set_num, size_hint=(1, 0.2), font_style="H5",
                    pos_hint={"center_y": 0.7, "center_x": 0.62 + set_add}, theme_text_color="Custom",
                    text_color=self.app.text_color
                    )
        )
        set_layout.add_widget(
            MDLabel(text=str(currReps), size_hint=(1, 0.2), font_style="H5",
                    pos_hint={"center_y": 0.7, "center_x": 0.865 + x_add + rep_inc}, theme_text_color="Custom",
                    text_color=self.app.text_color
                    )
        )
        set_layout.add_widget(
            MDLabel(text="X", size_hint=(1, 0.2), font_style="H5",
                    pos_hint={"center_y": 0.7, "center_x": 0.969 + x_add}, theme_text_color="Custom",
                    text_color=self.app.text_color
                    )
        )
        set_layout.add_widget(
            MDLabel(text=str(currWeight), size_hint=(1, 0.2), font_style="H5",
                    pos_hint={"center_y": 0.7, "center_x": 1.06 + x_add + weight_inc}, theme_text_color="Custom",
                    text_color=self.app.text_color
                    )
        )
        set_layout.add_widget(
            MDLabel(text=f"Reps", font_style="Caption",
                    pos_hint={"center_y": 0.3, "center_x": 0.86 + x_add},
                    theme_text_color="Secondary"
                    ))
        last_label = MDLabel(text=unit, font_style="Caption",
                             pos_hint={"center_y": 0.3, "center_x": 1.09 + x_add},
                             theme_text_color="Secondary"
                             )
        set_layout.add_widget(last_label)

        self.ids["sets_grid"].add_widget(set_layout)
        if len(self.sets) > 5:
            self.ids.sets_scroll.scroll_to(last_label, padding=10, animate=True)

    def save_exc(self):
        exc = self.ids["ex_name"].text
        sets_list = []
        # SessionScreen.session_rec[exc] = sets_list
        # for child in self.ids["md_list"].children:
        #     set = child.text
        #     sets_list.append(set)

        for set in self.sets:
            set_str = f"{set[0]}    X    {set[1]}"
            sets_list.append(set_str)
        self.app.root.ids['sessionscreen'].session_rec[exc] = sets_list
        # SessionScreen.session_rec[exc] = sets_list
        self.sets = []
        self.app.change_screen1("sessionscreen", -1, "right")
        # sets_list_str = ', '.join(sets_list)
        # SessionScreen.ex_reference_by_exc[exc].tertiary_text = "Done: " + sets_list_str

    def clear_screen(self):
        self.ids["sets_grid"].clear_widgets()
        self.ids["weight"].text = "0"
        self.ids["reps"].text = "0"

    def delete_set(self):
        sets_layout = self.ids["sets_grid"].children
        if sets_layout:
            self.ids["sets_grid"].remove_widget(sets_layout[0])
            self.sets.pop(-1)
        if self.sets:
            currReps, currWeight = self.sets[-1][0], self.sets[-1][1]
            self.ids["weight"].text = str(currWeight)
            self.ids["reps"].text = str(currReps)
        else:
            self.ids["weight"].text = "0"
            self.ids["reps"].text = "0"

    def remove_set(self, instance):
        self.ids["md_list"].remove_widget(instance)

    def change_scale(self, new_scale):
        self.weightScale = new_scale
        if new_scale != 2.5:
            self.repScale = new_scale
        else:
            self.repScale = 1

