import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from trade_backend.trader import AlpakaTrader, PolygonData

MARKET_ORDER = "market"
LIMIT_ORDER = "limit"
STOP_LIMIT_ORDER = "stop_limit"


class FSControlInterface(QWidget):
    def __init__(self, parent=None):
        super(FSControlInterface, self).__init__(parent)
        self.trader = AlpakaTrader()
        self.polygon_data = PolygonData()
        self.selected_order_type = MARKET_ORDER
        self.only_int = QIntValidator()
        self.setMinimumSize(600, 300)
        self.setMaximumSize(800, 400)
        self.parent_v_layout = QVBoxLayout()

        # margin is set to zero so that when the widget is used in another widget, its margin stays zero in that widget
        self.parent_v_layout.setContentsMargins(0, 0, 0, 0)

        self.top_h_layout_1 = QHBoxLayout()
        self.draw_fields_in_top_h_layout_1(self.top_h_layout_1)

        self.top_h_layout_2 = QHBoxLayout()
        self.draw_company_name_field_in_top_h_layout_2(self.top_h_layout_2)

        self.top_h_layout_3 = QHBoxLayout()
        self.draw_order_type_field_in_top_h_layout_2(self.top_h_layout_3)

        self.top_h_layout_4 = QHBoxLayout()
        self.draw_action_field_in_top_h_layout_4(self.top_h_layout_4)

        self.top_h_layout_5 = QHBoxLayout()
        self.draw_active_mode_in_top_h_layout_4(self.top_h_layout_5)

        self.top_h_layout_6 = QHBoxLayout()
        self.draw_confirm_field_in_top_h_layout_6(self.top_h_layout_6)

        self.top_v_layout_7 = QVBoxLayout()
        self.draw_offset_field_in_top_v_layout_7(self.top_v_layout_7)

        self.parent_v_layout.addLayout(self.top_h_layout_1)
        self.parent_v_layout.addLayout(self.top_h_layout_2)
        self.parent_v_layout.addLayout(self.top_h_layout_3)
        self.parent_v_layout.addLayout(self.top_h_layout_4)
        self.parent_v_layout.addLayout(self.top_h_layout_5)
        self.parent_v_layout.addLayout(self.top_h_layout_6)
        self.parent_v_layout.addLayout(self.top_v_layout_7)

        self.setLayout(self.parent_v_layout)

    def send_bottom_table(self, bottom_table):
        self.bottom_table = bottom_table

    def draw_offset_field_in_top_v_layout_7(self, v_layout):
        offset_label = QLabel("Offset")
        h_layout_for_offset_fields = QHBoxLayout()
        offset_cents_label = QLabel("Cents:")
        self.offset_cents_input = QLineEdit()
        self.offset_cents_input.setFixedSize(60, 20)
        offset_percentage_label = QLabel("%")
        self.offset_percentage_input = QLineEdit()
        self.offset_percentage_input.setFixedSize(60, 20)
        btn_offset_close = QPushButton("Close Now")
        btn_offset_close.clicked.connect(self.btn_offset_close_clicked)

        h_layout_for_offset_fields.addWidget(offset_cents_label)
        h_layout_for_offset_fields.addWidget(self.offset_cents_input)
        h_layout_for_offset_fields.addWidget(offset_percentage_label)
        h_layout_for_offset_fields.addWidget(self.offset_percentage_input)
        h_layout_for_offset_fields.addStretch()
        h_layout_for_offset_fields.addWidget(btn_offset_close)

        v_layout.addWidget(offset_label)
        v_layout.addLayout(h_layout_for_offset_fields)

    def btn_offset_close_clicked(self):
        print("Offset Close Button Clicked")

    def draw_confirm_field_in_top_h_layout_6(self, h_layout):
        self.confirmation_details = QLabel("...........")
        self.btn_confirm = QPushButton("Confirm")
        self.btn_confirm.clicked.connect(self.btn_confirm_clicked)

        h_layout.addStretch()
        h_layout.addWidget(self.confirmation_details)
        h_layout.addWidget(self.btn_confirm)

    def btn_confirm_clicked(self):
        print("Confirm Button Clicked")
        if self.placing_side == "BUY":
            if self.selected_order_type == MARKET_ORDER:
                self.trader.buy_order(self.selected_order_type, self.placing_symbol, self.placing_qty)
                self.set_confirmation_details("Order Placed: Refreshing order table")
                self.bottom_table.update_table()
                self.set_confirmation_details("Success")

            elif self.selected_order_type == LIMIT_ORDER:
                self.trader.buy_order(self.selected_order_type, self.placing_symbol, self.placing_qty,
                                      limit_price=self.placing_price)
                self.set_confirmation_details("Order Placed: Refreshing order table")
                self.bottom_table.update_table()
                self.set_confirmation_details("Success")

        elif self.placing_price == "SELL":
            if self.selected_order_type == MARKET_ORDER:
                self.trader.sell_order(self.selected_order_type, self.placing_symbol, self.placing_qty)
                self.set_confirmation_details("Order Placed: Refreshing order table")
                self.bottom_table.update_table()
                self.set_confirmation_details("Success")

            elif self.selected_order_type == LIMIT_ORDER:
                self.trader.sell_order(self.selected_order_type, self.placing_symbol, self.placing_qty,
                                       limit_price=self.placing_price)
                self.set_confirmation_details("Order Placed: Refreshing order table")
                self.bottom_table.update_table()
                self.set_confirmation_details("Success")
        else:
            print("Error")

    def set_confirmation_details(self, details):
        self.confirmation_details.setText(details)

    def get_confirmation_details(self):
        return self.confirmation_details.text()

    def draw_active_mode_in_top_h_layout_4(self, h_layout):
        active_mode_label = QLabel("Active Mode:")
        self.active_mode_status = QPushButton("OFF")
        self.active_mode_status.setFixedSize(40, 20)
        self.active_mode_status.setCheckable(True)
        self.active_mode_status.clicked.connect(lambda: self.active_mode_clicked(self.active_mode_status))
        h_layout.addStretch()
        h_layout.addWidget(active_mode_label)
        h_layout.addWidget(self.active_mode_status)
        h_layout.addStretch()

    def is_active_mode_on(self):
        self.active_mode_status.isChecked()

    def active_mode_clicked(self, btn):
        if btn.isChecked():
            btn.setText("ON")
            print("Active mode: ON")
            # Active mode just turned on
            # Do something

        else:
            btn.setText("OFF")
            print("Active mode: OFF")
            # Active mode just turned off
            # Do something

    def draw_action_field_in_top_h_layout_4(self, h_layout):
        """
        Generates two different Action UI in one layout for buy and sell
        :param h_layout:
        :return:
        """
        # Action 1,2 Digit box and buy/sell button configuration
        total_digit_fields = 9
        buy_button_position = 5
        buy_button_label = "."
        digit_box_max_square_size = 20

        # Creating digit box and buy button for Action 1
        action_1_v_layout = QVBoxLayout()
        action_1_label = QLabel("Action-1")
        action_1_price_input_h_layout = QHBoxLayout()
        self.action_1_digit_fields = []

        for i in range(0, total_digit_fields):
            if i == buy_button_position - 1:
                # set buy button label
                btn_buy = QPushButton(buy_button_label)
                btn_buy.setMaximumSize(digit_box_max_square_size, digit_box_max_square_size)
                btn_buy.clicked.connect(self.action_1_buy_button_clicked)
                self.action_1_digit_fields.append(btn_buy)
            else:
                # create digit QLineEdit
                digit_box = QLineEdit()
                digit_box.setValidator(self.only_int)
                digit_box.setMaxLength(1)
                digit_box.setMaximumSize(digit_box_max_square_size, digit_box_max_square_size)

                self.action_1_digit_fields.append(digit_box)

        # Creating digit box and buy button for Action 2
        action_2_v_layout = QVBoxLayout()
        action_2_label = QLabel("Action-2")
        action_2_price_input_h_layout = QHBoxLayout()
        self.action_2_digit_fields = []
        for i in range(0, total_digit_fields):
            if i == buy_button_position - 1:
                # set buy button label
                btn_buy = QPushButton(buy_button_label)
                btn_buy.setMaximumSize(digit_box_max_square_size, digit_box_max_square_size)
                btn_buy.clicked.connect(self.action_2_sell_button_clicked)
                self.action_2_digit_fields.append(btn_buy)
            else:
                # create digit QLineEdit
                digit_box = QLineEdit()
                digit_box.setValidator(self.only_int)
                digit_box.setMaxLength(1)
                digit_box.setMaximumSize(digit_box_max_square_size, digit_box_max_square_size)
                self.action_2_digit_fields.append(digit_box)

            # Double Buy, Double Sell
            self.btn_double_buy = QPushButton("Double Buy")
            self.btn_double_buy.setFixedSize(100, 30)
            self.btn_double_buy.clicked.connect(self.btn_double_buy_clicked)
            self.btn_double_sell = QPushButton("Double Sell")
            self.btn_double_sell.setFixedSize(100, 30)
            self.btn_double_sell.clicked.connect(self.btn_double_sell_clicked)

        # Adding items in Action 1 Horizontal Digit Box
        action_1_price_input_h_layout.addStretch()
        for item in self.action_1_digit_fields:
            action_1_price_input_h_layout.addWidget(item)
        action_1_price_input_h_layout.addStretch()

        # Adding items in Action 2 Horizontal Digit Box
        action_2_price_input_h_layout.addStretch()
        for item in self.action_2_digit_fields:
            action_2_price_input_h_layout.addWidget(item)
        action_2_price_input_h_layout.addStretch()

        # Adding UI's in Action 1 Vertical layout
        action_1_v_layout.addWidget(action_1_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        action_1_v_layout.addLayout(action_1_price_input_h_layout)
        action_1_v_layout.addWidget(self.btn_double_buy, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Adding UI's in Action 2 Vertical layout
        action_2_v_layout.addWidget(action_2_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        action_2_v_layout.addLayout(action_2_price_input_h_layout)
        action_2_v_layout.addWidget(self.btn_double_sell, alignment=Qt.AlignmentFlag.AlignHCenter)

        h_layout.addLayout(action_1_v_layout)
        h_layout.addLayout(action_2_v_layout)

    def btn_double_buy_clicked(self):
        print("Double Buy Button Clicked")
        is_possible, order_list_all = self.trader.double_buy_sell_checker(self.trader.get_symbol_name())

        if is_possible:
            self.trader.double_buy(order_list_all, self.selected_order_type, self.trader.get_symbol_name(),
                                   limit_price=self.placing_price, stop_limit=self.placing_stop_limit)
            print("BOught")
            self.set_confirmation_details("Please wait")
            self.bottom_table.update_table()
            self.set_confirmation_details("Success")
        else:
            self.set_confirmation_details("Double buy not possible")

    def btn_double_sell_clicked(self):
        print("Double Sell Button Clicked")
        is_possible, order_list_all = self.trader.double_buy_sell_checker(self.trader.get_symbol_name())
        if is_possible:
            self.trader.double_sell(order_list_all, self.selected_order_type, self.trader.get_symbol_name(),
                                    limit_price=self.placing_price, stop_limit=self.placing_stop_limit)
            self.set_confirmation_details("Please wait")
            self.bottom_table.update_table()
            self.set_confirmation_details("Success")
        else:
            self.set_confirmation_details("Double sell not possible")

    def action_1_buy_button_clicked(self):
        print("Action 1 Buy button clicked")
        collected_price = ""
        for i in self.action_1_digit_fields:
            digit = i.text()
            if digit == "":
                collected_price += "0"
            else:
                collected_price += digit

        self.placing_side = "BUY"
        self.placing_symbol = self.trader.get_symbol_name()
        self.placing_qty = self.get_quantity()
        self.placing_price = collected_price
        self.set_confirmation_details(
            f"{self.selected_order_type} side: {self.placing_side} on symbol: {self.placing_symbol}, qty: {self.placing_qty} with price: {self.placing_price} ")

    def get_quantity(self):
        return self.quantity_input.text()

    def action_2_sell_button_clicked(self):
        print("Action 2 Sell button clicked")
        collected_price = ""
        for i in self.action_2_digit_fields:
            digit = i.text()
            if digit == "":
                collected_price += "0"
            else:
                collected_price += digit

        print(collected_price)

        self.placing_side = "SELL"
        self.placing_symbol = self.trader.get_symbol_name()
        self.placing_qty = self.get_quantity()
        self.placing_price = collected_price
        self.set_confirmation_details(
            f"{self.selected_order_type} side: {self.placing_side} on symbol: {self.placing_symbol}, qty: {self.placing_qty} with price: {self.placing_price} ")

    def draw_order_type_field_in_top_h_layout_2(self, h_layout):
        btn_group = QButtonGroup()
        order_type_label = QLabel("Order type:")
        btn_limit = QRadioButton("Limit")
        btn_stop_limit = QRadioButton("Stop limit")
        btn_market = QRadioButton("Market")
        btn_group.addButton(btn_limit)
        btn_group.addButton(btn_stop_limit)
        btn_group.addButton(btn_market)
        btn_limit.clicked.connect(self.btn_limit_clicked)
        btn_stop_limit.clicked.connect(self.btn_stop_limit_clicked)
        btn_market.clicked.connect(self.btn_market_clicked)

        # Default checked is "Market Order"
        btn_market.setChecked(True)
        self.btn_market_clicked()
        # Default setup complete

        h_layout.addWidget(order_type_label)
        h_layout.addWidget(btn_limit)
        h_layout.addWidget(btn_stop_limit)
        h_layout.addWidget(btn_market)
        h_layout.addStretch()

    def btn_market_clicked(self):
        self.selected_order_type = MARKET_ORDER
        print("Market Order Selected")

    def btn_stop_limit_clicked(self):
        self.selected_order_type = STOP_LIMIT_ORDER
        print("Stop Limit Order Selected")

    def btn_limit_clicked(self):
        self.selected_order_type = LIMIT_ORDER
        print("Limit Order Selected")

    def draw_company_name_field_in_top_h_layout_2(self, h_layout):
        """
        Create UI widgets of company name field and adds them into the
        horizontal_box_layout given in the h_layout
        :param h_layout:
        :return:
        """
        company_label = QLabel("Company:")
        company_label.setMaximumWidth(50)
        company_label.setMinimumWidth(50)
        self.company_name = QLabel("Unknown")
        h_layout.addWidget(company_label)
        h_layout.addWidget(self.company_name)

    def symbol_input_enter_pressed(self):
        """
        Triggered when user presses "Enter" while keeping the keyboard cursor on Symbol Input field
        1. Fetches Inserted symbol from input field
        2. Creates a symbol asset in Trade object
        3. Fetches and sets company_name and short_status in the UI
        :return None
        """
        symbol = self.get_input_symbol()
        if self.trader.fetch_and_set_symbol_asset(symbol):
            self.set_company_name(self.trader.get_company_name())
            self.set_short_status(self.trader.get_current_symbol_shortable_status())
            self.set_quantity(
                self.polygon_data.get_30_min_res_with_quantity_formula(
                    self.polygon_data.get_last_30_min_data(self.get_input_symbol())))
        else:
            self.set_company_name(self.trader.COMPANY_FETCH_ERROR)
            self.set_short_status(self.trader.SHORTABLE_FETCH_ERROR)
            self.set_quantity(0)

    def set_quantity(self, quantity):
        self.quantity_input.setText(str(quantity))

    def draw_fields_in_top_h_layout_1(self, h_layout):
        """
        Create short and quantity fields and adds them in the h_layout
        :param h_layout:
        :return:
        """
        symbol_label = QLabel("Symbol:")
        self.symbol_input = QLineEdit()
        self.symbol_input.returnPressed.connect(self.symbol_input_enter_pressed)
        self.symbol_input.setMaximumWidth(120)
        short_label = QLabel("Short:")
        self.short_status = QLabel("Unknown")

        quantity_label = QLabel("Quantity:")
        self.quantity_input = QLineEdit()
        self.quantity_input.setMaximumWidth(90)
        h_layout.addWidget(symbol_label)
        h_layout.addWidget(self.symbol_input)
        h_layout.addWidget(short_label)
        h_layout.addWidget(self.short_status)
        h_layout.addStretch()
        h_layout.addWidget(quantity_label)
        h_layout.addWidget(self.quantity_input)

    def get_input_symbol(self):
        """

        :return: inserted value as string
        """
        return self.symbol_input.text().upper()

    def get_short_status(self):
        """

        :return: status of short (Y/N) as string
        """
        return self.short_status.text()

    def set_short_status(self, status):
        """
        stock data tell us about a stock if it is shortable or not
        the status is set here as QLabel
        Expected inputs are (Y/N)
        :param status:
        :return:
        """
        self.short_status.setText(status)

    def set_company_name(self, company_name):
        """
        sets company_name in the UI company_name field
        :param company_name:
        :return: None
        """
        self.company_name.setText(company_name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fs_control_interface = FSControlInterface()
    fs_control_interface.show()
    sys.exit(app.exec_())
