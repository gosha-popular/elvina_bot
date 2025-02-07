import asyncio
import html

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from icecream import ic

from data import groups
from handlers.commands.user_commands import main_menu
from loader import QUERY, ADMINS
from data.users import add_user_to_data_base, get_user
from states.user_states import Interview
from keyboards import user_keyboards as kb

router = Router(name=__name__)
admins = F.from_user.id.in_(ADMINS)


@router.message(F.text, StateFilter(Interview.name), ~F.chat.type.in_(['group', 'supergroup']))
async def input_name(message: Message, state: FSMContext):
    await add_user_to_data_base(user_id=message.from_user.id,
                                username=message.from_user.username,
                                name=message.text)
    await state.clear()
    await message.answer(
        text=f'Мы рады познакомиться с Вами, {html.escape(message.text)}!\n\n'
             f'Теперь наша очередь рассказать о себе.\n'
             f'Мы — команда, создающая <b>качественные, стильные и продающие сайты.</b>\n'
             f'Мы поможем воплотить Ваши идеи и получить сайт, который привлекает клиентов и увеличивает продажи.\n'
             f'Давайте разберемся, какой сайт Вам нужен!'
    )
    await main_menu(message, state)


@router.callback_query(F.data.contains('Меня зовут'), StateFilter(Interview.name),
                       ~F.chat.type.in_(['group', 'supergroup']))
async def inline_input_name(callback: CallbackQuery, state: FSMContext):
    name = callback.data.replace('Меня зовут', '')
    name = name.strip('!')
    await add_user_to_data_base(user_id=callback.from_user.id,
                                username=callback.from_user.username,
                                name=name.strip())
    await state.clear()
    await callback.message.answer(
        text=f'Мы рады познакомиться с Вами, {html.escape(name.strip())}!\n\n'
             f'Теперь наша очередь рассказать о себе.\n'
             f'Мы — команда, создающая <b>качественные, стильные и продающие сайты.</b>\n'
             f'Мы поможем воплотить Ваши идеи и получить сайт, который привлекает клиентов и увеличивает продажи.\n'
             f'Давайте разберемся, какой сайт Вам нужен!'
    )
    await main_menu(callback.message, state)


@router.message(F.contact, StateFilter(Interview.phone), ~F.chat.type.in_(['group', 'supergroup']))
async def share_contact(message: Message, state: FSMContext):
    await set_contact(message, state, number=message.contact.phone_number)


@router.message(F.text, StateFilter(Interview.phone))
async def share_contact(message: Message, state: FSMContext):
    await set_contact(message, state, number=message.text)


@router.callback_query(F.data, *Interview.query, ~F.chat.type.in_(['group', 'supergroup']))
async def callback_interview(callback: CallbackQuery, state: FSMContext):
    await query_interview(callback.message, state, callback=callback)


@router.message(F.text, *Interview.query, ~F.chat.type.in_(['group', 'supergroup']))
async def message_interview(message: Message, state: FSMContext):
    await query_interview(message, state)


@router.message(~F.text, *Interview.query, ~F.chat.type.in_(['group', 'supergroup']))
async def echo_interview(message: Message):
    await message.answer(
        text='Введите текст'
    )


@router.message(~admins, *Interview.query, ~F.chat.type.in_(['group', 'supergroup']))
async def query_interview(message: Message, state: FSMContext, callback=None):
    data = await state.get_data()
    if not data:
        await main_menu(message, state)
        await message.delete()
        return

    stack = data['stack']
    index = data['index']
    await state.update_data(
        {index: [QUERY[stack[index]], callback.data if callback else message.text]})

    if callback:
        if stack[index] in ['type'] and callback.data and 'Товары' in callback.data:
            data['enable'].append(stack[index])
        if stack[index] in ['integration'] and callback.data and 'Нет' in callback.data:
            data['enable'].append(stack[index])
        if stack[index] in ['info'] and callback.data and 'Да' in callback.data:
            data['enable'].append(stack[index])

    await state.update_data(enable=data['enable'])
    index += 1

    try:
        if 'type' not in data['enable']:
            if stack[index] in ['delivery']:
                index += 1
            if stack[index] in ['accounting']:
                index += 1

        if 'info' in data['enable']:
            if stack[index] in ['info_no']:
                index += 1

        if 'integration' in data['enable']:
            if stack[index] in ['integration_input']:
                index += 1

        _state = Interview.query[index]
        await state.set_state(Interview.query[index])

        _message = await message.answer(
            text=QUERY[stack[index]],
            reply_markup=await kb.get_keyboards(stack[index]))
        try:
            await message.bot.delete_message(message.chat.id, message_id=message.message_id)
        except:
            pass
        await state.update_data(message_id=_message.message_id, stack=stack, index=index)

    except IndexError as e:
        await state.set_state(Interview.phone)
        _message = await message.answer(
            text="📞 Оставьте ваш номер телефона, чтобы менеджер мог с вами связаться.",
            reply_markup=ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[
                    [KeyboardButton(text='Поделиться контактом', request_contact=True)]
                ]
            )
        )
        await message.bot.delete_message(message.chat.id, message_id=data['message_id'])
        await state.update_data(message_id=_message.message_id)


@router.message(~F.chat.type.in_(['group', 'supergroup']))
async def set_contact(message: Message, state: FSMContext, number):
    data = await state.get_data()
    data = await state.update_data({data['index']: ['Телефон', number]})
    await message.bot.delete_message(message.chat.id, message_id=data['message_id'])

    del data['stack'], data['index'], data['message_id'], data['enable']
    ic(data)
    text = f'#заявка \nПользователь: @{message.from_user.username} {(await get_user(message.from_user.id))[-1]}\n\n'
    for key, value in data.items():
        query, answer = value
        text += f'<b>{query}</b>\n - {answer}\n\n'
    await message.answer(
        text='✅ Отлично! Ваша заявка принята. Менеджер свяжется с Вами в ближайшее время',
        reply_markup=ReplyKeyboardRemove())

    await asyncio.sleep(2)
    await main_menu(message, state)
    _groups = await groups.get_list_group_mailing()
    for group in _groups:
        await message.bot.send_message(chat_id=group, text=text)
