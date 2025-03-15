"""
[RU]
Модуль фильтрации и проверки прав администратора.

Предоставляет middleware и фильтр для проверки, является ли
пользователь администратором бота.

[EN]
Admin rights filtering and verification module.

Provides middleware and filter for checking if a user
is a bot administrator.
"""

import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message
from data.database import get_admins_ids

admins_ids = []

class AdminMiddleware:
    """
    [RU]
    Middleware для загрузки списка ID администраторов.
    
    Обновляет глобальный список ID администраторов при каждом запросе,
    обеспечивая актуальность данных для фильтра AdminFilter.

    [EN]
    Middleware for loading admin IDs list.
    
    Updates global admin IDs list on each request,
    ensuring data relevance for AdminFilter.
    """
    async def __call__(self, handler, event, data):
        """
        [RU]
        Обработчик вызова middleware.

        Args:
            handler: Функция-обработчик события
            event: Объект события
            data: Словарь с данными

        Returns:
            Any: Результат выполнения обработчика

        [EN]
        Middleware call handler.

        Args:
            handler: Event handler function
            event: Event object
            data: Data dictionary

        Returns:
            Any: Handler execution result
        """
        global admins_ids
        admins_ids = await get_admins_ids()

        return await handler(event, data)


class AdminFilter(BaseFilter):
    """
    [RU]
    Фильтр для проверки прав администратора.
    
    Проверяет, является ли отправитель сообщения администратором бота,
    сравнивая его ID со списком ID администраторов.

    [EN]
    Filter for checking admin rights.
    
    Checks if message sender is a bot administrator by
    comparing their ID with admin IDs list.
    """
    async def __call__(self, message: Message) -> bool:
        """
        [RU]
        Проверяет права администратора.

        Args:
            message (Message): Объект сообщения Telegram

        Returns:
            bool: True если пользователь администратор, False если нет

        [EN]
        Checks admin rights.

        Args:
            message (Message): Telegram message object

        Returns:
            bool: True if user is admin, False if not
        """
        return message.from_user.id in admins_ids
