from datetime import datetime
from pathlib import Path
import logging
from typing import Optional, Union

from icecream import ic
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Text
from contextlib import asynccontextmanager

DATABASE_URL = f"sqlite+aiosqlite:///{Path('data', 'db.db')}"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    created_at = Column(DateTime, default=func.now())


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    is_mailing = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())


class Question(Base):
    """
    Модель для хранения вопросов.

    Attributes:
        id (int): Уникальный идентификатор вопроса
        content (str): Полное содержание вопроса
        created_at (datetime): Дата и время создания вопроса
        updated_at (datetime): Дата и время последнего обновления вопроса
        answers (relationship): Связь с ответами на вопрос
    """
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связь с ответами (один ко многим)
    answers = relationship('Answer', back_populates='question', cascade='all, delete-orphan')


class Answer(Base):
    """
    Модель для хранения ответов на вопросы.

    Attributes:
        id (int): Уникальный идентификатор ответа
        content (str): Содержание ответа
        created_at (datetime): Дата и время создания ответа
        updated_at (datetime): Дата и время последнего обновления ответа
        question_id (int): Внешний ключ, указывающий на связанный вопрос
        question (relationship): Связь с вопросом, к которому относится ответ
    """
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Внешний ключ к таблице вопросов (многие к одному)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)

    next = Column(Integer, )
    # Связь с вопросом
    question = relationship('Question', back_populates='answers')


@asynccontextmanager
async def get_db():
    """
    Контекстный менеджер для работы с сессией базы данных.

    Yields:
        AsyncSession: Объект асинхронной сессии SQLAlchemy
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
    Создает необходимые таблицы в базе данных.

    Returns:
        bool: True если операция успешна, False в случае ошибки
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
    Создает новую сессию базы данных.

    Returns:
        Optional[AsyncSession]: Объект сессии или None в случае ошибки
    """
    try:
        return async_session()
    except Exception as e:
        logging.error(f"Ошибка при создании сессии базы данных: {e}")
        return None


async def get_question_by_id(session: AsyncSession, question_id: int):
    """
    Получение вопроса по его ID вместе с ответами

    Args:
        session: Сессия базы данных
        question_id: ID вопроса

    Returns:
        Question: Объект вопроса с прикрепленными ответами
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    query = select(Question).options(selectinload(Question.answers)).where(Question.id == question_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_all_questions_with_answers(session: AsyncSession):
    """
    Получение всех вопросов с их ответами

    Args:
        session: Сессия базы данных

    Returns:
        list[Question]: Список вопросов с прикрепленными ответами
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    query = select(Question).options(selectinload(Question.answers))
    result = await session.execute(query)
    return result.scalars().all()


async def get_user(id: int) -> Optional[User]:
    """
    Проверяет существование пользователя в базе данных.

    Args:
        username (str): Имя пользователя для проверки

    Returns:
        bool: True если пользователь существует, False если нет
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
    async with get_db() as session:
        try:
            from sqlalchemy import select

            query = select(Admin.id)
            result = await session.execute(query)
            return ic(result.scalars().all())

        except Exception as e:
            logging.error(f"Ошибка при проверке пользователя: {e}")
            return None