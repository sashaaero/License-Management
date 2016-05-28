from datetime import date
import sqlite3
from collections import namedtuple

field_model = namedtuple('field_model', ['eng', 'rus', 'type'])


class License(dict):
    fields = [
        field_model('name',             'п.1 Наименование ПО',                                              str),
        field_model('year',             'п.2 Год поставки',                                                 int),
        field_model('id',               'п.3 № Лицензии',                                                   int),
        field_model('developer',        'п.4 Разработчик',                                                  str),
        field_model('firm',             'п.5 Фирма поставщик',                                              str),
        field_model('delivery_date',    'п.6 Дата выдачи лицензии',                                         date.today),
        field_model('expiration_date',  'п.7 Дата истечения периода программного сопровождения ',           date.today),
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
            self[field.eng] = field.type()

    def write(self):
        connection = sqlite3.connect('licenses.db')
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

            insert_q = 'INSERT INTO licenses VALUES (' + '?, ' * (len(self.fields) - 1) + '?)'
            cursor.execute(insert_q, tuple(self[field.eng] for field in self.fields))

    @staticmethod
    def read(attributes):
        connection = sqlite3.connect('licenses.db')
        with connection:
            cursor = connection.cursor()
            keys = list(attributes.keys())
            select_q = 'SELECT * FROM licenses WHERE ' + ' and '.join([key + '=?' for key in keys])
            result = cursor.execute(select_q, tuple(attributes[key] for key in keys))

        licenses = []
        fields = License.get_fields()

        for res in result.fetchall():
            temp = License()
            for i in range(len(res)):
                temp[fields[i].eng] = res[i]

            licenses.append(temp)

        return licenses

    @staticmethod
    def get_fields():
        return License.fields
