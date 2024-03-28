from aiogram.types import Message

from loguru import logger

from config import Config
from helper import bot


def is_numeric(s) -> bool:
    ''' Проверяет, является ли строка числом '''
    try:
        num = int(s)
        return True if num else False
    except ValueError:
        return False


async def try_send_message(user_id, text) -> Message:
    '''Пытается написать сообщение'''
    try:
        return await bot.send_message(chat_id=user_id, text=text)
    except Exception as e:
        logger.warning(f'Не удалось написать пользователю({user_id}) по причине {e}')


async def try_cick(chat_id, user_id) -> None:
    '''Пытается кикнуть пользователя из чата'''
    conf = Config()
    try:
        await bot.ban_chat_member(chat_id, user_id, revoke_messages=True)
        await bot.unban_chat_member(chat_id, user_id)
    except Exception as e:
        text = f'Не удалось кикнуть пользователя({user_id}) из чата({chat_id}) по причине {e}'
        await bot.send_message(conf.get_admin_id(), text)
        logger.warning(text)
