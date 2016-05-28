import sys
from PyQt5.QtWidgets import (QWidget,
                             QLabel, QLineEdit, QDateEdit, QCalendarWidget, QGridLayout)

from PyQt5.QtGui import QIntValidator
from license import License
from datetime import date


class Frame(QWidget):
    FIND = True
    EDIT = False

    @staticmethod
    def parse_date(input_str):
        y, m, d = reversed(list(map(int, input_str.split('.'))))
        return date(y, m, d)

    def __init__(self, desktop):
        super().__init__()
        self.input_forms = {}
        self.initGUI(desktop)
        self.mode = self.FIND

    def initGUI(self, desktop):
        self.setGeometry(
            desktop.width() * 0.1,
            desktop.height() * 0.1,
            desktop.width() * 0.8,
            desktop.height() * 0.8
        )
        self.setWindowTitle('Контроль лицензий')

        grid = QGridLayout()
        grid.setSpacing(10)

        fields = License.fields
        # Делаем словарь, чтобы потом мы могли изменять данные

        i = 1
        for field in fields:
            label = QLabel(field.rus)
            if field.type == str:
                self.input_forms[field.eng] = QLineEdit()
                if 'лицензионный ключ' in field.rus.lower():
                    self.input_forms[field.eng].setInputMask('>NNNNN-NNNNN-NNNNN-NNNNN-NNNNN;_')

            elif field.type == int:
                self.input_forms[field.eng] = QLineEdit()
                if 'год' in field.rus.lower():
                    self.input_forms[field.eng].setValidator(QIntValidator(1900, 2016))
                    self.input_forms[field.eng].setMaxLength(4)
            elif field.type == date.today:
                self.input_forms[field.eng] = QDateEdit()
                self.input_forms[field.eng].setCalendarPopup(True)

            grid.addWidget(label, i, 0)
            grid.addWidget(self.input_forms[field.eng], i, 1)
            i += 1

        self.setLayout(grid)

        start = self.input_forms['delivery_date'].dateTime()
        stop = self.input_forms['expiration_date'].dateTime()

        if start <= stop:
            print('Не выглядит правдой то, что лицензия истекает до ее активации')

