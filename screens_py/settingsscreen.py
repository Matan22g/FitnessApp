from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.picker import MDThemePicker

from customKv.toggle_behavior import MDToggleButton


class MyToggleButton(MDRectangleFlatButton, MDToggleButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_down = (0, 0, 1, 1)
        self.background_normal = (0.5, 0.5, 0.5, 1)
        self.text_color = (1, 1, 1, 1)
        self.allow_no_selection = False


class SettingsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self, *args):
        self.app.change_title("Settings")
        self.app.root.ids['toolbar'].right_action_items = [['', lambda x: None]]

        if self.app.units == 'metric':
            self.ids.kg_button.md_bg_color = (0, 0, 1, 1)
            self.ids.lbs_button.md_bg_color = (0.5, 0.5, 0.5, 1)
        else:
            self.ids.lbs_button.md_bg_color = (0, 0, 1, 1)
            self.ids.kg_button.md_bg_color = (0.5, 0.5, 0.5, 1)

        self.ids.user_name_label.text = self.app.user_name

    def on_enter(self, *args):
        self.app.title = "Settings"

    def change_mode(self, checkbox, value):
        if value:
            self.app.theme_cls.theme_style = "Dark"
        else:
            self.app.theme_cls.theme_style = "Light"

    def show_theme_picker(self):
        theme_dialog = MDThemePicker()
        theme_dialog.open()