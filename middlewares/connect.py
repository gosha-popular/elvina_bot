"""
[RU]
Модуль для управления соединением с базой данных.

Предоставляет middleware для автоматического управления сессиями базы данных
в обработчиках событий бота.

[EN]
Module for database connection management.

Provides middleware for automatic database session management
in bot event handlers.
"""

__all__ = ('DatabaseMiddleware', )

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from data.database import get_session, get_db


class DatabaseMiddleware(BaseMiddleware):
    """
    [RU]
    Middleware для управления соединением с базой данных.

    Автоматически создает сессию базы данных для каждого обработчика
    и закрывает её после завершения обработки. Добавляет объект сессии
    в данные обработчика под ключом "session".

    [EN]
    Middleware for database connection management.

    Automatically creates database session for each handler
    and closes it after processing is complete. Adds session object
    to handler data under "session" key.
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        """
        [RU]
        Обработчик вызова middleware.

        Args:
            handler: Функция-обработчик события
            event: Объект события Telegram
            data: Словарь с данными обработчика

        Returns:
            Any: Результат выполнения обработчика

        [EN]
        Middleware call handler.

        Args:
            handler: Event handler function
            event: Telegram event object
            data: Handler data dictionary

        Returns:
            Any: Handler execution result
        """

        async with get_db() as session:
            data["session"] = session
            return await handler(event, data)