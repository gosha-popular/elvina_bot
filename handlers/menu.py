"""
[RU]
Модуль обработки главного меню бота.

Содержит обработчики для основных разделов бота: главное меню,
контакты, примеры работ и заказ сайта. Управляет навигацией и
отображением информации пользователю.

[EN]
Bot main menu handling module.

Contains handlers for main bot sections: main menu,
contacts, work examples and site ordering. Manages navigation
and information display to the user.
"""

import html
from pathlib import Path

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states.user_states import Interview, Reference

router = Router(name=__name__)

hello_message = '''👋 Приветствуем Вас, {user}!\n
Мы — команда, создающая <b>качественные, стильные и продающие сайты.</b>\n
Мы поможем воплотить Ваши идеи и получить сайт, который привлекает клиентов и увеличивает продажи.\n
Давайте разберемся, какой сайт Вам нужен!'''


async def start_message(message: Message, name):
    """
    [RU]
    Отправляет приветственное сообщение и показывает главное меню.

    Args:
        message (Message): Объект сообщения Telegram
        name (str): Имя пользователя для приветствия

    [EN]
    Sends welcome message and shows main menu.

    Args:
        message (Message): Telegram message object
        name (str): Username for greeting
    """
    await message.answer(
        text=hello_message.format(
            user=html.escape(name)
        )
    )
    await main_menu(message)


async def main_menu(message: Message, state: FSMContext = None):
    """
    [RU]
    Отображает главное меню бота.

    Args:
        message (Message): Объект сообщения Telegram
        state (FSMContext, optional): Контекст состояния FSM

    [EN]
    Displays bot main menu.

    Args:
        message (Message): Telegram message object
        state (FSMContext, optional): FSM state context
    """
    if state:
        await state.clear()

    builder = InlineKeyboardBuilder()
    for name in ['💻 Заказать сайт', '📞 Наши контакты', '📂 Примеры работ']:
        builder.button(text=name, callback_data=name)
    builder.adjust(1, 2)

    await message.delete()
    await message.answer(
        text="🏠 Вы находитесь в главном меню",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.casefold().contains('главное меню'))
async def get_menu(callback: CallbackQuery, state: FSMContext):
    """
    [RU]
    Обработчик возврата в главное меню.

    Args:
        callback (CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM

    [EN]
    Handler for returning to main menu.

    Args:
        callback (CallbackQuery): Callback query object
        state (FSMContext): FSM state context
    """
    await main_menu(message=callback.message, state=state)


@router.callback_query(F.data.casefold().contains('наши контакты'))
async def main_contact(callback: CallbackQuery, state: FSMContext):
    """
    [RU]
    Отображает контактную информацию.

    Args:
        callback (CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM

    [EN]
    Displays contact information.

    Args:
        callback (CallbackQuery): Callback query object
        state (FSMContext): FSM state context
    """
    await state.clear()

    builder = InlineKeyboardBuilder()
    for name in ["💻 Заказать сайт", "📂 Примеры работ", "🏠 Главное меню"]:
        builder.button(text=name, callback_data=name)
    builder.adjust(2, 1)

    await callback.message.edit_text(
        text=f'Свяжитесь с нами:\n\n'
             f'📞 Телефон: +79991551043\n'
             f'📧 Email: site-it@mail.ru\n'
             f'📱 Telegram: @site_it',
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.casefold().contains('примеры работ'))
async def main_reference(callback: CallbackQuery, state: FSMContext):
    """
    [RU]
    Отображает категории примеров работ.

    Args:
        callback (CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM

    [EN]
    Displays work examples categories.

    Args:
        callback (CallbackQuery): Callback query object
        state (FSMContext): FSM state context
    """
    await state.clear()
    await state.set_state(Reference.view)

    ref_list = ["🚗 Автомобили",
                "💄 Бьюти-сфера",
                "🏗 Строительство",
                "🍕 Еда и товары",
                "🏭 Промышленность",
                "🏠 Ремонтные работы",
                "👨‍💻 Специалисты",
                "🏠 Вернуться в главное меню"]

    builder = InlineKeyboardBuilder()
    for name in ref_list:
        builder.button(text=name, callback_data=name)
    builder.adjust(1)

    await callback.message.edit_text(
        text=f"<b>Примеры работ.</b>\n\nВыберите категорию.",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.casefold().contains('заказать сайт'))
async def main_order(callback: CallbackQuery, state: FSMContext):
    """
    [RU]
    Начинает процесс заказа сайта.

    Args:
        callback (CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM

    [EN]
    Starts the website ordering process.

    Args:
        callback (CallbackQuery): Callback query object
        state (FSMContext): FSM state context
    """
    await state.clear()
    await state.set_state(Interview.question)
    await state.update_data(message=callback.message,)

    from handlers.interview.questions import ask_question
    await ask_question(callback.message, state)


@router.callback_query(Reference.view, ~F.data.contains('Назад'))
async def view_reference(callback: CallbackQuery):
    """
    [RU]
    Показывает примеры работ выбранной категории.

    Args:
        callback (CallbackQuery): Объект callback запроса

    [EN]
    Shows work examples for selected category.

    Args:
        callback (CallbackQuery): Callback query object
    """
    directory = None

    if callback.data == "🚗 Автомобили":
        directory = 'auto'
    elif callback.data == "💄 Бьюти-сфера":
        directory = 'beauty'
    elif callback.data == "🏗 Строительство":
        directory = 'building'
    elif callback.data == "🍕 Еда и товары":
        directory = 'food'
    elif callback.data == "🏭 Промышленность":
        directory = 'industry'
    elif callback.data == "🏠 Ремонтные работы":
        directory = 'repair'
    elif callback.data == "👨‍💻 Специалисты":
        directory = 'specialist'
    else:
        return

    photo_paths = [Path('.', 'data', 'image', directory, f'{num}.PNG') for num in range(1, 5)]
    media = [InputMediaPhoto(media=FSInputFile(path)) for path in photo_paths]
    await callback.message.answer_media_group(media=media)

    builder = InlineKeyboardBuilder()
    for name in ['Назад', '🏠 Вернуться в главное меню']:
        builder.button(text=name, callback_data=name)
    builder.adjust(1)

    await callback.message.answer(text=f'Примеры по теме {callback.data}', reply_markup=builder.as_markup())
    await callback.message.delete()


@router.callback_query(Reference.view, F.data.contains('Назад'))
async def view_reference(callback: CallbackQuery, state: FSMContext):
    """
    [RU]
    Обработчик возврата к списку категорий примеров работ.

    Args:
        callback (CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM

    [EN]
    Handler for returning to work examples categories list.

    Args:
        callback (CallbackQuery): Callback query object
        state (FSMContext): FSM state context
    """
    await main_reference(callback, state)
