from aiogram.fsm.state import StatesGroup, State


class SendPayedPhoto(StatesGroup):
    get_photo = State()
