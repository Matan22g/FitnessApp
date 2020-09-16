from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivymd.theming import ThemableBehavior
from kivy.properties import NumericProperty, BooleanProperty, StringProperty, ListProperty
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.event import EventDispatcher
from kivy.metrics import dp

Builder.load_string(
    """
<ItemCircles>:
    size_hint_x: None 
    canvas.before:
        Color:
            rgba: root._circles_color
        Line:  
            circle: [ self.pos[0]+self.width/2, self.pos[1]+self.height/2, self.width/2]
            width: dp(1)

<AKOnboardingItem>:

<AKOnboarding>: 
    orientation: 'vertical'

    MyCarousel:
        min_move:root.min_move
        anim_type: root.anim_type
        anim_move_duration: root.anim_move_duration
        id: carousel
        
    Widget:
        id: ghost_circle     
        size_hint: None, None 
        canvas.before:
            Color:
                rgba: root.circles_color if root.circles_color else root.theme_cls.primary_color
            Ellipse:  
                pos: self.pos
                size: self.size 
    FloatLayout:
        pos_hint: {"center_x": 0.5, "top": 0.55}
   
        BoxLayout:
            id: circles_box
            pos_hint: {"center_x": 0.5, "top": 0.64}
            size_hint: None,None 
            size: self.minimum_width , root.circles_size
            spacing: root.circles_size/2


    """
)


class ItemCircles(ThemableBehavior, Widget):
    _circles_color = ListProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MyCarousel(ThemableBehavior, Carousel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda x: self._add_circles())
        Window.bind(on_resize=self._on_resize)

    def _add_circles(self):
        self.total_circles = len(self.slides) - 1

        if self.parent.circles_color:
            circle_color = self.parent.circles_color
        else:
            circle_color = self.theme_cls.primary_color

        for _ in range(self.total_circles + 1):
            self.parent.ids.circles_box.add_widget(
                ItemCircles(width=self.parent.circles_size, _circles_color=circle_color))

        self._current_circle = self.total_circles
        Clock.schedule_once(lambda x: self._set_current_circle(animation=False))

    def on_size(self, *args):
        Clock.schedule_once(lambda x: self._set_current_circle(animation=False))
        return super().on_size(*args)

    def reset(self):
        self._current_circle = self.total_circles
        self._set_current_circle()
        self.load_slide(self.slides[0])

    def _set_current_circle(self, mode=None, animation=True):
        if mode == 'next':
            if self._current_circle > 0:
                self._current_circle -= 1
            else:
                self.parent._on_finish_dispatch()

        elif mode == 'previous':
            if self._current_circle < self.total_circles:
                self._current_circle += 1
        if animation:
            width = self.parent.ids.ghost_circle.width
            anim = Animation(
                pos=self.parent.ids.circles_box.children[self._current_circle].pos,
                t=self.anim_type,
                duration=self.anim_move_duration
            )
            anim.start(self.parent.ids.ghost_circle)
        else:
            self.parent.ids.ghost_circle.pos = self.parent.ids.circles_box.children[self._current_circle].pos

    def on_touch_up(self, touch):
        if abs(self._offset) > self.width * self.min_move:

            if self._offset > 0:  ## previous screen
                self._set_current_circle('previous')

            elif self._offset < 0:  ## next screen
                self._set_current_circle('next')

        return super().on_touch_up(touch)

    def _on_resize(self, *args):
        Clock.schedule_once(lambda x: self._set_current_circle(animation=False))


class AKOnboardingItem(BoxLayout):
    pass


class AKOnboarding(ThemableBehavior, FloatLayout, EventDispatcher):
    circles_size = NumericProperty(dp(20))
    skip_button = BooleanProperty(True)
    min_move = NumericProperty(0.05)
    anim_type = StringProperty('out_quad')
    anim_move_duration = NumericProperty(0.2)
    bottom_bar_radius = ListProperty([dp(20), dp(20), 0, 0])
    show_bottom_bar = BooleanProperty(True)
    bottom_bar_color = ListProperty(None)
    circles_color = ListProperty(None)

    def __init__(self, **kwargs):
        super(AKOnboarding, self).__init__(**kwargs)
        self.register_event_type('on_finish')
        Clock.schedule_once(lambda x: self._update())

    def add_widget(self, widget, index=0, canvas=None):
        if issubclass(widget.__class__, AKOnboardingItem):
            self.ids.carousel.add_widget(widget)
        else:
            super().add_widget(widget, index=index, canvas=canvas)

    def _on_finish_dispatch(self):
        self.dispatch('on_finish')

    def on_finish(self, *args):
        pass

    def reset(self):
        return self.ids.carousel.reset()

    def on_size(self, *args):
        self.ids.carousel.size = self.size

    def _update(self):
        self.ids.ghost_circle.size = [self.circles_size, self.circles_size]
