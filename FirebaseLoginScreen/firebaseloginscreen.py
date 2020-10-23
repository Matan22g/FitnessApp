from kivy import platform
from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty, StringProperty
from kivy.event import EventDispatcher
from kivy.network.urlrequest import UrlRequest
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
# Python imports
import sys
from FirebaseLoginScreen import progressspinner

sys.path.append("/".join(x for x in __file__.split("/")[:-1]))
from json import dumps
import os.path
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
import requests
import certifi

# from kivyauth.google_auth import initialize_google, login_google, logout_google
#


# Load the kv files
folder = os.path.dirname(os.path.realpath(__file__))
# Builder.load_file(folder + "/themedwidgets.kv")
Builder.load_file(folder + "/login_screen.kv")
Builder.load_file(folder + "/loadingpopup.kv")

# Import the screens used to log the user in
from FirebaseLoginScreen.login_screen import LoginScreen


# from FirebaseLoginScreen.login_google import initialize_google, login_google, logout_google


class FirebaseLoginScreen(Screen, EventDispatcher):
    dialog = None
    web_api_key = StringProperty()  # From Settings tab in Firebase project

    # Firebase Authentication Credentials - what developers want to retrieve
    refresh_token = ""
    localId = ""
    idToken = ""
    user_name = ""
    # Properties used to send events to update some parts of the UI
    login_success = BooleanProperty(False)  # Called upon successful sign in
    sign_up_msg = StringProperty()
    sign_in_msg = StringProperty()
    email = ""
    password = 0
    email_exists = BooleanProperty(False)
    email_not_found = BooleanProperty(False)

    debug = False
    popup = Factory.LoadingPopup()
    popup.background = folder + "/transparent_image.png"

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()

    # def on_enter(self, *args):
    #     if platform == 'android':
    #         initialize_google(self.after_login, self.error_listener)

    # def build(self):
    #     initialize_google(self.after_login, self.error_listener)
    #

    def after_login(self):
        pass

    def error_listener(self):
        pass

    def on_login_success(self, *args):
        pass

    def on_web_api_key(self, *args):
        """When the web api key is set, look for an existing account in local
        memory.
        """
        # Try to load the users info if they've already created an account
        self.refresh_token_file = App.get_running_app().user_data_dir + "/refresh_token.txt"
        if self.debug:
            print("Looking for a refresh token in:", self.refresh_token_file)
        if os.path.exists(self.refresh_token_file):
            self.load_saved_account()

    def sign_up(self, email, user_name, password):
        self.display_loading_screen()
        self.email = email
        if self.debug:
            print("Attempting to create a new account: ", email, password)

        if not user_name or user_name.find(" ") != -1:
            self.app.dialog = MDDialog(title="Error",
                                       text="Username invalid or missing - Use english letters and numbers, also spaces aren't allowed",
                                       radius=[10, 7, 10, 7],
                                       size_hint=(0.9, None))
            self.app.dialog.open()
            self.hide_loading_screen()
            return
        check_is_exist = self.is_user_exist(user_name)
        if check_is_exist == 2:  # no internet
            self.show_no_internet_msg()
            return
        if not check_is_exist:
            self.user_name = user_name
            signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" + self.web_api_key
            signup_payload = dumps(
                {"email": email, "password": password, "returnSecureToken": "true"})

            UrlRequest(signup_url, req_body=signup_payload,
                       on_success=self.successful_sign_up,
                       on_failure=self.sign_up_failure,
                       on_error=self.sign_up_error, ca_file=certifi.where())
        else:
            comment = " already taken"
            self.user_look_up_msg(user_name, comment)

    def is_user_exist(self, user_name):
        # Method to check if User Name exist. try and fix the loading spinner problem

        user_name = '"' + user_name.lower() + '"'

        try:
            check_req = requests.get(
                'https://gymbuddy2.firebaseio.com/.json?orderBy="user_name"&equalTo=' + user_name)
        except:
            return 2
        data = check_req.json()
        if self.debug:
            print("is_user_exist:", data)
        if data:
            return True
        else:
            return False

    def show_no_internet_msg(self):
        self.app.dialog = MDDialog(title="Error: no internet", text="internet connection is required",
                                   radius=[10, 7, 10, 7],
                                   size_hint=(0.9, None))
        self.app.dialog.open()
        self.hide_loading_screen()

    def user_look_up_msg(self, user_name, comment):
        """Displays an error message that the user exist.
        comment = already taken / doesnt exist
        """
        self.hide_loading_screen()

        self.email_exists = False  # Triggers hiding the sign in button
        msg = "Username: " + user_name + comment
        # Check if the error msg is the same as the last one
        if msg == self.sign_up_msg:
            msg = " " + msg + " "
        self.app.dialog = MDDialog(title="Choose another username", text=msg, radius=[10, 7, 10, 7],
                                   size_hint=(0.9, None))
        self.app.dialog.open()
        if self.debug:
            print("user_look_up_msg:", msg)

        self.sign_up_msg = msg
        if msg == "Email exists":
            self.email_exists = True

    def successful_sign_up(self, urlrequest, log_in_data):
        # my_data = '{"avatar": "man.png", "nicknames": {}, "friends": "", "workouts": "", "streak": "0", "my_friend_id": ""}'
        # my_data = '{"user_name": ' + '"' + self.user_name + '"' + ', ' + '"nicknames": {}, "friends": "", "workouts": "", "streak": "0", "my_friend_id": ""}'
        my_data = '{"user_name": ' + '"' + self.user_name.lower() + '"' + ', ' + '"real_user_name": ' + '"' + self.user_name + '"' + ', ' + '"email": ' + '"' + self.email + '"' + ', ' + '"friends": "", "workouts": "", "streak": "0", "temp_session": "", "sessions":"", "settings": {"units":"metric"}}'
        self.app.user_data = {"user_name": self.user_name.lower(), "real_user_name": self.user_name,
                              "email": self.email, "friends": "", "workouts": {}, "streak": 0, "temp_session": {},
                              "sessions": {}, "settings": {"units": "metric"}}
        self.app.sign_up = 1
        print("successful_sign_up")
        post_request = UrlRequest(
            "https://gymbuddy2.firebaseio.com/" + log_in_data['localId'] + ".json?auth=" + log_in_data['idToken'],
            ca_file=certifi.where(),
            req_body=my_data, method='PATCH')
        print(post_request)
        self.successful_login(urlrequest, log_in_data)

    # def on_friend_get_req_ok(self, *args):
    #     my_friend_id = self.friend_get_req.result
    #     self.app.set_friend_id(my_friend_id)
    #     friend_patch_data = '{"next_friend_id": %s}' % (my_friend_id+1)
    #     friend_patch_req = UrlRequest("https://gymbuddy2.firebaseio.com/.json?auth=" + self.app.id_token,
    #                                       req_body=friend_patch_data, ca_file = certifi.where(), method='PATCH')
    #     # Update firebase's next friend id field
    #     # Default streak
    #     # Default avatar
    #     # Friends list
    #     # Empty workouts area
    #     my_data = '{"avatar": "man.png", "nicknames": {}, "friends": "", "workouts": "", "streak": "0", "my_friend_id": %s}' % my_friend_id
    #     post_request = UrlRequest("https://gymbuddy2.firebaseio.com/" + self.app.local_id + ".json?auth=" + self.app.id_token, ca_file=certifi.where(),
    #                    req_body=my_data, method='PATCH')
    #

    def successful_login(self, urlrequest, log_in_data):
        """Collects info from Firebase upon successfully registering a new user.
        """
        self.hide_loading_screen()
        self.refresh_token = log_in_data['refreshToken']
        self.localId = log_in_data['localId']
        self.idToken = log_in_data['idToken']
        self.app.id_token = log_in_data['idToken']
        self.app.local_id = log_in_data['localId']
        self.save_refresh_token(self.refresh_token)
        self.login_success = True
        if self.debug:
            print("Successfully logged in a user: ", log_in_data)

    def sign_up_failure(self, urlrequest, failure_data):
        """Displays an error message to the user if their attempt to log in was
        invalid.
        """
        self.hide_loading_screen()
        self.email_exists = False  # Triggers hiding the sign in button
        if self.debug:
            print(failure_data)
        msg = failure_data['error']['message'].replace("_", " ").capitalize()
        # Check if the error msg is the same as the last one
        if msg == self.sign_up_msg:
            # Need to modify it somehow to make the error popup display
            msg = " " + msg + " "
        self.app.dialog = MDDialog(title="Error", text=msg, radius=[10, 7, 10, 7], size_hint=(0.9, None))
        self.app.dialog.open()
        self.sign_up_msg = msg
        if msg == "Email exists":
            self.email_exists = True
        if self.debug:
            print("Couldn't sign the user up: ", failure_data)

    def sign_up_error(self, *args):
        self.hide_loading_screen()
        if self.debug:
            print("Sign up Error: ", args)

    def get_user_name_email_success(self, req, result):
        # save email and call to sign with email method
        for user_key in result:
            user_data = result[user_key]
            email = user_data["email"]
            self.email = email
            self.email_sign_in(email, self.password)
            if self.debug:
                print("get_user_name_email_success:", user_data)

    def on_email_request_error(self, *args):
        print('failed to get user name')
        print(args)

    def get_user_name_email(self, user_name):
        # Query database and gets username email
        user_name = '"' + user_name.lower() + '"'
        link = 'https://gymbuddy2.firebaseio.com/.json?orderBy="user_name"&equalTo=' + user_name
        check_req = requests.get(link)
        req = UrlRequest(link, on_success=self.get_user_name_email_success, on_error=self.on_email_request_error,
                         on_failure=self.on_email_request_error,
                         ca_file=certifi.where(), verify=True)

    def sign_in(self, email, password):
        """Called when the "Log in" button is pressed.

        Checks whether the user trying to log in with username or email.
        """

        if self.debug:
            print("Attempting to sign user in: ", email, password)
        self.password = password
        # email @ check
        if "@" not in email:
            # checks if the such user exist
            if self.is_user_exist(email):
                try:
                    self.get_user_name_email(email)
                except:
                    self.show_no_internet_msg()
                    self.hide_loading_screen()
                    return
            else:
                comment = " Doesnt exist"
                self.user_look_up_msg(email, comment)
        else:
            self.email_sign_in(email, password)

    def email_sign_in(self, email, password):
        """Called when the "Log in" button is pressed.

        Sends the user's email and password in an HTTP request to the Firebase
        Authentication service.
        """

        sign_in_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=" + self.web_api_key
        sign_in_payload = dumps(
            {"email": email, "password": password, "returnSecureToken": True})

        UrlRequest(sign_in_url, req_body=sign_in_payload,
                   on_success=self.successful_login,
                   on_failure=self.sign_in_failure,
                   on_error=self.sign_in_error,ca_file=certifi.where())

    def sign_in_failure(self, urlrequest, failure_data):
        """Displays an error message to the user if their attempt to create an
        account was invalid.
        """
        self.hide_loading_screen()
        self.email_not_found = False  # Triggers hiding the sign in button
        msg = failure_data['error']['message'].replace("_", " ").capitalize()
        # Check if the error msg is the same as the last one
        if msg == self.sign_in_msg:
            # Need to modify it somehow to make the error popup display
            msg = " " + msg + " "
        self.sign_in_msg = msg
        self.app.dialog = MDDialog(title="Error", text=msg, radius=[10, 7, 10, 7], size_hint=(0.9, None))
        self.app.dialog.open()
        if msg == "Email not found":
            self.email_not_found = True
        if self.debug:
            print("Couldn't sign the user in: ", failure_data)

    def sign_in_error(self, *args):
        self.hide_loading_screen()
        if self.debug:
            print("Sign in error", args)

    def reset_password(self, email):
        """Called when the "Reset password" button is pressed.
        Sends an automated email on behalf of your Firebase project to the user
        with a link to reset the password.
        """
        if self.debug:
            print("Attempting to send a password reset email to: ", email)
        reset_pw_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key=" + self.web_api_key
        reset_pw_data = dumps({"email": email, "requestType": "PASSWORD_RESET"})

        UrlRequest(reset_pw_url, req_body=reset_pw_data,
                   on_success=self.successful_reset,
                   on_failure=self.sign_in_failure,
                   on_error=self.sign_in_error,ca_file=certifi.where())

    def successful_reset(self, urlrequest, reset_data):
        """Notifies the user that a password reset email has been sent to them.
        """
        self.hide_loading_screen()
        if self.debug:
            print("Successfully sent a password reset email", reset_data)
        self.sign_in_msg = "Reset password instructions sent to your email."
        self.app.dialog = MDDialog(title="Reset Passowrd", text="Reset password instructions sent to your email.",
                                   radius=[10, 7, 10, 7],
                                   size_hint=(0.9, None))
        self.app.dialog.open()

    def save_refresh_token(self, refresh_token):
        """Saves the refresh token in a local file to enable automatic sign in
        next time the app is opened.
        """
        if self.debug:
            print("Saving the refresh token to file: ", self.refresh_token_file)
        with open(self.refresh_token_file, "w") as f:
            f.write(refresh_token)

    def load_refresh_token(self):
        """Reads the refresh token from local storage.
        """
        if self.debug:
            print("Loading refresh token from file: ", self.refresh_token_file)
        with open(self.refresh_token_file, "r") as f:
            self.refresh_token = f.read()

    def load_saved_account(self):
        """Uses the refresh token to get the user's idToken and localId by
        sending it as a request to Google/Firebase's REST API.

        Called immediately when a web_api_key is set and if the refresh token
        file exists.
        """
        if self.debug:
            print("Attempting to log in a user automatically using a refresh token.")
        self.load_refresh_token()
        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + self.web_api_key
        refresh_payload = dumps({"grant_type": "refresh_token", "refresh_token": self.refresh_token})
        UrlRequest(refresh_url, req_body=refresh_payload,
                   on_success=self.successful_account_load,
                   on_failure=self.failed_account_load,
                   on_error=self.failed_account_load,ca_file=certifi.where())

    def successful_account_load(self, urlrequest, loaded_data):
        """Sets the idToken and localId variables upon successfully loading an
        account using the refresh token.
        """
        self.hide_loading_screen()
        if self.debug:
            print("Successfully logged a user in automatically using the refresh token")
        self.idToken = loaded_data['id_token']
        self.localId = loaded_data['user_id']
        self.app.id_token = loaded_data['id_token']
        self.app.local_id = loaded_data['user_id']
        self.login_success = True

    def failed_account_load(self, *args):
        self.hide_loading_screen()
        if self.debug:
            print("Failed to load an account.", args)

    def display_loading_screen(self, *args):
        self.popup.open()

    def hide_loading_screen(self, *args):
        self.popup.dismiss()
