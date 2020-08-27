from datetime import datetime
import calendar

from akivymd.uix.datepicker import AKDatePicker
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.behaviors import TouchBehavior
from kivymd.uix.card import MDCard
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import ThreeLineAvatarIconListItem
from screens_py.exercise_sessions import ExerciseSessionsScreen

from kivy.base import runTouchApp
from kivy.clock import Clock
from kivy.factory import Factory


class LongPressCard(MDCard):
    __events__ = ('on_long_press',)
    long_press = 0
    long_press_time = Factory.NumericProperty(1)
    key = Factory.NumericProperty(1)

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
        print(2)
        self.long_press = 1

    def on_short_press(self, *largs):
        view_session(self.key)

def view_session(sessions_date_key):
    print(sessions_date_key)
    key=MDApp.get_running_app().root.ids['previous_workouts_screen'].keys_by_num[sessions_date_key]
    MDApp.get_running_app().view_session(key)

    # self.app.del_session(sessions_date_key)


class PreviousWorkoutsScreen(Screen):

    workout_key_by_card = {}
    choose_date = ExerciseSessionsScreen.choose_date
    new_date = ExerciseSessionsScreen.new_date
    no_sessions_grid = ExerciseSessionsScreen.no_sessions_grid
    nearest = ExerciseSessionsScreen.nearest
    keys_by_num = {}

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self, *args):
        today = datetime.today()
        curr_month = int(today.month)
        curr_year = int(today.year)

        if self.app.sessions_by_month_year:
            if curr_year not in self.app.sessions_by_month_year:
                curr_year = self.nearest(list(self.app.sessions_by_month_year.keys()), curr_year)
            if curr_month not in self.app.sessions_by_month_year[curr_year]:
                curr_month = self.nearest(self.app.sessions_by_month_year[curr_year], curr_month)

            ##### TEST EMPTY MONTHS AND YEAR

        self.load_sessions(curr_year,curr_month)


    def load_sessions(self, year , month):
        print("loading sessions of", year, month)

        sessions_layout = self.ids.sessions_grid
        sessions_layout.clear_widgets()

        month_abb = calendar.month_abbr[month]
        self.app.root.ids['previous_workouts_screen'].ids["month_to_view"].text = month_abb+ ", " + str(year)

        if year in self.app.sessions_by_month_year and month in self.app.sessions_by_month_year[year]:
            sessions_dates = self.app.sessions_by_month_year[year][month]
        else:
            msg = "No sessions available for " + month_abb + ", " + str(year)
            self.no_sessions_grid(msg, sessions_layout)
            return

        total_session_num = len(sessions_dates)
        self.keys_by_num = {}

        for i, sessions_date in enumerate(sessions_dates):
            self.keys_by_num[i]=sessions_date
            session = self.app.sessions[sessions_date]
            new_card_layout = self.create_card(i, total_session_num, session.workout_name, session.date, session.duration,sessions_date)
            sessions_layout.add_widget(new_card_layout)

    def create_card(self, num_of_session, total_session_num, session_workout_name, session_date, session_duration, sessions_date_key):
        new_card_layout = MDFloatLayout()  # for centering
        help_layout = MDGridLayout(size_hint_y=0.05, rows=1, cols=2)


        excCard = LongPressCard(
            spacing=10,
            radius=[14],
            orientation="vertical",
            size_hint=(0.87, 0.97),
            padding=[11, 16, 0, 17],  # [padding_left, padding_top,padding_right, padding_bottom].
            pos_hint={"center_y": 0.5, "center_x": 0.5},
            elevation=1,
            long_press_time=0.5,
            on_long_press=lambda w: setattr(w, 'text', 'long press!'),
            on_short_press= self.view_session,
            key = num_of_session
        )

        # help_layout = self.create_top_card_layout(num_of_exc, num_of_exc_total, exc)
        # excCard.add_widget(help_layout)

        excnum = str(num_of_session + 1) + " of " + str(total_session_num)
        # workout_date = "Mon, 15 Jul"
        # workout_name = "ABC"
        # workout_duration = "44 mins"
        exc_num = MDLabel(
            text=excnum,
            font_style="Caption",
            size_hint=(0.3, 0.1),
            theme_text_color="Secondary",
        )

        session_date = session_date.ctime()[0:10]
        session_date = session_date[0:3]+ "," + session_date[3:]
        date_label = MDLabel(
            text=session_date,
            font_style="Subtitle2",
            size_hint=(0.97, 0.1),
            theme_text_color="Custom",
            text_color=self.app.theme_cls.primary_color
        )
        workout_name_label = MDLabel(
            text=session_workout_name,
            font_style="H5",
            theme_text_color="Custom",
            text_color=[0,0,0,1]
        )
        workout_duration_label = MDLabel(
            text=session_duration,
            font_style="Caption",
            size_hint=(0.3, 0.1),
            theme_text_color="Secondary",
        )

        help_layout.add_widget(date_label)
        help_layout.add_widget(exc_num)
        excCard.add_widget(help_layout)
        excCard.add_widget(workout_name_label)
        excCard.add_widget(workout_duration_label)

        new_card_layout.add_widget(excCard)
        self.workout_key_by_card[excCard] = sessions_date_key
        return new_card_layout




    def view_session(self, *args):
        print(args)
        workout_card = args[0]
        sessions_date_key = self.workout_key_by_card[workout_card]
        self.app.view_session(sessions_date_key)
        # self.app.del_session(sessions_date_key)

