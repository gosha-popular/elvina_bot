from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from data.groups import add_group
from loader import ADMINS

router = Router(name=__name__)


@router.message(F.from_user.id.in_(ADMINS), Command('add_group'), F.chat.type.in_(['group', 'supergroup']))
async def adding_group(message: Message):
    await add_group(message.chat.id, message.chat.title, True)
    await message.answer(
        text="Эта группа добавлена в список"
    )


@router.message(F.from_user.id.in_(ADMINS), Command('add_group'))
async def adding_group(message: Message):
    await message.answer(
        text="Чтобы добавить группу в список рассылки, во-первых, добавтье бот в группу, во-вторых, введите команду /add_group"
    )


@router.message(F.from_user.id.in_(ADMINS), Command('add_admin'))
async def assign_an_admin(message: Message, command: CommandObject):
    user = ()

    await message.answer(
        text='[name] назначен администратором'
    )

    await message.bot.send_message(
        chat_id=message.chat.id,
        text='Вы назначены администратором'
    )


@router.message(F.from_user.id.in_(ADMINS), Command('del_admin'))
async def assign_an_admin(message: Message, command: CommandObject):
    await message.answer(
        text='[name] разжалован'
    )
