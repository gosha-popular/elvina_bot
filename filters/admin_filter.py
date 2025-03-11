import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message
from data.database import get_admins_ids

admins_ids = []

class AdminMiddleware:
    async def __call__(self, handler, event, data):

        global admins_ids
        admins_ids = await get_admins_ids()

        return await handler(event, data)

class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in admins_ids
