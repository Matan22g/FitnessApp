import calendar
from calendar import monthrange
from datetime import datetime

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
# from kivy_garden.graph import BarPlot, Graph, MeshLinePlot
from kivymd.app import MDApp
from kivymd.material_resources import DEVICE_TYPE
from kivymd.uix.tab import MDTabsBase
from customKv.graph import BarPlot, Graph, MeshLinePlot


class Tab(FloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''


class Year_Plot(RelativeLayout):
    weights = []

    def __init__(self, **kwargs):
        super(Year_Plot, self).__init__(**kwargs)

        strMth = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        # x1 = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        x1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        y1 = self.weights

        yData = len(y1)

        xList = list(enumerate(strMth, 1))
        # if DEVICE_TYPE != 'mobile': print(f'xList={xList}')
        # for x in range(0, yData):
        #     if DEVICE_TYPE != 'mobile': print(f'xList[x]={xList[x]}')
        # intXmin = int(min(x1))
        # intXmax = int(max(x1))
        # if DEVICE_TYPE != 'mobile': print(f'intXmin={intXmin}')
        # if DEVICE_TYPE != 'mobile': print(f'intXmax={intXmax}')

        xdict = dict(enumerate(x1))
        # if DEVICE_TYPE != 'mobile': print(f'xdict={xdict}')
        # for x in range(0, yData):
        #     if DEVICE_TYPE != 'mobile':
        #         # print(f'calendar.month_abbr[x]={calendar.month_abbr[x+1]}')
        #         print(f'xdict[x]={xdict[x]}')

        intXmin = int(min(xdict.keys())) + 1
        intXmax = int(max(xdict.keys())) + 1
        # if DEVICE_TYPE != 'mobile': print(f'intXmin={intXmin}')
        # if DEVICE_TYPE != 'mobile': print(f'intXmax={intXmax}')

        intYmax = int(max(y1)) + 1
        intYmin = int(min(y1)) - 1

        intYmajor = int((intYmax - intYmin) / 5)

        degree_sign = u'\N{DEGREE SIGN}'

        self.graph = Graph(
            pos_hint={'x': 0, 'y': 0},
            # size_hint=(1, 0.9),
            # x_ticks_minor=5,
            x_ticks_major=3,
            # y_ticks_minor=1,
            y_ticks_major=intYmajor,
            y_grid=True,
            tick_color=[0, 0, 0, 1],
            x_axis=strMth,
            xmin=intXmin,
            xmax=intXmax,
            ymin=0,
            ymax=intYmax,
            x_grid_label=True,
            y_grid_label=True,
            xlabel='Month',
            ylabel=f'Weight (Kg)',
            draw_border=True,
        )

        self.plot = BarPlot(color=[1, 1, 1, 1], bar_width=40)

        # self.plot.points = [(x, y1[x]) for x in range(0, yData)]
        # self.plot.points = [(x, y1[x]) for x, y in enumerate(x1)]
        self.plot.points = [(x1[x], y1[x]) for x, y in enumerate(x1)]

        self.add_widget(self.graph)

        self.graph.add_plot(self.plot)


class Month_Plot(RelativeLayout):
    weights = []
    days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
            30]

    def __init__(self, **kwargs):
        super(Month_Plot, self).__init__(**kwargs)

        strMth = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        # x1 = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        x1 = self.days
        y1 = self.weights

        yData = len(y1)

        xList = list(enumerate(strMth, 1))
        # if DEVICE_TYPE != 'mobile': print(f'xList={xList}')
        # for x in range(0, yData):
        #     if DEVICE_TYPE != 'mobile': print(f'xList[x]={xList[x]}')
        # intXmin = int(min(x1))
        # intXmax = int(max(x1))
        # if DEVICE_TYPE != 'mobile': print(f'intXmin={intXmin}')
        # if DEVICE_TYPE != 'mobile': print(f'intXmax={intXmax}')

        xdict = dict(enumerate(x1))
        # if DEVICE_TYPE != 'mobile': print(f'xdict={xdict}')
        # for x in range(0, yData):
        #     if DEVICE_TYPE != 'mobile':
        #         # print(f'calendar.month_abbr[x]={calendar.month_abbr[x+1]}')
        #         print(f'xdict[x]={xdict[x]}')

        intXmin = int(min(xdict.keys())) + 1
        intXmax = int(max(xdict.keys())) + 1
        # if DEVICE_TYPE != 'mobile': print(f'intXmin={intXmin}')
        # if DEVICE_TYPE != 'mobile': print(f'intXmax={intXmax}')

        intYmax = int(max(y1)) + 1
        intYmin = int(min(y1)) - 1

        intYmajor = int((intYmax - intYmin) / 5)

        degree_sign = u'\N{DEGREE SIGN}'

        self.graph = Graph(
            pos_hint={'x': 0, 'y': 0},
            # size_hint=(1, 0.9),
            # x_ticks_minor=5,
            x_ticks_major=6,
            # y_ticks_minor=1,
            y_ticks_major=intYmajor,
            y_grid=True,
            tick_color=[0, 0, 0, 1],
            x_axis=strMth,
            xmin=intXmin,
            xmax=intXmax,
            ymin=0,
            ymax=intYmax,
            x_grid_label=True,
            y_grid_label=True,
            xlabel='Day',
            ylabel=f'Weight (Kg)',
            draw_border=True,
        )

        self.plot = BarPlot(color=[1, 1, 1, 1], bar_width=20, bar_spacing=0.9)

        # self.plot.points = [(x, y1[x]) for x in range(0, yData)]
        # self.plot.points = [(x, y1[x]) for x, y in enumerate(x1)]
        self.plot.points = [(x1[x], y1[x]) for x, y in enumerate(x1)]

        self.add_widget(self.graph)

        self.graph.add_plot(self.plot)


class ExerciseStatsScreen(Screen):
    curr_graph = 0
    month_graph = 0
    year_graph = 0
    session_date = {}  # same as exerise sessions screen
    stats_dict = {}
    by_year_dict = {}
    sessions = {}
    curr_month = 0
    curr_year = 0
    curr_mode = ''
    today_date = datetime.today()
    curr_month_best = ''
    curr_year_best = ''
    exericse_name = ' '

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.sub_title = "Welcome to Home Screen"

    def on_leave(self, *args):
        try:
            self.ids.stats_layout.remove_widget(self.curr_graph)
        except:
            pass

    def on_pre_enter(self, *args):
        self.curr_graph = 0
        self.month_graph = 0
        self.year_graph = 0
        self.curr_month_best = ''
        self.curr_year_best = ''

        self.app.root.ids['toolbar'].right_action_items = [['', lambda x: None]]
        self.stats_dict = {}
        self.by_year_dict = {}

        if self.sessions:
            self.calc_month_best()
            max_year = max(list(self.session_date.keys()))
            max_month = max(list(self.session_date[max_year].keys()))
            self.add_month_plot(max_year, max_month)
            self.add_year_plot(max_year)
            self.curr_year = max_year
            self.curr_month = [max_year, max_month]
            self.ids.curr_label.text = str(max_year)
        else:
            self.session_date = {}

            self.curr_month = [self.today_date.year, self.today_date.month]
            self.curr_year = self.today_date.year
            self.ids.curr_label.text = str(self.today_date.year)
            self.set_record(0, 0)
            self.ids.no_data.opacity = 1

        self.app.root.ids['exercise_stats_screen'].ids["md_tabs"].switch_tab(
            '[size=' + str(self.app.headline_text_size) + ']Year[/size]')

        try:
            self.app.change_title(self.exericse_name + " Stats")
        except:
            pass

    def calc_month_best(self):
        for year in self.session_date:
            for month in self.session_date[year]:
                month_sessions_list = self.session_date[year][month]
                self.set_month_stats(month_sessions_list, year, month)

    def set_month_stats(self, month_sessions_list, year, month):

        num_of_days_in_month = monthrange(year, month)[1]
        list_of_days = [day + 1 for day in range(num_of_days_in_month)]
        month_set_list = [0 for i in range(num_of_days_in_month)]

        best_weight = 0
        best_set = 0

        for session_key in month_sessions_list:
            session_exc = self.sessions[session_key][1]
            session_day = session_key.day

            maybe_best_set = self.app.find_best_set(session_exc)
            set = maybe_best_set.split()
            maybe_best_weight = float(set[2])
            maybe_best_reps = int(set[0])
            month_set_list[session_day - 1] = maybe_best_weight
            if maybe_best_weight > best_weight:
                best_set = maybe_best_set
                best_weight = maybe_best_weight
            elif maybe_best_weight == best_weight:
                if maybe_best_reps > int(best_set.split()[0]):
                    best_set = maybe_best_set
                    best_weight = maybe_best_weight
        best_set_of_the_month = best_set
        best_weight_of_the_month = best_weight

        if year not in self.stats_dict:
            self.stats_dict[year] = {}
        self.stats_dict[year][month] = [list_of_days, month_set_list, best_set_of_the_month]

        self.by_year_dict[year] = {}

    def on_enter(self, *args):
        self.app.title = "Stats"

    def add_month_plot(self, year, month):
        try:
            self.ids.stats_layout.remove_widget(self.curr_graph)
        except:
            pass

        if year in self.stats_dict:
            if month in self.stats_dict[year]:
                month_days_list = self.stats_dict[year][month][0]
                month_sets_lits = self.stats_dict[year][month][1]
                Month_Plot.days = month_days_list
                Month_Plot.weights = month_sets_lits
                month_graph = Month_Plot(size_hint_y=None, height=self.app.window_size[1] / 2,
                                         pos_hint={"center_y": 0.3, "center_x": 0.5})

                month_best_set = self.stats_dict[year][month][2]
                new_label = calendar.month_abbr[month] + " ," + str(year)
                self.set_record(month_best_set, new_label)
                self.curr_month_best = month_best_set

                self.curr_graph = month_graph
                self.curr_month = [year, month]
                self.curr_mode = 'Month'
                self.month_graph = month_graph
                self.ids.stats_layout.add_widget(month_graph)
                self.ids.no_data.opacity = 0

            else:
                self.ids.no_data.opacity = 1
                self.set_record(0, 0)

        else:
            self.ids.no_data.opacity = 1
            self.set_record(0, 0)

    def add_year_plot(self, year):
        try:
            self.ids.stats_layout.remove_widget(self.curr_graph)
        except:
            pass
        if year in self.stats_dict:
            best_set = [0 for i in range(12)]
            best_month_set_list = []
            for month in self.stats_dict[year]:
                best_month_set = self.stats_dict[year][month][2]
                best_set[month - 1] = float(best_month_set.split()[2])
                best_month_set_list.append(best_month_set)

            best_set_of_the_year = self.app.find_best_set(best_month_set_list)
            self.set_record(best_set_of_the_year, str(year))
            self.curr_year_best = best_set_of_the_year

            Year_Plot.weights = best_set
            year_graph = Year_Plot(size_hint_y=None, height=self.app.window_size[1] / 2,
                                   pos_hint={"center_y": 0.3, "center_x": 0.5})

            self.curr_graph = year_graph
            self.curr_year = year
            self.curr_mode = 'Year'

            self.year_graph = year_graph
            self.ids.stats_layout.add_widget(year_graph)
            self.ids.no_data.opacity = 0

        else:
            self.ids.no_data.opacity = 1
            self.set_record(0, 0)

    def on_tab_switch(self, *args):
        period = args[3][9:14]
        self.curr_mode = period
        try:
            self.ids.stats_layout.remove_widget(self.curr_graph)
        except:
            pass
        if period == 'Month':
            if self.month_graph:
                self.ids.stats_layout.add_widget(self.month_graph)
                self.curr_graph = self.month_graph
            month_abb = calendar.month_abbr[self.curr_month[1]]
            new_label = month_abb + " ," + str(self.curr_month[0])
            self.ids.curr_label.text = new_label
            self.set_record(self.curr_month_best, new_label)

        else:
            if self.year_graph:
                self.ids.stats_layout.add_widget(self.year_graph)
            self.curr_graph = self.year_graph
            new_label = str(self.curr_year)
            self.ids.curr_label.text = new_label
            self.set_record(self.curr_year_best, new_label)

    def switch_left(self, *args):
        print(args[0].icon[8:])

        direction = args[0].icon[8:]
        curr_mode = self.curr_mode

        new_label = ''

        if direction == 'left':
            to_add = -1
        else:
            to_add = 1

        if curr_mode == 'Month':
            curr_year = self.curr_month[0]
            new_month = self.curr_month[1] + to_add

            if new_month > 12:
                new_month = new_month % 12
                curr_year += 1

            if new_month == 0:
                new_month = 12
                curr_year -= 1

            if self.is_date_future(new_month, curr_year):
                return
            else:
                new_label = calendar.month_abbr[new_month] + " ," + str(curr_year)
                self.curr_month = [curr_year, new_month]
                self.ids.curr_label.text = new_label
                self.add_month_plot(curr_year, new_month)

        else:
            new_label = self.curr_year + to_add
            if self.is_date_future(self.today_date.month, new_label):
                return
            else:
                self.curr_year = new_label
                self.ids.curr_label.text = str(new_label)
                self.add_year_plot(new_label)

    def is_date_future(self, month, year):
        curr_month = self.today_date.month
        curr_year = self.today_date.year

        if int(year) > curr_year:
            return True
        if int(year) < curr_year:
            return False
        if int(month) > curr_month:
            return True
        return False

    def set_record(self, record, period):
        if record:
            record = record.split()
            best_reps = record[0]
            best_weight = record[2]
            self.app.root.ids['exercise_stats_screen'].ids["best_month_title"].text = "Best of " + period

            self.app.root.ids['exercise_stats_screen'].ids["best_month_reps"].text = best_reps
            self.app.root.ids['exercise_stats_screen'].ids["best_month_weight"].text = best_weight
        else:
            self.app.root.ids['exercise_stats_screen'].ids["best_month_title"].text = "N/A"

            self.app.root.ids['exercise_stats_screen'].ids["best_month_reps"].text = "0"
            self.app.root.ids['exercise_stats_screen'].ids["best_month_weight"].text = "0"
