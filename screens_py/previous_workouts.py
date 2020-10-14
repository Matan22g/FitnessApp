import copy
from datetime import datetime
import calendar

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDTextButton, MDRoundFlatButton, MDFillRoundFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import Snackbar

from screens_py.exercise_sessions import ExerciseSessionsScreen
from screens_py.sessionscreen import SessionScreen

from kivy.base import runTouchApp
from kivy.clock import Clock
from kivy.factory import Factory


class LongPressCard(MDCard):
    __events__ = ('on_long_press',)
    long_press = 0
    long_press_time = Factory.NumericProperty(1)
    card_id = 0

    def on_state(self, instance, value):
        if value == 'down':
            lpt = self.long_press_time
            self._clockev = Clock.schedule_once(self._do_long_press, lpt)
        else:
            self._clockev.cancel()
            if not self.long_press:
                self.on_short_press()
            self.long_press = 0

    def _do_long_press(self, dt):
        self.dispatch('on_long_press')

    def on_long_press(self, *largs):
        app = MDApp.get_running_app()
        app.root.ids['previous_workouts_screen'].show_checkbox("True")
        self.long_press = 1

    def on_short_press(self, *largs):
        app = MDApp.get_running_app()
        # TODO fix short press, and session page related to picking date
        delete_mode = app.root.ids['previous_workouts_screen'].delete_mode
        check_box_list = app.root.ids['previous_workouts_screen'].session_card_by_checkBox
        if not delete_mode:
            if app.root.ids['previous_workouts_screen'].weight_history:
                return
            app.root.ids['previous_workouts_screen'].view_session(self.card_id)
        else:
            if app.root.ids['previous_workouts_screen'].weight_history:
                check_box = self.card_id.children[0].children[0]
            else:
                check_box = self.card_id.children[0].children[1]

            check_box.active = not (check_box.active)
            app.root.ids['previous_workouts_screen'].update_delete_num('previous_workouts_screen', check_box_list)


class PreviousWorkoutsScreen(Screen):
    session_card_by_checkBox = {}
    session_key_by_card = {}
    choose_date = ExerciseSessionsScreen.choose_date
    new_date = ExerciseSessionsScreen.new_date
    no_sessions_grid = ExerciseSessionsScreen.no_sessions_grid
    nearest = ExerciseSessionsScreen.nearest
    update_delete_num = SessionScreen.update_delete_num
    delete_mode = 0
    num_to_del = 0

    curr_year = 0
    curr_month = 0

    weight_history = 0

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def help_button(self, method):
        if method == "tune":
            self.choose_date()
        else:
            self.show_del_exercise_dialog()

    def on_pre_enter(self, *args):
        self.app.change_title("Recent Workouts")

        curr_month, curr_year = self.find_closest_date()

        self.show_checkbox(False)

        self.app.root.ids['toolbar'].right_action_items = [
            ['', lambda x: None]]

        if self.app.root.ids['previous_workouts_screen'].weight_history:
            self.app.change_title("Weight History")
            self.app.remove_bottom_nav()
            self.curr_month = curr_month
            self.curr_year = curr_year
            self.load_weight_history(self.curr_year, self.curr_month)
            self.app.root.ids['toolbar'].left_action_items = [
                ["chevron-left", lambda x: self.app.back_to_last_screen()]]
            self.app.root.ids['toolbar'].right_action_items = [
                ['plus', lambda x: self.app.show_update_weight_dialog()]]

        elif self.app.reload_for_running_session:

            self.curr_month = curr_month
            self.curr_year = curr_year
            self.load_sessions(self.curr_year, self.curr_month)

        else:
            if not self.curr_month and not self.curr_year:
                self.curr_month = curr_month
                self.curr_year = curr_year

            else:
                return
            self.load_sessions(self.curr_year, self.curr_month)

        self.fix_headline_pos()
        # self.fix_grid_heights()

    def fix_headline_pos(self):
        if self.app.root.ids['previous_workouts_screen'].weight_history or self.app.reload_for_running_session:
            self.app.root.ids['previous_workouts_screen'].ids["month_to_view"].pos_hint = {"center_x": 0.57,
                                                                                           "top": 1.015}
            self.app.root.ids['previous_workouts_screen'].ids["icon_grid"].pos_hint = {"center_x": 0.775,
                                                                                       "center_y": 0.915}
        else:
            self.app.root.ids['previous_workouts_screen'].ids["month_to_view"].pos_hint = {"center_x": 0.57, "top": 1.0}
            self.app.root.ids['previous_workouts_screen'].ids["icon_grid"].pos_hint = {"center_x": 0.775,
                                                                                       "center_y": 0.895}

    def find_closest_date(self):
        today = datetime.today()
        curr_month = int(today.month)
        curr_year = int(today.year)

        if self.app.root.ids['previous_workouts_screen'].weight_history:
            look_up_dict = self.app.weight_history_by_month_year
        else:
            look_up_dict = self.app.sessions_by_month_year

        if look_up_dict:
            if curr_year not in look_up_dict:
                curr_year = self.nearest(list(look_up_dict.keys()), curr_year)
            if curr_month not in look_up_dict[curr_year]:
                curr_month = self.nearest(look_up_dict[curr_year], curr_month)

        return curr_month, curr_year

    def on_leave(self, *args):
        if self.app.root.ids['previous_workouts_screen'].weight_history:
            self.app.root.ids['previous_workouts_screen'].weight_history = 0
            self.curr_month = 0
            self.curr_year = 0

    def load_sessions(self, year, month):
        if self.app.debug:
            print("loading sessions of", year, month)
        self.curr_year = year
        self.curr_month = month
        sessions_layout = self.ids.sessions_grid
        sessions_layout.clear_widgets()

        month_abb = calendar.month_abbr[month]
        self.app.root.ids['previous_workouts_screen'].ids["month_to_view"].text = month_abb + ", " + str(year)

        print('self.app.sessions_by_month_year', self.app.sessions_by_month_year)
        print("session", self.app.sessions)
        if year in self.app.sessions_by_month_year and month in self.app.sessions_by_month_year[year]:
            sessions_dates = self.app.sessions_by_month_year[year][month]
        else:
            msg = "No sessions available for " + month_abb + ", " + str(year)
            self.no_sessions_grid(msg, sessions_layout)
            return

        # dict_of_row_height = {0: 100}
        # sessions_layout.rows_minimum = dict_of_row_height

        total_session_num = len(sessions_dates)
        # for i in range(total_session_num):
        #     dict_of_row_height[i] = 100
        # sessions_layout.rows_minimum = dict_of_row_height
        if self.app.reload_for_running_session:
            total_session_num = 0
            for sessions_date in sessions_dates:
                session = self.app.sessions[sessions_date]
                if session.workout_name == self.app.reload_for_running_session:
                    total_session_num += 1
        num_of_session = 0
        for sessions_date in sessions_dates:
            print("sessions_date", sessions_date)
            print("sessions_date", month)

            session = self.app.sessions[sessions_date]
            if self.app.reload_for_running_session:
                if session.workout_name == self.app.reload_for_running_session:
                    num_of_session += 1
                    new_card_layout = self.create_card(session.workout_name,
                                                       session.date,
                                                       session.duration, sessions_date, len(session.exercises))
                    sessions_layout.add_widget(new_card_layout)

            else:
                num_of_session += 1
                new_card_layout = self.create_card(session.workout_name,
                                                   session.date,
                                                   session.duration, sessions_date, len(session.exercises))
                sessions_layout.add_widget(new_card_layout)

    # def create_card1(self, num_of_session, total_session_num, session_workout_name, session_date, session_duration,
    #                 sessions_date_key, num_exc_completed):
    #     new_card_layout = MDFloatLayout()  # for centering
    #     help_layout = MDGridLayout(size_hint_y=0.05, rows=1, cols=3)
    #
    #     if self.app.reload_for_running_session:
    #         excCard = MDCard(
    #             spacing=8,
    #             radius=[80],
    #             orientation="vertical",
    #             size_hint=(0.87, 0.97),
    #             padding=[40, 40, 0, 40],  # [padding_left, padding_top,padding_right, padding_bottom].
    #             pos_hint={"center_y": 0.5, "center_x": 0.5},
    #             background="resources/card_back.png",
    #             elevation=1,
    #             on_release=self.view_session,
    #         )
    #     else:
    #         excCard = LongPressCard(
    #             spacing=8,
    #             radius=[80],
    #             orientation="vertical",
    #             size_hint=(0.87, 0.97),
    #             padding=[40, 40, 0, 40],  # [padding_left, padding_top,padding_right, padding_bottom].
    #             pos_hint={"center_y": 0.5, "center_x": 0.5},
    #             background="resources/card_back.png",
    #             elevation=1,
    #             long_press_time=0.5,
    #             on_long_press=lambda w: setattr(w, 'text', 'long press!')
    #         )
    #     excCard.card_id = excCard
    #     # help_layout = self.create_top_card_layout(num_of_exc, num_of_exc_total, exc)
    #     # excCard.add_widget(help_layout)
    #
    #     excnum = str(num_of_session) + " of " + str(total_session_num)
    #     # workout_date = "Mon, 15 Jul"
    #     # workout_name = "ABC"
    #     # workout_duration = "44 mins"
    #     exc_num = MDLabel(
    #         text=excnum,
    #         font_style="Caption",
    #         size_hint=(0.3, 0.1),
    #         theme_text_color="Custom",
    #         text_color=self.app.text_color
    #     )
    #     deleteBox = MDCheckbox(
    #         size_hint=(0.5, 0.75)
    #     )
    #     deleteBox.opacity = 0
    #     self.session_card_by_checkBox[deleteBox] = excCard
    #     session_date = session_date.ctime()[0:10]
    #     session_date = session_date[0:3] + "," + session_date[3:]
    #     date_label = MDLabel(
    #         text=session_date,
    #         font_style="Subtitle2",
    #         size_hint=(0.97, 0.1),
    #         theme_text_color="Custom",
    #         text_color=self.app.text_color
    #     )
    #     workout_name_label = MDLabel(
    #         text=session_workout_name,
    #         font_style="H5",
    #         theme_text_color="Custom",
    #         text_color=self.app.text_color
    #     )
    #     workout_duration_label = MDLabel(
    #         text=session_duration + "    " + str(num_exc_completed) + " Exercises Completed",
    #         font_style="Caption",
    #         size_hint=(0.6, 0.1),
    #         theme_text_color="Custom",
    #         text_color=self.app.text_color
    #     )
    #
    #     help_layout.add_widget(date_label)
    #     help_layout.add_widget(deleteBox)
    #     help_layout.add_widget(exc_num)
    #
    #     excCard.add_widget(help_layout)
    #
    #     if self.app.reload_for_running_session:
    #         middle_layout = MDGridLayout(rows=1, cols=2, size_hint=(0.8, 0.4))
    #         middle_layout.add_widget(workout_name_label)
    #
    #         middle_layout.add_widget(MDTextButton(
    #             text="Load",
    #             font_size=str(self.app.headline_text_size * 0.9),
    #             custom_color=self.app.text_color,
    #             on_release=self.load_for_running_session))
    #
    #         # middle_layout.add_widget(nothing_label)
    #
    #         excCard.add_widget(middle_layout)
    #     else:
    #         excCard.add_widget(workout_name_label)
    #
    #     excCard.add_widget(workout_duration_label)
    #
    #     new_card_layout.add_widget(excCard)
    #     self.session_key_by_card[excCard] = sessions_date_key
    #     return new_card_layout

    def create_card(self, session_workout_name, session_date, session_duration,
                    sessions_date_key, num_exc_completed):
        new_card_layout = MDFloatLayout()  # for centering

        if self.app.reload_for_running_session:
            excCard = MDCard(
                spacing=8,
                radius=[80, 0, 80, 0],
                orientation="horizontal",
                size_hint=(0.95, 0.97),
                padding=[40, 40, 20, 40],  # [padding_left, padding_top,padding_right, padding_bottom].
                pos_hint={"center_y": 0.5, "center_x": 0.5},
                background="resources/card_back_prev.png",
                elevation=1,
                on_release=self.view_session,
            )
        else:
            excCard = LongPressCard(
                spacing=8,
                radius=[80, 0, 80, 0],
                orientation="horizontal",
                size_hint=(0.95, 0.97),
                padding=[40, 40, 20, 40],  # [padding_left, padding_top,padding_right, padding_bottom].
                pos_hint={"center_y": 0.5, "center_x": 0.5},
                background="resources/card_back_prev.png",
                elevation=1,
                long_press_time=0.5,
                on_long_press=lambda w: setattr(w, 'text', 'long press!')
            )
        excCard.card_id = excCard
        # help_layout = self.create_top_card_layout(num_of_exc, num_of_exc_total, exc)
        # excCard.add_widget(help_layout)
        session_date = session_date.ctime()[0:10]
        session_date = " " + session_date[8:] + "\n " + session_date[4:7]
        print(session_date)
        date_size_hint_x = 0.2
        if self.app.reload_for_running_session:
            date_size_hint_x = 0.25

        date_label = MDLabel(
            text=session_date,
            font_style="H6",
            size_hint=(date_size_hint_x, 1),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        excCard.add_widget(date_label)
        main_layout = MDGridLayout(rows=2, cols=2, spacing=20)
        deleteBox = MDCheckbox(
            size_hint=(0.5, 0.75),
            on_release=self.update_del_num
        )
        deleteBox.opacity = 0
        self.session_card_by_checkBox[deleteBox] = excCard

        workout_name_label = MDLabel(
            text=session_workout_name,
            font_style="H5",
            theme_text_color="Custom",
            text_color=self.app.text_color,
            size_hint=(1.6, 1.6)
        )
        workout_completed_label = MDLabel(
            text=str(num_exc_completed) + " Exercises Completed",
            font_style="Caption",
            size_hint=(0.8, 0.4),
            theme_text_color="Secondary"
        )
        workout_duration_label = MDLabel(
            text="  " + session_duration,
            font_style="Caption",
            size_hint=(0.6, 0.1),
            theme_text_color="Secondary"
        )

        main_layout.add_widget(workout_name_label)
        main_layout.add_widget(deleteBox)

        # main_layout.add_widget(workout_duration_label)

        main_layout.add_widget(workout_completed_label)
        # if self.app.reload_for_running_session:
        #     main_layout.add_widget(MDLabel(
        #         text="",
        #         size_hint=(0.1,0.1)))
        #
        #     main_layout.add_widget(MDFillRoundFlatButton(
        #         text="LOAD",
        #         text_color=(1, 1, 1, 1),
        #         size_hint=(0.3,1.5),
        #         on_release=self.load_for_running_session))

        excCard.add_widget(main_layout)
        if self.app.reload_for_running_session:
            excCard.add_widget(MDFillRoundFlatButton(
                text="LOAD",
                text_color=(1, 1, 1, 1),
                on_release=self.load_for_running_session))

        new_card_layout.add_widget(excCard)
        self.session_key_by_card[excCard] = sessions_date_key
        return new_card_layout

    def view_session(self, *args):
        workout_card = args[0]
        sessions_date_key = self.session_key_by_card[workout_card]
        self.app.view_session(sessions_date_key)

    def update_del_num(self, *args):
        self.app.root.ids['previous_workouts_screen'].update_delete_num('previous_workouts_screen',
                                                                        self.session_card_by_checkBox)

    def show_checkbox(self, to_show):

        self.app.root.ids['previous_workouts_screen'].ids["num_to_delete"].text = ""
        if to_show == "False" or not to_show:
            to_show = 0
        else:
            to_show = 1

        if to_show:
            self.app.root.ids['previous_workouts_screen'].delete_mode = 1
            self.ids["help_button"].icon = 'trash-can-outline'

        else:
            self.app.root.ids['previous_workouts_screen'].delete_mode = 0
            self.ids["help_button"].icon = 'tune'

        for checkbox_id in self.session_card_by_checkBox:
            checkbox_id.active = 0
            checkbox_id.selected_color = self.app.theme_cls.primary_color

            if to_show:
                checkbox_id.opacity = 1
            else:
                checkbox_id.opacity = 0

    # def delete_selected(self):
    #     print("trying to delete")

    def show_del_exercise_dialog(self):
        num_to_del = self.app.root.ids['previous_workouts_screen'].ids["num_to_delete"].text
        title = "Select session to delete"
        if self.app.root.ids['previous_workouts_screen'].weight_history:
            title = "Select weight record to delete"
        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
                               title=title,
                               buttons=[
                                   MDFlatButton(
                                       text="Ok", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.cancel_del_exc
                                   )
                               ],
                               )
        if num_to_del:
            if int(num_to_del):

                msg = "Delete " + num_to_del + " Session?"
                warning = "Warning: deleting session record cannot be undone"
                if self.app.root.ids['previous_workouts_screen'].weight_history:
                    msg = "Delete " + num_to_del + " records?"
                    warning = "Warning: deleting weight record cannot be undone"

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
                                               on_release=self.del_session
                                           ),
                                       ],
                                       )
        self.dialog.open()

    def del_session(self, *args):
        self.dialog.dismiss()

        for checkbox in list(
                self.session_card_by_checkBox):  # force a copy to avoid "dict changed size during iteration"
            if checkbox.active:
                session_card = self.session_card_by_checkBox.pop(checkbox, None)
                session_key = self.session_key_by_card.pop(session_card, None)

                self.ids["sessions_grid"].remove_widget(session_card)
                if self.app.root.ids['previous_workouts_screen'].weight_history:
                    self.app.del_weight_by_key(session_key)
                else:
                    self.app.del_session(session_key)
        self.show_checkbox(False)

        if self.app.root.ids['previous_workouts_screen'].weight_history:
            Snackbar(text="Weight record Deleted!").show()
            self.load_weight_history(self.curr_year, self.curr_month)

        else:
            Snackbar(text="Session Deleted!").show()
            self.load_sessions(self.curr_year, self.curr_month)

    def fix_grid_heights(self):
        grid = self.ids.sessions_grid
        self.ids.sessions_grid.height = sum(x.height for x in grid.children)

    def cancel_del_exc(self, caller):
        self.dialog.dismiss()

    def load_for_running_session(self, *args):
        sessions_date_key = self.session_key_by_card[args[0].parent]
        session = self.app.sessions[sessions_date_key]
        session_sets_dict = session.exercises
        self.app.root.ids['sessionscreen'].session_rec = copy.deepcopy(session_sets_dict)
        workout = self.app.root.ids['sessionscreen'].workout
        for exc in list(session_sets_dict):
            if exc not in workout:
                self.app.root.ids['sessionscreen'].workout.append(exc)
        self.app.running_session_workout = copy.deepcopy(self.app.root.ids['sessionscreen'].workout)
        self.app.change_screen1("sessionscreen", -1)
        self.app.reload_for_running_session = ""
        self.curr_month = 0
        self.curr_year = 0

    def load_weight_history(self, year, month):
        if self.app.debug:
            print("loading sessions of", year, month)
        self.curr_year = year
        self.curr_month = month
        sessions_layout = self.ids.sessions_grid
        sessions_layout.clear_widgets()

        month_abb = calendar.month_abbr[month]
        self.app.root.ids['previous_workouts_screen'].ids["month_to_view"].text = month_abb + ", " + str(year)

        if year in self.app.weight_history_by_month_year and month in self.app.weight_history_by_month_year[year]:
            weight_history_dates = self.app.weight_history_by_month_year[year][month]
            if not weight_history_dates:
                msg = "No data available for " + month_abb + ", " + str(year)
                self.no_sessions_grid(msg, sessions_layout)

        else:
            msg = "No data available for " + month_abb + ", " + str(year)
            self.no_sessions_grid(msg, sessions_layout)
            return

        # dict_of_row_height = {0: 100}
        # sessions_layout.rows_minimum = dict_of_row_height

        total_session_num = len(weight_history_dates)
        # for i in range(total_session_num):
        #     dict_of_row_height[i] = 100
        # sessions_layout.rows_minimum = dict_of_row_height
        num_of_session = 0
        for sessions_date in weight_history_dates:
            num_of_session += 1
            new_card_layout = self.create_weight_card(self.app.weights[sessions_date],
                                                      sessions_date)
            sessions_layout.add_widget(new_card_layout)

    def create_weight_card(self, weight, weight_date):
        new_card_layout = MDFloatLayout()  # for centering
        help_layout = MDGridLayout(size_hint_y=0.05, rows=1, cols=3)
        excCard = LongPressCard(
            spacing=8,
            radius=[80, 0, 80, 0],
            orientation="horizontal",
            size_hint=(0.95, 0.97),
            padding=[40, 40, 20, 40],  # [padding_left, padding_top,padding_right, padding_bottom].
            pos_hint={"center_y": 0.5, "center_x": 0.5},
            background="resources/card_back_prev.png",
            elevation=1,
            long_press_time=0.5,
            on_long_press=lambda w: setattr(w, 'text', 'long press!')
        )
        excCard.card_id = excCard
        # help_layout = self.create_top_card_layout(num_of_exc, num_of_exc_total, exc)
        # excCard.add_widget(help_layout)

        label_weight_date = weight_date.ctime()[0:10]
        label_weight_date = label_weight_date[8:] + "\n" + label_weight_date[4:7]
        weight, unit = self.app.fix_weight_by_unit(weight)

        date_label = MDLabel(
            text=label_weight_date,
            font_style="H6",
            size_hint=(0.2, 1),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        excCard.add_widget(date_label)

        main_layout = MDGridLayout(rows=1, cols=2, spacing=20)
        deleteBox = MDCheckbox(
            size_hint=(0.5, 0.75),
            on_release=self.update_del_num
        )
        deleteBox.opacity = 0
        self.session_card_by_checkBox[deleteBox] = excCard

        weight_label = MDLabel(
            text=str(weight) + " " + unit,
            font_style="H5",
            theme_text_color="Custom",
            text_color=self.app.text_color,
            size_hint=(1.4, 1.6),
            halign='center'
        )

        main_layout.add_widget(weight_label)
        main_layout.add_widget(deleteBox)

        # main_layout.add_widget(MDFillRoundFlatButton(
        #     text="Load",
        #     text_color=(1, 1, 1, 1),
        #     size_hint_y=0.1,
        #     on_release=self.load_for_running_session))
        excCard.add_widget(main_layout)

        new_card_layout.add_widget(excCard)
        self.session_key_by_card[excCard] = weight_date
        return new_card_layout

