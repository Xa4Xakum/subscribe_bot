import asyncio
from datetime import datetime, timedelta

import aioschedule
from aiogram.enums.chat_member_status import ChatMemberStatus

from loguru import logger

from core.utils.database import DataBase
from core.utils.operations import try_send_message, try_cick
from config import Config
from helper import bot, dp


async def on_startup():
    logger.warning('БОТ ОНЛАЙН')
    logger.warning(await bot.get_me())


async def new_schedule():
    aioschedule.every().day.at('12:00').do(check_subs)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


def include_user_routers(dp):
    from core.handlers import user
    dp.include_routers(
        user.r
    )


def include_admin_routers(dp):
    from core.handlers import admin
    dp.include_routers(
        admin.r
    )


async def check_subs():
    db = DataBase()
    conf = Config()
    users = db.get_all_users()
    ended = 0
    cicked = 0
    one_day = 0
    three_days = 0
    for user in users:
        if user.payed_up_to < datetime.now():
            ended += 1
            chat_user = await bot.get_chat_member(conf.get_chat_id(), user_id=user.user_id)
            logger.info(chat_user.status)
            if chat_user.status not in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
                await try_cick(chat_id=conf.get_chat_id(), user_id=user.user_id)
                await try_send_message(user.user_id, 'Ваша подписка закончилась, вы были исключены')
                cicked += 1
        elif user.payed_up_to < datetime.now() + timedelta(1):
            await try_send_message(user.user_id, 'Внимание! у вас осталось меньше суток, чтобы продлить подписку!')
            one_day += 1
        elif user.payed_up_to < datetime.now() + timedelta(3):
            three_days += 1
            await try_send_message(user.user_id, 'У вас осталось меньше 3 дней, чтобы продлить подписку')

        await asyncio.sleep(0.5)

    try:
        await bot.send_message(
            conf.get_admin_id(), (
                f'Подписки проверены\n\n'
                f'Истекла у {ended} пользователей\n'
                f'Удалены с канала {cicked} пользователей\n'
                f'Остался 1 день у {one_day} пользователей\n'
                f'Осталось 3 дня у {three_days} пользователей\n'
                f'Всего в базе {len(users)} пользователей'
            )
        )
    except Exception as e:
        logger.error(f'АДМИНУ НЕЛЬЗЯ БЛОКИРОВАТЬ БОТА! поймана ошибка {e}')


def set_loggers():
    logger.add(
        'logs/{time}.log',
        level='INFO',
        backtrace=True,
        diagnose=True,
        rotation='00:00',
        retention='1 week',
        catch=True
    )
    logger.add(
        'errors/{time}.log',
        level='ERROR',
        backtrace=True,
        diagnose=True,
        rotation='00:00',
        retention='1 week',
        catch=True
    )


if __name__ == "__main__":

    set_loggers()
    include_admin_routers(dp)
    include_user_routers(dp)
    dp.startup.register(on_startup)
    asyncio.run(dp.start_polling(bot))
