from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
Window.size = (420, 630)


# from kivymd.theming import ThemableBehavior
# from kivymd.uix.list import OneLineIconListItem, MDList
# from kivy.lang import Builder
# from kivy.uix.boxlayout import BoxLayout
# from kivy.properties import StringProperty

# name mainapp loads main kv file by default


class HomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"
        self.hint_binary_number = "fucking hint text"

    def on_enter(self, *args):
        self.app.title = "Home"

    def is_binary(self, binary_number):
        try:
            decimal = int(binary_number, 2)
            self.ids["solution"].text = f'Your Number in Binary: {decimal}'
            self.ids["solution"].theme_text_color = "Primary"
        except ValueError:
            self.ids["solution"].text = "This is not Binary"
            self.ids["solution"].theme_text_color = "Error"


class LoginScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome! \nPlease Log in"
        self.hint_username = "User Name"
        self.hint_password = "Password"

    def on_enter(self, *args):
        self.app.title = "Login"

    def is_binary(self, binary_number):
        try:
            decimal = int(binary_number, 2)
            self.ids["solution"].text = f'Your Number in Binary: {decimal}'
            self.ids["solution"].theme_text_color = "Primary"
        except ValueError:
            self.ids["solution"].text = "This is not Binary"
            self.ids["solution"].theme_text_color = "Error"


class SettingsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_enter(self, *args):
        self.app.title = "Settings"

    def change_mode(self, checkbox, value):
        if value:
            self.app.theme_cls.theme_style = "Dark"
        else:
            self.app.theme_cls.theme_style = "Light"


class MainApp(MDApp):

    def change_screen(self, screen_name):
        # Get the screen manager from the kv file
        screen_manager = self.root.ids['screen_manager']
        # screen_manager.transition
        screen_manager.current = screen_name
        screen_manager = self.root.ids



MainApp().run()
