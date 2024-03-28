from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link
from aiogram.types import FSInputFile

from loguru import logger

from core.utils.filters import ChatType, TypeOfContent
from core.utils.keyboards import Keyboards
from core.utils.states import SendPayedPhoto
from core.utils.database import DataBase
from core.utils.operations import is_numeric

from config import Config
from helper import bot

r = Router()
r.message.filter(ChatType('private'))



@r.message(F.text, Command('start'))
async def start(msg: Message, state: FSMContext):

    await state.set_state(None)
    await state.set_data({})

    kb = Keyboards()
    params = msg.text.split()
    db = DataBase()
    referer = None

    logger.info(params)
    if len(params) == 2:
        await add_referal(params[1], msg.from_user.id)
        referer = int(params[1])

    user = db.get_user(msg.from_user.id)
    if user is None:
        logger.info('Пользователя нет в бд')
        db.add_user(
            user_id=msg.from_user.id,
            referer=referer,
            payed_up_to=datetime.now()
        )
    elif user.referer is None:
        db.edit_user_referer(msg.from_user.id, referer)

    await msg.answer(
        'Присоединяйтесь к VIP группе Scalp Meet 🚀 и получите:\n'
        ' • Экспертные курсы по скальпингу 📈\n'
        ' • Сообщество профи для обмена знаниями 🤝\n'
        ' • Анализ ошибок для улучшения торговли 🔍\n'
        ' • Инсайдерскую информацию о рыночных событиях 📊\n'
        'VIP подписчики также получают:\n'
        ' • Топовые сигналы от ведущих трейдеров 🏆\n'
        ' • Персональную обратную связь по портфелю 📝\n'
        ' • Эксклюзивные встречи для сети контактов 👥\n'
        ' • Инсайды от ключевых игроков рынка 🗝️\n\n'

        '<b>Станьте частью элитного крипто-клуба и торгуйте как профи! 💼🔥</b>',
        parse_mode='html',
        reply_markup=kb.to_our_tarifs()
    )


@r.message(F.text == Keyboards.to_menu_btn.text)
async def menu(msg: Message, state: FSMContext):

    await state.set_state(None)
    await state.set_data({})

    kb = Keyboards()
    db = DataBase()
    referer = None
    user = db.get_user(msg.from_user.id)

    if user is None:
        db.add_user(
            user_id=msg.from_user.id,
            referer=referer,
            payed_up_to=datetime.now()
        )

    user = db.get_user(msg.from_user.id)

    if user.payed_up_to < datetime.now():
        text = 'Чтобы получить доступ к каналу, оплатите подписку и отправьте мне скриншот'
    else:
        text = (
            f'Ваша подписка действует до {user.payed_up_to}\n'
            f'Не забудьте вовремя ее оплатить, чтобы не потерять доступ'
        )

    await msg.answer(
        text=text,
        reply_markup=kb.menu_markup()
    )


@r.message(F.text == Keyboards.payed.text)
async def payed(msg: Message, state: FSMContext):

    kb = Keyboards()

    await msg.answer(
        'Отправьте одно фото, где можно четко разобрать кому, сколько и в какой валюте вы отправили деньги',
        reply_markup=kb.to_menu_markup()
    )
    await state.set_state(SendPayedPhoto.get_photo)


@r.message(StateFilter(SendPayedPhoto.get_photo), TypeOfContent('photo'))
async def get_payed_photo(msg: Message, state: FSMContext):

    kb = Keyboards()
    conf = Config()
    db = DataBase()

    data = await state.get_data()
    if 'sended' in data:
        await msg.answer('Вы можете отправить только один скриншот! Отправил с первым скриншотом')
        await state.set_state(None)
        await state.set_data({})
        return

    msg_to_admin = await bot.send_photo(
        chat_id=conf.get_admin_id(),
        photo=msg.photo[0].file_id,
        caption=f'Фото от @{msg.from_user.username}',
        reply_markup=kb.rewiew_markup()
    )

    db.add_pay(
        pay_from_user_id=msg.from_user.id,
        pay_message_id=msg_to_admin.message_id,
    )

    await msg.answer(
        'Отправил на рассмотрение, дам знать, когда будут результаты',
        reply_markup=kb.to_menu_markup()
    )
    await state.set_state(None)
    await state.set_data({})


@r.message(F.text == Keyboards.my_referals.text)
async def my_referals(msg: Message):
    kb = Keyboards()
    db = DataBase()
    link = await create_start_link(bot, str(msg.from_user.id))

    user = db.get_user(msg.from_user.id)
    logger.info(user)

    referals = db.get_all_referals(msg.from_user.id)
    text = (
        f'При приглашение человека вы получаете автоматически 2 дополнительные недели в сообществе!'
        f'Ваша реферальная ссылка: {link}\n'
        f'Количество ваших рефералов: {len(referals)}'
    )
    await msg.answer(text=text, reply_markup=kb.to_menu_markup())


@r.message(F.text == Keyboards.get_chat_link.text)
async def get_chat_link(msg: Message):
    conf = Config()
    kb = Keyboards()
    db = DataBase()
    user = db.get_user(msg.from_user.id)

    if user:
        if user.payed_up_to < datetime.now():
            await msg.answer('Ваша подписка закончилась!')
            return
    else:
        await msg.answer(
            'Странно... вас нет в моей базе данных, я не могу выдать вам ссылку. '
            'Напишите /start и попробуйте еще раз'
        )
        return

    link = await bot.create_chat_invite_link(conf.get_chat_id(), expire_date=timedelta(1), member_limit=1)
    user = await bot.get_chat_member(chat_id=conf.get_chat_id(), user_id=msg.from_user.id)

    if user is None:
        await msg.answer(
            'Вы можете вступить по этой <b>одноразовой</b> ссылке',
            reply_markup=kb.to_channel(link.invite_link),
            protect_content=True
        )
    else:
        await msg.answer('Вы уже вступили в чат!')


@r.message(F.text == Keyboards.tarifs.text)
async def tarifs(msg: Message):
    kb = Keyboards()
    requisites = FSInputFile("core/photos/requisites.jpg")
    await msg.answer_photo(
        requisites,
        'Сейчас есть три тарифа:\n\n'
        '1 месяц - 90 usdt\n'
        '3 месяца - 220 usdt\n'
        '6 месяцев - 380 usdt\n\n'
        '<code>TC4fi8Kcax1F5YmQjQort89T7ddrsPZz8H</code> - нажми, чтобы скопировать',
        reply_markup=kb.to_menu_markup(),
        parse_mode='html'
    )


@r.message(F.text == Keyboards.our_tarifs.text)
async def our_tarifs(msg: Message):
    kb = Keyboards()
    requisites = FSInputFile("core/photos/requisites.jpg")
    await msg.answer_photo(
        requisites,
        'Сейчас есть три тарифа:\n\n'
        '1 месяц - 90 usdt\n'
        '3 месяца - 220 usdt\n'
        '6 месяцев - 380 usdt\n\n'
        '<code>TC4fi8Kcax1F5YmQjQort89T7ddrsPZz8H</code> - нажми, чтобы скопировать',
        reply_markup=kb.payed_markup(),
        parse_mode='html'
    )


async def add_referal(referer, user_id):
    db = DataBase()

    if not is_numeric(referer):
        logger.warning(f'referer is not numeric({referer})')
        return

    referer = int(referer)
    ref_from_db = db.get_user(referer)

    if ref_from_db is None or referer == user_id:
        logger.info('ref_from_db is None')
        return

    user = db.get_user(user_id)

    if user is not None:
        if user.referer is None:
            if ref_from_db.payed_up_to < datetime.now():
                await bot.send_message(
                    ref_from_db.user_id,
                    'Вы привели реферала, поэтому вам снова открыт доступ на 2 недели!'
                )
            db.add_subscribe(referer, timedelta(14))

    else:
        if ref_from_db.payed_up_to < datetime.now():
            await bot.send_message(
                ref_from_db.user_id,
                'Вы привели реферала, поэтому вам снова открыт доступ на 2 недели!'
            )

            db.add_subscribe(referer, timedelta(14))
