__all__ = ('router', 'questions')

from aiogram import Router

from .name import router as name_router
from .questions import router as question_router
from .phone import router as phone_router


router = Router(name=__name__)

router.include_routers(
    name_router,
    question_router,
    phone_router,
)