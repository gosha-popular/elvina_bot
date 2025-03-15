import logging

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

from data.database import async_session, Question, Answer, Group
from filters.admin_filter import AdminFilter, AdminMiddleware

router = Router(name=__name__)
router.message.filter(AdminFilter())
router.message.outer_middleware(AdminMiddleware())

text = '<b>Question:</b>\n' + \
       '{question}\n' + \
       '<b>Answers:</b>\n' + \
       '{answers}\n' + \
       '\n<b>Write new answer in next message 👇</b>\n'


@router.message(Command('add_group'), F.chat.type.in_(['group', 'supergroup']))
async def adding_group(message: Message, session: AsyncSession):
    ic(message)
    group = Group(
        id=message.chat.id,
        title=message.chat.title,
    )
    session.add(group)
    await session.commit()

    await message.answer(
        text="Эта группа добавлена в список"
    )


@router.message(Command('add_group'))
async def adding_group(message: Message):
    await message.answer(
        text="Чтобы добавить группу в список рассылки, во-первых, добавтье бот в группу, во-вторых, введите команду /add_group"
    )


@router.message(Command('add_admin'))
async def assign_an_admin(message: Message, command: CommandObject):
    _id = command.args
    # TODO: Не реализованная функция
    await message.answer(
        text='[name] назначен администратором'
    )

    await message.bot.send_message(
        chat_id=message.chat.id,
        text='Вы назначены администратором'
    )


@router.message(Command('del_admin'))
async def assign_an_admin(message: Message, command: CommandObject):
    # TODO: Не реализованная функция
    await message.answer(
        text='[name] разжалован'
    )


class SetQuestion(StatesGroup):
    question = State()
    answer = State()


@router.message(Command('add_question'))
async def add_question(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    logging.info('''Call command add_question, arguments {}. Called admin - {}'''.format(
        command.args, message.from_user.id))

    builder = InlineKeyboardBuilder()
    builder.button(text='Reset', callback_data='reset')

    if command.args:
        await state.set_state(SetQuestion.answer)
        await enter_question(message, state, command.args)
    else:
        await state.clear()
        await state.set_state(SetQuestion.question)

        msg = await message.answer(
            text='Enter your question in next message 👇',
            reply_markup=builder.as_markup()
        )
        await state.update_data(message=msg)


builder = InlineKeyboardBuilder()
builder.button(
    text='Save', callback_data='save')
builder.button(
    text='Reset', callback_data='reset'
)
builder.adjust(1)


@router.message(SetQuestion.question, F.text.as_('question'))
async def enter_question(message: Message, state: FSMContext, question):
    await state.update_data(question=question)
    await state.set_state(SetQuestion.answer)
    msg = await state.get_value('message', None)

    if not msg:
        func = message.answer
    else:
        func = msg.edit_text
    msg = await func(
        text=text.format(
            question=question,
            answers='',
        ),
        reply_markup=builder.as_markup()
    )

    await state.update_data(message=msg)
    await message.delete()


@router.message(SetQuestion.answer, F.text.as_('answer'))
async def add_answer(message: Message, state: FSMContext, answer):
    question = await state.get_value('question')
    answers: list = await state.get_value('answers', [])
    answers.append(answer)
    await state.update_data(answers=answers)
    msg: Message = await state.get_value('message')
    await msg.edit_text(
        text=text.format(
            question=question,
            answers='\n'.join(answers)
        ),
        reply_markup=builder.as_markup()
    )
    await message.delete()


@router.callback_query(F.data == "save")
async def save_to_database(callback_query, state: FSMContext):
    data = await state.get_data()
    question_text = data.get('question')
    answers_list = data.get('answers', [])

    try:
        async with async_session() as session:
            async with session.begin():  # Явно начинаем транзакцию
                # Создаем новый вопрос
                new_question = Question(
                    content=question_text
                )
                session.add(new_question)
                await session.flush()

                # Создаем ответы
                for answer_text in answers_list:
                    new_answer = Answer(
                        content=answer_text,
                        question_id=new_question.id
                    )
                    session.add(new_answer)
                # Коммит произойдет автоматически при выходе из контекстного менеджера

            await callback_query.message.edit_text(
                "✅ Вопрос и ответы успешно сохранены в базу данных!"
            )
            await state.clear()

    except Exception as e:
        logging.error(f"Ошибка при сохранении в БД: {e}")
        await callback_query.message.edit_text(
            f"❌ Произошла ошибка при сохранении в базу данных: {str(e)}"
        )
