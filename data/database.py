"""
[RU]
Модуль для работы с базой данных.

Определяет модели данных, предоставляет функции для работы с базой данных
и управления соединениями. Использует SQLAlchemy для асинхронной работы с SQLite.

[EN]
Database operations module.

Defines data models, provides functions for database operations
and connection management. Uses SQLAlchemy for async work with SQLite.
"""

from datetime import datetime
from pathlib import Path
import logging
from typing import Optional, Union

from icecream import ic
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Text
from contextlib import asynccontextmanager

DATABASE_URL = f"sqlite+aiosqlite:///{Path('data', 'db.db')}"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    """
    [RU]
    Базовый класс для всех моделей базы данных.

    Attributes:
        created_at (DateTime): Дата и время создания записи

    [EN]
    Base class for all database models.

    Attributes:
        created_at (DateTime): Record creation date and time
    """
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """
    [RU]
    Модель для хранения информации о пользователях.

    Attributes:
        id (int): Telegram ID пользователя
        username (str): Имя пользователя в Telegram
        name (str): Отображаемое имя пользователя

    [EN]
    Model for storing user information.

    Attributes:
        id (int): Telegram user ID
        username (str): Telegram username
        name (str): User display name
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    name = Column(String)


class Admin(Base):
    """
    [RU]
    Модель для хранения информации об администраторах.

    Attributes:
        id (int): Telegram ID администратора
        username (str): Имя пользователя администратора в Telegram

    [EN]
    Model for storing admin information.

    Attributes:
        id (int): Telegram admin ID
        username (str): Telegram admin username
    """
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    username = Column(String)


class Group(Base):
    """
    [RU]
    Модель для хранения информации о группах.

    Attributes:
        id (int): Telegram ID группы
        title (str): Название группы
        is_mailing (bool): Флаг для рассылки сообщений

    [EN]
    Model for storing group information.

    Attributes:
        id (int): Telegram group ID
        title (str): Group title
        is_mailing (bool): Message mailing flag
    """
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    is_mailing = Column(Boolean, default=True)


class Question(Base):
    """
    [RU]
    Модель для хранения вопросов анкеты.

    Attributes:
        id (int): Уникальный идентификатор вопроса
        content (str): Текст вопроса
        answers (relationship): Связь с вариантами ответов
        created_at (datetime): Дата и время создания

    [EN]
    Model for storing questionnaire questions.

    Attributes:
        id (int): Unique question identifier
        content (str): Question text
        answers (relationship): Relation to answer options
        created_at (datetime): Creation date and time
    """
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    answers = relationship('Answer', back_populates='question', cascade='all, delete-orphan')


class Answer(Base):
    """
    [RU]
    Модель для хранения вариантов ответов.

    Attributes:
        id (int): Уникальный идентификатор ответа
        content (str): Текст ответа
        question_id (int): ID связанного вопроса
        next (int): ID следующего вопроса
        question (relationship): Связь с вопросом
        created_at (datetime): Дата и время создания

    [EN]
    Model for storing answer options.

    Attributes:
        id (int): Unique answer identifier
        content (str): Answer text
        question_id (int): Related question ID
        next (int): Next question ID
        question (relationship): Relation to question
        created_at (datetime): Creation date and time
    """
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    next = Column(Integer)
    question = relationship('Question', back_populates='answers')


@asynccontextmanager
async def get_db():
    """
    [RU]
    Контекстный менеджер для работы с сессией базы данных.

    Yields:
        AsyncSession: Объект асинхронной сессии SQLAlchemy

    [EN]
    Context manager for database session handling.

    Yields:
        AsyncSession: SQLAlchemy async session object
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logging.error(f"Ошибка при работе с базой данных: {e}")
            raise


async def create_database() -> bool:
    """
    [RU]
    Создает все необходимые таблицы в базе данных.

    Returns:
        bool: True если создание успешно, False в случае ошибки

    [EN]
    Creates all necessary database tables.

    Returns:
        bool: True if creation successful, False if error occurred
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("База данных успешно инициализирована")
        return True
    except Exception as e:
        logging.error(f"Ошибка при создании базы данных: {e}")
        return False


async def get_session() -> Optional[AsyncSession]:
    """
    [RU]
    Создает новую сессию базы данных.

    Returns:
        Optional[AsyncSession]: Объект сессии или None в случае ошибки

    [EN]
    Creates new database session.

    Returns:
        Optional[AsyncSession]: Session object or None if error occurred
    """
    try:
        return async_session()
    except Exception as e:
        logging.error(f"Ошибка при создании сессии базы данных: {e}")
        return None


async def get_question_by_id(session: AsyncSession, question_id: int):
    """
    [RU]
    Получает вопрос по его ID вместе с вариантами ответов.

    Args:
        session (AsyncSession): Сессия базы данных
        question_id (int): ID вопроса

    Returns:
        Question: Объект вопроса с прикрепленными ответами

    [EN]
    Gets question by ID with answer options.

    Args:
        session (AsyncSession): Database session
        question_id (int): Question ID

    Returns:
        Question: Question object with attached answers
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    query = select(Question).options(selectinload(Question.answers)).where(Question.id == question_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_all_questions_with_answers(session: AsyncSession):
    """
    [RU]
    Получает все вопросы с их вариантами ответов.

    Args:
        session (AsyncSession): Сессия базы данных

    Returns:
        list[Question]: Список вопросов с прикрепленными ответами

    [EN]
    Gets all questions with their answer options.

    Args:
        session (AsyncSession): Database session

    Returns:
        list[Question]: List of questions with attached answers
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    query = select(Question).options(selectinload(Question.answers))
    result = await session.execute(query)
    return result.scalars().all()


async def get_user(id: int) -> Optional[User]:
    """
    [RU]
    Получает информацию о пользователе по его ID.

    Args:
        id (int): Telegram ID пользователя

    Returns:
        Optional[User]: Объект пользователя или None если не найден

    [EN]
    Gets user information by ID.

    Args:
        id (int): Telegram user ID

    Returns:
        Optional[User]: User object or None if not found
    """
    async with get_db() as session:
        try:
            from sqlalchemy import select

            query = select(User).where(User.id == id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logging.error(f"Ошибка при проверке пользователя: {e}")
            return False

async def get_admins_ids() -> Optional[Admin]:
    """
    [RU]
    Получает список ID всех администраторов.

    Returns:
        Optional[list[int]]: Список ID администраторов или None в случае ошибки

    [EN]
    Gets list of all admin IDs.

    Returns:
        Optional[list[int]]: List of admin IDs or None if error occurred
    """
    async with get_db() as session:
        try:
            from sqlalchemy import select

            query = select(Admin.id)
            result = await session.execute(query)
            return ic(result.scalars().all())

        except Exception as e:
            logging.error(f"Ошибка при проверке пользователя: {e}")
            return None