from pathlib import Path

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto
from loader import QUERY
from keyboards import user_keyboards as kb

from handlers.commands.user_commands import main_menu
from states.user_states import Interview, Reference

from util.names import MenuNames

router = Router(name=__name__)


@router.callback_query(F.data.casefold().contains(MenuNames.menu.casefold()))
async def get_menu(callback: CallbackQuery, state: FSMContext):
    await main_menu(message=callback.message, state=state)
    await callback.message.delete()


@router.callback_query(F.data.casefold().contains(MenuNames.contact.casefold()))
async def main_contact(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        text=f'Свяжитесь с нами:\n\n'
             f'📞 Телефон: +79991551043\n'
             f'📧 Email: site-it@mail.ru\n'
             f'📱 Telegram: @site_it',
        reply_markup=
        await kb.build_inline_keyboard(
            ["💻 Заказать сайт", "📂 Примеры работ", "🏠 Главное меню"], (2, 1))
    )

    await callback.message.delete()


@router.callback_query(F.data.casefold().contains(MenuNames.reference.casefold()))
async def main_reference(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Reference.view)
    await callback.message.answer(
        text=f"<b>Примеры работ.</b>\n\nВыберите категорию.",
        reply_markup=
        await kb.build_inline_keyboard(
            ["🚗 Автомобили",
             "💄 Бьюти-сфера",
             "🏗 Строительство",
             "🍕 Еда и товары",
             "🏭 Промышленность",
             "🏠 Ремонтные работы",
             "👨‍💻 Специалисты",
             "🏠 Вернуться в главное меню"])
    )

    await callback.message.delete()


@router.callback_query(F.data.casefold().contains(MenuNames.order.casefold()))
async def main_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    stack = ["sphere", "type", "which_site", "integration", "integration_input",
             "info", "info_no", "billing", "delivery", "accounting", "example"]

    index = 0
    await state.set_state(Interview.query[index])
    await state.update_data(message_id=callback.message.message_id, stack=stack, index=index, enable=[])
    await callback.message.answer(
        text=QUERY[stack[index]],
        reply_markup=await kb.get_keyboards(stack[index])
    )
    await callback.message.delete()


@router.callback_query(Reference.view, ~F.data.contains('Назад'))
async def view_reference(callback: CallbackQuery):
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

    photo_paths = [Path('.','data','image', directory, f'{num}.PNG') for num in range(1, 5)]
    media = [InputMediaPhoto(media=FSInputFile(path)) for path in photo_paths]
    await callback.message.answer_media_group(media=media)
    await callback.message.answer(text=f'Примеры по теме {callback.data}', reply_markup=await kb.build_inline_keyboard(
            ['Назад', '🏠 Вернуться в главное меню']
        ))
    await callback.message.delete()


@router.callback_query(Reference.view, F.data.contains('Назад'))
async def view_reference(callback: CallbackQuery, state: FSMContext):
    await main_reference(callback, state)