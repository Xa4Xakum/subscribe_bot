from aiogram import Bot, Dispatcher
from config import Config


conf = Config()
dp = Dispatcher()
bot = Bot(token=conf.get_token())
