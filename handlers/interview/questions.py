"""
[RU]
Модуль обработки вопросов анкеты.

Управляет процессом опроса пользователя, загружает вопросы из базы данных,
обрабатывает ответы и определяет следующий вопрос на основе ответов пользователя.

[EN]
Questionnaire questions handling module.

Manages the user survey process, loads questions from the database,
processes answers and determines the next question based on user responses.
"""

import asyncio

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

from data.database import Question, get_db, get_all_questions_with_answers
from handlers.interview import phone
from states.user_states import Interview

router = Router(name=__name__)
router.message.filter(StateFilter(Interview.question))
router.callback_query.filter(StateFilter(Interview.question))

questions_cache = {}


async def load_questions():
    """
    [RU]
    Загрузка всех вопросов в кэш при старте.
    
    Returns:
        dict: Словарь с вопросами, где ключ - id вопроса.

    [EN]
    Load all questions into cache at startup.
    
    Returns:
        dict: Dictionary with questions where key is question id.
    """
    if not questions_cache:
        ic('No cache')
        async with get_db() as session:
            questions = await get_all_questions_with_answers(session)
            for question in questions:
                questions_cache[question.id] = question
    return questions_cache


@router.message(F.text.as_('answer'))
async def ask_question(message: Message, state: FSMContext, answer=None):
    """
    [RU]
    Обработчик для отображения вопроса и обработки ответа пользователя.

    Args:
        message (Message): Объект сообщения Telegram
        state (FSMContext): Контекст состояния FSM
        answer (str, optional): Предыдущий ответ пользователя

    [EN]
    Handler for displaying question and processing user's answer.

    Args:
        message (Message): Telegram message object
        state (FSMContext): FSM state context
        answer (str, optional): Previous user's answer
    """
    _message = await state.get_value('message', None)
    _index = await state.get_value('index', 1)
    _question = await state.get_value('question', None)
    _answers = await state.get_value('answers', {})

    if _question:
        if (new_answer := answer.split(':'))[-1].isdigit():
            _index = int(new_answer[-1])
        else:
            _index += 1

        _answers[_question] = new_answer[0]
        await state.update_data(answers=_answers)

    text = None
    builder = InlineKeyboardBuilder()

    if _message:
        send = _message.edit_text
    else:
        _message = message
        send = _message.answer

    if message.bot.id != message.from_user.id:
        await message.delete()

    # Используем кэшированные вопросы
    await load_questions()
    question = questions_cache.get(_index)

    if question:
        text = question.content
        await state.update_data(question=text)
        for answer in question.answers:
            builder.button(text=answer.content, callback_data=':'.join([str(answer.content), str(answer.next)]))
        builder.button(text='🏠 Вернуться в главное меню', callback_data='главное меню')

    builder.adjust(1)
    if not text:
        ic('not text')
        await phone.ask_phone(state=state)
    else:
        _message = await send(
            text=text,
            reply_markup=builder.as_markup()
        )
        await state.update_data(message=_message, index=_index)


@router.callback_query(~F.data.contains('главное меню'))
async def ask_question_callback(callback: CallbackQuery, state: FSMContext):
    """
    [RU]
    Обработчик callback-запросов для ответов на вопросы.

    Args:
        callback (CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM

    [EN]
    Callback query handler for question answers.

    Args:
        callback (CallbackQuery): Callback query object
        state (FSMContext): FSM state context
    """
    await callback.answer()
    await ask_question(callback.message, state, callback.data)
