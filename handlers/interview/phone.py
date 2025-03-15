"""
[RU]
Модуль обработки получения контактных данных пользователя.

Управляет процессом запроса и получения номера телефона пользователя,
а также отправкой собранной информации менеджерам в группу.

[EN]
Module for handling user contact information.

Manages the process of requesting and receiving user's phone number,
and sending collected information to managers in the group.
"""

import asyncio
import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardMarkup
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

from data.database import User, get_user, Group
from handlers.menu import main_menu
from states.user_states import Interview

router = Router(name=__name__)


@router.message(StateFilter(Interview.question))
async def ask_phone(state: FSMContext):
    """
    [RU]
    Запрашивает номер телефона у пользователя.
    
    Отображает клавиатуру с кнопкой для отправки контакта.

    Args:
        state (FSMContext): Контекст состояния FSM

    [EN]
    Requests phone number from user.
    
    Displays keyboard with contact sharing button.

    Args:
        state (FSMContext): FSM state context
    """
    message: Message = await state.get_value('message')
    question = '📞 Оставьте ваш номер телефона, чтобы менеджер мог с вами связаться.'
    await state.set_state(Interview.phone)
    _message = await message.answer(
        text=question,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='Поделиться контактом', request_contact=True, )]],
            resize_keyboard=True
        )
    )
    await message.delete()

    await state.update_data(question=question, message=_message)


@router.message(F.text | F.contact, StateFilter(Interview.phone))
async def get_contact(message: Message, state: FSMContext, session: AsyncSession):
    """
    [RU]
    Обрабатывает полученный контакт или текстовый номер телефона.
    
    Сохраняет контактные данные и отправляет заявку менеджерам.
    После успешной отправки возвращает пользователя в главное меню.

    Args:
        message (Message): Объект сообщения Telegram
        state (FSMContext): Контекст состояния FSM
        session (AsyncSession): Сессия базы данных

    [EN]
    Processes received contact or text phone number.
    
    Saves contact information and sends application to managers.
    Returns user to main menu after successful submission.

    Args:
        message (Message): Telegram message object
        state (FSMContext): FSM state context
        session (AsyncSession): Database session
    """
    _message = await state.get_value('message', None)
    question = await state.get_value('question', None)
    answers = await state.get_value('answers', {})

    if _message:
        await _message.delete()

    if question:
        phone_number = message.contact.phone_number if message.contact else message.text
        answers[question] = f'<a href="tel:+{phone_number}">+{phone_number}</a>'

        # message for managers
        user: User = await get_user(message.from_user.id)
        text = f'#заявка\nПользователь:\n{'@' + message.from_user.username if message.from_user.username else ''}\n{user.name}\n'
        text += '\n'.join([f'<b>Q: {key}</b>\nA: {value}\n' for key, value in answers.items()])
        try:
            from sqlalchemy import select

            query = select(Group.id)
            result = await session.execute(query)
            groups = result.scalars().all()

            for group in groups:
                await message.bot.send_message(
                    chat_id=group,
                    text=text
                )

        except Exception as e:
            logging.error(f"Ошибка при проверке пользователя: {e}")
        finally:
            ic('Тут вообще происходит что то?')
            _message = await message.answer(
                text='✅ Отлично! Ваша заявка принята. Менеджер свяжется с Вами в ближайшее время',
                reply_markup=ReplyKeyboardRemove()
            )
            await asyncio.sleep(1)
            await main_menu(message, state)
            await state.clear()
