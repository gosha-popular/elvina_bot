from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from icecream import ic

from data import users

from keyboards import user_keyboards as kb
from loader import ADMINS

from states.user_states import Interview

router = Router(name=__name__)

hello_message = '''👋 Приветствуем Вас, {user}!\n
Мы — команда, создающая <b>качественные, стильные и продающие сайты.</b>\n
Мы поможем воплотить Ваши идеи и получить сайт, который привлекает клиентов и увеличивает продажи.\n
Давайте разберемся, какой сайт Вам нужен!'''


@router.message(~F.from_user.id.in_(ADMINS), CommandStart(), ~F.chat.type.in_(['group', 'supergroup']))
async def wellcome(message: Message, state: FSMContext):
    await state.clear()
    is_reg = await users.user_is_in_table(user_id=message.from_user.id)
    if is_reg:
        user = await users.get_user(message.from_user.id)
        await message.answer(
            text=hello_message.format(
                user=user[-1]
            )
        )
        await main_menu(message, state)

    else:
        text = '''👋 Приветствуем Вас!\nДавайте познакомимся. Как Вас зовут?'''
        await state.set_state(Interview.name)
        await message.answer(
            text=text,
            reply_markup=await kb.build_inline_keyboard([f'Меня зовут {message.from_user.full_name}!'])
        )


async def main_menu(message: Message, state: FSMContext):
    await state.clear()
    keyboard = await kb.build_inline_keyboard(['💻 Заказать сайт', '📞 Наши контакты', '📂 Примеры работ'], (1, 2))
    await message.answer(
        text="🏠 Вы находитесь в главном меню",
        reply_markup=keyboard
    )


@router.message(Command('help'))
async def help(message: Message):
    pass
