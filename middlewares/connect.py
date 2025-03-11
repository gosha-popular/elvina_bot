__all__ = ('DatabaseMiddleware', )

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from data.database import get_session


class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware для управления соединением с базой данных.
    Добавляет объект сессии в данные обработчика.
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

        session: AsyncSession = await get_session()

        data["session"] = session

        try:
            return await handler(event, data)
        finally:
            await session.close()