
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


class UserButtons():
    '''Кнопки пользователей'''

    to_menu_btn = KeyboardButton(text='В меню')
    payed = KeyboardButton(text='Оплатил')
    my_referals = KeyboardButton(text='Мои рефералы')
    get_chat_link = KeyboardButton(text='Получить ссылку')
    tarifs = KeyboardButton(text='Тарифы')
    our_tarifs = KeyboardButton(text='Наши тарифы')


class AdminButtons():
    '''Кнопки админов'''

    accept = InlineKeyboardButton(text='✅Принять', callback_data='Отклонить')
    decline = InlineKeyboardButton(text='❌Отклонить', callback_data='Отклонить')
    month = InlineKeyboardButton(text='Месяц', callback_data='Месяц')
    three_month = InlineKeyboardButton(text='3 месяца', callback_data='3 месяца')
    halfe_year = InlineKeyboardButton(text='6 месяцев', callback_data='6 месяцев')
    back = InlineKeyboardButton(text='Отмена', callback_data='Отмена')


class Buttons(UserButtons, AdminButtons):
    '''Все кнопки бота'''


class UserKeyboards(Buttons):
    '''Клавиатуры пользователей'''


    def menu_markup(self) -> ReplyKeyboardMarkup:
        '''Клавиатура меню'''

        builder = ReplyKeyboardBuilder()
        builder.add(
            self.payed,
            self.my_referals,
            self.tarifs,
            self.get_chat_link
        )

        builder.adjust(1)

        return builder.as_markup(resize_keyboard=True)


    def to_menu_markup(self) -> ReplyKeyboardMarkup:
        '''Клавиатура для перехода в меню'''

        builder = ReplyKeyboardBuilder()
        builder.add(self.to_menu_btn)
        builder.adjust(1)

        return builder.as_markup(resize_keyboard=True)


    def to_channel(self, link) -> InlineKeyboardMarkup:
        '''Клавиатура с кнопкой перехода на канал'''

        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text='Перейти', url=link)
        )
        builder.adjust(2)
        return builder.as_markup()


    def to_tarifs(self) -> ReplyKeyboardMarkup:
        '''Клавиатура перехода к тарифам'''

        builder = ReplyKeyboardBuilder()
        builder.add(self.tarifs)
        builder.adjust(1)

        return builder.as_markup(resize_keyboard=True)


    def to_our_tarifs(self) -> ReplyKeyboardMarkup:
        '''Клавиатура перехода к тарифам'''

        builder = ReplyKeyboardBuilder()
        builder.add(self.our_tarifs)
        builder.adjust(1)

        return builder.as_markup(resize_keyboard=True)


    def payed_markup(self) -> ReplyKeyboardMarkup:
        '''Клавиатура с кнопкой "оплатил"'''

        builder = ReplyKeyboardBuilder()
        builder.add(self.payed)
        builder.adjust(1)

        return builder.as_markup(resize_keyboard=True)


class AdminKeyboards(Buttons):
    '''Клавиатуры админов'''


    def rewiew_markup(self) -> InlineKeyboardMarkup:
        '''Клавиатура рассмотрения'''

        builder = InlineKeyboardBuilder()
        builder.add(
            self.accept,
            self.decline
        )
        builder.adjust(2)
        return builder.as_markup()


    def how_long(self) -> InlineKeyboardMarkup:
        '''Клавиатура с выбором срока подписки'''

        builder = InlineKeyboardBuilder()
        builder.add(
            self.month,
            self.three_month,
            self.halfe_year,
            self.back
        )
        builder.adjust(1)
        return builder.as_markup()


class Keyboards(UserKeyboards, AdminKeyboards):
    '''Все клавиатуры бота'''
