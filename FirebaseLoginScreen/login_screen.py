from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.properties import StringProperty
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.textfield import MDTextField

from customKv.relativelayout import MDRelativeLayout
from customKv.backdrop import MDBackdrop1

from customKv.onboarding import AKOnboarding, AKOnboardingItem
from kivy.animation import Animation


# from kivymd.uix.backdrop import MDBackdrop

class Tab(FloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''


class ClickableTextFieldRound(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()
    # Here specify the required parameters for MDTextFieldRound:
    # [...]

class LoginScreen(Screen):
    pos_y_inc = 0
    txt_diff = 0

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self, *args):
        if self.app.window_size[1] < 1335:
            self.txt_diff = -0.04
            self.pos_y_inc = -0.01

    def on_open(self):

        anim_sign_in = Animation(opacity=1, duration=0.3, pos_hint={"center_x": 0.5, "center_y": 1.03})
        anim_sign_in.start(self.ids['frontlayer'].ids['sign_in_label'])

        anim_sign_in = Animation(opacity=0, duration=0.3)
        anim_sign_in.start(self.ids['frontlayer'].ids['md_tabs'])
        self.ids['frontlayer'].ids['md_tabs'].disabled = True

    def on_close(self):
        anim_sign_in = Animation(duration=0.25, pos_hint={"center_x": .375, "y": .01})
        anim_sign_in.bind(on_complete=self.on_complete_trans)
        anim_sign_in.start(self.ids['frontlayer'].ids['sign_in_label'])

    def on_complete_trans(self, *args):
        anim_sign_in = Animation(opacity=1, duration=0.4)
        anim_sign_in.start(self.ids['frontlayer'].ids['md_tabs'])

        self.ids['frontlayer'].ids['sign_in_label'].opacity = 0
        self.ids['frontlayer'].ids['md_tabs'].disabled = False

    def on_tab_switch(self, *args):
        method = args[3].split()
        method = method[1][:2]
        button = self.ids['frontlayer'].ids['sign_in_button']
        if method == "up":
            self.sign_in_to_sign_up()
        else:
            self.sign_up_to_sign_in()

    def sign_in_to_sign_up(self):
        # anim_sign_in = Animation(pos_hint ={"center_x": .5, "center_y": .2},duration=0.2)
        anim_pass = Animation(pos_hint={"center_x": .5, "center_y": .5 + self.pos_y_inc + self.txt_diff * 2},
                              duration=0.2)
        anim_username = Animation(opacity=1, duration=0.4)
        anim_forget_pass = Animation(opacity=0, duration=0.15)

        # anim_sign_in.start(self.ids['frontlayer'].ids['sign_in_button'])
        anim_username.start(self.ids['frontlayer'].ids['username'])
        anim_forget_pass.start(self.ids['frontlayer'].ids['forget_pass'])
        self.ids['frontlayer'].ids['sign_in_button'].text = "Sign up"
        anim_pass.start(self.ids['frontlayer'].ids['password'])

        self.ids['frontlayer'].ids['email'].hint_text = " Email"
        self.ids['frontlayer'].ids['forget_pass'].disabled = True

    def sign_up_to_sign_in(self):

        self.ids['frontlayer'].ids['forget_pass'].disabled = False

        # anim_sign_in = Animation(pos_hint ={"center_x": .5, "center_y": .3},duration=0.2)
        anim_pass = Animation(pos_hint={"center_x": .5, "center_y": .65 + self.pos_y_inc + self.txt_diff * 2},
                              duration=0.2)
        anim_username = Animation(opacity=0, duration=0.3)
        anim_forget_pass = Animation(opacity=1, duration=0.2)

        anim_forget_pass.start(self.ids['frontlayer'].ids['forget_pass'])
        # anim_sign_in.start(self.ids['frontlayer'].ids['sign_in_button'])
        anim_pass.start(self.ids['frontlayer'].ids['password'])
        anim_username.start(self.ids['frontlayer'].ids['username'])
        self.ids['frontlayer'].ids['sign_in_button'].text = "Sign in"
        self.ids['frontlayer'].ids['email'].hint_text = " Email or Username"

    def sign_in(self, *args):
        method = args[0]
        email = args[1]
        password = args[2]
        username = args[3]
        if method == 'Sign up':
            pass
        else:
            FirebaseLoginScreen.sign_in(email, password)