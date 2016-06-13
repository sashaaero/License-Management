from datetime import date
import sqlite3
from collections import namedtuple
from config import *

field_model = namedtuple('field_model', ['eng', 'rus', 'type'])


class License(dict):
    fields = [
        field_model('name',             'п.1 Наименование ПО',                                              str),
        field_model('year',             'п.2 Год поставки',                                                 int),
        field_model('id',               'п.3 № Лицензии',                                                   int),
        field_model('developer',        'п.4 Разработчик',                                                  str),
        field_model('firm',             'п.5 Фирма поставщик',                                              str),
        field_model('delivery_date',    'п.6 Дата выдачи лицензии',                                         date),
        field_model('expiration_date',  'п.7 Дата истечения периода программного сопровождения ',           date),
        field_model('license_key',      'п.8 Лицензионный ключ',                                            str),
        field_model('letter',           'п.8а Лицензионный договор или соответствующее письмо',             str),
        field_model('note',             'п.8б Примечание',                                                  str),
        field_model('distribution',     'п.9 Распределение лицензий',                                       str),
        field_model('redistribution',   'п.10 Перераспределение лицензий',                                  str),
        field_model('person',           'п.11 ФИО сотрудника, ответственного за использование лицензии',    str),
        field_model('ip',               'п.12 ip-адрес',                                                    str),
        field_model('server',           'п.13 Имя сервера',                                                 str),
        field_model('task',             'п.14 Выполняемая задача',                                          str),
        field_model('act',              'п.15 Акт об установке системы Windows',                            str),
        field_model('department',       'п.16 Наименование отдела',                                         str)
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for field in self.fields:
            self[field.eng] = None

    def __str__(self):
        """
        Когда-то была идея предпоказа данных в лицензии
        как хинт при наведении на номер лицензии, но сейчас кажется бесполезным
        """
        res = ''
        for field in self.fields:
            value = self[field.eng] if field.type == str else str(self[field.eng])
            if value == '' or value == '0':
                continue

            res += '%s: %s\n' % (field.rus, value)

        return res[:-1]  # убираем перенос строки после последнего данного

    def delete(self):
        """
        Удаляет данную лицензию
        """
        connetion = sqlite3.connect(database)
        with connetion:
            cursor = connetion.cursor()
            cursor.execute('DELETE FROM licenses WHERE id=?', (self['id'],))

    def write(self):
        """
        Записывает лицензию в базу
        По пути проверяет, есть ли такая таблица, если что -- создает ее и записывает
        """
        connection = sqlite3.connect(database)
        with connection:
            cursor = connection.cursor()
            check_q = 'SELECT name FROM sqlite_master WHERE type="table" AND name="licenses";'
            response = cursor.execute(check_q)
            if len(response.fetchall()) == 0:
                # надо создать базу
                create_q = 'CREATE TABLE licenses (' + ', '.join([field.eng
                                                                  if field.eng != 'id' else 'id INTEGER PRIMARY KEY'
                                                                  for field in self.fields]) + ')'
                cursor.execute(create_q)
                connection.commit()

            insert_q = 'INSERT OR REPLACE INTO licenses VALUES (' + '?, ' * (len(self.fields) - 1) + '?)'
            cursor.execute(insert_q, tuple(self[field.eng] for field in self.fields))


    @staticmethod
    def get_by_id(_id):
        """
        Возвращает лицензию по айди.
        Если в базе нет таблицы licenses -- создает её
        """
        connection = sqlite3.connect(database)
        with connection:
            cursor = connection.cursor()
            try:
                res = cursor.execute('SELECT * FROM licenses WHERE "id"=?', (str(_id),))
                obj = res.fetchall()
                if len(obj) == 0:
                    return

                obj = obj[0]
                license = License()
                for i in range(len(obj)):
                    license[License.fields[i].eng] = obj[i]

                return license
            except sqlite3.OperationalError:
                create_q = 'CREATE TABLE licenses (' + ', '.join([field.eng
                                                                  if field.eng != 'id' else 'id INTEGER PRIMARY KEY'
                                                                  for field in License.fields]) + ')'
                cursor.execute(create_q)
                connection.commit()

    @staticmethod
    def find(attributes=None):
        """
        Возвращает список id лицензий, которые подходят под заданные атрибуты
        Атрибуты могут быть пустыми
        """
        connection = sqlite3.connect(database)
        with connection:
            cursor = connection.cursor()
            select_q = 'SELECT id FROM licenses '
            if attributes:
                keys = list(attributes.keys())
                select_q += 'WHERE ' + ' and '.join([key + '=?' for key in keys])
                result = cursor.execute(select_q, tuple(attributes[key] for key in keys))
            else:
                result = cursor.execute(select_q)

        return [_id[0] for _id in result.fetchall()]
