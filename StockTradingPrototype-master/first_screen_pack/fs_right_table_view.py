import csv
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

sample_data = "sample_data/data.csv"


class ClientInfoTable(QWidget):
    def __init__(self, parent=None):
        super(ClientInfoTable, self).__init__(parent)
        self.v_layout = QVBoxLayout()
        self.table_view = QTableView()
        self.model = QStandardItemModel()
        self.table_view.setModel(self.model)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.doubleClicked.connect(self.cell_clicked)

        header = self.table_view.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.v_layout.addWidget(self.table_view)
        self.setLayout(self.v_layout)
        self.setMinimumSize(300, 300)
        self.populate_client_info_table(self.csv_to_two_dim_data(sample_data))

    def populate_client_info_table(self, two_dim_data):
        # First row is always column names
        self.model.setHorizontalHeaderLabels(two_dim_data[0])
        # Adding other row as QTableView Row
        for index in range(1, len(two_dim_data)):
            items = []
            for field in two_dim_data[index]:
                item = QStandardItem(field)
                item.setTextAlignment(Qt.AlignCenter)
                items.append(item)
            self.model.appendRow(items)

    def csv_to_two_dim_data(self, csv_file):
        two_dim_csv = []
        with open(csv_file, "r") as fileInput:
            for row in csv.reader(fileInput):
                items = []
                for field in row:
                    items.append(field)
                two_dim_csv.append(items)
        return two_dim_csv

    def cell_clicked(self):
        pass


if __name__ == "__main__":
    sample_data = "../" + sample_data
    app = QApplication(sys.argv)
    client_info_table = ClientInfoTable()
    client_info_table.show()
    sys.exit(app.exec_())
