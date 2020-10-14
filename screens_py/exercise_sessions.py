import calendar
from datetime import datetime

from kivy.core.window import Window

from customKv.datepicker import AKDatePicker
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.card import MDCard, MDSeparator
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from screens_py.sessionscreen import SessionScreen


class ExerciseSessionsScreen(Screen):
    exercise = ""
    sessions = []
    dates = {}
    create_set_label = SessionScreen.create_set_label
    str_to_set = SessionScreen.str_to_set

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self, *args):
        self.app.root.ids['toolbar'].right_action_items = [['', lambda x: None]]

        self.dates = {}
        self.sessions = []
        # self.app.change_title(self.exercise + " History")
        self.app.change_title("Exercise History")
        self.app.root.ids['exercise_sessions_screen'].ids["exc_name"].text = self.exercise
        if self.app.debug:
            print("entering history", self.exercise)
        if self.exercise in self.app.exc_sessions:
            if "record" in self.app.exc_sessions[self.exercise]:
                record = self.app.exc_sessions[self.exercise]["record"][0]
                record_date = self.app.exc_sessions[self.exercise]["record"][1]

                month_abb = calendar.month_abbr[record_date.month]
                record_date = month_abb + ", " + str(record_date.year)
                self.set_record(record, record_date)

            else:
                self.set_record(0, 0)

            self.sessions = self.app.exc_sessions[self.exercise]
            self.app.root.ids['exercise_stats_screen'].sessions = self.sessions
            self.app.root.ids['exercise_stats_screen'].exericse_name = self.exercise

            self.sort_sessions()
            today = datetime.today()
            curr_month = int(today.month)
            curr_year = int(today.year)
            if curr_month in self.dates[curr_year]:
                month = curr_month
            else:
                month = self.nearest(self.dates[curr_year], curr_month)

            self.load_sessions(curr_year, month)
        else:
            self.set_record(0, 0)
            self.no_sessions_grid("No records for " + self.exercise, self.ids.sets_grid)
            self.app.root.ids['exercise_stats_screen'].sessions = {}
            self.app.root.ids['exercise_stats_screen'].exericse_name = self.exercise

    def set_record(self, record, date):
        if record:
            record = record.split()
            best_reps = record[0]
            best_weight = record[2]

            self.app.root.ids['exercise_stats_screen'].ids["record"].text = "Overall Best"
            self.app.root.ids['exercise_stats_screen'].ids["record_date"].text = date

            self.app.root.ids['exercise_stats_screen'].ids["best_reps"].text = best_reps

            if self.app.units == "metric":
                self.app.root.ids['exercise_stats_screen'].ids["weight_unit"].text = " Kg"

            else:
                self.app.root.ids['exercise_stats_screen'].ids["weight_unit"].text = " Lbs"
                best_weight = str(round(float(best_weight) * self.app.kg_to_pounds, 2))

            self.app.root.ids['exercise_stats_screen'].ids["best_weight"].text = best_weight

        else:
            self.app.root.ids['exercise_stats_screen'].ids["best_reps"].text = "0"
            self.app.root.ids['exercise_stats_screen'].ids["best_weight"].text = "0"
            self.app.root.ids['exercise_stats_screen'].ids["record"].text = "N/A"
            self.app.root.ids['exercise_stats_screen'].ids["record_date"].text = ""

    # def set_month_record(self, record, month):
    #     return
    #     if record:
    #         record = record.split()
    #         best_reps = record[0]
    #         best_weight = record[2]
    #         self.app.root.ids['exercise_sessions_screen'].ids["best_month_title"].text = "Best of " + month
    #
    #         self.app.root.ids['exercise_sessions_screen'].ids["best_month_reps"].text = best_reps
    #         self.app.root.ids['exercise_sessions_screen'].ids["best_month_weight"].text = best_weight
    #     else:
    #         self.app.root.ids['exercise_sessions_screen'].ids["best_month_title"].text = "N/A"
    #
    #         self.app.root.ids['exercise_sessions_screen'].ids["best_month_reps"].text = "0"
    #         self.app.root.ids['exercise_sessions_screen'].ids["best_month_weight"].text = "0"

    def nearest(self, items, pivot):
        return min(items, key=lambda x: abs(x - pivot))

    def sort_sessions(self):
        dates = [date for date in self.sessions if date != "record"]
        dates.sort(reverse=True)
        for date in dates:
            year = int(date.year)
            month = int(date.month)

            if year not in self.dates:
                self.dates[year] = {}

            if month not in self.dates[year]:
                self.dates[year][month] = [date]

            else:
                self.dates[year][month].append(date)
        self.app.root.ids['exercise_stats_screen'].session_date = self.dates

        print(self.dates)

    def on_enter(self, *args):
        pass

    def on_leave(self, *args):
        # always deleting all splits and remaining with one tab.
        pass

    def load_sessions(self, year, month):
        print("loading sessions of", year, month)
        print("self.dates", self.dates)
        print("self.sessions", self.sessions)
        print("self.sessions", self.sessions)

        sessions_layout = self.ids.sets_grid
        sessions_layout.clear_widgets()
        month_abb = calendar.month_abbr[month]
        self.app.root.ids['exercise_sessions_screen'].ids["date_label"].text = "Previous sessions, " + month_abb

        dict_of_row_height = {}

        if year in self.dates and month in self.dates[year]:
            sessions_keys = self.dates[year][month]  # represents all session dates given a certain month
        else:
            msg = "No sessions available for " + month_abb + ", " + str(year)
            self.no_sessions_grid(msg, sessions_layout)
            return

        # month = sessions_keys[0].ctime()[4:7]

        window_height = Window.size[1]
        row_height = window_height / 6
        row_enlarger_inc = window_height / 16.6

        for i, session_key in enumerate(sessions_keys):
            session = self.sessions[session_key][1]
            dict_of_row_height[i] = row_height
            session_workout_name = self.sessions[session_key][0]
            row_enlarger = row_enlarger_inc * (len(session) - 1)
            if len(session_workout_name) > 9:
                row_enlarger = row_enlarger * 1.125
            else:
                dict_of_row_height[i] = window_height / 7.5
            dict_of_row_height[i] += row_enlarger

        self.ids.sets_grid.rows_minimum = dict_of_row_height
        total_session_num = len(sessions_keys)

        best_weight = 0
        best_set = 0
        for i, session_key in enumerate(sessions_keys):
            session_exc = self.sessions[session_key][1]
            session_workout_name = self.sessions[session_key][0]
            session_date = session_key.ctime()[0:10]
            session_date = session_date[0:3] + "," + session_date[3:]
            new_card_layout = self.create_card(session_exc, i, total_session_num, session_workout_name, session_date)

            sessions_layout.add_widget(new_card_layout)

            # maybe_best_set = self.app.find_best_set(session_exc)
            # set = maybe_best_set.split()
            # maybe_best_weight = float(set[2])
            # if maybe_best_weight > best_weight:
            #     best_set = maybe_best_set
            #     best_weight = maybe_best_weight


    def no_sessions_grid(self, msg, layout):
        new_card_layout = MDFloatLayout()  # for centering

        excCard = MDCard(
            spacing=15,
            radius=[80],
            orientation="vertical",
            size_hint=(0.87, 0.7),
            padding=[11, 16, 0, 25],  # [padding_left, padding_top,padding_right, padding_bottom].
            pos_hint={"center_y": 0.5, "center_x": 0.5},
            background="resources/card_back.png",
            elevation=1

        )
        workout_name = MDLabel(
            text=msg,
            halign='center',
            font_style="Subtitle2",
            size_hint=(1, 0.1),
            theme_text_color="Custom",
            text_color=self.app.text_color
        )

        excCard.add_widget(workout_name)
        new_card_layout.add_widget(excCard)
        try:
            if self.ids.sets_grid == layout:
                dict_of_row_height = {0: 250}
                layout.rows_minimum = dict_of_row_height
        except:
            pass
        layout.clear_widgets()
        layout.add_widget(new_card_layout)

    def create_card(self, session, num_of_session, total_session_num, session_workout_name, session_date):
        new_card_layout = MDFloatLayout()  # for centering

        excCard = MDCard(
            spacing=5,
            radius=[80],
            orientation="vertical",
            size_hint=(0.87, 0.97),
            padding=[25, 16, 15, 25],  # [padding_left, padding_top,padding_right, padding_bottom].
            pos_hint={"center_y": 0.5, "center_x": 0.5},
            background="resources/card_back.png",
            elevation=1

        )

        # help_layout = self.create_top_card_layout(num_of_exc, num_of_exc_total, exc)
        # excCard.add_widget(help_layout)

        excnum = str(num_of_session + 1) + " of " + str(total_session_num)

        exc_num = MDLabel(
            text="    " + excnum,
            font_style="Caption",
            theme_text_color="Secondary",
            pos_hint={"center_y": 0.85, "center_x": 0.17}
        )
        # help_layout.add_widget(exc_num)
        # excCard.add_widget(help_layout)
        name_layout_y_size = 1.5
        if len(session_workout_name) > 9:
            name_layout_y_size = 3
        name_layout = MDGridLayout(rows=1, cols=3, size_hint_y=name_layout_y_size)
        workout = session_workout_name
        workout_name = MDLabel(
            text=workout,
            font_style="H5",
            theme_text_color="Custom",
            text_color=self.app.text_color,
            size_hint_x=1.5
        )
        workout_date = MDLabel(
            text=str(session_date),
            font_style="Caption",
            theme_text_color="Custom",
            text_color=self.app.text_color
        )
        name_layout.add_widget(workout_name)
        name_layout.add_widget(workout_date)
        name_layout.add_widget(exc_num)

        excCard.add_widget(name_layout)
        seperate = MDSeparator(height="1dp", color=self.app.text_color
                               )
        excCard.add_widget(seperate)

        # session = ["3   X   8", "3   X   8", "3   X   8", "3   X   8"]

        for num_of_set, set in enumerate(session):
            set_label, set_number, reps_label = self.create_set_label(set, num_of_set)

            exc_layout = MDGridLayout(rows=1, cols=2)
            units_layout = MDGridLayout(rows=1, cols=2, size_hint_y=1.5)
            exc_layout.add_widget(set_label)
            exc_layout.add_widget(set_number)
            units_layout.add_widget(MDLabel(text="", size_hint_x=0.9))
            units_layout.add_widget(reps_label)

            excCard.add_widget(exc_layout)
            excCard.add_widget(units_layout)

        new_card_layout.add_widget(excCard)
        return new_card_layout

    def choose_date(self):
        new_date = AKDatePicker(callback=self.new_date)
        new_date.open()
        print(new_date)

    def new_date(self, date):
        if not date:
            return
        new_date = '%d / %d / %d' % (date.day, date.month, date.year)
        if self.app.root.ids['previous_workouts_screen'].weight_history:
            self.load_weight_history(int(date.year), int(date.month))
        else:
            self.load_sessions(int(date.year), int(date.month))
