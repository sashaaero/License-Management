from PyQt5.QtWidgets import QApplication
import sys
import license
from frame import Frame


def main():
    app = QApplication(sys.argv)
    desktop = app.desktop().screenGeometry()
    frame = Frame(desktop)
    frame.show()
    sys.exit(app.exec_())

main()
