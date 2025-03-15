"""
[RU]
Модуль для загрузки конфигурации бота.

Предоставляет класс Config для работы с переменными окружения
и получения токена бота из .env файла.

[EN]
Module for loading bot configuration.

Provides Config class for working with environment variables
and getting bot token from .env file.
"""

import os, dotenv


class Config:
    """
    [RU]
    Класс для управления конфигурацией бота.
    
    Загружает переменные окружения из .env файла и предоставляет
    методы для получения конфигурационных значений.

    [EN]
    Class for managing bot configuration.
    
    Loads environment variables from .env file and provides
    methods for getting configuration values.
    """

    def __init__(self):
        """
        [RU]
        Инициализирует объект Config.
        
        Загружает переменные окружения и сохраняет токен бота.

        [EN]
        Initializes Config object.
        
        Loads environment variables and stores bot token.
        """
        dotenv.load_dotenv()
        self._token = os.getenv('BOT_TOKEN')

    def get_token(self) -> str:
        """
        [RU]
        Возвращает токен бота.
        
        Returns:
            str: Токен для доступа к Telegram Bot API.

        [EN]
        Returns bot token.
        
        Returns:
            str: Token for accessing Telegram Bot API.
        """
        return self._token
