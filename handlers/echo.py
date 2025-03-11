from tokenize import group

from aiogram import Router
from aiogram.enums import ChatMemberStatus
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER
from aiogram.types import ChatMemberUpdated
from icecream import ic

router = Router(name=__name__)


