import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from first_screen_pack.first_screen import FirstScreen
from second_screen_pack.second_screen import SecondScreen

class TabbedScreen(QTabWidget):
    def __init__(self, parent=None):
        super(TabbedScreen, self).__init__(parent)
        self.setMinimumSize(1080, 600)
        self.first_screen = FirstScreen()
        self.second_screen = SecondScreen()

        self.addTab(self.first_screen, "Tab 1")
        self.addTab(self.second_screen, "Tab 2")

        self.setTabText(0, "Screen 1")
        self.setTabText(1, "Screen 2")
        self.setWindowTitle("Stock Trading Prototype")


def main():
    app = QApplication(sys.argv)
    ex = TabbedScreen()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
