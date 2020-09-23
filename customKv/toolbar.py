"""
Components/Toolbar
==================

.. seealso::

    `Material Design spec, App bars: top <https://material.io/components/app-bars-top>`_

    `Material Design spec, App bars: bottom <https://material.io/components/app-bars-bottom/app-bars-bottom.html>`_

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/app-bar-top.png
    :align: center

`KivyMD` provides the following toolbar positions for use:

- Top_
- Bottom_

.. Top:
Top
---

.. code-block:: python

    from kivy.lang import Builder

    from kivymd.app import MDApp

    KV = '''
    BoxLayout:
        orientation: "vertical"

        CustomMDToolbar:
            title: "CustomMDToolbar"

        MDLabel:
            text: "Content"
            halign: "center"
    '''


    class Test(MDApp):
        def build(self):
            return Builder.load_string(KV)


    Test().run()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/toolbar-1.png
    :align: center

Add left menu
-------------

.. code-block:: kv

    CustomMDToolbar:
        title: "CustomMDToolbar"
        left_action_items: [["menu", lambda x: app.callback()]]

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/toolbar-2.png
    :align: center

Add right menu
--------------

.. code-block:: kv

    CustomMDToolbar:
        title: "CustomMDToolbar"
        right_action_items: [["dots-vertical", lambda x: app.callback()]]

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/toolbar-3.png
    :align: center

Add two item to the right menu
------------------------------

.. code-block:: kv

    CustomMDToolbar:
        title: "CustomMDToolbar"
        right_action_items: [["dots-vertical", lambda x: app.callback_1()], ["clock", lambda x: app.callback_2()]]

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/toolbar-4.png
    :align: center

Change toolbar color
--------------------

.. code-block:: kv

    CustomMDToolbar:
        title: "CustomMDToolbar"
        md_bg_color: app.theme_cls.accent_color

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/toolbar-5.png
    :align: center

Change toolbar text color
-------------------------

.. code-block:: kv

    CustomMDToolbar:
        title: "CustomMDToolbar"
        specific_text_color: app.theme_cls.accent_color

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/toolbar-6.png
    :align: center

Shadow elevation control
------------------------

.. code-block:: kv

    CustomMDToolbar:
        title: "Elevation 10"
        elevation: 10

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/toolbar-7.png
    :align: center

.. Bottom:
Bottom
------

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/app-bar-bottom.png
    :align: center

Usage
-----

.. code-block:: python

    from kivy.lang import Builder

    from kivymd.app import MDApp

    KV = '''
    BoxLayout:

        # Will always be at the bottom of the screen.
        MDBottomAppBar:

            CustomMDToolbar:
                title: "Title"
                icon: "git"
                type: "bottom"
                left_action_items: [["menu", lambda x: x]]
    '''


    class Test(MDApp):
        def build(self):
            return Builder.load_string(KV)


    Test().run()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/toolbar-8.png
    :align: center

Event on floating button
------------------------

Event ``on_action_button``:

.. code-block:: kv

    MDBottomAppBar:

        CustomMDToolbar:
            title: "Title"
            icon: "git"
            type: "bottom"
            left_action_items: [["menu", lambda x: x]]
            on_action_button: app.callback(self.icon)

Floating button position
------------------------

Mode:

- `'free-end'`
- `'free-center'`
- `'end'`
- `'center'`

.. code-block:: kv

    MDBottomAppBar:

        CustomMDToolbar:
            title: "Title"
            icon: "git"
            type: "bottom"
            left_action_items: [["menu", lambda x: x]]
            mode: "end"

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/toolbar-9.png
    :align: center

.. code-block:: kv

    MDBottomAppBar:

        CustomMDToolbar:
            title: "Title"
            icon: "git"
            type: "bottom"
            left_action_items: [["menu", lambda x: x]]
            mode: "free-end"

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/toolbar-10.png
    :align: center

.. seealso::

    `Components-Bottom-App-Bar <https://github.com/kivymd/KivyMD/wiki/Components-Bottom-App-Bar>`_
"""

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    ListProperty,
    NumericProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import (
    RectangularElevationBehavior,
    SpecificBackgroundColorBehavior,
)
from kivymd.uix.button import MDFloatingActionButton, MDIconButton

Builder.load_string(
    """
#:import m_res kivymd.material_resources


<MDActionBottomAppBarButton>:
    md_bg_color: self.theme_cls.primary_color

    canvas.before:
        PushMatrix
        Scale:
            origin: self.center
            x: root._scale_x
            y: root._scale_y
    canvas.after:
        PopMatrix


<CustomMDToolbar>
    size_hint_y: None
    height: root.theme_cls.standard_increment
    padding: [root.theme_cls.horizontal_margins - dp(12), 0]
    opposite_colors: True
    elevation: root.elevation
    # md_bg_color: self.theme_cls.primary_color if root.type != "bottom" else [0, 0, 0, 0]
    orientation: 'vertical'
    canvas:
        Color:
            rgba: root.theme_cls.primary_color
        RoundedRectangle:
            pos:
                self.pos \
                if root.mode == "center" else \
                (self.width - root.action_button.width + dp(6), self.y)
            size:
                (((self.width - root.action_button.width) / 2 - dp(6), self.height) \
                if root.mode == "center" else \
                (root.action_button.width - dp(6), self.height)) if root.type == "bottom" else (0, 0)
            radius:
                (0, root.round, 0, 0) if root.mode == "center" else (root.round, 0, 0, 0)
        Rectangle:
            pos:
                ((self.width / 2 - root.action_button.width / 2) - dp(6), self.y - root._shift) \
                if root.mode == "center" else \
                (self.width - root.action_button.width * 2 - dp(6), self.y - root._shift)
            size:
                (root.action_button.width + dp(6) * 2, self.height - root._shift * 2) \
                if root.type == "bottom" else (0, 0)
        RoundedRectangle:
            pos:
                ((self.width + root.action_button.width) / 2 + dp(6), self.y) \
                if root.mode == "center" else self.pos
            size:
                (((self.width - root.action_button.width) / 2 + dp(6), self.height) \
                if root.mode == "center" else \
                ((self.width - root.action_button.width * 2 - dp(6)), self.height)) \
                if root.type == "bottom" else (0, 0)
            radius: (root.round, 0, 0, 0) if root.mode == "center" else (0, root.round, 0, 0)
        Color:
            rgba: 1, 1, 1, 1
        Ellipse:
            pos:
                (self.center[0] - root.action_button.width / 2 - dp(6), self.center[1] - root._shift * 2) \
                if root.mode == "center" else \
                (self.width - root.action_button.width * 2 - dp(6), self.center[1] - root._shift * 2)
            size:
                (root.action_button.width + dp(6) * 2, root.action_button.width) \
                if root.type == "bottom" else (0, 0)
            angle_start: root._angle_start
            angle_end: root._angle_end
            
    BoxLayout:
        orientation: 'horizontal'
        BoxLayout:
            id: left_actions
            orientation: 'horizontal'
            size_hint_x: None
            padding: [0, (self.height - dp(48))/2]
    
        BoxLayout:
            padding: dp(12), 0
    
            MDLabel:
                id: label_title
                font_style: 'H5'
                opposite_colors: root.opposite_colors
                theme_text_color: 'Custom'
                text_color: root.specific_text_color
                text: root.title
                shorten: True
                shorten_from: 'right'
                halign: 'center'
    
        BoxLayout:
            id: right_actions
            orientation: 'horizontal'
            size_hint_x: None
            padding: [0, (self.height - dp(48)) / 2]
    
"""
)


class MDActionBottomAppBarButton(MDFloatingActionButton):
    _scale_x = NumericProperty(1)
    _scale_y = NumericProperty(1)


class CustomMDToolbar(
    ThemableBehavior,
    RectangularElevationBehavior,
    SpecificBackgroundColorBehavior,
    BoxLayout,
):
    """
    :Events:
        `on_action_button`
            Method for the button used for the :class:`~MDBottomAppBar` class.
    """

    elevation = NumericProperty(6)
    """
    Elevation value.

    :attr:`elevation` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `6`.
    """

    left_action_items = ListProperty()
    """The icons on the left of the toolbar.
    To add one, append a list like the following:

    .. code-block:: kv

        left_action_items: [`'icon_name'`, callback]

    where `'icon_name'` is a string that corresponds to an icon definition and
    ``callback`` is the function called on a touch release event.

    :attr:`left_action_items` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    right_action_items = ListProperty()
    """The icons on the left of the toolbar.
    Works the same way as :attr:`left_action_items`.

    :attr:`right_action_items` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    title = StringProperty()
    """Text toolbar.

    :attr:`title` is an :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    md_bg_color = ListProperty([0, 0, 0, 0])
    """Color toolbar.

    :attr:`md_bg_color` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[0, 0, 0, 0]`.
    """

    anchor_title = StringProperty("left")

    mode = OptionProperty(
        "center", options=["free-end", "free-center", "end", "center"]
    )
    """Floating button position. Onle for :class:`~MDBottomAppBar` class.
    Available options are: `'free-end'`, `'free-center'`, `'end'`, `'center'`.

    :attr:`mode` is an :class:`~kivy.properties.OptionProperty`
    and defaults to `'center'`.
    """

    round = NumericProperty("10dp")
    """
    Rounding the corners at the notch for a button.
    Onle for :class:`~MDBottomAppBar` class.

    :attr:`round` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `'10dp'`.
    """

    icon = StringProperty("android")
    """
    Floating button. Onle for :class:`~MDBottomAppBar` class.

    :attr:`icon` is an :class:`~kivy.properties.StringProperty`
    and defaults to `'android'`.
    """

    icon_color = ListProperty()
    """
    Color action button. Onle for :class:`~MDBottomAppBar` class.

    :attr:`icon_color` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    type = OptionProperty("top", options=["top", "bottom"])
    """
    When using the :class:`~MDBottomAppBar` class, the parameter ``type``
    must be set to `'bottom'`:

    .. code-block:: kv

        MDBottomAppBar:

            CustomMDToolbar:
                type: "bottom"

    Available options are: `'top'`, `'bottom'`.

    :attr:`type` is an :class:`~kivy.properties.OptionProperty`
    and defaults to `'top'`.
    """

    _shift = NumericProperty("3.5dp")
    _angle_start = NumericProperty(90)
    _angle_end = NumericProperty(270)

    def __init__(self, **kwargs):
        self.action_button = MDActionBottomAppBarButton()
        super().__init__(**kwargs)
        self.register_event_type("on_action_button")
        self.action_button.bind(
            on_release=lambda x: self.dispatch("on_action_button")
        )
        self.action_button.x = Window.width / 2 - self.action_button.width / 2
        self.action_button.y = (
                (self.center[1] - self.height / 2)
                + self.theme_cls.standard_increment / 2
                + self._shift
        )
        if not self.icon_color:
            self.icon_color = self.theme_cls.primary_color
        Window.bind(on_resize=self._on_resize)
        self.bind(specific_text_color=self.update_action_bar_text_colors)
        Clock.schedule_once(
            lambda x: self.on_left_action_items(0, self.left_action_items)
        )
        Clock.schedule_once(
            lambda x: self.on_right_action_items(0, self.right_action_items)
        )

    def on_action_button(self, *args):
        pass

    def on_md_bg_color(self, instance, value):
        if self.type == "bottom":
            self.md_bg_color = [0, 0, 0, 0]

    def on_left_action_items(self, instance, value):
        self.update_action_bar(self.ids["left_actions"], value)

    def on_right_action_items(self, instance, value):
        self.update_action_bar(self.ids["right_actions"], value)

    def update_action_bar(self, action_bar, action_bar_items):
        action_bar.clear_widgets()
        new_width = 0
        for item in action_bar_items:
            new_width += dp(48)
            action_bar.add_widget(
                MDIconButton(
                    icon=item[0],
                    on_release=item[1],
                    opposite_colors=True,
                    text_color=self.specific_text_color,
                    theme_text_color="Custom",
                )
            )
        action_bar.width = new_width

    def update_action_bar_text_colors(self, instance, value):
        for child in self.ids["left_actions"].children:
            child.text_color = self.specific_text_color
        for child in self.ids["right_actions"].children:
            child.text_color = self.specific_text_color

    def _on_resize(self, instance, width, height):
        if self.mode == "center":
            self.action_button.x = width / 2 - self.action_button.width / 2
        else:
            self.action_button.x = width - self.action_button.width * 2

    def on_icon(self, instance, value):
        self.action_button.icon = value

    def on_icon_color(self, instance, value):
        self.action_button.md_bg_color = value

    def on_mode(self, instance, value):
        def set_button_pos(*args):
            self.action_button.x = x
            self.action_button.y = y
            self.action_button._hard_shadow_size = (0, 0)
            self.action_button._soft_shadow_size = (0, 0)
            anim = Animation(_scale_x=1, _scale_y=1, d=0.05)
            anim.bind(on_complete=self.set_shadow)
            anim.start(self.action_button)

        if value == "center":
            self.set_notch()
            x = Window.width / 2 - self.action_button.width / 2
            y = (
                    (self.center[1] - self.height / 2)
                    + self.theme_cls.standard_increment / 2
                    + self._shift
            )
        elif value == "end":

            self.set_notch()
            x = Window.width - self.action_button.width * 2
            y = (
                    (self.center[1] - self.height / 2)
                    + self.theme_cls.standard_increment / 2
                    + self._shift
            )
            self.right_action_items = []
        elif value == "free-end":
            self.remove_notch()
            x = Window.width - self.action_button.width - dp(10)
            y = self.action_button.height + self.action_button.height / 2
        elif value == "free-center":
            self.remove_notch()
            x = Window.width / 2 - self.action_button.width / 2
            y = self.action_button.height + self.action_button.height / 2
        self.remove_shadow()
        anim = Animation(_scale_x=0, _scale_y=0, d=0.05)
        anim.bind(on_complete=set_button_pos)
        anim.start(self.action_button)

    def remove_notch(self):
        self._angle_start = 0
        self._angle_end = 0
        self.round = 0
        self._shift = 0

    def set_notch(self):
        self._angle_start = 90
        self._angle_end = 270
        self.round = dp(10)
        self._shift = dp(3.5)

    def remove_shadow(self):
        self.action_button._hard_shadow_size = (0, 0)
        self.action_button._soft_shadow_size = (0, 0)

    def set_shadow(self, *args):
        self.action_button._hard_shadow_size = (dp(112), dp(112))
        self.action_button._soft_shadow_size = (dp(112), dp(112))


class MDBottomAppBar(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None

    def add_widget(self, widget, index=0, canvas=None):
        if widget.__class__ is CustomMDToolbar:
            super().add_widget(widget)
            return super().add_widget(widget.action_button)
