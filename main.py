import asyncio
import logging
from pathlib import Path

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import loader
from handlers import router
from aiogram import Bot, Dispatcher


async def main():
    if loader.CONFIG:
        bot = Bot(
            token=loader.CONFIG['BOT_TOKEN'],
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    else:
        raise ValueError('No token')

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        handlers=[
                            logging.FileHandler(Path('logs', 'bot.log')),
                            logging.StreamHandler()
                        ])
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
