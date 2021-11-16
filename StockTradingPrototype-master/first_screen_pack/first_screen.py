import sys
from PyQt5.QtWidgets import *

from first_screen_pack.fs_bottom_table_view import StockInfoTable
from first_screen_pack.fs_control_interface import FSControlInterface
from first_screen_pack.fs_right_table_view import ClientInfoTable


class FirstScreen(QWidget):
    def __init__(self, parent=None):
        super(FirstScreen, self).__init__(parent)
        self.setMinimumSize(1000, 580)
        self.parent_v_layout = QVBoxLayout()
        self.top_h_layout_1 = QHBoxLayout()
        self.draw_buttons_in_top_h_layout_1(self.top_h_layout_1)
        self.top_h_layout_2 = QHBoxLayout()
        self.fs_bottom_table_widget = StockInfoTable()
        self.draw_control_interface_and_client_info_table(self.top_h_layout_2)


        # All of the child layout must be added in parent_v_layout
        self.parent_v_layout.addLayout(self.top_h_layout_1)
        self.parent_v_layout.addLayout(self.top_h_layout_2)
        self.parent_v_layout.addWidget(self.fs_bottom_table_widget)
        self.setLayout(self.parent_v_layout)

    def draw_control_interface_and_client_info_table(self, h_layout):
        # Create control interface
        self.fs_control_interface = FSControlInterface()

        h_layout.addWidget(self.fs_control_interface)
        # Create table widget
        client_info_table = ClientInfoTable()

        # From control interface we control firstscreen bottom table, so lets refer
        self.fs_control_interface.send_bottom_table(self.fs_bottom_table_widget)
        h_layout.addWidget(client_info_table)

    def draw_buttons_in_top_h_layout_1(self, h_layout):
        btn_use_last = QPushButton("User Last")
        btn_upload_csv = QPushButton("Upload")
        btn_download_report = QPushButton("Download")

        btn_use_last.clicked.connect(self.btn_use_last_clicked)
        btn_upload_csv.clicked.connect(self.btn_upload_csv_clicked)
        btn_download_report.clicked.connect(self.btn_download_report_clicked)
        h_layout.addWidget(btn_use_last)
        h_layout.addStretch()
        h_layout.addWidget(btn_upload_csv)
        h_layout.addWidget(btn_download_report)

    def btn_use_last_clicked(self):
        # Do something
        print("Use last button clicked")

    def btn_upload_csv_clicked(self):
        # Do something
        print("Upload button clicked")

    def btn_download_report_clicked(self):
        # Do something
        print("Download button clicked")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    first_screen = FirstScreen()
    first_screen.show()
    sys.exit(app.exec_())
