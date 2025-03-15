"""
[RU]
Модуль обработки получения имени пользователя.

Управляет процессом запроса и получения имени пользователя,
предлагает использовать имя из профиля Telegram или ввести другое имя.
Сохраняет информацию о пользователе в базе данных.

[EN]
Module for handling username acquisition.

Manages the process of requesting and receiving username,
offers to use name from Telegram profile or enter different name.
Saves user information in the database.
"""

import html
import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from data.database import User
from handlers.menu import start_message
from states.user_states import Interview

router = Router(name=__name__)
router.message.filter(StateFilter(Interview.name))
router.callback_query.filter(StateFilter(Interview.name))

async def start(message: Message, state: FSMContext):
    """
    [RU]
    Начинает диалог знакомства с пользователем.
    
    Отправляет приветственное сообщение и предлагает использовать
    имя из профиля Telegram.

    Args:
        message (Message): Объект сообщения Telegram
        state (FSMContext): Контекст состояния FSM

    [EN]
    Starts the greeting dialogue with user.
    
    Sends welcome message and offers to use name
    from Telegram profile.

    Args:
        message (Message): Telegram message object
        state (FSMContext): FSM state context
    """
    text = '''👋 Приветствуем Вас!\nДавайте познакомимся. Как Вас зовут?'''

    builder = InlineKeyboardBuilder()
    builder.button(text=f'Меня зовут {html.escape(message.from_user.first_name)}!', callback_data=message.from_user.first_name)

    await state.set_state(Interview.name)
    await message.answer(
        text=text,
        reply_markup=builder.as_markup()
    )


@router.message()
async def input_my_name_is(message: Message, state: FSMContext, session: AsyncSession):
    """
    [RU]
    Обрабатывает введенное пользователем имя.
    
    Сохраняет имя пользователя и переходит к главному меню.

    Args:
        message (Message): Объект сообщения Telegram
        state (FSMContext): Контекст состояния FSM
        session (AsyncSession): Сессия базы данных

    [EN]
    Processes user-entered name.
    
    Saves username and proceeds to main menu.

    Args:
        message (Message): Telegram message object
        state (FSMContext): FSM state context
        session (AsyncSession): Database session
    """
    user = message.text
    await add_user(user, session)
    await start_message(message, user)
    await state.clear()

@router.callback_query()
async def callback_my_name_is(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    [RU]
    Обрабатывает выбор имени из профиля Telegram.
    
    Сохраняет имя пользователя и переходит к главному меню.

    Args:
        callback (CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM
        session (AsyncSession): Сессия базы данных

    [EN]
    Processes name selection from Telegram profile.
    
    Saves username and proceeds to main menu.

    Args:
        callback (CallbackQuery): Callback query object
        state (FSMContext): FSM state context
        session (AsyncSession): Database session
    """
    await callback.answer()
    user = callback.from_user
    await add_user(user, session)
    await start_message(callback.message, callback.data)
    await state.clear()

async def add_user(user, session):
    """
    [RU]
    Добавляет информацию о пользователе в базу данных.

    Args:
        user: Объект пользователя Telegram
        session: Сессия базы данных

    [EN]
    Adds user information to database.

    Args:
        user: Telegram user object
        session: Database session
    """
    try:
        session.add(User(
            id=user.id,
            username=user.username,
            name=user.first_name,
        ))
        await session.commit()
    except Exception as e:
        logging.error(e)


