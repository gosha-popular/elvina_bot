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
    user = message.text
    await add_user(user, session)
    await start_message(message, user)
    await state.clear()

@router.callback_query()
async def callback_my_name_is(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    user = callback.from_user
    await add_user(user, session)
    await start_message(callback.message, callback.data)
    await state.clear()

async def add_user(user, session):
    try:
        session.add(User(
            id=user.id,
            username=user.username,
            name=user.first_name,
        ))
        await session.commit()
    except Exception as e:
        logging.error(e)


