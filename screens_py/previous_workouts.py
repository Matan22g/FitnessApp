from datetime import datetime
import calendar

from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
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
        delete_mode = app.root.ids['previous_workouts_screen'].delete_mode
        check_box_list = app.root.ids['previous_workouts_screen'].session_card_by_checkBox
        if not delete_mode:
            app.root.ids['previous_workouts_screen'].view_session(self.card_id)
        else:
            check_box = self.card_id.children[2].children[1]
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

        self.show_checkbox(False)
        self.load_sessions(curr_year, curr_month)
        self.fix_grid_heights()

    def load_sessions(self, year, month):
        if self.app.debug:
            print("loading sessions of", year, month)

        sessions_layout = self.ids.sessions_grid
        sessions_layout.clear_widgets()

        month_abb = calendar.month_abbr[month]
        self.app.root.ids['previous_workouts_screen'].ids["month_to_view"].text = month_abb + ", " + str(year)

        if year in self.app.sessions_by_month_year and month in self.app.sessions_by_month_year[year]:
            sessions_dates = self.app.sessions_by_month_year[year][month]
        else:
            msg = "No sessions available for " + month_abb + ", " + str(year)
            self.no_sessions_grid(msg, sessions_layout)
            return
        dict_of_row_height = {0: 100}
        sessions_layout.rows_minimum = dict_of_row_height

        total_session_num = len(sessions_dates)
        # for i in range(total_session_num):
        #     dict_of_row_height[i] = 100
        # sessions_layout.rows_minimum = dict_of_row_height

        for i, sessions_date in enumerate(sessions_dates):
            session = self.app.sessions[sessions_date]
            new_card_layout = self.create_card(i, total_session_num, session.workout_name, session.date,
                                               session.duration, sessions_date)
            sessions_layout.add_widget(new_card_layout)

    def create_card(self, num_of_session, total_session_num, session_workout_name, session_date, session_duration,
                    sessions_date_key):
        new_card_layout = MDFloatLayout()  # for centering
        help_layout = MDGridLayout(size_hint_y=0.05, rows=1, cols=3)

        excCard = LongPressCard(
            spacing=10,
            radius=[14],
            orientation="vertical",
            size_hint=(0.87, 0.97),
            padding=[11, 16, 0, 17],  # [padding_left, padding_top,padding_right, padding_bottom].
            pos_hint={"center_y": 0.5, "center_x": 0.5},
            elevation=1,
            long_press_time=0.5,
            on_long_press=lambda w: setattr(w, 'text', 'long press!')
        )
        excCard.card_id = excCard
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
        deleteBox = MDCheckbox(
            size_hint=(0.5, 0.3)
        )
        deleteBox.opacity = 0
        self.session_card_by_checkBox[deleteBox] = excCard
        session_date = session_date.ctime()[0:10]
        session_date = session_date[0:3] + "," + session_date[3:]
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
            text_color=[0, 0, 0, 1]
        )
        workout_duration_label = MDLabel(
            text=session_duration,
            font_style="Caption",
            size_hint=(0.3, 0.1),
            theme_text_color="Secondary",
        )

        help_layout.add_widget(date_label)
        help_layout.add_widget(deleteBox)
        help_layout.add_widget(exc_num)

        excCard.add_widget(help_layout)
        excCard.add_widget(workout_name_label)
        excCard.add_widget(workout_duration_label)

        new_card_layout.add_widget(excCard)
        self.session_key_by_card[excCard] = sessions_date_key
        return new_card_layout

    def view_session(self, *args):
        workout_card = args[0]
        sessions_date_key = self.session_key_by_card[workout_card]
        self.app.view_session(sessions_date_key)

    def show_checkbox(self, to_show):

        self.app.root.ids['previous_workouts_screen'].ids["num_to_delete"].text = ""
        if to_show == "False" or not to_show:
            to_show = 0
        else:
            to_show = 1

        if to_show:
            self.app.root.ids['previous_workouts_screen'].delete_mode = 1
            self.ids["date_button"].opacity = 0
            self.ids["date_button"].disabled = True
            self.ids["delete_sessions"].opacity = 1
            self.ids["delete_sessions"].disabled = False

        else:
            self.app.root.ids['previous_workouts_screen'].delete_mode = 0
            self.ids["date_button"].opacity = 1
            self.ids["date_button"].disabled = False
            self.ids["delete_sessions"].opacity = 0
            self.ids["delete_sessions"].disabled = True

        for checkbox_id in self.session_card_by_checkBox:
            checkbox_id.active = 0
            if to_show:
                checkbox_id.opacity = 1
            else:
                checkbox_id.opacity = 0

    # def delete_selected(self):
    #     print("trying to delete")

    def show_del_exercise_dialog(self):
        num_to_del = self.app.root.ids['previous_workouts_screen'].ids["num_to_delete"].text
        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.7, None),
                               title="Select session to delete",
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

                self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.7, None),
                                       title=msg,
                                       text=warning,
                                       buttons=[
                                           MDFlatButton(
                                               text="DELETE", text_color=self.app.theme_cls.primary_color,
                                               on_release=self.del_session
                                           ),
                                           MDFlatButton(
                                               text="CANCEL", text_color=self.app.theme_cls.primary_color,
                                               on_release=self.cancel_del_exc
                                           )
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
                self.app.del_session(session_key)

        self.on_pre_enter()
        Snackbar(text="Session Deleted!").show()
        self.show_checkbox(False)

    def fix_grid_heights(self):
        grid = self.ids.sessions_grid
        self.ids.sessions_grid.height = sum(x.height for x in grid.children)

    def cancel_del_exc(self, caller):
        self.dialog.dismiss()
