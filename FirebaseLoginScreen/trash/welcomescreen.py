from kivy.uix.screenmanager import Screen
# from kivy.lang import Builder
# from kivy.properties import StringProperty, BooleanProperty
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.screenmanager import Screen
# from kivymd.app import MDApp
# from kivymd.theming import ThemableBehavior
# from kivy.uix.carousel import Carousel
# from kivy.uix.image import AsyncImage
# from kivy.uix.floatlayout import FloatLayout
# from kivymd.uix.tab import MDTabsBase
# from kivymd.icon_definitions import md_icons

class WelcomeScreen(Screen):
    pass

#
# class Tab(FloatLayout, MDTabsBase):
#     pass
#
#
# class WelcomeScreen(Screen):
#     def __init__(self, **kw):
#         super().__init__(**kw)
#         self.app = MDApp.get_running_app()
#
#     icons = list(md_icons.keys())[15:30]
#
#
#     def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
#         count_icon = [k for k, v in md_icons.items() if v == tab_text]
#         instance_tab.ids.icon.icon = count_icon[0]
#
#
# class CarouselApp(Screen):
#     def build(self):
#         carousel = Carousel(direction='right')
#         return carousel
#
#
# class ExampleBackdrop(Screen):
#     pass
#
#
# class ItemBackdropBackLayer(ThemableBehavior, BoxLayout):
#     icon = StringProperty("android")
#     text = StringProperty()
#     selected_item = BooleanProperty(False)
#
#     def on_touch_down(self, touch):
#         if self.collide_point(touch.x, touch.y):
#             for item in self.parent.children:
#                 if item.selected_item:
#                     item.selected_item = False
#             self.selected_item = True
#         return super().on_touch_down(touch)
#
#
# class MDBackdrop:
#     def open(self, open_up_to=20):
#         pass
