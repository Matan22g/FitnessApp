import json

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix import taptargetview
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.taptargetview import MDTapTargetView

from customKv.tab import MDTabsBase, MDTabs

import copy


class Tab(FloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''


class MDTabs_custom(MDTabs):
    '''Class implementing content for a tab.'''


class AddExerciseContent(BoxLayout):
    pass


class WorkoutScreen(Screen):
    workout_key = 0
    workout_name = "ABC"
    num_of_splits = 0
    workout = []  # original workout
    temp_workout = []  # used for creating or editing workout
    dialog = 0
    split_active = 1  # remeber which split the user clicked on
    del_button_id_by_exc = {}  # del_button.parent.parent is the md card
    exc_by_del_button = {}
    stats_button_id_by_exc = {}  # not used yet
    exc_by_stats_button = {}
    edit_mode = 0
    exc_to_del = ""
    tabs_by_split = {}
    create_mode = 0  # used when creating new workout
    tap_target_view = 0
    exc_limit = 15
    split_limit = 7

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_enter(self, *args):
        self.app.root.ids['workoutscreen'].ids["split_tabs"].switch_tab("Split 1")
        if self.create_mode:
            # self.start_add_split_animation()
            if not self.app.workoutsParsed:
                Clock.schedule_once(self.start_add_split_animation, .1)

    # def on_pre_leave(self, *args):
    #     self.app.clear_canvas()
    #     self.app.add_top_canvas()

    def on_leave(self, *args):
        # always deleting all splits and remaining with one tab.
        self.reset_tabs()

    def stop_add_split_animation(self):
        if self.is_animation_running():
            self.app.root.ids['workoutscreen'].tap_target_view.stop()

    def is_animation_running(self):
        print(self.app.root.ids['workoutscreen'].tap_target_view.state)
        if self.app.root.ids['workoutscreen'].tap_target_view.state == 'close':
            return False
        return True

    def start_add_split_animation(self, *args):
        self.app.root.ids['workoutscreen'].tap_target_view.start()

    def on_pre_enter(self, *args):
        try:
            self.app.add_bottom_canvas()
        except:
            print("on sign up")
        self.app.root.ids['workoutscreen'].tap_target_view = MDTapTargetView(
            widget=self.ids.add_split,
            title_text="Add Splits",
            description_text="press this button to add split days",
            widget_position="right_top",
            target_circle_color=(1, 0, 0)
        )
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
            self.app.change_title("Building: " + self.workout_name)
            self.app.root.ids['toolbar'].right_action_items = [['help', lambda x: self.app.show_workout_help()]]

        else:
            self.switch_mode("view")
            screen_manager = self.app.root.ids['screen_manager1']

            if screen_manager.current == "workoutscreen":
                self.app.root.ids['toolbar'].right_action_items = [
                    ['dots-vertical', lambda x: self.app.open_workout_menu()]]
            workout_key_to_view = self.app.workout_key_to_view
            workout_to_view = list(self.app.workoutsParsed[workout_key_to_view][0].values())
            workout_name = list(self.app.workoutsParsed[workout_key_to_view][0].keys())[0]

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

    def show_no_exc(self, to_show):
        if to_show:
            self.app.root.ids['workoutscreen'].ids["down_arrow_icon"].opacity = 1
            self.app.root.ids['workoutscreen'].ids["add_exc_label"].opacity = 1
        else:
            self.app.root.ids['workoutscreen'].ids["down_arrow_icon"].opacity = 0
            self.app.root.ids['workoutscreen'].ids["add_exc_label"].opacity = 0

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
        screen_manager = self.app.root.ids['screen_manager1']
        # if screen_manager.current != "workoutscreen" and screen_manager.current != "sessionscreen" and screen_manager.current != "exercise_sessions_screen":
        #     self.app.root.ids['toolbar'].right_action_items = [
        #         ['menu', lambda x: self.app.root.ids['nav_drawer'].set_state()]]

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
        # used for loading all exercises when switching tabs.
        # also when the user switches modes. edit/view.

        # self.clear_tabs()
        if self.app.debug:
            print("EDIT MODE: ", self.edit_mode)
        if self.edit_mode:
            self.switch_mode("edit")
        else:
            self.switch_mode("view")
            self.temp_workout = copy.deepcopy(self.workout)

        # INSERT fix for slider being too short after delete -- try mimic pressing on first one
        # self.app.root.ids['workoutscreen'].ids["del_split"].text = "Split 1"

        self.load_exc(1)  # loading first split as defualt
        self.app.root.ids['workoutscreen'].split_active = 1
        self.app.root.ids['workoutscreen'].ids["split_tabs"].switch_tab("Split 1")

    def show_view_buttons(self, to_show):

        if to_show:
            screen_manager = self.app.root.ids['screen_manager1']

            if screen_manager.current == "workoutscreen":
                self.app.root.ids['toolbar'].right_action_items = [
                    ['dots-vertical', lambda x: self.app.open_workout_menu()]]

            screen_manager = self.app.root.ids['screen_manager1']
            # if screen_manager.current == "workoutscreen":
            #     self.app.root.ids['toolbar'].right_action_items = [
            #         ['menu', lambda x: self.app.root.ids['nav_drawer'].set_state()]]
            self.show_exc_del_buttons(False)
            self.show_exc_stats_buttons(True)
            self.app.root.ids['workoutscreen'].ids["split_tabs"].size_hint = (0.9, .65)
            self.app.root.ids['workoutscreen'].ids["start_session"].opacity = 1
            self.app.root.ids['workoutscreen'].ids["start_session"].text_color = (1, 1, 2, 1)
            self.app.root.ids['workoutscreen'].ids["start_session"].disabled = False

            # self.app.root.ids['workoutscreen'].ids["buttons_layout"].opacity = 1
            # self.app.root.ids['workoutscreen'].ids["buttons_layout"].disabled = False

        else:
            self.app.root.ids['workoutscreen'].ids["start_session"].opacity = 0
            self.app.root.ids['workoutscreen'].ids["start_session"].disabled = True

            # self.app.root.ids['workoutscreen'].ids["buttons_layout"].opacity = 0
            # self.app.root.ids['workoutscreen'].ids["buttons_layout"].disabled = True

    def show_edit_buttons(self, to_show):
        if to_show:
            # self.app.root.ids['workoutscreen'].ids["split_tabs"].size_hint = (1, .65)
            # self.app.root.ids['toolbar'].right_action_items = [
            #     ['content-save', lambda x: self.show_save_workout_dialog()]]
            self.app.root.ids['toolbar'].right_action_items = [['help', lambda x: self.app.show_workout_help()]]

            self.show_exc_del_buttons(True)
            self.show_exc_stats_buttons(False)
            self.app.root.ids['workoutscreen'].ids["split_tabs"].size_hint = (0.82, .65)

            # self.app.root.ids['workoutscreen'].ids["add_exc"].opacity = 1
            # self.app.root.ids['workoutscreen'].ids["add_exc"].disabled = False
            # self.app.root.ids['workoutscreen'].ids["add_exc"].text_color = (1, 1, 1, 1)

            self.app.root.ids['workoutscreen'].ids["add_split"].opacity = 1
            self.app.root.ids['workoutscreen'].ids["add_split"].disabled = False

            # self.app.root.ids['workoutscreen'].ids["del_split"].opacity = 1
            # self.app.root.ids['workoutscreen'].ids["del_split"].disabled = False
            # self.app.root.ids['workoutscreen'].ids["del_split"].text_color = (1, 1, 1, 1)

            self.ids["edit_grid"].opacity = 1
            self.ids["edit_grid"].disabled = False
            self.ids["edit_grid"].pos_hint = {"center_x": .5, "top": .12 - self.app.bottom_buttons_inc}

        else:
            self.ids["edit_grid"].opacity = 0
            self.ids["edit_grid"].disabled = True
            self.ids["edit_grid"].pos_hint = {"center_x": .5, "top": .0}

            # self.app.root.ids['workoutscreen'].ids["add_exc"].opacity = 0
            # self.app.root.ids['workoutscreen'].ids["add_exc"].disabled = True

            self.app.root.ids['workoutscreen'].ids["add_split"].opacity = 0
            self.app.root.ids['workoutscreen'].ids["add_split"].disabled = True

            # self.app.root.ids['workoutscreen'].ids["del_split"].opacity = 0
            # self.app.root.ids['workoutscreen'].ids["del_split"].disabled = True

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
        split_limit = self.split_limit
        if self.num_of_splits > split_limit - 1:
            self.app.show_ok_msg(self.app.dismiss_dialog, "Limit Reached",
                                 "Cant have more than " + str(self.split_limit) + " splits")
            return
        self.num_of_splits = len(self.app.root.ids['workoutscreen'].ids["split_tabs"].get_tab_list()) + 1
        if self.app.debug:
            print("trying to add split")
            print("num of split to add:", self.num_of_splits)
        # tab = Tab(text=f"[size=70]Split {self.num_of_splits}[/size]")
        tab = Tab(text="[size=" + str(self.app.headline_text_size) + f"]Split {self.num_of_splits}[/size]")

        self.app.root.ids['workoutscreen'].ids["split_tabs"].add_widget(tab)
        # in case of new split space for new exercises being saved
        if len(self.temp_workout) < self.num_of_splits:
            self.temp_workout.append([])
        self.reload_page()

    def on_tab_switch(self, *args):
        """  args 3 = ['[size=100]Split', '1[/size]'] """

        split_chosen = args[3]
        split_chosen = split_chosen.split()
        split_chosen = int(split_chosen[1][0])
        self.load_exc(split_chosen)
        self.split_active = split_chosen
        # self.app.root.ids['workoutscreen'].ids["del_split"].text = "Split " + str(split_chosen)
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
            dict_of_row_height[i] = 270
        self.ids.exc_cards.rows_minimum = dict_of_row_height

    def load_exc(self, split):
        if self.edit_mode:
            workout = self.temp_workout
        else:
            workout = self.workout
        if len(workout) > split - 1:
            workout = workout[split - 1]
            num_of_exc_total = len(workout)

            if not num_of_exc_total:
                self.show_no_exc(True)
            else:
                self.show_no_exc(False)

            exercises_layout = self.ids.exc_cards
            exercises_layout.clear_widgets()
            # self.calc_exc_row_height(split)
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
            spacing=2,
            radius=[80],
            orientation="vertical",
            size_hint=(0.95, 0.8),
            padding=[20, 0, 0, 20],  # [padding_left, padding_top,padding_right, padding_bottom].
            pos_hint={"center_y": 0.5, "center_x": 0.5},
            background="resources/card_back.png"
        )

        help_layout = MDGridLayout(rows=1, cols=2, size_hint_y=0.4)
        excnum = str(num_of_exc + 1) + " of " + str(num_of_exc_total)
        exc_num = MDLabel(
            text=excnum,
            font_style="Caption",
            theme_text_color="Secondary",
        )
        del_Button = MDIconButton(
            icon="trash-can-outline",
            theme_text_color="Custom",
            text_color=self.app.text_color,
            on_release=self.show_del_exercise_dialog,
        )

        self.del_button_id_by_exc[exc] = del_Button
        self.exc_by_del_button[del_Button] = exc

        help_layout.add_widget(exc_num)
        help_layout.add_widget(del_Button)
        excCard.add_widget(help_layout)

        name_layout = MDGridLayout(rows=1, cols=2,
                                   padding=[0, 10, 0, 25])  # [padding_left, padding_top,padding_right, padding_bottom])
        exc_name = MDLabel(
            text=exc,
            font_style="H5",
            theme_text_color="Custom",
            text_color=self.app.text_color
        )

        # consider hiding option
        sButton = MDIconButton(
            icon="history",
            theme_text_color="Custom",
            text_color=self.app.theme_cls.primary_color,
            on_release=self.show_exc_history,
        )

        self.stats_button_id_by_exc[exc] = sButton
        self.exc_by_stats_button[sButton] = exc

        name_layout.add_widget(exc_name)
        name_layout.add_widget(sButton)

        excCard.add_widget(name_layout)
        card_layout.add_widget(excCard)
        return card_layout

    def show_exc_history(self, *args):
        exc_name = args[0].parent.children[1].text
        self.app.show_exc_history(exc_name)



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
        split_to_add = self.split_active
        exc_limit = self.exc_limit
        num_of_exc_in_split = len(self.temp_workout[split_to_add - 1])
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
        split_to_add = self.split_active
        new_exercise = args[0].parent.parent.parent.children[2].children[0].children[0].text

        # If the user hasnt written any name, dont do nothing.
        if new_exercise:
            self.temp_workout[split_to_add - 1].append(new_exercise)
            self.load_exc(split_to_add)
            self.dialog.dismiss()
            new_card = self.del_button_id_by_exc[new_exercise].parent.parent
            if len(self.temp_workout) > 5:
                self.ids.scroll.scroll_to(new_card, padding=10, animate=True)

    def show_del_exercise_dialog(self, *args):
        del_button = args[0]
        exc_name = self.exc_by_del_button[del_button]
        self.exc_to_del = exc_name
        
        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
                               title="Delete " + exc_name + "?",
                               buttons=[

                                   MDFlatButton(
                                       text="CANCEL", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.cancel_exc_del
                                   ),
                                   MDFlatButton(
                                       text="DELETE", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.del_exc
                                   ),
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
        # split_to_del = self.split_active
        split_to_del = self.num_of_splits

        if self.num_of_splits > 1:
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
                                   title="Delete " + "Split " + str(split_to_del) + "?",
                                   buttons=[

                                       MDFlatButton(
                                           text="CANCEL", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.dismiss_dialog
                                       ),
                                       MDFlatButton(
                                           text="DELETE", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.del_active_split
                                       ),
                                   ],
                                   )
        else:
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
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
        # self.del_split(self.app.root.ids['workoutscreen'].split_active)
        self.del_split(self.app.root.ids['workoutscreen'].num_of_splits)

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
            tab.text = "[size=" + str(self.app.headline_text_size) + "]Split " + str(split_num + 1) + "[/size]"

        self.num_of_splits = len(self.app.root.ids['workoutscreen'].ids["split_tabs"].get_tab_list())
        self.reload_page()

    def leave_in_middle_edit_workout(self):
        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
                               title="Are you sure you want to quit?",
                               text= "You will lose all unsaved progress.",
                               buttons=[

                                   MDFlatButton(
                                       text="EXIT", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.cancel_edit_mode
                                   ),
                                   MDFlatButton(
                                       text="STAY", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.dismiss_dialog
                                   ),
                               ],
                               )
        self.dialog.open()

    def cancel_edit_mode(self, *args):
        self.dismiss_dialog()
        if self.app.root.ids['workoutscreen'].create_mode:
            # self.app.root.ids['toolbar'].right_action_items = [
            #     ['menu', lambda x: self.app.root.ids['nav_drawer'].set_state()]]
            self.edit_mode = 0
            self.app.root.ids['workoutscreen'].create_mode = 0
            self.app.root.ids['bottom_nav'].switch_tab('1')
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

    def start_session(self, *args):
        try:
            self.dismiss_dialog()
        except:
            print("no dialog was open")
        self.app.start_workout(self.workout_key, self.split_active)

    def show_start_workout_dialog(self):
        self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
                               title="Start a new session?",
                               text="Starting a new session will delete the current running session data",
                               buttons=[

                                   MDFlatButton(
                                       text="CANCEL", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.dismiss_dialog
                                   ),
                                   MDFlatButton(
                                       text="START", text_color=self.app.theme_cls.primary_color,
                                       on_release=self.start_session
                                   ),
                               ],
                               )
        self.dialog.open()

    def show_save_workout_dialog(self):

        if self.valid_workout():
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
                                   title="Save " + self.workout_name + "?",
                                   buttons=[

                                       MDFlatButton(
                                           text="CANCEL", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.dismiss_dialog
                                       ),
                                       MDFlatButton(
                                           text="SAVE", text_color=self.app.theme_cls.primary_color,
                                           on_release=self.save_workout
                                       ),
                                   ],
                                   )
        else:
            self.dialog = MDDialog(radius=[10, 7, 10, 7], size_hint=(0.9, 0.2),
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
        Workout = "[{%s: %s},%s]" % (
        '"' + workout_name + '"', '"' + str(workout_exc) + '"', '"' + str(self.app.today_date) + '"')
        data = json.dumps(Workout)

        if self.create_mode:
            self.create_mode = 0
            self.app.root.ids['workoutscreen'].create_mode = 0
            link = "https://gymbuddy2.firebaseio.com/%s/workouts.json?auth=%s" % (self.app.local_id, self.app.id_token)
            self.app.upload_data(data, link, 1)
            self.app.root.ids['workoutscreen'].edit_mode = 0

        else:
            link = "https://gymbuddy2.firebaseio.com/%s/workouts/%s.json?auth=%s" % (
            self.app.local_id, workout_key, self.app.id_token)
            self.app.upload_data(data, link, 2, workout_key)
            self.app.root.ids['workoutscreen'].edit_mode = 0

        self.dismiss_dialog()
        self.workout_key = 0

    def test(self, *args):
        print(3)
