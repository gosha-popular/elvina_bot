import hashlib
import os

from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

from data.database import get_user, User, get_db, Admin
from handlers.menu import main_menu, start_message
from handlers.interview import name

router = Router(name=__name__)
router.message.filter(~F.chat.type.in_(['group', 'supergroup']))




@router.message(CommandStart())
async def wellcome(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    user: User = await get_user(message.from_user.id)
    if user:
        await start_message(message, user.name)
    else:
        await name.start(message, state)

@router.message(Command('pin'))
async def pin(message: Message, command: CommandObject, session: AsyncSession):
    try:

        password = command.args

        if not password:
            await message.answer("Пожалуйста, введите пароль после команды /pin")
            return

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        saved_hash = os.getenv('PASSWORD')

        if password_hash == saved_hash:
            await message.answer("Пароль верный! ✅")
            admin = Admin(
                id=message.from_user.id,
                username=message.from_user.username
            )
            session.add(admin)
            await session.commit()
        else:
            await message.answer("Неверный пароль! ❌")

    except Exception as e:
        await message.answer(f"Произошла ошибка при проверке пароля: {str(e)}")




