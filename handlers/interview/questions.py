import asyncio

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

from data.database import Question, get_db, get_question_by_id
from handlers.interview import phone
from states.user_states import Interview

router = Router(name=__name__)
router.message.filter(StateFilter(Interview.question))
router.callback_query.filter(StateFilter(Interview.question))


@router.message(F.text.as_('answer'))
async def ask_question(message: Message, state: FSMContext, answer=None):
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

    async with get_db() as session:
        question = await get_question_by_id(session, _index)
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
    await callback.answer()
    await ask_question(callback.message, state, callback.data)
