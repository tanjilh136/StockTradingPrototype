import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QApplication
from second_screen_pack.Charts import CandleStickInstance, LineChartInstance
from second_screen_pack.time_and_sales import TimeAndSales
import pandas as pd
from trade_backend.trader import PolygonData

sample_data = "sample_data/sample-candlestick-data.csv"
movers_data_update_path = "app_data/market/updated_sorted_movers.csv"
downloaded_symbol_data_base_path = "app_data/market/barset/"


class SecondScreen(QWidget):
    def __init__(self, parent=None):
        super(SecondScreen, self).__init__(parent)
        self.setMinimumSize(1000, 580)
        self.parent_v_layout = QVBoxLayout()
        self.parent_v_layout.setContentsMargins(0, 0, 0, 0)
        top_control_widget = Top_Control_Section()
        top_control_widget.setMinimumHeight(105)
        top_control_widget.setMaximumHeight(105)
        self.grid_ob = Grid_Control_Section()
        top_control_widget.refer_grid_ob(self.grid_ob)
        self.parent_v_layout.addWidget(top_control_widget)
        self.parent_v_layout.addWidget(self.grid_ob)

        self.setLayout(self.parent_v_layout)


class Top_Control_Section(QWidget):
    def __init__(self, parent=None):
        super(Top_Control_Section, self).__init__(parent)
        h_layout = QHBoxLayout()
        self.movers_asc_order = pd.read_csv(movers_data_update_path)
        self.current_start_index = 0
        if len(self.movers_asc_order) < 8:
            self.current_stop_index = len(self.movers_asc_order) - 1
        else:
            self.current_stop_index = 7

        h_layout.addLayout(self.p_m_a_layout())
        h_layout.addLayout(self.ts_sp_layout())
        h_layout.addStretch()
        h_layout.addLayout(self.stock_tickers_layout())
        h_layout.addStretch()
        h_layout.addLayout(self.show_next_layout())
        h_layout.addLayout(self.show_t_show_l_layout())
        self.setLayout(h_layout)
        self.btn_show_tops_clicked()

    def refer_grid_ob(self, grid_ob):
        self.grid_ob = grid_ob

    def show_t_show_l_layout(self):
        btn_min_width = 100
        btn_min_height = 40

        v_layout = QVBoxLayout()
        self.btn_show_tops = QPushButton("Show Tops")
        self.btn_show_low = QPushButton("Show Low")

        self.btn_show_tops.setMinimumSize(btn_min_width, btn_min_height)
        self.btn_show_low.setMinimumSize(btn_min_width, btn_min_height)
        self.btn_show_tops.setMaximumSize(btn_min_width, btn_min_height)
        self.btn_show_low.setMaximumSize(btn_min_width, btn_min_height)

        # Setting Signal Slot (Listeners)
        self.btn_show_tops.clicked.connect(self.btn_show_tops_clicked)
        self.btn_show_low.clicked.connect(self.btn_show_low_clicked)

        v_layout.addWidget(self.btn_show_tops)
        v_layout.addWidget(self.btn_show_low)
        return v_layout

    def btn_show_tops_clicked(self):
        print("Show Tops Clicked")
        self.current_start_index = 0
        if len(self.movers_asc_order) < 8:
            self.current_stop_index = len(self.movers_asc_order) - 1
        else:
            self.current_stop_index = 7

        dx = self.movers_asc_order.loc[(self.movers_asc_order.index >= self.current_start_index) & (
                self.movers_asc_order.index <= self.current_stop_index)]
        dx.reset_index(inplace=True)
        self.set_ticker_ui_data(dx)

    def btn_show_low_clicked(self):
        print("Show Low Clicked")

        if len(self.movers_asc_order) < 8:
            self.current_start_index = 0

        else:
            self.current_start_index = len(self.movers_asc_order) - 8

        self.current_stop_index = len(self.movers_asc_order) - 1

        dx = self.movers_asc_order.loc[(self.movers_asc_order.index >= self.current_start_index) & (
                self.movers_asc_order.index <= self.current_stop_index)]
        dx.reset_index(inplace=True)
        self.set_ticker_ui_data(dx)

    def show_next_layout(self):
        btn_min_width = 100
        gap_between_buttons = 3
        btn_min_height = (25 + gap_between_buttons) * 2
        v_layout = QVBoxLayout()
        v_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.btn_show_next = QPushButton("Show Next")
        self.btn_show_next.clicked.connect(self.btn_show_next_clicked)
        self.btn_show_next.setMinimumSize(btn_min_width, btn_min_height)
        v_layout.addWidget(self.btn_show_next)
        return v_layout

    def btn_show_next_clicked(self):
        print("Show Next Clicked")
        if self.current_stop_index != len(self.movers_asc_order) - 1:
            if (len(self.movers_asc_order) - self.current_stop_index) > 8:
                self.current_start_index = self.current_stop_index + 1
                self.current_stop_index = self.current_stop_index + 8
            else:
                self.current_stop_index = len(self.movers_asc_order) - 1
                self.current_start_index = self.current_stop_index - 7
                # Bug Report
                # When data are less than 8 then the program will crash

        else:
            # No data in next
            print("No next data")
        dx = self.movers_asc_order.loc[(self.movers_asc_order.index >= self.current_start_index) & (
                self.movers_asc_order.index <= self.current_stop_index)]
        dx.reset_index(inplace=True)
        self.set_ticker_ui_data(dx)
        # self.set_ticker_ui_data(self.movers_asc_order[self.current_start_index:self.current_stop_index + 1])

    def stock_tickers_layout(self):
        main_h_layout = QHBoxLayout()
        btn_min_height = 43
        total_symbols_to_display = 8

        self.btn_symbol_name_array = []
        self.btn_symbol_value_array = []

        for i in range(total_symbols_to_display):
            symbol_data_holder_v_layout = QVBoxLayout()
            self.btn_symbol_name_array.append(QPushButton())
            self.btn_symbol_value_array.append(QPushButton())

            self.btn_symbol_name_array[i].setStyleSheet(stock_ticker_symbol_btn_style)
            self.btn_symbol_value_array[i].setStyleSheet(stock_ticker_value_btn_style)
            self.btn_symbol_name_array[i].setMinimumHeight(btn_min_height)
            self.btn_symbol_value_array[i].setMinimumHeight(btn_min_height)
            symbol_data_holder_v_layout.addWidget(self.btn_symbol_name_array[i])
            symbol_data_holder_v_layout.addWidget(self.btn_symbol_value_array[i])
            main_h_layout.addLayout(symbol_data_holder_v_layout)

        # Setting Signal Slot (Listeners) for 8 buttons
        self.btn_symbol_name_array[0].clicked.connect(
            lambda: self.btn_symbol_name_clicked(self.btn_symbol_name_array[0], 0))
        self.btn_symbol_name_array[1].clicked.connect(
            lambda: self.btn_symbol_name_clicked(self.btn_symbol_name_array[1], 1))
        self.btn_symbol_name_array[2].clicked.connect(
            lambda: self.btn_symbol_name_clicked(self.btn_symbol_name_array[2], 2))
        self.btn_symbol_name_array[3].clicked.connect(
            lambda: self.btn_symbol_name_clicked(self.btn_symbol_name_array[3], 3))
        self.btn_symbol_name_array[4].clicked.connect(
            lambda: self.btn_symbol_name_clicked(self.btn_symbol_name_array[4], 4))
        self.btn_symbol_name_array[5].clicked.connect(
            lambda: self.btn_symbol_name_clicked(self.btn_symbol_name_array[5], 5))
        self.btn_symbol_name_array[6].clicked.connect(
            lambda: self.btn_symbol_name_clicked(self.btn_symbol_name_array[6], 6))
        self.btn_symbol_name_array[7].clicked.connect(
            lambda: self.btn_symbol_name_clicked(self.btn_symbol_name_array[7], 7))

        main_h_layout.setSpacing(0)
        return main_h_layout

    def set_ticker_ui_data(self, df):

        """
        :param df: contans data to be displayed
        :return:
        """
        print(df)
        for ticker_index in range(len(self.btn_symbol_name_array)):
            try:
                print(df["ticker"][ticker_index])
                print(df["percent"][ticker_index])
                self.btn_symbol_name_array[ticker_index].setText(str(df["ticker"][ticker_index]))
                self.btn_symbol_value_array[ticker_index].setText(str(df["percent"][ticker_index]))
            except:
                self.btn_symbol_name_array[ticker_index].setText(str(""))
                self.btn_symbol_value_array[ticker_index].setText("")

    def btn_symbol_name_clicked(self, btn, pos):
        print(f"Symbol {btn.text()} Clicked: {pos}")
        self.grid_ob.grid_data_updater(btn.text())

    def ts_sp_layout(self):
        btn_min_width = 100
        btn_min_height = 25
        left_v_layout_2 = QVBoxLayout()
        label_top_symbol = QLabel("Top Symbol")
        label_top_symbol.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_show_previous = QPushButton("Show Previous")

        label_top_symbol.setMinimumSize(btn_min_width, btn_min_height)
        self.btn_show_previous.setMinimumSize(btn_min_width, (btn_min_height + 3) * 2)
        label_top_symbol.setMaximumSize(btn_min_width, btn_min_height)
        self.btn_show_previous.setMaximumSize(btn_min_width, (btn_min_height + 3) * 2)

        # Setting Signal Slot (Listeners)
        self.btn_show_previous.clicked.connect(self.btn_show_previous_clicked)
        left_v_layout_2.addWidget(label_top_symbol)
        left_v_layout_2.addWidget(self.btn_show_previous)
        return left_v_layout_2

    def btn_show_previous_clicked(self):
        print("Show Previous Clicked")
        if self.current_start_index != 0:
            if self.current_start_index > 7:
                self.current_stop_index = self.current_start_index - 1
                self.current_start_index = self.current_start_index - 8
            else:
                self.current_start_index = 0
                if len(self.movers_asc_order) >= 8:
                    self.current_stop_index = 7
                else:
                    self.current_stop_index = len(self.movers_asc_order) - 1
        else:
            # No data in previous
            print("No previous data")

        dx = self.movers_asc_order.loc[(self.movers_asc_order.index >= self.current_start_index) & (
                self.movers_asc_order.index <= self.current_stop_index)]
        dx.reset_index(inplace=True)
        self.set_ticker_ui_data(dx)

    def p_m_a_layout(self):
        btn_min_width = 100
        btn_min_height = 25
        left_v_layout_1 = QVBoxLayout()
        self.btn_pre_market = QPushButton("Pre Market")
        self.btn_market = QPushButton("Market")
        self.btn_after_hours = QPushButton("After Hours")

        self.btn_pre_market.setMinimumSize(btn_min_width, btn_min_height)
        self.btn_market.setMinimumSize(btn_min_width, btn_min_height)
        self.btn_after_hours.setMinimumSize(btn_min_width, btn_min_height)

        self.btn_pre_market.setMaximumSize(btn_min_width, btn_min_height)
        self.btn_market.setMaximumSize(btn_min_width, btn_min_height)
        self.btn_after_hours.setMaximumSize(btn_min_width, btn_min_height)

        # Setting Signal Slot (Listeners)
        self.btn_pre_market.clicked.connect(self.btn_pre_market_clicked)
        self.btn_market.clicked.connect(self.btn_market_clicked)
        self.btn_after_hours.clicked.connect(self.btn_after_hours_clicked)

        left_v_layout_1.addWidget(self.btn_pre_market)
        left_v_layout_1.addWidget(self.btn_market)
        left_v_layout_1.addWidget(self.btn_after_hours)
        return left_v_layout_1

    def btn_pre_market_clicked(self):
        print("Pre Market Clicked")

    def btn_market_clicked(self):
        print("Market Clicked")

    def btn_after_hours_clicked(self):
        print("After Hours Clicked")


class Grid_Control_Section(QWidget):
    COLUMN1 = 1
    COLUMN2 = 2
    COLUMN3 = 3
    COLUMN4 = 4

    def __init__(self, parent=None):
        super(Grid_Control_Section, self).__init__(parent)
        self.setStyleSheet(grid_widget_style)
        self.column_name_color = "#DBE2F1"
        self.row_name_color = "#DBE2F1"
        h_layout = QHBoxLayout()
        h_layout.setSpacing(0)
        h_layout.addWidget(self.row_names_layout())
        h_layout.addWidget(self.first_column_layout())
        h_layout.addWidget(self.second_column_layout())
        h_layout.addWidget(self.third_column_layout())
        h_layout.addWidget(self.fourth_column_layout())
        self.fill_waiting_column = self.COLUMN1
        self.polygon_api = PolygonData()
        self.setLayout(h_layout)

    def grid_data_updater(self, symbol_name):
        if self.fill_waiting_column == self.COLUMN1:
            self.label_symbol_1.setText(symbol_name)
            self.fill_waiting_column = self.COLUMN2

        elif self.fill_waiting_column == self.COLUMN2:
            self.label_symbol_2.setText(symbol_name)
            self.fill_waiting_column = self.COLUMN3

        elif self.fill_waiting_column == self.COLUMN3:
            self.label_symbol_3.setText(symbol_name)
            self.fill_waiting_column = self.COLUMN4

        elif self.fill_waiting_column == self.COLUMN4:
            self.label_symbol_4.setText(symbol_name)
            self.fill_waiting_column = self.COLUMN1

    def grid_reset(self, symbol_name="Symbol Name"):
        # Clear Symbol Labels
        self.label_symbol_1.setText(symbol_name)
        self.label_symbol_2.setText(symbol_name)
        self.label_symbol_3.setText(symbol_name)
        self.label_symbol_4.setText(symbol_name)

    def row_names_layout(self):
        frame = QWidget()
        first_row_min_max_height = 50
        v_layout = QVBoxLayout()
        label_symbol = QLabel("Symbol")
        label_symbol.setAlignment(Qt.AlignCenter)
        label_symbol.setStyleSheet("background-color:white")
        label_symbol.setMinimumSize(100, first_row_min_max_height)
        label_symbol.setMaximumSize(100, first_row_min_max_height)

        row_1_label = QLabel("Markets")
        row_2_label = QLabel("5 days")
        row_3_label = QLabel("Time and Sales")
        row_1_label.setAlignment(Qt.AlignCenter)
        row_2_label.setAlignment(Qt.AlignCenter)
        row_3_label.setAlignment(Qt.AlignCenter)
        row_1_label.setStyleSheet("background-color:" + self.row_name_color)
        row_2_label.setStyleSheet("background-color:" + self.row_name_color)
        row_3_label.setStyleSheet("background-color:" + self.row_name_color)

        v_layout.setSpacing(0)
        v_layout.addWidget(label_symbol)
        v_layout.addWidget(row_1_label)
        v_layout.addWidget(row_2_label)
        v_layout.addWidget(row_3_label)

        v_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(v_layout)
        frame.setFixedWidth(100)
        return frame

    def btn_time_and_sales_clicked(self, symbol):
        df = PolygonData().get_time_n_sales(symbol)
        print("Time and sales data fetched")
        # self is used to bypass garbaze collector
        self.client_info_table = TimeAndSales(df)
        self.client_info_table.populate_client_info_table(df.to_numpy())
        self.client_info_table.show()

    def first_column_layout(self):
        current_column_no = 2
        txt_line_chart = "Line Chart"
        txt_candle_stick_chart = "Candlestick Chart"
        frame = QWidget()
        first_row_min_max_height = 50
        v_layout = QVBoxLayout()
        v_layout.setSpacing(0)

        self.label_symbol_1 = QLabel("")
        self.label_symbol_1.setAlignment(Qt.AlignCenter)
        self.label_symbol_1.setStyleSheet("background-color:" + self.column_name_color)
        self.label_symbol_1.setMinimumHeight(first_row_min_max_height)
        self.label_symbol_1.setMaximumHeight(first_row_min_max_height)

        # Widgets for row 2 (first row contains symbol names)

        # Market Data Row
        row_2_widget = QWidget()
        row_2_v_layout = QVBoxLayout()
        row_2_widget.setLayout(row_2_v_layout)
        row_2_v_layout.setAlignment(Qt.AlignCenter)
        self.btn_line_chart_column_2_row_2 = QPushButton(txt_line_chart)
        self.btn_candlestick_chart_column_2_row_2 = QPushButton(txt_candle_stick_chart)

        # Setting signal slot in market data row
        self.btn_line_chart_column_2_row_2.clicked.connect(
            lambda: self.btn_line_chart_clicked(self.label_symbol_1.text(), current_column_no, self.MARKET_ROW))
        self.btn_candlestick_chart_column_2_row_2.clicked.connect(
            lambda: self.btn_candlestick_chart_clicked(self.label_symbol_1.text(),
                                                       current_column_no, self.MARKET_ROW))

        row_2_v_layout.addWidget(self.btn_line_chart_column_2_row_2)
        row_2_v_layout.addWidget(self.btn_candlestick_chart_column_2_row_2)

        # Widgets for row 3 (first row contains symbol names)
        # 5 Days Row
        row_3_widget = QWidget()
        row_3_v_layout = QVBoxLayout()
        row_3_widget.setLayout(row_3_v_layout)
        row_3_v_layout.setAlignment(Qt.AlignCenter)
        self.btn_line_chart_column_2_row_3 = QPushButton(txt_line_chart)
        self.btn_candlestick_chart_column_2_row_3 = QPushButton(txt_candle_stick_chart)

        # Setting signal slot in 5 days row
        self.btn_line_chart_column_2_row_3.clicked.connect(
            lambda: self.btn_line_chart_clicked(self.label_symbol_1.text(), current_column_no, self.FIVE_DAYS_ROW))
        self.btn_candlestick_chart_column_2_row_3.clicked.connect(
            lambda: self.btn_candlestick_chart_clicked(self.label_symbol_1.text(), current_column_no,
                                                       self.FIVE_DAYS_ROW))

        row_3_v_layout.addWidget(self.btn_line_chart_column_2_row_3)
        row_3_v_layout.addWidget(self.btn_candlestick_chart_column_2_row_3)

        # Widgets for row 4 (first row contains symbol names)
        row_4_widget = QWidget()
        row_4_v_layout = QVBoxLayout()
        row_4_widget.setLayout(row_4_v_layout)
        row_4_v_layout.setAlignment(Qt.AlignCenter)
        self.time_column_2_row_4 = QPushButton("Time and Sales")
        self.time_column_2_row_4.clicked.connect(
            lambda: self.btn_time_and_sales_clicked(self.label_symbol_1.text()))
        row_4_v_layout.addWidget(self.time_column_2_row_4)

        v_layout.addWidget(self.label_symbol_1)
        v_layout.addWidget(row_2_widget)
        v_layout.addWidget(row_3_widget)
        v_layout.addWidget(row_4_widget)
        v_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(v_layout)
        return frame

    def display_candle_stick(self, file, file_type="csv"):
        # must use self to show window, otherwise garbase collector will
        # destroy local variable which results the window destroyed
        self.candle = CandleStickInstance(file=file, file_type=file_type)
        self.candle.show()

    def display_line_chart(self, file, file_type="csv"):
        self.line = LineChartInstance(file=file, file_type=file_type)
        self.line.show()

    MARKET_ROW = "MARKET_ROW"
    FIVE_DAYS_ROW = "FIVE_DAYS_ROW"

    def btn_line_chart_clicked(self, symbol, column_n, row_name):
        if row_name == self.MARKET_ROW:
            df = self.polygon_api.get_prev_n_days_trade_data(symbol, 0, "minute")
            self.display_line_chart(file=df, file_type="df")

        elif row_name == self.FIVE_DAYS_ROW:
            df = self.polygon_api.get_prev_n_days_trade_data(symbol, 5, "minute")
            self.display_line_chart(file=df, file_type="df")

    def btn_candlestick_chart_clicked(self, symbol, column_n, row_name):
        if row_name == self.MARKET_ROW:
            df = self.polygon_api.get_prev_n_days_trade_data(symbol, 0, "minute")
            self.display_candle_stick(file=df, file_type="df")

        elif row_name == self.FIVE_DAYS_ROW:
            df = self.polygon_api.get_prev_n_days_trade_data(symbol, 5, "minute")
            self.display_candle_stick(file=df, file_type="df")

    def second_column_layout(self):
        current_column_no = 3
        txt_line_chart = "Line Chart"
        txt_candle_stick_chart = "Candlestick Chart"
        frame = QWidget()
        first_row_min_max_height = 50
        v_layout = QVBoxLayout()
        v_layout.setSpacing(0)

        self.label_symbol_2 = QLabel("")
        self.label_symbol_2.setAlignment(Qt.AlignCenter)
        self.label_symbol_2.setStyleSheet("background-color:" + self.column_name_color)
        self.label_symbol_2.setMinimumHeight(first_row_min_max_height)
        self.label_symbol_2.setMaximumHeight(first_row_min_max_height)

        # Widgets for row 2 (first row contains symbol names)
        row_2_widget = QWidget()
        row_2_v_layout = QVBoxLayout()
        row_2_widget.setLayout(row_2_v_layout)
        row_2_v_layout.setAlignment(Qt.AlignCenter)
        self.btn_line_chart_column_3_row_2 = QPushButton(txt_line_chart)
        self.btn_candlestick_chart_column_3_row_2 = QPushButton(txt_candle_stick_chart)

        # Setting signal slot
        self.btn_line_chart_column_3_row_2.clicked.connect(
            lambda: self.btn_line_chart_clicked(self.label_symbol_2.text(), current_column_no, self.MARKET_ROW))
        self.btn_candlestick_chart_column_3_row_2.clicked.connect(
            lambda: self.btn_candlestick_chart_clicked(self.label_symbol_2.text(), current_column_no, self.MARKET_ROW))

        row_2_v_layout.addWidget(self.btn_line_chart_column_3_row_2)
        row_2_v_layout.addWidget(self.btn_candlestick_chart_column_3_row_2)

        # Widgets for row 3 (first row contains symbol names)
        row_3_widget = QWidget()
        row_3_v_layout = QVBoxLayout()
        row_3_widget.setLayout(row_3_v_layout)
        row_3_v_layout.setAlignment(Qt.AlignCenter)
        self.btn_line_chart_column_3_row_3 = QPushButton(txt_line_chart)
        self.btn_candlestick_chart_column_3_row_3 = QPushButton(txt_candle_stick_chart)

        # Setting signal slot
        self.btn_line_chart_column_3_row_3.clicked.connect(
            lambda: self.btn_line_chart_clicked(self.label_symbol_2.text(), current_column_no, self.FIVE_DAYS_ROW))
        self.btn_candlestick_chart_column_3_row_3.clicked.connect(
            lambda: self.btn_candlestick_chart_clicked(self.label_symbol_2.text(), current_column_no,
                                                       self.FIVE_DAYS_ROW))

        row_3_v_layout.addWidget(self.btn_line_chart_column_3_row_3)
        row_3_v_layout.addWidget(self.btn_candlestick_chart_column_3_row_3)

        # Widgets for row 4 (first row contains symbol names)
        row_4_widget = QWidget()
        row_4_v_layout = QVBoxLayout()
        row_4_widget.setLayout(row_4_v_layout)
        row_4_v_layout.setAlignment(Qt.AlignCenter)
        self.time_column_3_row_4 = QPushButton("Time and Sales")
        self.time_column_3_row_4.clicked.connect(
            lambda: self.btn_time_and_sales_clicked(self.label_symbol_2.text()))

        row_4_v_layout.addWidget(self.time_column_3_row_4)

        v_layout.addWidget(self.label_symbol_2)
        v_layout.addWidget(row_2_widget)
        v_layout.addWidget(row_3_widget)
        v_layout.addWidget(row_4_widget)
        v_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(v_layout)
        return frame

    def third_column_layout(self):
        current_column_no = 4
        txt_line_chart = "Line Chart"
        txt_candle_stick_chart = "Candlestick Chart"
        frame = QWidget()
        first_row_min_max_height = 50
        v_layout = QVBoxLayout()
        v_layout.setSpacing(0)

        self.label_symbol_3 = QLabel("")
        self.label_symbol_3.setAlignment(Qt.AlignCenter)
        self.label_symbol_3.setStyleSheet("background-color:" + self.column_name_color)
        self.label_symbol_3.setMinimumHeight(first_row_min_max_height)
        self.label_symbol_3.setMaximumHeight(first_row_min_max_height)

        # Widgets for row 2 (first row contains symbol names)
        row_2_widget = QWidget()
        row_2_v_layout = QVBoxLayout()
        row_2_widget.setLayout(row_2_v_layout)
        row_2_v_layout.setAlignment(Qt.AlignCenter)
        self.btn_line_chart_column_4_row_2 = QPushButton(txt_line_chart)
        self.btn_candlestick_chart_column_4_row_2 = QPushButton(txt_candle_stick_chart)

        # Setting signal slot
        self.btn_line_chart_column_4_row_2.clicked.connect(
            lambda: self.btn_line_chart_clicked(self.label_symbol_3.text(), current_column_no, self.MARKET_ROW))
        self.btn_candlestick_chart_column_4_row_2.clicked.connect(
            lambda: self.btn_candlestick_chart_clicked(self.label_symbol_3.text(), current_column_no, self.MARKET_ROW))

        row_2_v_layout.addWidget(self.btn_line_chart_column_4_row_2)
        row_2_v_layout.addWidget(self.btn_candlestick_chart_column_4_row_2)

        # Widgets for row 3 (first row contains symbol names)
        row_3_widget = QWidget()
        row_3_v_layout = QVBoxLayout()
        row_3_widget.setLayout(row_3_v_layout)
        row_3_v_layout.setAlignment(Qt.AlignCenter)
        self.btn_line_chart_column_4_row_3 = QPushButton(txt_line_chart)
        self.btn_candlestick_chart_column_4_row_3 = QPushButton(txt_candle_stick_chart)

        # Setting signal slot
        self.btn_line_chart_column_4_row_3.clicked.connect(
            lambda: self.btn_line_chart_clicked(self.label_symbol_3.text(), current_column_no, self.FIVE_DAYS_ROW))
        self.btn_candlestick_chart_column_4_row_3.clicked.connect(
            lambda: self.btn_candlestick_chart_clicked(self.label_symbol_3.text(), current_column_no,
                                                       self.FIVE_DAYS_ROW))

        row_3_v_layout.addWidget(self.btn_line_chart_column_4_row_3)
        row_3_v_layout.addWidget(self.btn_candlestick_chart_column_4_row_3)

        # Widgets for row 4 (first row contains symbol names)
        row_4_widget = QWidget()
        row_4_v_layout = QVBoxLayout()
        row_4_widget.setLayout(row_4_v_layout)
        row_4_v_layout.setAlignment(Qt.AlignCenter)
        self.time_column_4_row_4 = QPushButton("Time and Sales")
        self.time_column_4_row_4.clicked.connect(
            lambda: self.btn_time_and_sales_clicked(self.label_symbol_3.text()))

        row_4_v_layout.addWidget(self.time_column_4_row_4)

        v_layout.addWidget(self.label_symbol_3)
        v_layout.addWidget(row_2_widget)
        v_layout.addWidget(row_3_widget)
        v_layout.addWidget(row_4_widget)
        v_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(v_layout)
        return frame

    def fourth_column_layout(self):
        current_column_no = 5
        txt_line_chart = "Line Chart"
        txt_candle_stick_chart = "Candlestick Chart"
        frame = QWidget()
        first_row_min_max_height = 50
        v_layout = QVBoxLayout()
        v_layout.setSpacing(0)

        self.label_symbol_4 = QLabel("")
        self.label_symbol_4.setAlignment(Qt.AlignCenter)
        self.label_symbol_4.setStyleSheet("background-color:" + self.column_name_color)
        self.label_symbol_4.setMinimumHeight(first_row_min_max_height)
        self.label_symbol_4.setMaximumHeight(first_row_min_max_height)

        # Widgets for row 2 (first row contains symbol names)
        row_2_widget = QWidget()
        row_2_v_layout = QVBoxLayout()
        row_2_widget.setLayout(row_2_v_layout)
        row_2_v_layout.setAlignment(Qt.AlignCenter)
        self.btn_line_chart_column_5_row_2 = QPushButton(txt_line_chart)
        self.btn_candlestick_chart_column_5_row_2 = QPushButton(txt_candle_stick_chart)

        # Setting signal slot
        self.btn_line_chart_column_5_row_2.clicked.connect(
            lambda: self.btn_line_chart_clicked(self.label_symbol_4.text(), current_column_no, self.MARKET_ROW))
        self.btn_candlestick_chart_column_5_row_2.clicked.connect(
            lambda: self.btn_candlestick_chart_clicked(self.label_symbol_4.text(), current_column_no, self.MARKET_ROW))

        row_2_v_layout.addWidget(self.btn_line_chart_column_5_row_2)
        row_2_v_layout.addWidget(self.btn_candlestick_chart_column_5_row_2)

        # Widgets for row 3 (first row contains symbol names)
        row_3_widget = QWidget()
        row_3_v_layout = QVBoxLayout()
        row_3_widget.setLayout(row_3_v_layout)
        row_3_v_layout.setAlignment(Qt.AlignCenter)
        self.btn_line_chart_column_5_row_3 = QPushButton(txt_line_chart)
        self.btn_candlestick_chart_column_5_row_3 = QPushButton(txt_candle_stick_chart)

        # Setting signal slot
        self.btn_line_chart_column_5_row_3.clicked.connect(
            lambda: self.btn_line_chart_clicked(self.label_symbol_4.text(), current_column_no, self.FIVE_DAYS_ROW))
        self.btn_candlestick_chart_column_5_row_3.clicked.connect(
            lambda: self.btn_candlestick_chart_clicked(self.label_symbol_4.text(), current_column_no,
                                                       self.FIVE_DAYS_ROW))

        row_3_v_layout.addWidget(self.btn_line_chart_column_5_row_3)
        row_3_v_layout.addWidget(self.btn_candlestick_chart_column_5_row_3)

        # Widgets for row 4 (first row contains symbol names)
        row_4_widget = QWidget()
        row_4_v_layout = QVBoxLayout()
        row_4_widget.setLayout(row_4_v_layout)
        row_4_v_layout.setAlignment(Qt.AlignCenter)
        self.time_column_5_row_4 = QPushButton("Time and Sales")
        self.time_column_5_row_4.clicked.connect(
            lambda: self.btn_time_and_sales_clicked(self.label_symbol_4.text()))

        row_4_v_layout.addWidget(self.time_column_5_row_4)

        v_layout.addWidget(self.label_symbol_4)
        v_layout.addWidget(row_2_widget)
        v_layout.addWidget(row_3_widget)
        v_layout.addWidget(row_4_widget)
        v_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(v_layout)
        return frame


grid_widget_style = """QWidget {
    border: 1px solid #8f8f91;
    background-color: white;
}
QLabel{
    border:0px
}
QPushButton {
    background-color: #AFC8FF 
}
QPushButton:hover {
    background-color: #9CB8F4
}
QPushButton:pressed {
    background-color: #89A7E9
}"""
stock_ticker_symbol_btn_style = """QPushButton {
    border-top: 1px solid #8f8f91;
    border-left: 1px solid #8f8f91;
    border-right: 1px solid #8f8f91;
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #B4FCBA, stop: 1 #f6f7fa);
    min-width: 80px;
}
QPushButton:hover {
    background-color: #B4FCBA
}
QPushButton:pressed {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #f6f7fa, stop: 1 #B4FCBA);
}

QPushButton:flat {
    border: none; /* no border for a flat push button */
}

QPushButton:default {
    border-color: navy; /* make the default button prominent */
}"""
stock_ticker_value_btn_style = """QPushButton {
    border-top: 0px solid #8f8f91;
    border-left: 1px solid #8f8f91;
    border-right: 1px solid #8f8f91;
    border-bottom: 1px solid #8f8f91;
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #f6f7fa, stop: 1 #B4FCBA);
    min-width: 80px;
}

QPushButton:pressed {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #B4FCBA, stop: 1 #f6f7fa);
}

QPushButton:flat {
    border: none; /* no border for a flat push button */
}

QPushButton:default {
    border-color: navy; /* make the default button prominent */
}"""
if __name__ == "__main__":
    sample_data = "../" + sample_data
    movers_data_update_path = "../" + movers_data_update_path
    downloaded_symbol_data_base_path = "../" + downloaded_symbol_data_base_path
    app = QApplication(sys.argv)
    second_screen = SecondScreen()
    second_screen.show()
    sys.exit(app.exec_())
