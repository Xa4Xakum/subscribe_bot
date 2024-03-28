
from enum import Enum

import os

from dotenv import load_dotenv


class Modes(Enum):
    '''Список режимов, в которых можно запустить бота'''

    # тестовый режим, все базы данных дублируются на скулайт, сообщения кидаются
    # в продублированные чаты с припиской, куда должны прийти
    test = 'TEST'
    relise = 'RELISE'


class Config():
    '''Параметры бота'''

    cities = [
        'Москва',
        'Санкт-Петербург',
        'Сочи'
    ]

    def __init__(self, mode=Modes.test.value):
        load_dotenv()

        self.mode: str = mode


    def get_token(self):
        '''Токен бота в соответствии с режимом'''

        if self.mode == Modes.test.value:
            return os.getenv('TOKEN_TEST')
        if self.mode == Modes.relise.value:
            return os.getenv('TOKEN')


    def get_admin_id(self):
        return int(os.getenv('ADMIN_ID'))


    def get_db_connection(self):

        if self.mode == Modes.test.value:
            return 'sqlite:///core/xakum.db'
        if self.mode == Modes.relise.value:
            db_con = 'sqlite:///core/xakum.db'
            return db_con


    def get_chat_id(self):
        if self.mode == Modes.test.value:
            return os.getenv('CHAT_ID_TEST')
        if self.mode == Modes.relise.value:
            return os.getenv('CHAT_ID')
