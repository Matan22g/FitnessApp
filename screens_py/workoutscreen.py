from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.tab import MDTabsBase
import copy

class Tab(FloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''

    def on_touch_down(self, touch):
        print(touch)
        '''Receive a touch down event.

        :Parameters:
            `touch`: :class:`~kivy.input.motionevent.MotionEvent` class
                Touch received. The touch is in parent coordinates. See
                :mod:`~kivy.uix.relativelayout` for a discussion on
                coordinate systems.

        :Returns: bool
            If True, the dispatching of the touch event will stop.
            If False, the event will continue to be dispatched to the rest
            of the widget tree.
        '''
        if self.collide_point(touch.x, touch.y):
            print('down')

        if self.disabled and self.collide_point(*touch.pos):
            print("hereerererererereereeeeeeeeeeeeeeee")
            return True
        for child in self.children[:]:
            if child.dispatch('on_touch_down', touch):
                print("nanananananaannnaanan")

                return True

class AddExerciseContent(BoxLayout):
    pass

class WorkoutScreen(Screen):
    workout_key = 0
    workout_name = "ABC"
    num_of_splits = 0
    workout = []
    temp_workout = []
    dialog = 0
    split_active = 1
    del_button_id_by_exc = {}  # del_button.parent.parent is the md card
    exc_by_del_button = {}
    stats_button_id_by_exc = {}
    exc_by_stats_button = {}
    edit_mode = 0
    exc_to_del = ""
    tabs_by_split = {}
    create_mode = 0
    first_tab = 0
    tabs_label_by_tab = {}
    # tabs_id_by_split = {}

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()


    def on_enter(self, *args):
        self.app.root.ids['workoutscreen'].ids["split_tabs"].switch_tab("Split 1")

    def on_leave(self, *args):
        self.reset_tabs()
    def on_pre_enter(self, *args):

        self.app.change_title(self.workout_name)

        if self.app.debug:
            print("entering workout screen")
            print("create mode:", self.create_mode)
            print("edit mode:", self.edit_mode)
            print("temp_workout", self.temp_workout)
            print("workout", self.workout)
            print("workout name", self.workout_name)

        if self.app.root.ids['workoutscreen'].create_mode:
            if self.app.debug:
                print("entering workout screen")
                if self.create_mode:
                    print("In create mode:")
            self.switch_mode("edit")
            self.temp_workout = [[]]
            self.reset_tabs()
            self.reload_page()

        else:
            self.switch_mode("view")

            workout_key_to_view = self.app.workout_key_to_view
            workout_to_view = list(self.app.workoutsParsed[workout_key_to_view].values())
            workout_name = list(self.app.workoutsParsed[workout_key_to_view].keys())[0]

            self.workout_name = workout_name
            self.workout_key = workout_key_to_view
            self.workout = workout_to_view[0]
            self.app.change_title(self.workout_name)

            self.temp_workout = copy.deepcopy(self.workout)
            self.reset_tabs()

            if self.app.debug:
                print("In VIEW mode:")
                print("workout to load", workout_to_view)
                print("workout_key", self.workout_key)
                print("temp_workout", self.temp_workout)
                print("workout", self.workout)
                print("workout name", self.workout_name)
                print("TRYING TO RELOAD")

            self.set_split_tabs()
            self.reload_page()
            self.app.root.ids['workoutscreen'].workout_key = self.app.workout_key_to_view
            self.app.root.ids['workoutscreen'].ids["split_tabs"].switch_tab("Split 1")

    def reset_tabs(self):
        # reseting to one tab in case of create workout, or to original workout, in case of exit edit.

        if self.app.debug:
            print("trying to reset tabs:")
        num_of_tabs = len(self.app.root.ids['workoutscreen'].ids["split_tabs"].get_tab_list())
        if self.app.debug:
            print("num of tabs on tabs list:", num_of_tabs)
        if num_of_tabs > 1:
            if self.app.debug:
                print("theres more than 1 tab, so deleting the rest")
            min_amount = 1
            while num_of_tabs > min_amount:
                self.del_split(num_of_tabs)
                num_of_tabs -= 1
        elif not num_of_tabs:
            self.add_split()

    def switch_mode(self, mode):
        if mode == "view":
            self.edit_mode = 0
            self.show_view_buttons(True)
            self.show_edit_buttons(False)
        else:
            self.edit_mode = 1
            self.show_view_buttons(False)
            self.show_edit_buttons(True)

    def reload_page(self):
        # self.clear_tabs()
        if self.app.debug:
            print("EDIT MODE: ", self.edit_mode)
        if self.edit_mode:
            self.switch_mode("edit")
        else:
            self.switch_mode("view")
            self.temp_workout = copy.deepcopy(self.workout)

        # INSERT fix for slider being too short after delete -- try mimic pressing on first one
        self.app.root.ids['workoutscreen'].ids["del_split"].text = "Split 1"

        self.load_exc(1)  # loading first split as defualt
        self.app.root.ids['workoutscreen'].split_active = 1
        self.app.root.ids['workoutscreen'].ids["split_tabs"].switch_tab("Split 1")

    def show_view_buttons(self, to_show):

        if to_show:
            screen_manager = self.app.root.ids['screen_manager1']
            if screen_manager.current == "workoutscreen":
                self.app.root.ids['toolbar'].right_action_items = [
                    ['menu', lambda x: self.app.root.ids['nav_drawer'].set_state()]]
            self.show_exc_del_buttons(False)
            self.show_exc_stats_buttons(True)
            self.app.root.ids['workoutscreen'].ids["split_tabs"].size_hint = (1, .65)
            self.app.root.ids['workoutscreen'].ids["edit_workout"].opacity = 1
            self.app.root.ids['workoutscreen'].ids["edit_workout"].disabled = False
            self.app.root.ids['workoutscreen'].ids["start_session"].opacity = 1
            self.app.root.ids['workoutscreen'].ids["start_session"].disabled = False
        else:
            self.app.root.ids['workoutscreen'].ids["edit_workout"].opacity = 0
            self.app.root.ids['workoutscreen'].ids["edit_workout"].disabled = True
            self.app.root.ids['workoutscreen'].ids["start_session"].opacity = 0
            self.app.root.ids['workoutscreen'].ids["start_session"].disabled = False

    def show_edit_buttons(self, to_show):
        if to_show:
            # self.app.root.ids['workoutscreen'].ids["split_tabs"].size_hint = (1, .65)
            self.app.root.ids['toolbar'].right_action_items = [
                ['content-save', lambda x: self.show_save_workout_dialog()]]
            self.show_exc_del_buttons(True)
            self.show_exc_stats_buttons(False)
            self.app.root.ids['workoutscreen'].ids["split_tabs"].size_hint = (0.825, .65)

            self.app.root.ids['workoutscreen'].ids["add_exc"].opacity = 1
            self.app.root.ids['workoutscreen'].ids["add_exc"].disabled = False
            self.app.root.ids['workoutscreen'].ids["add_exc"].text_color = self.app.theme_cls.primary_color

            self.app.root.ids['workoutscreen'].ids["add_split"].opacity = 1
            self.app.root.ids['workoutscreen'].ids["add_split"].disabled = False

            self.app.root.ids['workoutscreen'].ids["del_split"].opacity = 1
            self.app.root.ids['workoutscreen'].ids["del_split"].disabled = False
            self.app.root.ids['workoutscreen'].ids["del_split"].text_color = self.app.theme_cls.primary_color

        else:
            self.app.root.ids['workoutscreen'].ids["add_exc"].opacity = 0
            self.app.root.ids['workoutscreen'].ids["add_exc"].disabled = True

            self.app.root.ids['workoutscreen'].ids["add_split"].opacity = 0
            self.app.root.ids['workoutscreen'].ids["add_split"].disabled = True

            self.app.root.ids['workoutscreen'].ids["del_split"].opacity = 0
            self.app.root.ids['workoutscreen'].ids["del_split"].disabled = True

    def set_split_tabs(self):
        # setting the amount of tabs according to orig_workout_leng

        if self.app.debug:
            print("trying to set tabs:")
            print("current num_of_split:", self.num_of_splits)

        if self.num_of_splits > 1:
            self.num_of_splits = 1
        workout = self.workout
        if self.edit_mode:
            workout = self.temp_workout
        orig_workout_leng = len(workout)
        if orig_workout_leng:
            for i in range(orig_workout_leng - 1):
                self.add_split()

    def add_split(self):
        print("trying to add split")
        self.num_of_splits = len(self.app.root.ids['workoutscreen'].ids["split_tabs"].get_tab_list()) + 1
        print("num of split to add:", self.num_of_splits)

        tab = Tab(text=f"Split {self.num_of_splits}")
        self.app.root.ids['workoutscreen'].ids["split_tabs"].add_widget(tab)
        tabs_list = self.app.root.ids['workoutscreen'].ids["split_tabs"].get_tab_list()
        if self.num_of_splits == 1:
            print("initial tab", tab)
            self.first_tab = tabs_list[0]
        self.tabs_label_by_tab[tab] = tabs_list[0]

        # self.tabs_by_split[self.num_of_splits] = tab
        if len(self.temp_workout) < self.num_of_splits:
            self.temp_workout.append([])
        self.reload_page()

    def on_tab_switch(self, *args):

        split_chosen = args[3]
        split_chosen = int(split_chosen[6])
        self.load_exc(split_chosen)
        self.split_active = split_chosen
        self.app.root.ids['workoutscreen'].ids["del_split"].text = "Split " + str(split_chosen)

        if self.app.debug:
            print("switched to:", self.split_active)
            print("num of splits: ", self.num_of_splits)
            print("workout so far: ", self.temp_workout)
            print("original workout: ", self.workout)

        # self.on_pre_enter()
        # self.need_height_fix = 1
        # self.ids.scroll.scroll_y=0

    def calc_exc_row_height(self, split):
        if self.edit_mode:
            workout = self.temp_workout
        else:
            workout = self.workout
        dict_of_row_height = {}
        for i, exc in enumerate(workout[split - 1]):
            dict_of_row_height[i] = 125
        self.ids.exc_cards.rows_minimum = dict_of_row_height

    def load_exc(self, split):
        if self.edit_mode:
            workout = self.temp_workout
        else:
            workout = self.workout
        if len(workout) > split - 1:
            workout = workout[split - 1]
            num_of_exc_total = len(workout)
            exercises_layout = self.ids.exc_cards
            exercises_layout.clear_widgets()
            self.calc_exc_row_height(split)
            for num_of_exc, exc_name in enumerate(workout):
                card_layout = self.create_exc_card(exc_name, num_of_exc, num_of_exc_total)
                exercises_layout.add_widget(card_layout)
            if self.edit_mode:
                self.show_exc_del_buttons(True)
                self.show_exc_stats_buttons(False)
            else:
                self.show_exc_del_buttons(False)
                self.show_exc_stats_buttons(True)

    def create_exc_card(self, exc, num_of_exc, num_of_exc_total):

        card_layout = MDFloatLayout()  # for centering
        excCard = MDCard(
            spacing=5,
            radius=[14],
            orientation="vertical",
            size_hint=(0.95, 0.8),
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
        del_Button = MDIconButton(
            icon="trash-can-outline",
            user_font_size="25sp",
            theme_text_color="Custom",
            pos_hint={"center_y": 0.85, "center_x": 0.95},
            text_color=self.app.theme_cls.primary_color,
            on_release=self.show_del_exercise_dialog
        )

        self.del_button_id_by_exc[exc] = del_Button
        self.exc_by_del_button[del_Button] = exc

        help_layout.add_widget(exc_num)
        help_layout.add_widget(del_Button)
        excCard.add_widget(help_layout)

        name_layout = MDGridLayout(size_hint_y=0.1, rows=1, cols=2)
        exc_name = MDLabel(
            text=exc,
            font_style="H5",
            size_hint=(1, 0.1),
            theme_text_color="Custom",
            text_color=self.app.theme_cls.primary_color
        )

        # consider hiding option
        sButton = MDIconButton(
            icon="history",
            user_font_size="25sp",
            theme_text_color="Custom",
            text_color=self.app.theme_cls.primary_color,
            on_release=self.test
        )

        self.stats_button_id_by_exc[exc] = sButton
        self.exc_by_stats_button[sButton] = exc

        name_layout.add_widget(exc_name)
        name_layout.add_widget(sButton)

        excCard.add_widget(name_layout)
        card_layout.add_widget(excCard)
        return card_layout

    def show_exc_del_buttons(self, to_Show):
        for del_button_id in self.exc_by_del_button:
            if to_Show:
                del_button_id.opacity = 1
                del_button_id.disabled = False
            else:
                del_button_id.opacity = 0
                del_button_id.disabled = True

    def show_exc_stats_buttons(self, to_Show):
        for stats_button_id in self.exc_by_stats_button:
            if to_Show:
                stats_button_id.opacity = 1
                stats_button_id.disabled = False
            else:
                stats_button_id.opacity = 0
                stats_button_id.disabled = True

    def show_add_exercise_dialog(self):
        self.dialog = MDDialog(
            radius=[10, 7, 10, 7],
            size_hint=(0.9, 0.2),
            title="New Exercise:",
            type="custom",
            content_cls=AddExerciseContent(),
            buttons=[

                MDFlatButton(
                    text="OK",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=self.add_exercise
                ),
                MDFlatButton(
                    text="Cancel",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=self.dismiss_dialog
                )
            ],
        )
        self.dialog.open()

    def dismiss_dialog(self, *args):
        self.dialog.dismiss()

    def add_exercise(self, *args):
        split_to_add = self.split_active
        new_exercise = args[0].parent.parent.parent.children[2].children[0].children[0].text

        # If the user hasnt written any name, dont do nothing.
        if new_exercise:
            self.temp_workout[split_to_add - 1].append(new_exercise)
            self.load_exc(split_to_add)
            self.dialog.dismiss()
            new_card = self.del_button_id_by_exc[new_exercise].parent.parent
            self.ids.scroll.scroll_to(new_card, padding=10, animate=True)

    def show_del_exercise_dialog(self, *args):
        del_button = args[0]
        exc_name = self.exc_by_del_button[del_button]
        self.exc_to_del = exc_name
        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.7, None),
                               title="Delete " + exc_name + "?",
                               buttons=[
                                   MDFlatButton(
                                       text="DELETE", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.del_exc
                                   ),
                                   MDFlatButton(
                                       text="CANCEL", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.cancel_exc_del
                                   )
                               ],
                               )
        self.dialog.open()

    def cancel_exc_del(self, *args):
        self.dialog.dismiss()
        self.exc_to_del = ""

    def del_exc(self, *args):
        self.dialog.dismiss()
        exc_to_del = self.exc_to_del
        self.del_exc_info(exc_to_del)
        self.exc_to_del = ""

    def del_exc_info(self, exc_name):
        split_active = self.app.root.ids['workoutscreen'].split_active

        if self.app.debug:
            print("trying to delete info about:", exc_name)
            print("current active split:", split_active)
            print("exc split is:", self.temp_workout[split_active - 1])
        try:
            exc_card_id = self.del_button_id_by_exc[exc_name].parent.parent
            self.ids["exc_cards"].remove_widget(exc_card_id)
            del_button = self.del_button_id_by_exc.pop(exc_name, None)
            self.exc_by_del_button.pop(del_button, None)
            stats_button = self.stats_button_id_by_exc.pop(exc_name, None)
            self.exc_by_stats_button.pop(stats_button, None)
        except KeyError:
            print("keyerror", exc_name)
        if exc_name in self.temp_workout[split_active - 1]:
            self.temp_workout[split_active - 1].remove(exc_name)

        self.load_exc(split_active)

    def show_del_split_dialog(self, *args):
        if self.num_of_splits > 1:
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.7, None),
                                   title="Delete " + "Split " + str(self.split_active) + "?",
                                   buttons=[
                                       MDFlatButton(
                                           text="DELETE", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.del_active_split
                                       ),
                                       MDFlatButton(
                                           text="CANCEL", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.dismiss_dialog
                                       )
                                   ],
                                   )
        else:
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.7, None),
                                   title="Cant have 0 Splits",
                                   buttons=[
                                       MDFlatButton(
                                           text="OK", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.dismiss_dialog
                                       )
                                   ],
                                   )
        self.dialog.open()

    def del_active_split(self, *args):
        self.del_split(self.app.root.ids['workoutscreen'].split_active)

    def del_split(self, split_to_del):
        if self.app.debug:
            print("trying to delete split ", split_to_del)
            print("before delete: ", self.temp_workout)
        if self.dialog:
            self.dismiss_dialog()
        ind_of_split_to_del = (self.num_of_splits - split_to_del)

        if self.edit_mode:
            if len(self.temp_workout) >= split_to_del:
                for exc in self.temp_workout[split_to_del - 1]:
                    self.del_exc_info(exc)

        if len(self.temp_workout) >= split_to_del:
            self.temp_workout.pop(split_to_del - 1)
        if self.app.debug:
            print("after delete: ", self.temp_workout)

        self.app.root.ids['workoutscreen'].ids["split_tabs"].remove_widget(
            self.app.root.ids['workoutscreen'].ids["split_tabs"].get_tab_list()[ind_of_split_to_del])

        for split_num, tab in enumerate(reversed(self.app.root.ids['workoutscreen'].ids["split_tabs"].get_tab_list())):
            tab.text = "Split " + str(split_num + 1)

        self.num_of_splits = len(self.app.root.ids['workoutscreen'].ids["split_tabs"].get_tab_list())
        self.reload_page()

    def leave_in_middle_edit_workout(self):
        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.7, None),
                               title="You will lose all unsaved progress. Are you sure you want to quit?",
                               buttons=[
                                   MDFlatButton(
                                       text="Stay", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.dismiss_dialog
                                   ),
                                   MDFlatButton(
                                       text="Exit", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.cancel_edit_mode
                                   )
                               ],
                               )
        self.dialog.open()

    def cancel_edit_mode(self, *args):
        self.dismiss_dialog()
        if self.app.root.ids['workoutscreen'].create_mode:
            self.app.root.ids['toolbar'].right_action_items = [
                ['menu', lambda x: self.app.root.ids['nav_drawer'].set_state()]]
            self.edit_mode = 0
            self.app.root.ids['workoutscreen'].create_mode = 0
            self.app.change_screen1("homescreen")
        else:
            self.reset_tabs()
            self.edit_mode = 0
            self.on_pre_enter()

    def valid_workout(self):
        if self.app.debug:
            print("validing workout")
        full_splits = 0
        empty_splits = []
        for i, split in enumerate(self.temp_workout):
            if not split:
                empty_splits.append(i)
            else:
                full_splits += 1

        if full_splits:
            if self.app.debug:
                print("Theres one exc at least")
                print(self.temp_workout)
            self.temp_workout = [split for split in self.temp_workout if split]
            return True
        else:
            return False


    def switch_to_first_split(self):
        pass

    def start_session(self):
        self.app.start_workout(self.workout_key, self.split_active)

    def show_save_workout_dialog(self):

        if self.valid_workout():
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.7, None),
                                   title="Save " + self.workout_name + "?",
                                   buttons=[
                                       MDFlatButton(
                                           text="Save", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.save_workout
                                       ),
                                       MDFlatButton(
                                           text="CANCEL", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.dismiss_dialog
                                       )
                                   ],
                                   )
        else:
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.7, None),
                                   title="Cant save empty workout",
                                   buttons=[
                                       MDFlatButton(
                                           text="OK", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.dismiss_dialog
                                       )
                                   ],
                                   )
        self.dialog.open()

    def save_workout(self, *args):

        workout_name = self.workout_name
        workout_key = self.workout_key
        workout_exc = self.temp_workout
        if self.create_mode:
            self.create_mode = 0
            self.app.upload_new_workout(workout_name, workout_exc)
        else:
            self.app.update_existing_workout(workout_key, workout_name, workout_exc)
        self.dismiss_dialog()
        self.workout_key = 0

    def test(self, *args):
        print(3)
