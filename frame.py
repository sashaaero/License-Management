from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QDateEdit, QCalendarWidget, QGridLayout,
    QMessageBox, QListWidget, QVBoxLayout,
    QPushButton, QMenuBar
)

from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QDate, Qt
from license import License
from datetime import date
import re


class Frame(QWidget):
    MIN_DATE = QDate(1800, 1, 1)
    EDIT = True
    NEW = False

    @staticmethod
    def parse_date(input_str):
        y, m, d = [int(s) for s in input_str.split('-')]
        return date(y, m, d)

    def __init__(self, desktop):
        super().__init__()
        self.curr_id = None
        self.filter = License()
        self.input_forms = {}
        self.initGUI(desktop)
        self.setWindowTitle('Контроль лицензий')
        self.state = self.EDIT

    def initGUI(self, desktop):
        """
        Главный метод инициализации всего графического интерфейса
        """
        self.setGeometry(
            desktop.width() * 0.1,
            desktop.height() * 0.1,
            desktop.width() * 0.8,
            desktop.height() * 0.8
        )

        # Кнопки
        self.action_button = QPushButton('Поиск')
        self.action_button.clicked.connect(self.act)

        self.clear_button = QPushButton('Очистить')
        self.clear_button.clicked.connect(self.clear_forms)

        self.new_button = QPushButton('Создать')
        self.new_button.clicked.connect(self.new)

        self.delete_button = QPushButton('Удалить')
        self.delete_button.clicked.connect(self.delete)

        # Компоновщики
        panel = QGridLayout()
        left_side = QVBoxLayout()
        grid = QGridLayout()

        fields = License.fields

        # Инициализируем список баз
        list_label = QLabel("Лицензии")
        list_label.setAlignment(Qt.AlignCenter)

        self.list_view = QListWidget()
        self.update_list(self.list_view)
        self.list_view.setFixedWidth(desktop.width() * 0.15)
        self.list_view.currentItemChanged.connect(self.fill)
        self.list_view.itemClicked.connect(self.fill)

        # создаем формы для ввода данных
        i = 1
        for field in fields:
            label = QLabel(field.rus)
            if field.type == str:
                self.input_forms[field.eng] = QLineEdit()
                if 'лицензионный ключ' in field.rus.lower():
                    self.input_forms[field.eng].setInputMask('>NNNNN-NNNNN-NNNNN-NNNNN-NNNNN;_')
                elif 'ip' in field.rus:
                    self.input_forms[field.eng].setInputMask('000.000.000.000')

            elif field.type == int:
                self.input_forms[field.eng] = QLineEdit()
                self.input_forms[field.eng].setValidator(QIntValidator())
                if 'год' in field.rus.lower():
                    self.input_forms[field.eng].setValidator(QIntValidator(1900, 2016))
                    self.input_forms[field.eng].setMaxLength(4)
            elif field.type == date:
                self.input_forms[field.eng] = QDateEdit()
                self.input_forms[field.eng].setCalendarPopup(True)
                self.input_forms[field.eng].setMinimumDate(self.MIN_DATE)
                self.input_forms[field.eng].setDate(self.MIN_DATE)

            self.input_forms[field.eng].setEnabled(False)

            grid.addWidget(label, i, 0)
            grid.addWidget(self.input_forms[field.eng], i, 1)
            i += 1

        left_side.addWidget(list_label)
        left_side.addWidget(self.list_view)
        left_side.setSpacing(10)

        panel.addLayout(left_side, 1, 1)
        panel.addLayout(grid, 1, 2, 1, 3)
        panel.addWidget(self.new_button, 2, 1)
        panel.addWidget(self.action_button, 2, 2)
        panel.addWidget(self.clear_button, 2, 3)
        panel.addWidget(self.delete_button, 2, 4)
        self.setLayout(panel)

    def update_title(self):
        """
        Функция обновляет название программы в зависимости от состояния прграммы
        """
        title = 'Контроль лицензий'
        if self.state == self.NEW:
            title += ' - новая лицензия'
        elif self.curr_id is not None:
            title += ' - Лицензия №%d' % self.curr_id

        self.setWindowTitle(title)

    def update_list(self, attrs=None):
        """
        Функция обновляет список лицензий
        1. Когда применен фильтр по поиску
        2. Когда удалилась лицензия
        3. Когда добавилась новая лицензия
        """
        self.list_view.clear()
        license_list = License.find(attrs)

        self.list_view.addItem('Фильтр')

        for license in license_list:
            self.list_view.addItem(str(license))

    def unblock_forms(self):
        """
        Разблокирует формы
        """
        if self.input_forms['id'].isEnabled():
            return
        for k, form in self.input_forms.items():
            form.setEnabled(True)

    def fill(self, _id, useless=None):
        """
        Заполняет поля лицензей, получая как параметр ее id
        Так же очищает лицензию, если useless == 0
        Дополнительно меняет состояние программы и название кнопки
        """
        if useless:
            self.unblock_forms()

        if self.state == self.NEW:
            reply = self.open_dialog("Вы не сохранили изменения, все равно выйти?", "Предупреждение")
            if not reply:
                return

        if _id is None: return

        if useless == 0:    # трюк, чтобы не писать лишнего метода на очистку
                            # параметр useless все равно передается от события
            license = License()
        elif _id.text() == 'Фильтр':
            license = self.filter
            self.action_button.setText('Поиск')
            self.delete_button.setEnabled(False)
            self.curr_id = None
            self.state = None
        else:
            license = License.get_by_id(_id.text())
            self.action_button.setText('Сохранить')
            self.delete_button.setEnabled(True)
            self.curr_id = int(_id.text())
            self.state = self.EDIT

        self.update_title()

        for field in License.fields:
            if not license[field.eng]:
                if field.type == date:
                    self.input_forms[field.eng].setDate(self.MIN_DATE)
                #elif field.
                else:
                    self.input_forms[field.eng].clear()

                continue

            if field.type == date:
                l_date = Frame.parse_date(license[field.eng])
                in_date = QDate(l_date)
                self.input_forms[field.eng].setDate(in_date)
            elif field.type == str:
                self.input_forms[field.eng].setText(license[field.eng])
            else:
                self.input_forms[field.eng].setText(str(license[field.eng]))

    def parse_attributes(self):
        """
        Парсит только непустые поля, и возвращает словарь артрибутов для поиска
        """
        attrs = {}
        for field in License.fields:
            if field.type == date:
                val = self.input_forms[field.eng].date()
                if val != self.MIN_DATE:
                    attrs[field.eng] = val.toPyDate()
            else:
                if field.eng == 'license_key':
                    val = self.input_forms[field.eng].text()
                    if re.match('-'.join([r'\w' * 5 for _ in range(5)]), val):
                        attrs[field.eng] = val
                else:
                    val = self.input_forms[field.eng].text()
                    if val != '':
                        attrs[field.eng] = field.type(val)

        return attrs

    def parse_license(self):
        """
        Парсит лицензию целиком, и если значения пустые, прописывает дефолтные
        """
        curr_license = License()
        for field in License.fields:
            if field.type == date:
                curr_license[field.eng] = \
                    self.input_forms[field.eng].date().toPyDate()
            else:
                value = self.input_forms[field.eng].text()
                if field.type == int:
                    if field.eng == 'id':
                        if value == '':
                            return
                        else:
                            curr_license[field.eng] = int(value)
                    else:
                        curr_license[field.eng] = int(value) if value else 0
                else:
                    curr_license[field.eng] = value

        return curr_license

    def open_dialog(self, msg, header='Error'):
        """
        Общая функция для оповещений пользователя об ошибках
        """
        reply = QMessageBox.question(self, header, msg,
                                     QMessageBox.No |
                                     QMessageBox.Yes,
                                     QMessageBox.No)

        return reply == QMessageBox.Yes

    def clear_forms(self):
        """
        Функция по очистке форм
        """
        self.fill('clear', 0)

    def new(self):
        """
        Функция, реагирующая на нажатие кнопки "Создать"
        """
        self.unblock_forms()
        self.clear_forms()
        self.action_button.setText('Сохранить')
        self.state = self.NEW
        self.update_title()

    def delete(self):
        """
        Функция, реагирующая на нажатие кнопки "Удалить"
        """
        reply = self.open_dialog("Вы собираетесь удалить лицензию №%d" % self.curr_id, "Удаление")
        if reply:
            license = License.get_by_id(self.curr_id)
            license.delete()
            self.clear_forms()
            self.update_list()

    def act(self):
        """
        Функция, реагирующя на нажатие кнопок "Сохранить" и "Найти"
        Меняет свое действие и название в зависимости от текущего состояния программы
        """
        self.unblock_forms()
        if self.action_button.text() == 'Сохранить':
            license = self.parse_license()
            if not license:
                QMessageBox.question(self, "Ошибка", "Поле № Лицензии не может быть пустым",
                                     QMessageBox.Ok)
                return

            if self.state == self.NEW:
                if License.get_by_id(int(self.input_forms['id'].text())):
                    QMessageBox.question(self,  "Ошибка",
                     "Лицензия с номером %s уже есть в базе\nСохранение невозможно"  % (self.input_forms['id'].text()),
                     QMessageBox.Ok)
                    return

            license.write()
            self.curr_id = license['id']
            self.state = self.EDIT
            self.update_list()

        else:
            attrs = self.parse_attributes()
            self.update_list(attrs)
            self.state = self.EDIT

