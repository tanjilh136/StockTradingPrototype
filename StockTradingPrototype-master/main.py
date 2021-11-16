import sys

from PyQt5.QtWidgets import *
from tabbed_screen.tabbed_screen import TabbedScreen
from second_screen_pack.barset_generator import generate_barset_forever
from threading import Thread

def main():
    app = QApplication(sys.argv)
    ex = TabbedScreen()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    # Run the following thread to continuously collect barset for secondscreen
    t1 = Thread(target=generate_barset_forever)
    t1.start()
    main()
