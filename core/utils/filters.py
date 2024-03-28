from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message

from config import Config


class ChatType(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type


class RequestChat(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        conf = Config()
        return message.chat.id == conf.admins_chat


class ReplyToMessege(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.reply_to_message is None:
            return False
        return True


class GreatAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        conf = Config()
        return conf.get_admin_id() == message.from_user.id


class TypeOfContent(BaseFilter):
    def __init__(self, content_type: Union[str, list]):
        self.content_type = content_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.content_type, list):
            return message.content_type in self.content_type
        return message.content_type == self.content_type
