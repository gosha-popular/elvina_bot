"""
[RU]
Основной файл запуска Telegram-бота для автоворонки продаж.

Этот модуль инициализирует и запускает бота, настраивает логирование
и подключает все необходимые компоненты (роутеры, middleware).

[EN]
Main file for launching the Telegram bot for sales funnel automation.

This module initializes and launches the bot, configures logging,
and connects all necessary components (routers, middleware).
"""

import asyncio
import logging
import os
from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from data import database

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from loader import Config
from handlers import router
from aiogram import Bot, Dispatcher

from middlewares import DatabaseMiddleware

dp = Dispatcher()

async def on_startup():
    """
    [RU]
    Функция, выполняемая при запуске бота.
    
    Создает директорию для логов если она не существует и настраивает систему логирования.
    Также инициализирует базу данных.

    [EN]
    Function executed when the bot starts.
    
    Creates a log directory if it doesn't exist and configures the logging system.
    Also initializes the database.
    """
    log_dir = Path('logs')
    if not log_dir.exists():
        log_dir.mkdir()


    handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'bot'),
        when='midnight',  # 'midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    handler.suffix = "%Y-%m-%d_%H-%M-%S"
    handler.namer = lambda x: x + '.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        handlers=[
            handler, StreamHandler()
        ]
    )

    await database.create_database()


async def main():
    """
    [RU]
    Основная функция запуска бота.
    
    Регистрирует обработчик запуска, инициализирует бота с настройками,
    подключает middleware и роутеры, запускает поллинг обновлений.

    [EN]
    Main bot launch function.
    
    Registers startup handler, initializes bot with settings,
    connects middleware and routers, starts update polling.
    """
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
