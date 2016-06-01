from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QDateEdit, QCalendarWidget, QGridLayout,
    QMessageBox
)

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

    def update_window_title(self):
        title = 'Контроль лицензий'
        if self.state == self.EDIT:
            if self.input_forms['id'].text == '':
                title += ' - Создание'
            else:
                title += ' - Редактирование (%s)' % self.input_forms['id'].text
        else:
            title += ' - Поиск'

        self.setWindowTitle(title)


    def __init__(self, desktop):
        super().__init__()
        self.state = self.FIND
        self.input_forms = {}
        self.initGUI(desktop)

    def initGUI(self, desktop):
        self.setGeometry(
            desktop.width() * 0.1,
            desktop.height() * 0.1,
            desktop.width() * 0.8,
            desktop.height() * 0.8
        )
        # self.setWindowTitle('Контроль лицензий')
        self.update_window_title()

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

        self.parse_license()

    def parse_license(self):
        curr_license = License()
        fields = License.fields
        for field in fields:
            if field.type == date.today:
                #curr_license[field.eng] = \
                    #self.parse_date(str(self.input_forms[field.eng].dateTime()))
                print(self.input_forms[field.eng].dateTime().toString())


    def open_dialog(self, msg, header='Error'):
        reply = QMessageBox.question(self, header, msg,
                                     QMessageBox.No |
                                     QMessageBox.Yes,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            print("Yes was clicked")
        elif reply == QMessageBox.No:
            print("No was clicked")

