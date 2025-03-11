import asyncio
import logging
from pathlib import Path

from data import database

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from loader import Config
from handlers import router
from aiogram import Bot, Dispatcher

from middlewares import DatabaseMiddleware

logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                        handlers=[
                            logging.FileHandler(Path('logs', 'bot.log')),
                            logging.StreamHandler()
                        ])

dp = Dispatcher()

async def on_startup():
    await database.create_database()


async def main():
    dp.startup.register(on_startup)

    bot = Bot(
        token=Config().get_token(),
    )
    bot.default = DefaultBotProperties(parse_mode=ParseMode.HTML)

    dp.update.outer_middleware(DatabaseMiddleware())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
