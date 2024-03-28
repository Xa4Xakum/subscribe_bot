import asyncio
from datetime import timedelta, datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.enums.chat_member_status import ChatMemberStatus

from loguru import logger

from core.utils.filters import GreatAdmin
from core.utils.keyboards import Keyboards
from core.utils.database import DataBase
from core.utils.operations import try_cick, try_send_message

from helper import bot
from config import Config

r = Router()
r.message.filter(GreatAdmin())
r.callback_query.filter(GreatAdmin())


@r.callback_query(F.data == Keyboards.accept.callback_data)
async def accept_payed(call: CallbackQuery):

    kb = Keyboards()

    await call.answer('На какой срок подписка?')
    await call.message.edit_reply_markup(reply_markup=kb.how_long())


@r.callback_query(
    F.data.in_([
        Keyboards.month.callback_data,
        Keyboards.three_month.callback_data,
        Keyboards.halfe_year.callback_data
    ])
)
async def get_time_payed(call: CallbackQuery):
    db = DataBase()
    kb = Keyboards()
    pay = db.get_pay_by_msg_id(call.message.message_id)
    conf = Config()

    if pay is None:
        await call.answer('Не могу найти в бд такой запрос!')
        return

    if call.data == Keyboards.three_month.callback_data:
        delta = timedelta(90)
    elif call.data == Keyboards.halfe_year.callback_data:
        delta = timedelta(180)
    else:
        delta = timedelta(30)

    db.add_subscribe(pay.pay_from_user_id, delta)
    link = await bot.create_chat_invite_link(conf.get_chat_id(), expire_date=timedelta(1), member_limit=1)

    await bot.send_message(
        chat_id=pay.pay_from_user_id,
        text=(
            f'Ваша оплата на {call.data} принята✅\n'
            'Теперь вы можете подписаться(ссылка действует 1 день и только на одного человека)'
        ),
        reply_markup=kb.to_channel(link.invite_link),
        protect_content=True
    )

    await call.message.edit_caption(caption=call.message.caption + f'\n\n✅Принято на {call.data}')


@r.callback_query(F.data == Keyboards.back.callback_data)
async def back(call: CallbackQuery):
    kb = Keyboards()
    await call.message.edit_reply_markup(reply_markup=kb.rewiew_markup())


@r.callback_query(F.data == Keyboards.decline.callback_data)
async def decline_payed(call: CallbackQuery):

    db = DataBase()
    kb = Keyboards()
    pay = db.get_pay_by_msg_id(call.message.message_id)

    if pay is None:
        await call.answer('Не могу найти в бд такой запрос!')
        return

    await bot.send_message(
        chat_id=pay.pay_from_user_id,
        text='Ваша оплата отклонена❌',
        reply_markup=kb.to_channel()
    )

    await call.message.edit_caption(caption=call.message.caption + '\n\n❌Отклонено')


@r.message(Command('stat'))
async def stats(msg: Message):
    db = DataBase()
    users = db.get_all_users()
    not_referals = db.get_all_referals(None)

    await msg.answer(
        text=(
            f'Не имеют реферера: {len(not_referals)}\n'
            f'Чьи-то рефералы: {len(users) - len(not_referals)}\n'
            f'Всего пользователей: {len(users)}\n'
        )
    )


@r.message(Command('help'))
async def help(msg: Message):
    await msg.answer(
        f'/help - покажет все доступные команды\n'
        f'/stat - Покажет статистику пользователей\n'
        f'/userstat user_id - покажет статистику пользователя, user_id - телеграмм id искомого пользователя, пример с вашим id:\n'
        f'/userstat {msg.from_user.id}\n'
        f'/id - Дает id чата, id написавшего команду человека и id сообщения, '
        f'опционально можно написать команду ответом на сообщение и получить '
        f'id и username написавшего сообщение, на которое был ответ\n'
        f'/check - проверить подписки пользователей\n'
        f'/editsub user_id sub - изменить подписку пользователя, где user_id - id пользователя, который можно получить командой '
        f'/id, sub - время подписки, сколько дней начиная с сегодняшнего будет у пользователя'
    )


@r.message(Command('userstat'))
async def userstat(msg: Message):
    db = DataBase()
    params = msg.text.split()

    if len(params) < 2:
        await msg.answer('В команде обязательно должен присутствовать id пользователя')
        return

    user_id = int(params[1])
    user = db.get_user(user_id)
    referals = db.get_all_referals(user_id)

    if user is None:
        await msg.answer(
            f'В моей бд нет такого пользователя, известно лишь, '
            f'что у него было {len(referals)} рефералов'
        )
        return

    await msg.answer(
        f'Статистика по {user_id}\n'
        f'Реферер: {f"<code>{user.referer}</code>" if user.referer is not None else "Отсутствует"}\n'
        f'Количество рефералов: {len(referals)}\n'
        f'Подписка до: {user.payed_up_to}\n',
        parse_mode='html'
    )


@r.message(Command('id'))
async def get_id(msg: Message):
    text = (
        f'chat_id: <code>{msg.chat.id}</code>\n'
        f'msg_id: <code>{msg.message_id}</code>\n'
        f'from_user_id: <code>{msg.from_user.id}</code>\n'
    )

    if msg.reply_to_message:
        text += (
            f'reply_to_msg_from_user_id: <code>{msg.reply_to_message.from_user.id}\n</code>'
            f'reply_to_msg_from_username: <code>{msg.reply_to_message.from_user.username}\n</code>'
        )

    await msg.answer(text=text, parse_mode='html')


@r.message(Command('check'))
async def check_subs(msg: Message):
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
        await msg.answer(
            f'Подписки проверены\n\n'
            f'Истекла у {ended} пользователей\n'
            f'Удалены с канала {cicked} пользователей\n'
            f'Остался 1 день у {one_day} пользователей\n'
            f'Осталось 3 дня у {three_days} пользователей\n'
            f'Всего в базе {len(users)} пользователей'
        )
    except Exception as e:
        logger.error(f'АДМИНУ НЕЛЬЗЯ БЛОКИРОВАТЬ БОТА! поймана ошибка {e}')


@r.message(Command('editsub'))
async def edit_sub(msg: Message):
    db = DataBase()
    params = msg.text.split()

    db.edit_user_payed_up(int(params[1]), datetime.now() + timedelta(int(params[2])))

    await msg.answer('Готово')
